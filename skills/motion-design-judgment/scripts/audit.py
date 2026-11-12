# -*- coding: utf-8 -*-
"""审查用的补充测量。用法: python -I audit.py <id> [bpm]

输出（文本 + <工作目录>/<id>_audit.json）:
  A. 切点 / 脉冲事件 与 音频起音 的重合率（相对随机的提升倍数）
  B. 切点对半拍到八拍各级周期的相位集中度（需要给出 bpm）；切点相对拍网格的帧偏移直方图
  C. 逐帧步进的周期（整帧步进的窗口占比 + 平均频谱在各周期上的突出度）
  D. 每 5 秒窗口里 画面运动量 / 切点数 与 响度 / 起音密度 的相关
  E. 音频段落交界 与 画面大变化 的距离
"""
import sys, os, json
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
WORK = os.environ.get("MOTION_WORK") or os.path.join(os.getcwd(), "motion_work")   # 中间结果目录，可用环境变量 MOTION_WORK 改
BPM = {}   # 需要时在这里按编号填人工核对过的速度；通常直接在命令行给 bpm


def local_norm(env, win):
    k = np.ones(win, dtype=np.float64) / win
    m = np.convolve(env, k, mode="same")
    e = np.maximum(env - m, 0.0)
    return e / (e.std() + 1e-9)


def per_frame(env, sr, pts, fps):
    te = np.arange(len(env)) / sr + 0.0232      # STFT 窗口中心（1024/22050/2 秒）
    h = 0.5 / fps
    lo = np.searchsorted(te, pts - h); hi = np.searchsorted(te, pts + h)
    out = np.zeros(len(pts), dtype=np.float64)
    for i, (a, b) in enumerate(zip(lo, hi)):
        if b > a:
            out[i] = env[a:b].max()
    return out


def strong_onsets(A, q=80):
    nz = A[A > 0]
    if len(nz) < 20:
        return None
    thr = np.percentile(nz, q)
    on = np.zeros(len(A), bool)
    on[1:-1] = (A[1:-1] >= thr) & (A[1:-1] >= A[:-2]) & (A[1:-1] >= A[2:])
    return on


def coincidence(on, idx, tol=1):
    if on is None or len(idx) == 0:
        return None
    near = on.copy()
    for s in range(1, tol + 1):
        near[s:] |= on[:-s]; near[:-s] |= on[s:]
    p = float(near.mean()); m = len(idx); k = int(near[idx].sum())
    z = (k - m * p) / np.sqrt(m * p * (1 - p) + 1e-9)
    return dict(n=m, hit=k, rate=round(k / m, 3), chance=round(p, 3), lift=round((k / m) / (p + 1e-9), 2), z=round(float(z), 1))


def profile(A, idx, lags=range(-4, 5)):
    n = len(A); mu = A.mean() + 1e-9
    out = []
    for L in lags:
        j = idx + L; j = j[(j >= 0) & (j < n)]
        out.append(round(float(A[j].mean() / mu), 2) if len(j) else 0.0)
    return out


def comb_phase(envn, sr, T):
    P = T * sr; n = len(envn)
    ks = np.arange(max(1, int((n - 1 - P) / P)))
    best = (-1.0, 0.0)
    for ph in np.linspace(0, P, int(np.ceil(P)), endpoint=False):
        pos = ph + ks * P; i0 = pos.astype(np.int64); fr = pos - i0
        v = envn[i0] * (1 - fr) + envn[np.minimum(i0 + 1, n - 1)] * fr
        sc = float(v.mean())
        if sc > best[0]:
            best = (sc, float(ph))
    return best[1] / sr, best[0]


def refine_bpm(envn, sr, bpm):
    best = (-1.0, bpm, 0.0)
    for bb in np.arange(bpm - 0.6, bpm + 0.6001, 0.01):
        ph, sc = comb_phase(envn, sr, 60.0 / bb)
        if sc > best[0]:
            best = (sc, float(bb), ph)
    return best[1], best[2], best[0]


def offsets(t, phase, T, fps):
    d = ((t - phase + T / 2.0) % T) - T / 2.0
    return d * fps


def hist_str(off, half):
    b = np.round(off).astype(int)
    lo, hi = -int(np.floor(half)), int(np.floor(half))
    return " ".join(f"{k:+d}:{int((b == k).sum())}" for k in range(lo, hi + 1))


def step_analysis(d, fps):
    win, hop = 24, 12
    counts = {p: 0 for p in (2, 3, 4, 5, 6)}
    active = 0; ranges3 = []
    for s in range(0, len(d) - win, hop):
        w = d[s:s + win]
        if np.median(w) < 0.0006 and w.mean() < 0.003:
            continue
        active += 1
        best_p = 0
        for p in (2, 3, 4, 5, 6):
            med = np.array([np.median(w[k::p]) for k in range(p)])
            order = np.argsort(med)[::-1]
            if med[order[0]] >= 0.004 and med[order[0]] / (med[order[1]] + 0.0005) >= 4.0:
                best_p = p
        if best_p:
            counts[best_p] += 1
            if best_p == 3:
                ranges3.append(s)
    # 平均频谱
    W = 60; han = np.hanning(W)
    acc = np.zeros(W // 2 + 1); nw = 0
    for s in range(0, len(d) - W, 30):
        w = d[s:s + W]
        if w.mean() < 0.003:
            continue
        w = np.minimum(w, np.percentile(w, 92))      # 压掉切点的尖峰
        x = (w - w.mean()) * han
        sp = np.abs(np.fft.rfft(x)) ** 2
        if sp.sum() <= 0:
            continue
        acc += sp / sp.sum(); nw += 1
    spec = {}
    if nw:
        acc /= nw
        base = np.median(acc[6:])
        for p in (2, 2.5, 3, 4, 5, 6):
            k = int(round(W / p))
            spec[str(p)] = round(float(acc[k] / (base + 1e-12)), 2)
    # 3 帧步进的时间段（合并相邻窗口）
    segs = []
    for s in ranges3:
        if segs and s - segs[-1][1] <= hop:
            segs[-1][1] = s + win
        else:
            segs.append([s, s + win])
    return dict(active_windows=active, frac={str(p): round(counts[p] / max(1, active), 3) for p in counts}, spectrum=spec,
                seg3=[(round(a / fps, 1), round(b / fps, 1)) for a, b in segs])


def pearson(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 6 or a[ok].std() == 0 or b[ok].std() == 0:
        return float("nan")
    return float(np.corrcoef(a[ok], b[ok])[0, 1])


def novelty(F, half):
    T = len(F); out = np.zeros(T)
    for t in range(half, T - half):
        out[t] = np.linalg.norm(F[t - half:t].mean(axis=0) - F[t:t + half].mean(axis=0))
    return out


def peaks(x, k, mind):
    order = np.argsort(x)[::-1]; sel = []
    for i in order:
        if x[i] <= 0:
            break
        if all(abs(i - j) >= mind for j in sel):
            sel.append(int(i))
        if len(sel) >= k:
            break
    return sorted(sel)


def tc(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


def main():
    vid = sys.argv[1]
    bpm = float(sys.argv[2]) if len(sys.argv) > 2 else BPM.get(vid)
    meta = json.load(open(os.path.join(WORK, vid + "_meta.json"), encoding="utf-8"))
    S = json.load(open(os.path.join(WORK, vid + "_summary.json"), encoding="utf-8"))
    M = dict(np.load(os.path.join(WORK, vid + "_metrics.npz")))
    A = dict(np.load(os.path.join(WORK, vid + "_audio.npz")))
    pts = M["pts"].astype(np.float64); fps = meta["fps"]; n = len(pts); sr = float(A["env_sr"])
    ev = S["events"]
    cut = np.array([e["frame"] for e in ev if e["kind"] == "cut"], dtype=int)
    fla = np.array([e["frame"] for e in ev if e["kind"].startswith("flash")], dtype=int)
    pul = np.array([e["frame"] for e in ev if e["kind"] == "pulse"], dtype=int)
    out = dict(id=vid, fps=fps, n_cut=len(cut), n_flash=len(fla), n_pulse=len(pul))
    print(f"=== {vid} fps={fps:g} cuts={len(cut)} flash={len(fla)} pulse={len(pul)}")

    # A. 重合率
    envn = A["envn"].astype(np.float64)
    lo = local_norm(A["lo"].astype(np.float64), int(sr)); hi = local_norm(A["hi"].astype(np.float64), int(sr))
    Af = per_frame(envn, sr, pts, fps); Al = per_frame(lo, sr, pts, fps); Ah = per_frame(hi, sr, pts, fps)
    on = strong_onsets(Af); onl = strong_onsets(Al); onh = strong_onsets(Ah); acc = strong_onsets(Af, 96)
    resA = {}
    for name, idx in (("cut", cut), ("flash", fla), ("pulse", pul)):
        c = coincidence(on, idx)
        if c:
            c["profile"] = profile(Af, idx)
            c["low"] = coincidence(onl, idx); c["high"] = coincidence(onh, idx); c["accent"] = coincidence(acc, idx)
            resA[name] = c
            lw = c["low"]["lift"] if c["low"] else float("nan"); hg = c["high"]["lift"] if c["high"] else float("nan")
            ac = c["accent"]
            acs = f"accent±1f {ac['rate'] * 100:3.0f}% (chance {ac['chance'] * 100:2.0f}%, lift {ac['lift']:.2f}, z {ac['z']:+.1f})" if ac else ""
            print(f"A {name:5s} n={c['n']:3d} onset±1f {c['rate'] * 100:4.0f}% (chance {c['chance'] * 100:3.0f}%, lift {c['lift']:.2f}, z {c['z']:+.1f}) | {acs} | low {lw:.2f} high {hg:.2f} | profile -4..+4 {c['profile']}")
    out["A"] = resA

    # B. 拍网格
    if bpm:
        bb, ph, sc = refine_bpm(envn, sr, bpm)
        T = 60.0 / bb; fpb = fps * T
        tcut = pts[cut]
        ob = offsets(tcut, ph, T, fps); o8 = offsets(tcut, ph, T / 2, fps)
        rb = abs(np.exp(2j * np.pi * (tcut - ph) / T).mean()); r8 = abs(np.exp(2j * np.pi * (tcut - ph) / (T / 2)).mean())
        r2 = abs(np.exp(2j * np.pi * (tcut - ph) / (2 * T)).mean())
        # 以众数偏移为中心的集中度
        bins = np.round(ob).astype(int); vals, cnt = np.unique(bins, return_counts=True); mode = int(vals[np.argmax(cnt)])
        within = float((np.abs(ob - mode) <= 0.6).mean()); chance = min(1.0, 1.2 / fpb)
        bins8 = np.round(o8).astype(int); v8, c8 = np.unique(bins8, return_counts=True); mode8 = int(v8[np.argmax(c8)])
        within8 = float((np.abs(o8 - mode8) <= 0.6).mean()); chance8 = min(1.0, 1.2 / (fpb / 2))
        # 分三段看众数是否漂移
        thirds = []
        for a in range(3):
            sel = (tcut >= pts[-1] * a / 3) & (tcut < pts[-1] * (a + 1) / 3)
            if sel.sum() >= 5:
                bsel = np.round(ob[sel]).astype(int); vv, cc = np.unique(bsel, return_counts=True)
                thirds.append(int(vv[np.argmax(cc)]))
            else:
                thirds.append(None)
        mult = (0.5, 1, 1.5, 2, 3, 4, 8)
        Rm = {m: float(abs(np.exp(2j * np.pi * tcut / (T * m)).mean())) for m in mult}
        Rs = "  ".join(f"{m:g}b R={Rm[m]:.2f}(p={np.exp(-len(tcut) * Rm[m] ** 2):.3f})" for m in mult)
        print(f"B bpm {bpm:g} -> {bb:.2f} (frames/beat {fpb:.2f}) | cut phase-lock by period: {Rs}")
        print(f"B beat-offset hist(frames) {hist_str(ob, fpb / 2)} | mode {mode:+d}, within±0.6f {within * 100:.0f}% (chance {chance * 100:.0f}%), mode by thirds {thirds}")
        print(f"B 8th-offset  hist(frames) {hist_str(o8, fpb / 4)} | mode {mode8:+d}, within±0.6f {within8 * 100:.0f}% (chance {chance8 * 100:.0f}%)")
        out["B"] = dict(R_by_period={str(m): round(Rm[m], 3) for m in mult}, bpm=bb, frames_per_beat=fpb, phase=ph, R_beat=float(rb), R_8th=float(r8), R_2beat=float(r2), mode=mode, within=within, chance=chance,
                        mode8=mode8, within8=within8, chance8=chance8, thirds=thirds)

    # C. 步进
    st = step_analysis(M["d_abs"].astype(np.float64), fps)
    seg = st["seg3"]; segs = " ".join(f"{tc(a)}-{tc(b)}" for a, b in seg[:14]) + (" ..." if len(seg) > 14 else "")
    tot3 = sum(b - a for a, b in seg)
    print(f"C stepped-window share (whole-frame) {st['frac']} of {st['active_windows']} active windows | spectrum prominence by period(frames) {st['spectrum']}")
    print(f"C 3-frame stepping segments: total {tot3:.1f}s: {segs}")
    out["C"] = st

    # D. 相关
    W = S["windows"][:-1] if len(S["windows"]) > 3 else S["windows"]
    mot = [w["motion"] for w in W]; cuts5 = [w["cuts"] for w in W]; evs = [w["events"] for w in W]
    rms = [w["rms"] if w["rms"] > -60 else np.nan for w in W]; low = [w["low"] if w["low"] > -60 else np.nan for w in W]
    hig = [w["high"] if w["high"] > -60 else np.nan for w in W]; ons = [w["onset"] for w in W]
    D = dict(motion_rms=pearson(mot, rms), cuts_rms=pearson(cuts5, rms), motion_low=pearson(mot, low), motion_high=pearson(mot, hig),
             cuts_high=pearson(cuts5, hig), events_onset=pearson(evs, ons), luma_rms=pearson([w["luma"] for w in W], rms))
    print("D corr(5s windows): " + "  ".join(f"{k} {v:+.2f}" for k, v in D.items()))
    out["D"] = {k: (None if not np.isfinite(v) else round(v, 3)) for k, v in D.items()}

    # E. 段落
    ch = np.load(os.path.join(WORK, vid + "_colorhist.npy")).astype(np.float64)
    nz = np.where(ch.sum(axis=1) > 0)[0]; ch = ch[: nz.max() + 1]
    H = np.sqrt(ch / (ch.sum(axis=1, keepdims=True) + 1e-9))
    vn = novelty(H, 3)                                   # 1 s 分辨率
    feats = np.stack([np.maximum(A["rms_db"], -40), np.maximum(A["low_db"], -40), np.maximum(A["high_db"], -40)], axis=1).astype(np.float64)
    feats = (feats - feats.mean(axis=0)) / (feats.std(axis=0) + 1e-9)
    an = novelty(feats, 8)                               # 0.5 s 分辨率，前后各 4 s
    dur = pts[-1]
    ap = [p * 0.5 for p in peaks(an, 8, 16) if 4 < p * 0.5 < dur - 4]
    vp = [float(p) for p in peaks(vn, 14, 4)]
    pairs = []
    for a in ap:
        if not vp:
            break
        j = int(np.argmin([abs(a - v) for v in vp])); pairs.append((a, vp[j], vp[j] - a))
    hitE = sum(1 for _, _, dlt in pairs if abs(dlt) <= 1.5)
    chanceE = min(1.0, len(vp) * 3.0 / max(1.0, dur))
    print(f"E audio section boundaries -> nearest big visual change (Δs): " + "  ".join(f"{tc(a)}→{tc(v)}({dlt:+.1f})" for a, v, dlt in pairs)
          + f" | within 1.5s: {hitE}/{len(pairs)} (chance {chanceE * 100:.0f}%)")
    out["E"] = dict(pairs=[(round(a, 1), round(v, 1), round(dlt, 1)) for a, v, dlt in pairs], hit=hitE, n=len(pairs), chance=round(chanceE, 3))
    with open(os.path.join(WORK, vid + "_audit.json"), "w", encoding="utf-8") as fo:
        json.dump(out, fo, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
