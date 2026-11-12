# -*- coding: utf-8 -*-
"""逐帧核对工具。
  python -I seq.py d <id> <f0> <f1> [每行帧数=12]     打印帧间差×1000（· 表示 <0.6 的保持帧，* 表示硬切）
  python -I seq.py bar <id> <bpm> <拍数/周期> [细分=4]   切点在一个周期内的位置直方图（按十六分音符等细分）
  python -I seq.py hold <id> <f0> <f1>                 该范围内「连续保持帧数」的直方图
  python -I seq.py mod <id> <f0> <f1> <m>               该范围内事件帧号对 m 取余的分布
"""
import sys, os, json
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
WORK = os.environ.get("MOTION_WORK") or os.path.join(os.getcwd(), "motion_work")   # 中间结果目录，可用环境变量 MOTION_WORK 改


def load(vid):
    M = dict(np.load(os.path.join(WORK, vid + "_metrics.npz")))
    S = json.load(open(os.path.join(WORK, vid + "_summary.json"), encoding="utf-8"))
    meta = json.load(open(os.path.join(WORK, vid + "_meta.json"), encoding="utf-8"))
    return M, S, meta


def cmd_d(a):
    vid, f0, f1 = a[0], int(a[1]), int(a[2]); per = int(a[3]) if len(a) > 3 else 12
    M, S, meta = load(vid)
    d = M["d_abs"] * 1000; chg = M["chg"]
    cuts = {e["frame"] for e in S["events"] if e["kind"] == "cut"}
    print(f"{vid} frames {f0}-{f1}  fps {meta['fps']:g}  (value = mean abs diff x1000; '·' hold, '*' detected cut)")
    for s in range(f0, f1 + 1, per):
        row = []
        for i in range(s, min(f1 + 1, s + per)):
            v = d[i]
            row.append(("  ·" if v < 0.6 else f"{v:3.0f}") + ("*" if i in cuts else " "))
        print(f"f{s:5d} {M['pts'][s]:7.2f}s | " + " ".join(row))


def cmd_hold(a):
    vid, f0, f1 = a[0], int(a[1]), int(a[2])
    M, S, meta = load(vid)
    d = M["d_abs"][f0:f1 + 1]
    moving = d >= 0.0006
    runs = []; cur = 0
    for mv in moving:
        if mv:
            runs.append(cur + 1); cur = 0     # 一次更新 + 之前的保持帧数 = 这张画面停留的帧数
        else:
            cur += 1
    vals, cnt = np.unique(runs, return_counts=True)
    tot = sum(cnt)
    print(f"{vid} f{f0}-{f1}: frames-per-image histogram (1 = every frame changes): " + "  ".join(f"{v}:{c}({c / tot * 100:.0f}%)" for v, c in zip(vals, cnt) if c / tot >= 0.01))


def cmd_mod(a):
    vid, f0, f1, m = a[0], int(a[1]), int(a[2]), int(a[3])
    M, S, meta = load(vid)
    ev = [e for e in S["events"] if f0 <= e["frame"] <= f1]
    for kind in ("cut", "pulse", "all"):
        fr = [e["frame"] for e in ev if kind == "all" or e["kind"] == kind or (kind == "cut" and e["kind"].startswith("flash"))]
        h = {k: sum(1 for f in fr if (f - f0) % m == k) for k in range(m)}
        print(f"{vid} f{f0}-{f1} {kind:5s} n={len(fr):3d} (frame-f0) mod {m}: {h}")
    print("frames:", " ".join(f"{e['frame'] - f0}{e['kind'][0]}" for e in ev))


def cmd_bar(a):
    vid, bpm, beats = a[0], float(a[1]), float(a[2]); sub = int(a[3]) if len(a) > 3 else 4
    M, S, meta = load(vid)
    pts = M["pts"]; T = 60.0 / bpm; P = T * beats
    nb = int(round(beats * sub))
    for kind in ("cut", "pulse"):
        t = np.array([pts[e["frame"]] for e in S["events"] if e["kind"] == kind])
        if len(t) == 0:
            continue
        pos = ((t % P) / P * nb)
        h = np.bincount(np.round(pos).astype(int) % nb, minlength=nb)
        exp = len(t) / nb
        z = (h - exp) / np.sqrt(exp + 1e-9)
        print(f"{vid} {kind} n={len(t)} position in a {beats:g}-beat cycle ({nb} bins, frames/bin {meta['fps'] * T / sub:.2f}): " + " ".join(f"{c}" for c in h)
              + "  | z: " + " ".join(f"{v:+.1f}" for v in z))


if __name__ == "__main__":
    {"d": cmd_d, "bar": cmd_bar, "hold": cmd_hold, "mod": cmd_mod}[sys.argv[1]](sys.argv[2:])
