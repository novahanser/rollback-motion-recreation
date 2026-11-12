# -*- coding: utf-8 -*-
"""起音包络自相关峰值: python -I acf.py <id> [t0 t1]  -> 列出 0.15-2.5s 内最强的周期"""
import sys, os, numpy as np
WORK = os.environ.get("MOTION_WORK") or os.path.join(os.getcwd(), "motion_work")   # 中间结果目录，可用环境变量 MOTION_WORK 改
vid = sys.argv[1]
A = np.load(os.path.join(WORK, vid + "_audio.npz"))
env = A["envn"].astype(np.float64); sr = float(A["env_sr"])
if len(sys.argv) > 3:
    env = env[int(float(sys.argv[2]) * sr):int(float(sys.argv[3]) * sr)]
env = env - env.mean()
n = len(env)
f = np.fft.rfft(env, 2 * n); acf = np.fft.irfft(f * np.conj(f))[:n]; acf /= acf[0]
lo, hi = int(0.15 * sr), min(n - 2, int(2.5 * sr))
peaks = [(acf[i], i) for i in range(lo, hi) if acf[i] > acf[i - 1] and acf[i] >= acf[i + 1]]
peaks.sort(reverse=True)
print(vid, "ACF peaks (lag s -> bpm if beat; value):")
for v, i in peaks[:14]:
    # 抛物线插值
    d = (acf[i - 1] - acf[i + 1]) / (2 * (acf[i - 1] - 2 * acf[i] + acf[i + 1]) + 1e-12)
    lag = (i + d) / sr
    print(f"  {lag:.4f}s  {60 / lag:7.2f} bpm  x2={120 / lag:7.2f}  x4={240 / lag:7.2f}   {v:.3f}")
