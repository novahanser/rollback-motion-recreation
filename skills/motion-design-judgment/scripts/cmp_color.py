# -*- coding: utf-8 -*-
"""逐帧比较两段对齐的视频在「原片的高彩度像素」上的颜色差。
用法: python -I cmp_color.py <参考视频> <参考起始秒> <被比视频> <帧数> [标签]"""
import sys, os, subprocess
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
FF = os.environ.get("FFMPEG_DIR", "")   # ffmpeg 不在 PATH 里时，把环境变量 FFMPEG_DIR 指到它所在的目录
FFMPEG = os.path.join(FF, "ffmpeg") if FF else "ffmpeg"
FFPROBE = os.path.join(FF, "ffprobe") if FF else "ffprobe"
def frames(path, ss, n, w=320, h=180):
    cmd = [FFMPEG, "-v", "error", "-ss", f"{ss:.4f}", "-i", path, "-map", "0:v:0", "-frames:v", str(n),
           "-vf", f"scale={w}:{h}:in_color_matrix=bt709:flags=area,format=rgb24", "-f", "rawvideo", "-"]
    raw = subprocess.check_output(cmd)
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3).astype(np.int32)
ref, ss, test, n = sys.argv[1], float(sys.argv[2]), sys.argv[3], int(sys.argv[4]); tag = sys.argv[5] if len(sys.argv) > 5 else ""
A = frames(ref, ss, n); B = frames(test, 0.0, n)
k = min(len(A), len(B)); A, B = A[:k], B[:k]
mx = A.max(axis=3); mn = A.min(axis=3); sat = (mx - mn) > 90
bs = (B.max(axis=3) - B.min(axis=3)) > 90
both = sat & bs                                     # 两边都是高彩度的像素（避开重绘素材位置不同的区域）
d = np.abs(A - B)
print(f"{tag:26s} frames {k} | all px: mean|ΔRGB| {d.mean():.2f} | ref-saturated px ({sat.mean() * 100:.1f}%): {d[sat].mean():.2f} | both-saturated px ({both.mean() * 100:.1f}%): ΔR {d[both][:, 0].mean():.1f} ΔG {d[both][:, 1].mean():.1f} ΔB {d[both][:, 2].mean():.1f} mean {d[both].mean():.2f}")
# 色相分组（玫红 / 蓝）
def hue_sel(X, lo, hi):
    r, g, b = X[..., 0], X[..., 1], X[..., 2]
    return (r > 150) & (g < 90) & (b > 60) & (b < 170) if lo == "rose" else (b > 150) & (r < 140) & (g < 170)
for name in ("rose", "blue"):
    s = both & hue_sel(A, name, None)
    if s.sum() > 500:
        print(f"    {name}: ref mean {tuple(int(v) for v in A[s].mean(axis=0).round())}  test mean {tuple(int(v) for v in B[s].mean(axis=0).round())}  mean|Δ| {np.abs(A[s] - B[s]).mean():.1f}  ({s.mean() * 100:.1f}% of px)")
