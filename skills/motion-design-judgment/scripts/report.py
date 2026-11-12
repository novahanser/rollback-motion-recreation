# -*- coding: utf-8 -*-
"""根据扫描结果输出一个视频的量化摘要（文本 + JSON）。

用法: python -I report.py <id> [win_s=5] [bpm=手动指定]
"""
import sys, os, json
import numpy as np
import cv2
sys.stdout.reconfigure(encoding="utf-8")

WORK = os.environ.get("MOTION_WORK") or os.path.join(os.getcwd(), "motion_work")   # 中间结果目录，可用环境变量 MOTION_WORK 改


def rolling_median(x, half):
    n = len(x); out = np.empty(n, dtype=np.float32)
    for i in range(n):
        a = max(0, i - half); b = min(n, i + half + 1)
        seg = np.concatenate([x[a:i], x[i + 1:b]])
        out[i] = np.median(seg) if len(seg) else 0.0
    return out


def detect_events(M):
    d = M["d_abs"]; dh = M["d_hist"]; chg = M["chg"]; d2 = M["d2"]
    n = len(d)
    base = rolling_median(d, 8)
    ev = []
    for i in range(1, n - 1):
        if d[i] < 0.012 or d[i] < 2.5 * base[i] + 0.006:
            continue
        a = max(0, i - 2); b = min(n, i + 3)
        if d[i] < d[a:b].max():
            continue
        kind = "pulse"
        if dh[i] >= 0.30 or chg[i] >= 0.45:
            kind = "cut"
        # 单帧插入：i 帧与前一帧差别大，i+1 帧又回到接近 i-1 帧
        if i + 1 < n and d[i + 1] > 0.5 * d[i] and d2[i + 1] < 0.35 * d[i]:
            kind = "flash1"
        elif i + 2 < n and kind == "cut":
            # 两帧插入：i+2 帧与 i-1 相近（用 d 近似判断：i+2 再次大变且 i+1 稳定）
            if d[i + 1] < 0.3 * d[i] and d[i + 2] > 0.6 * d[i]:
                kind = "flash2"
        ev.append((i, kind, float(d[i]), float(dh[i]), float(chg[i])))
    return ev, base


def hold_stats(M):
    d = M["d_abs"]; n = len(d)
    eps = 0.0006
    still = d < eps
    res = {"still_frac": float(still.mean())}
    # 孤立的保持帧：前后都在动、自身不动（=按二拍一动），或连续两帧不动（=一拍三）
    iso1 = 0; iso2 = 0; moving = 0
    i = 1
    while i < n - 2:
        if d[i] >= 0.004:
            moving += 1
        if d[i - 1] >= 0.004 and d[i] < 0.25 * d[i - 1] and d[i] < 0.002:
            if d[i + 1] >= 0.004:
                iso1 += 1
            elif i + 2 < n and d[i + 1] < 0.002 and d[i + 2] >= 0.004:
                iso2 += 1
        i += 1
    res["moving_frac"] = float(moving / n)
    res["hold1_per_moving"] = float(iso1 / max(1, moving))
    res["hold2_per_moving"] = float(iso2 / max(1, moving))
    # 运动帧序列的周期性：归一化后在滞后 2/3/4 的自相关
    x = np.log(d + 1e-4); x = x - x.mean()
    ac = {}
    for lag in (1, 2, 3, 4, 5, 6):
        ac[lag] = float((x[:-lag] * x[lag:]).mean() / (x.var() + 1e-9))
    res["logdiff_autocorr"] = {k: round(v, 3) for k, v in ac.items()}
    return res


def rayleigh(times, period):
    if len(times) == 0:
        return 0.0, 0.0
    ph = 2 * np.pi * (np.asarray(times) / period)
    z = np.exp(1j * ph).mean()
    return float(abs(z)), float(np.angle(z))


def palette(hist, k=8, iters=25):
    idx = np.arange(4096)
    rgb = np.stack([(idx >> 8) * 17, ((idx >> 4) & 15) * 17, (idx & 15) * 17], axis=1).astype(np.uint8)
    w = hist.astype(np.float64)
    keep = w > 0
    rgbk = rgb[keep]; wk = w[keep]
    lab = cv2.cvtColor(rgbk.reshape(-1, 1, 3), cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float64)
    # 贪心初始化：权重大且互相远
    order = np.argsort(wk)[::-1]
    cents = [lab[order[0]]]
    for _ in range(1, min(k, len(lab))):
        dist = np.min(np.stack([np.linalg.norm(lab - c, axis=1) for c in cents]), axis=0)
        score = dist * np.sqrt(wk / wk.max())
        cents.append(lab[np.argmax(score)])
    cents = np.array(cents)
    for _ in range(iters):
        dd = np.linalg.norm(lab[:, None, :] - cents[None, :, :], axis=2)
        asg = dd.argmin(axis=1)
        for j in range(len(cents)):
            sel = asg == j
            if sel.any():
                cents[j] = (lab[sel] * wk[sel, None]).sum(axis=0) / wk[sel].sum()
    out = []
    for j in range(len(cents)):
        sel = asg == j
        if not sel.any():
            continue
        share = wk[sel].sum() / wk.sum()
        c = (rgbk[sel].astype(np.float64) * wk[sel, None]).sum(axis=0) / wk[sel].sum()
        out.append((share, "#%02X%02X%02X" % tuple(int(round(v)) for v in c)))
    out.sort(reverse=True)
    return out


def main():
    vid = sys.argv[1]
    win = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
    manual_bpm = float(sys.argv[3]) if len(sys.argv) > 3 else None
    meta = json.load(open(os.path.join(WORK, vid + "_meta.json"), encoding="utf-8"))
    M = dict(np.load(os.path.join(WORK, vid + "_metrics.npz")))
    A = dict(np.load(os.path.join(WORK, vid + "_audio.npz")))
    AJ = json.load(open(os.path.join(WORK, vid + "_audio.json"), encoding="utf-8"))
    pts = M["pts"]; fps = meta["fps"]; n = len(pts); dur = float(pts[-1])
    print(f"=== {vid}  {meta['width']}x{meta['height']}  fps={fps:.3f}  frames={n}  dur={dur:.2f}s")
    ev, base = detect_events(M)
    cuts = [e for e in ev if e[1] in ("cut", "flash1", "flash2")]
    hard = [e for e in ev if e[1] == "cut"]
    fl = [e for e in ev if e[1].startswith("flash")]
    print(f"events={len(ev)} (cut={len(hard)}, flash={len(fl)}, pulse={len(ev) - len(cuts)})  cut/min={len(hard) / dur * 60:.1f}  events/min={len(ev) / dur * 60:.1f}")
    ct = np.array([pts[e[0]] for e in hard])
    if len(ct) > 2:
        sl = np.diff(ct)
        q = np.percentile(sl, [10, 25, 50, 75, 90])
        print("shot length s  p10/25/50/75/90 = " + "/".join(f"{v:.2f}" for v in q) + f"  max={sl.max():.2f}  (frames p50={q[2] * fps:.1f})")
        # 以帧为单位的镜头长度直方图（最常见的几个值）
        slf = np.round(sl * fps).astype(int)
        vals, cnt = np.unique(slf, return_counts=True)
        top = sorted(zip(cnt, vals), reverse=True)[:10]
        print("most common shot lengths (frames:count) = " + ", ".join(f"{v}:{c}" for c, v in top))
    hs = hold_stats(M)
    print("holds:", json.dumps(hs, ensure_ascii=False))
    # 节拍与同步
    cands = AJ["tempo_candidates"]
    print("tempo candidates (bpm, acf, comb, phase_s): " + "; ".join(f"{c['bpm']}/{c['acf_score']}/{c['comb_score']}/{c['phase_s']}" for c in cands))
    te_all = np.array([pts[e[0]] for e in ev]); te_cut = ct
    test_bpms = []
    if manual_bpm:
        test_bpms.append(manual_bpm)
    for c in cands[:5]:
        for mult in (1.0, 2.0, 0.5, 1.5, 2.0 / 3.0, 4.0 / 3.0, 0.75):
            b = c["bpm"] * mult
            if 70 <= b <= 240 and all(abs(b - t) > 0.6 for t in test_bpms):
                test_bpms.append(b)
    rows = []
    for b in test_bpms:
        # 用视觉事件微调 BPM
        best = (0, b)
        for bb in np.arange(b - 0.8, b + 0.8001, 0.004):
            r, _ = rayleigh(te_all, 60.0 / bb)
            if r > best[0]:
                best = (r, bb)
        bb = best[1]
        T = 60.0 / bb
        r1, p1 = rayleigh(te_all, T); r2, _ = rayleigh(te_all, T / 2); r4, _ = rayleigh(te_all, T / 4)
        rc1, _ = rayleigh(te_cut, T); rc2, _ = rayleigh(te_cut, T / 2)
        rb, _ = rayleigh(te_all, T * 4)
        rows.append((r1, b, bb, r2, r4, rc1, rc2, rb, p1))
    rows.sort(reverse=True)
    print(f"visual-event phase locking (N events={len(te_all)}, cuts={len(te_cut)}); R=Rayleigh 向量长度, 0=无关 1=完全锁定")
    print("  bpm_audio -> bpm_vis   R_beat  R_1/2  R_1/4  Rcut_beat Rcut_1/2 R_bar  frames/beat")
    for r1, b, bb, r2, r4, rc1, rc2, rb, p1 in rows[:8]:
        print(f"  {b:8.2f} -> {bb:8.3f}  {r1:.3f}  {r2:.3f}  {r4:.3f}   {rc1:.3f}    {rc2:.3f}   {rb:.3f}   {fps * 60 / bb:.3f}")
    # 分窗表
    env_sr = float(A["env_sr"])
    nw = int(np.ceil(dur / win))
    print(f"--- window table ({win:g}s): t | motion*1000 | events cuts | luma sat | white black color | edge*100 | rms_dB low_dB high_dB | onset")
    seg = 0.5
    table = []
    for wi in range(nw):
        a = wi * win; b = a + win
        sel = (pts >= a) & (pts < b)
        if not sel.any():
            continue
        ne = sum(1 for e in ev if a <= pts[e[0]] < b); nc = sum(1 for e in hard if a <= pts[e[0]] < b)
        sa = int(a / seg); sb = max(sa + 1, int(b / seg))
        rms = float(A["rms_db"][sa:sb].mean()) if sa < len(A["rms_db"]) else float("nan")
        low = float(A["low_db"][sa:sb].mean()) if sa < len(A["low_db"]) else float("nan")
        high = float(A["high_db"][sa:sb].mean()) if sa < len(A["high_db"]) else float("nan")
        ons = float(A["onset_rate"][sa:sb].mean()) if sa < len(A["onset_rate"]) else float("nan")
        row = dict(t=a, motion=float(M["d_abs"][sel].mean() * 1000), events=ne, cuts=nc, luma=float(M["luma"][sel].mean()),
                   sat=float(M["sat"][sel].mean()), white=float(M["white"][sel].mean()), black=float(M["black"][sel].mean()),
                   color=float(M["color"][sel].mean()), edge=float(M["edge"][sel].mean() * 100), rms=rms, low=low, high=high, onset=ons)
        table.append(row)
        print(f"{int(a // 60)}:{a % 60:04.1f} | {row['motion']:6.1f} | {ne:3d} {nc:3d} | {row['luma']:.2f} {row['sat']:.2f} | {row['white']:.2f} {row['black']:.2f} {row['color']:.2f} | {row['edge']:5.2f} | {rms:6.1f} {low:6.1f} {high:6.1f} | {ons:.2f}")
    # 调色板
    ch = np.load(os.path.join(WORK, vid + "_colorhist.npy")).astype(np.float64)
    nz = np.where(ch.sum(axis=1) > 0)[0]; ch = ch[: nz.max() + 1]
    pal = palette(ch.sum(axis=0), k=8)
    print("palette(all): " + "  ".join(f"{h} {s * 100:.0f}%" for s, h in pal))
    idx = np.arange(4096)
    rr = (idx >> 8) * 17; gg = ((idx >> 4) & 15) * 17; bb_ = (idx & 15) * 17
    chroma = np.maximum(np.maximum(rr, gg), bb_) - np.minimum(np.minimum(rr, gg), bb_)
    tot_all = ch.sum()
    hs_ = ch.sum(axis=0) * (chroma >= 85)
    if hs_.sum() > 0:
        acc = palette(hs_, k=6)
        frac = hs_.sum() / tot_all
        print(f"accents(chroma>=85, {frac * 100:.1f}% of pixels): " + "  ".join(f"{h} {s * frac * 100:.1f}%" for s, h in acc))
    parts = 4
    pals = []
    for pi in range(parts):
        a = int(len(ch) * pi / parts); b = int(len(ch) * (pi + 1) / parts)
        pp = palette(ch[a:b].sum(axis=0), k=6)
        pals.append(pp)
        hp = ch[a:b].sum(axis=0) * (chroma >= 85)
        accs = ""
        if hp.sum() > 0:
            fr_ = hp.sum() / ch[a:b].sum()
            accs = "  || accents: " + "  ".join(f"{h} {s * fr_ * 100:.1f}%" for s, h in palette(hp, k=4))
        print(f"palette({a}-{b}s): " + "  ".join(f"{h} {s * 100:.0f}%" for s, h in pp) + accs)
    summ = dict(meta=meta, n_events=len(ev), n_cuts=len(hard), n_flash=len(fl), holds=hs, tempo_candidates=cands,
                sync=[dict(bpm_audio=round(b, 3), bpm_vis=round(bb, 3), R_beat=round(r1, 3), R_half=round(r2, 3), R_quarter=round(r4, 3),
                           Rcut_beat=round(rc1, 3), R_bar=round(rb, 3)) for r1, b, bb, r2, r4, rc1, rc2, rb, p1 in rows[:8]],
                windows=table, palette=[(round(s, 4), h) for s, h in pal],
                events=[dict(frame=int(e[0]), t=round(float(pts[e[0]]), 3), kind=e[1], d=round(e[2], 4), dh=round(e[3], 3), chg=round(e[4], 3)) for e in ev])
    with open(os.path.join(WORK, vid + "_summary.json"), "w", encoding="utf-8") as fo:
        json.dump(summ, fo, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
