# -*- coding: utf-8 -*-
"""分段速度：python -I tempo_track.py <id> [窗长秒=12] [步长秒=6] [bpm下限=150] [bpm上限=240]
每个窗口在给定范围内找梳状相关最高的 BPM，用来看曲速是否变化。"""
import sys, os, numpy as np
sys.stdout.reconfigure(encoding="utf-8")
W = os.environ.get("MOTION_WORK") or os.path.join(os.getcwd(), "motion_work")   # 中间结果目录，可用环境变量 MOTION_WORK 改
vid = sys.argv[1]; win = float(sys.argv[2]) if len(sys.argv) > 2 else 12.0; hop = float(sys.argv[3]) if len(sys.argv) > 3 else 6.0
lo = float(sys.argv[4]) if len(sys.argv) > 4 else 150.0; hi = float(sys.argv[5]) if len(sys.argv) > 5 else 240.0
A = np.load(os.path.join(W, vid + "_audio.npz")); env = A["envn"].astype(np.float64); sr = float(A["env_sr"])
def acf_bpm(x):
    x = x - x.mean(); n = len(x)
    f = np.fft.rfft(x, 2 * n); ac = np.fft.irfft(f * np.conj(f))[:n]; ac /= ac[0] + 1e-9
    best = (-1, 0)
    for b in np.arange(lo, hi + 0.01, 0.25):
        L = 60.0 / b * sr; s = 0.0
        for m, wgt in ((1, 1.0), (2, 0.8), (4, 0.6), (8, 0.4)):
            xx = L * m; i0 = int(xx); fr = xx - i0
            if i0 + 1 < n: s += wgt * (ac[i0] * (1 - fr) + ac[i0 + 1] * fr)
        if s > best[0]: best = (s, b)
    return best[1], best[0]
dur = len(env) / sr; t = 0.0; out = []
while t + win <= dur:
    seg = env[int(t * sr):int((t + win) * sr)]
    if seg.std() > 1e-6:
        b, s = acf_bpm(seg); out.append((t, b, s))
    t += hop
print(vid, f"range {lo:g}-{hi:g} BPM, window {win:g}s:")
print("  " + "  ".join(f"{int(t // 60)}:{int(t % 60):02d}→{b:.1f}({s:.1f})" for t, b, s in out))
