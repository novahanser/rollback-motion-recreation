# -*- coding: utf-8 -*-
"""量一块棋盘格在连续几帧里的格子大小和相位，用来判断它是固定在屏幕上的，还是跟着别的东西一起动。

用法: python -I chk_phase.py <编号> <起始帧> <结束帧> <x0> <y0> <x1> <y1> [步长=1]
窗口用帧的原始像素坐标。只统计窗口里接近无彩、偏亮的像素（棋盘格的两种灰），别的颜色的遮挡物不参与。

输出每帧: 窗口里棋盘格像素的占比、格子的周期（像素）、格子的朝向是否与屏幕对齐（水平/垂直边缘能量占比）、相位 (dx, dy)。
相位逐帧不变 → 格子固定在屏幕上；相位随相机或形状的位移同步变化 → 格子是贴在那个东西上的纹理。
"""
import os, sys
import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
import vis


def analyse(rgb):
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
    sat = rgb.max(2).astype(int) - rgb.min(2).astype(int)
    ok = (sat < 18) & (g > 140)
    frac = float(ok.mean())
    if frac < 0.25:
        return frac, None, None, None, None
    gz = np.where(ok, g, np.nan)
    med = np.nanmedian(gz)
    z = np.where(ok, g - med, 0.0)
    # 周期：行方向和列方向的自相关
    def period(a):
        best = None
        prof = np.zeros(80)
        for r in a:
            if np.abs(r).sum() == 0:
                continue
            ac = np.correlate(r, r, "full")[len(r) - 1:len(r) - 1 + 80]
            if ac[0] > 0:
                prof += ac / ac[0]
        k = int(np.argmax(prof[6:70]) + 6)
        return k, float(prof[k] / max(1e-6, prof[6:70].mean()))
    px, qx = period(z); py, qy = period(z.T)
    per = int(round((px + py) / 2))
    # 朝向：梯度方向直方图里水平加垂直方向的能量占比
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0); gy = cv2.Sobel(g, cv2.CV_32F, 0, 1)
    mag = np.hypot(gx, gy); sel = ok & (mag > np.percentile(mag[ok], 80))
    ang = (np.degrees(np.arctan2(gy[sel], gx[sel])) % 90)
    axis = float(((ang < 8) | (ang > 82)).mean()) if sel.sum() > 50 else float("nan")
    # 相位
    yy, xx = np.mgrid[0:g.shape[0], 0:g.shape[1]]
    half = max(2, per // 2); best = (-1, 0, 0)
    for dx in range(per):
        for dy in range(half):
            t = ((((xx + dx) // half) + ((yy + dy) // half)) % 2) * 2 - 1
            sc = float(abs((z * t).sum()))
            if sc > best[0]:
                best = (sc, dx % half, dy)
    return frac, (px, py), axis, (best[1], best[2]), best[0] / max(1.0, ok.sum())


def main():
    vid = sys.argv[1]; f0, f1 = int(sys.argv[2]), int(sys.argv[3])
    x0, y0, x1, y1 = (int(v) for v in sys.argv[4:8]); step = int(sys.argv[8]) if len(sys.argv) > 8 else 1
    m = vis.meta(vid); W = m["width"]
    print(f"{vid} window x{x0}-{x1} y{y0}-{y1} (frame {W}x{m['height']})")
    print("  frame: checker px share | period x,y (px) | axis-aligned edge share | phase dx,dy (mod half period) | strength")
    for n in range(f0, f1 + 1, step):
        fr = np.array(vis.read_frames(m, n, 1, W)[0])[y0:y1, x0:x1]
        frac, per, axis, ph, q = analyse(fr)
        if per is None:
            print(f"  f{n}: {frac * 100:4.0f}% — 棋盘格像素太少"); continue
        print(f"  f{n}: {frac * 100:4.0f}% | {per[0]:2d},{per[1]:2d} | {axis * 100:3.0f}% | ({ph[0]:2d},{ph[1]:2d}) | {q:.1f}")


if __name__ == "__main__":
    main()
