# -*- coding: utf-8 -*-
"""逐帧打印音频的起音强度，和同一帧的帧间差排在一起，用来核对某几帧画面上的事件是否落在起音上。

用法: python -I onset_at.py <编号> <起始帧> <结束帧> [每行帧数=12]
标记: # = 全片起音强度最高的 4% 的帧（重音）；* = 最高的 20% 里的局部峰值。
需要先跑过 scan_video.py 和 scan_audio.py。起音强度是按频谱变化估计的，不是听出来的。"""
import os, sys, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.stdout.reconfigure(encoding="utf-8")
import audit
vid, f0, f1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); per = int(sys.argv[4]) if len(sys.argv) > 4 else 12
W = audit.WORK
meta = json.load(open(os.path.join(W, vid + "_meta.json"), encoding="utf-8"))
M = dict(np.load(os.path.join(W, vid + "_metrics.npz"))); A = dict(np.load(os.path.join(W, vid + "_audio.npz")))
pts = M["pts"].astype(float); fps = meta["fps"]; sr = float(A["env_sr"])
Af = audit.per_frame(A["envn"].astype(float), sr, pts, fps)
acc = audit.strong_onsets(Af, 96); on = audit.strong_onsets(Af, 80)
d = M["d_abs"]
print(f"{vid} f{f0}-{f1}: onset strength x10 per frame ('#' top-4% accent, '*' top-20% onset peak) / frame diff x1000")
for a in range(f0, f1 + 1, per):
    b = min(f1 + 1, a + per)
    s1 = " ".join(f"{Af[i] * 10:4.0f}{'#' if acc[i] else ('*' if on[i] else ' ')}" for i in range(a, b))
    s2 = " ".join(f"{d[i] * 1000:4.0f} " for i in range(a, b))
    print(f"f{a:5d} {pts[a]:7.2f}s on | {s1}\n{'':16s}df | {s2}")
