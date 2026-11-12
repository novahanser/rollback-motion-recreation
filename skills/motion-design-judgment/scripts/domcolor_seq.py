# -*- coding: utf-8 -*-
"""逐帧打印画面里面积最大的两种颜色，用来看大色块的颜色是每帧都在变，还是每隔几帧换一次。

用法: python -I domcolor_seq.py <编号> <起始帧> <结束帧> [每行帧数=8]
做法: 每帧缩到 320 宽，颜色按 4 bit/通道量化，取像素最多的两个箱各自的中位色和占比。
最后一行给出「前两大颜色的组合」连续保持了几帧。相机在动的镜头里，帧间差分不出换色和运动，用这个脚本。"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.stdout.reconfigure(encoding="utf-8")
import vis
vid, f0, f1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); per = int(sys.argv[4]) if len(sys.argv) > 4 else 8
m = vis.meta(vid)
frames = vis.read_frames(m, f0, f1 - f0 + 1, 320)
out = []; prev = None; runs = []; run = 1
for i, im in enumerate(frames):
    px = np.array(im).reshape(-1, 3).astype(np.int32)
    key = ((px[:, 0] >> 4) << 8) | ((px[:, 1] >> 4) << 4) | (px[:, 2] >> 4)
    c = np.bincount(key, minlength=4096); order = np.argsort(c)[::-1][:2]
    cols = []
    for b in order:
        md = np.median(px[key == b], 0).astype(int); cols.append(f"#{md[0]:02X}{md[1]:02X}{md[2]:02X}:{c[b] / len(px) * 100:.0f}%")
    sig = tuple(int(b) for b in order)
    if prev is not None:
        if set(sig) == set(prev): run += 1
        else: runs.append(run); run = 1
    prev = sig
    out.append(f"f{f0 + i} " + " ".join(cols))
runs.append(run)
for k in range(0, len(out), per): print("  " + " | ".join(out[k:k + per]))
print("  前两大颜色组合连续保持的帧数:", runs)
