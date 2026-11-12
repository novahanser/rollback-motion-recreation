# -*- coding: utf-8 -*-
"""找出「只停一帧的画面」，并按它和前后两帧的关系分类。

用法: python -I oneframe.py <编号> [输出.csv] [-q]

一帧画面: 进入它和离开它都是硬变化的帧。硬变化的门槛与 report.py 判硬切时相同（帧间差明显高于邻近帧，
并且色彩直方图或半数像素发生了变化），但不做「邻近取最大」的抑制，所以相邻的硬变化都保留。
连续的一帧画面合成一「串」；超过 6 帧的串只报起止（多半是高速运动或频闪，要另外看）。

对每个一帧画面 B（前一帧 A，后一帧 C）量:
  AC      A 与 C 的相关。高 = 镜头内的闪（闪完回到原来的画面）；低 = 落在切点上
  inv     255-B 与 A（或 C）的相关。高 = B 是相邻画面的反相
  eA、eC  B 的边缘图与 A、C 的边缘图的相关。高 = 版式留下来了，换的是底或颜色
  纯色、二值   B 是不是几乎只有一个颜色；是不是只有黑白两级
分类只是候选: 纯色帧 / 反相 / 二值版本 / 同版式换底换色 / 另一幅画面。每一类都要抽帧看过再用。
需要先跑过 scan_video.py；有 scan_audio.py 的结果时，顺带统计它们落在重音上的比例。
"""
import os, sys, json, csv
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
import vis  # noqa: E402

WORK = vis.WORK
LUM = np.array([0.299, 0.587, 0.114], dtype=np.float32)


def rolling_q(x, half, q):
    n = len(x); out = np.empty(n, dtype=np.float32)
    for i in range(n):
        a = max(0, i - half); b = min(n, i + half + 1)
        seg = np.concatenate([x[a:i], x[i + 1:b]])
        out[i] = np.percentile(seg, q) if len(seg) else 0.0
    return out


def feats(im):
    a = np.asarray(im).astype(np.float32)
    g = a @ LUM
    chroma = a.max(2) - a.min(2)
    e = np.abs(np.diff(g, axis=1))[:-1, :] + np.abs(np.diff(g, axis=0))[:, :-1]
    return dict(g=g, e=e, luma=float(g.mean() / 255), std=float(g.std() / 255), chroma=float(chroma.mean() / 255),
                bil=float((((g < 40) | (g > 215)) & (chroma < 40)).mean()), rgb=np.median(a.reshape(-1, 3), 0))


def corr(x, y):
    x = x.ravel() - x.mean(); y = y.ravel() - y.mean()
    d = float(np.sqrt((x * x).sum() * (y * y).sum()))
    return float((x * y).sum() / d) if d > 1e-6 else 0.0


def classify(A, B, C):
    ac = corr(A["g"], C["g"])
    inv_a = corr(255.0 - B["g"], A["g"]); inv_c = corr(255.0 - B["g"], C["g"])
    ea = corr(A["e"], B["e"]); ec = corr(B["e"], C["e"])
    r, g, b = (int(v) for v in B["rgb"])
    if B["std"] < 0.035:
        if B["luma"] > 0.85 and B["chroma"] < 0.08:
            kind = "纯色帧:白"
        elif B["luma"] < 0.10:
            kind = "纯色帧:黑"
        else:
            kind = f"纯色帧:#{r:02X}{g:02X}{b:02X}"
    elif max(inv_a, inv_c) >= 0.55:
        kind = "反相"
    elif B["bil"] >= 0.90 and max(A["bil"] if ea >= ec else C["bil"], 0) < 0.75 and max(ea, ec) >= 0.20:
        kind = "二值版本"
    elif max(ea, ec) >= 0.40:
        kind = "同版式换底换色"
    else:
        kind = "另一幅画面"
    if ac >= 0.75:
        ctx = "镜头内"
    else:
        ctx = "切点上"
        if max(ea, ec, inv_a, inv_c) >= 0.35:
            ctx += "·像前一个镜头" if max(ea, inv_a) >= max(ec, inv_c) else "·像后一个镜头"
        else:
            ctx += "·两边都不像"
    return kind, ctx, ac, max(inv_a, inv_c), ea, ec


def main():
    args = [a for a in sys.argv[1:] if a != "-q"]; quiet = "-q" in sys.argv
    vid = args[0]; outcsv = args[1] if len(args) > 1 else None
    m = vis.meta(vid)
    M = dict(np.load(os.path.join(WORK, vid + "_metrics.npz")))
    d = M["d_abs"]; dh = M["d_hist"]; chg = M["chg"]; pts = M["pts"].astype(float); n = len(d)
    fps = m["fps"]
    base = rolling_q(d, 8, 25)
    hard = (d >= 0.012) & ((dh >= 0.30) | (chg >= 0.45)) & ((d >= 2.5 * base + 0.006) | ((chg >= 0.80) & (dh >= 0.50)))
    hard[0] = False
    one = np.zeros(n, bool); one[1:n - 1] = hard[1:n - 1] & hard[2:n]
    runs = []; i = 1
    while i < n - 1:
        if one[i]:
            j = i
            while j + 1 < n - 1 and one[j + 1]:
                j += 1
            runs.append((i, j)); i = j + 1
        else:
            i += 1
    acc = None
    ap = os.path.join(WORK, vid + "_audio.npz")
    if os.path.exists(ap):
        try:
            import audit
            A = dict(np.load(ap))
            Af = audit.per_frame(A["envn"].astype(float), float(A["env_sr"]), pts, fps)
            acc = audit.strong_onsets(Af, 96)
        except Exception:
            acc = None
    rows = []; longs = []
    for a, b in runs:
        k = b - a + 1
        if k > 6:
            fr = [feats(im) for im in vis.read_frames(m, a, min(k, 24), 320)]
            alt = float(np.mean([corr(fr[t]["g"], fr[t + 2]["g"]) for t in range(len(fr) - 2)])) if len(fr) > 2 else 0.0
            adj = float(np.mean([corr(fr[t]["g"], fr[t + 1]["g"]) for t in range(len(fr) - 1)]))
            longs.append((a, b, k, alt, adj)); continue
        fr = [feats(im) for im in vis.read_frames(m, a - 1, k + 2, 320)]
        if len(fr) < k + 2:
            continue
        for t in range(k):
            A_, B_, C_ = fr[t], fr[t + 1], fr[t + 2]
            kind, ctx, ac, inv, ea, ec = classify(A_, B_, C_)
            f = a + t
            hit = bool(acc is not None and acc[max(0, f - 1):f + 2].any())
            rows.append(dict(id=vid, frame=f, t=round(float(pts[f]), 3), run=k, pos=t + 1, kind=kind, ctx=ctx,
                             AC=round(ac, 2), inv=round(inv, 2), eA=round(ea, 2), eC=round(ec, 2),
                             lumaA=round(A_["luma"], 2), lumaB=round(B_["luma"], 2), lumaC=round(C_["luma"], 2),
                             accent=int(hit)))
    dur = float(pts[-1])
    print(f"{vid}: {n} 帧, {dur:.0f} 秒, 硬变化 {int(hard.sum())} 次; 一帧画面 {len(rows)} 个（{len(rows) / dur * 60:.1f} 个/分钟）,"
          f" 分成 {len(set((r['frame'] - r['pos']) for r in rows))} 串; 超过 6 帧的长串 {len(longs)} 段")
    from collections import Counter
    ck = Counter(r["kind"].split(":")[0] for r in rows); cc = Counter(r["ctx"].split("·")[0] for r in rows)
    cr = Counter(r["run"] for r in rows if r["pos"] == 1)
    print("  类别: " + ", ".join(f"{k} {v}" for k, v in ck.most_common()))
    print("  位置: " + ", ".join(f"{k} {v}" for k, v in cc.most_common()) + " | 串长: " + ", ".join(f"{k} 帧×{v}" for k, v in sorted(cr.items())))
    if acc is not None and len(rows) >= 8:
        p0 = float(np.mean([acc[max(0, f - 1):f + 2].any() for f in range(1, n - 1)]))
        p1 = float(np.mean([r["accent"] for r in rows]))
        print(f"  落在重音上（前后 1 帧）: {p1 * 100:.0f}%，随机水平 {p0 * 100:.0f}%，{p1 / p0 if p0 > 0 else 0:.1f} 倍")
    for a, b, k, alt, adj in longs:
        what = "两幅画面交替（频闪）" if alt >= 0.75 and adj < 0.6 else "每帧都不同（高速运动或逐帧换画面）"
        print(f"  长串 f{a}-{b}（{pts[a]:.2f}—{pts[b]:.2f} 秒，{k} 帧）: 隔帧相关 {alt:.2f}，邻帧相关 {adj:.2f} → {what}")
    if not quiet:
        for r in rows:
            print(f"  f{r['frame']:5d} {vis.tc(r['t'])} 串{r['run']}/{r['pos']} {r['kind']:<12} {r['ctx']:<14} AC={r['AC']:.2f} inv={r['inv']:.2f}"
                  f" eA={r['eA']:.2f} eC={r['eC']:.2f} 亮度 {r['lumaA']:.2f}>{r['lumaB']:.2f}>{r['lumaC']:.2f}{' #' if r['accent'] else ''}")
    if outcsv and rows:
        new = not os.path.exists(outcsv)
        with open(outcsv, "a", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            if new:
                w.writeheader()
            w.writerows(rows)


if __name__ == "__main__":
    main()
