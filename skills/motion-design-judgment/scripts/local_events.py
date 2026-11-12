# -*- coding: utf-8 -*-
"""逐帧找画面里「局部」的变化：一个字、一个小图形的出现、替换或消失。整帧的帧间差看不出这类小事件。

用法: python -I local_events.py <编号> <起始帧> <结束帧> [宽=960] [阈值=28] [x0,y0,x1,y1 只看这个区域(0-1)]

每帧输出: 变化像素占比(‰)、变化区域的包围盒（占画面的百分比位置）、变化块的个数。
  没有变化的帧记作「·」。连续的「·」就是这块区域的停留时间。
做法: 相邻两帧转灰度、轻微模糊后相减，超过阈值的像素做一次开运算去掉孤立噪点，再取连通域。
相机在动的镜头里整帧都在变，这个脚本就没有意义了；它适合构图不动、元素逐个进出的镜头。
"""
import os, sys
import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
import vis


def main():
    vid, f0, f1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    W = int(sys.argv[4]) if len(sys.argv) > 4 else 960
    thr = int(sys.argv[5]) if len(sys.argv) > 5 else 28
    crop = [float(v) for v in sys.argv[6].split(",")] if len(sys.argv) > 6 else None
    m = vis.meta(vid)
    frames = vis.read_frames(m, f0 - 1, f1 - f0 + 2, W)
    prev = None
    print(f"{vid} f{f0}-{f1} fps {m['fps']:g}  (变化像素‰ | 包围盒 x%..x% y%..y% | 块数)  「·」= 没有局部变化")
    run = 0; out = []
    for i, im in enumerate(frames):
        g = cv2.GaussianBlur(cv2.cvtColor(np.array(im), cv2.COLOR_RGB2GRAY), (3, 3), 0).astype(np.int16)
        if crop:
            H0, W0 = g.shape
            g = g[int(crop[1] * H0):int(crop[3] * H0), int(crop[0] * W0):int(crop[2] * W0)]
        if prev is not None:
            n = f0 - 1 + i
            d = (np.abs(g - prev) > thr).astype(np.uint8)
            d = cv2.morphologyEx(d, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
            cnt = int(d.sum()); H, Wd = d.shape
            if cnt < max(6, 0.00004 * H * Wd):
                out.append(f"f{n}:·")
            else:
                ys, xs = np.nonzero(d)
                nlab, lab, stats, _ = cv2.connectedComponentsWithStats(cv2.dilate(d, np.ones((9, 9), np.uint8)), connectivity=8)
                blobs = int((stats[1:, cv2.CC_STAT_AREA] > 60).sum())
                up = float((g[d > 0] - prev[d > 0]).mean())
                out.append(f"f{n}:{cnt / (H * Wd) * 1000:.1f}‰ x{xs.min() / Wd * 100:.0f}..{xs.max() / Wd * 100:.0f} y{ys.min() / H * 100:.0f}..{ys.max() / H * 100:.0f} b{blobs}{'↑' if up > 8 else ('↓' if up < -8 else '')}")
        prev = g
    for k in range(0, len(out), 6):
        print("  " + " | ".join(out[k:k + 6]))


if __name__ == "__main__":
    main()
