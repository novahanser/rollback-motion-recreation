# -*- coding: utf-8 -*-
"""逐帧跟踪一个元素：它在一个窗口里的包围盒、质心和面积，以及离终点还有多远。

用法: python -I elemtrack.py <编号> <起始帧> <结束帧> <x0,y0,x1,y1> <条件> [最小面积=30] [输出条带.jpg]
  窗口用 0—1 的比例，要框住元素运动的全程，又尽量不带进别的东西。
  条件（哪些像素算这个元素）:
    dark[:阈值]     比阈值暗的像素（默认 90）
    light[:阈值]    比阈值亮的像素（默认 170）
    #RRGGBB[:容差]  与这个颜色接近的像素（默认容差 60，RGB 距离）
    diff[:阈值]     与起始帧的前一帧相比变了的像素（默认 30）——元素落在静止的背景上时用

每帧输出: 包围盒的左、上、宽、高（原始像素），质心，面积，相邻两帧的质心位移。
末尾把最后一帧当作终点，列出每帧质心离终点的距离、相邻两帧「剩余距离」之比，以及宽度相对终点的比例。
  剩余距离每帧乘一个差不多的数（比值恒定且小于 1）→ 指数式减速，常见于「先快后慢地停住」
  每帧走的距离差不多 → 匀速
  距离先小后大 → 加速
  越过终点再回来 → 回弹
这些是位置序列的形状，不是关键帧参数。同一条曲线可以由好几种做法得到。
"""
import os, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
import vis


def main():
    vid, f0, f1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    crop = vis.parse_crop(sys.argv[4]); cond = sys.argv[5]
    minarea = 30; strip = None
    for a in sys.argv[6:]:
        if a.isdigit():
            minarea = int(a)
        else:
            strip = a
    m = vis.meta(vid); W, H = m["width"], m["height"]
    x0 = int(crop[0] * W); y0 = int(crop[1] * H)
    pre = 1 if cond.startswith("diff") and f0 > 0 else 0
    ims = vis.read_frames(m, f0 - pre, f1 - f0 + 1 + pre, 99999, crop)
    arr = [np.asarray(im).astype(np.int32) for im in ims]
    ref = arr[0] if pre else None
    if pre:
        arr = arr[1:]; ims = ims[1:]
    kind, _, par = cond.partition(":")
    rows = []
    for k, a in enumerate(arr):
        g = (a[..., 0] * 299 + a[..., 1] * 587 + a[..., 2] * 114) // 1000
        if kind == "dark":
            mk = g < (int(par) if par else 90)
        elif kind == "light":
            mk = g > (int(par) if par else 170)
        elif kind == "diff":
            mk = np.abs(a - ref).max(2) > (int(par) if par else 30)
        else:
            c = np.array([int(kind[1:3], 16), int(kind[3:5], 16), int(kind[5:7], 16)])
            mk = np.sqrt(((a - c) ** 2).sum(2)) < (int(par) if par else 60)
        mk = cv2.morphologyEx(mk.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)).astype(bool)
        ar = int(mk.sum())
        if ar < minarea:
            rows.append((f0 + k, None)); continue
        ys, xs = np.nonzero(mk)
        rows.append((f0 + k, (x0 + xs.min(), y0 + ys.min(), xs.max() - xs.min() + 1, ys.max() - ys.min() + 1,
                              x0 + xs.mean(), y0 + ys.mean(), ar)))
    print(f"{vid} f{f0}-{f1} 窗口 {crop} 条件 {cond}（画面 {W}×{H}）")
    prev = None
    for f, r in rows:
        if r is None:
            print(f"  f{f}: —"); prev = None; continue
        dx = dy = 0.0
        if prev is not None:
            dx = r[4] - prev[4]; dy = r[5] - prev[5]
        print(f"  f{f}: 左 {r[0]:5d} 上 {r[1]:5d} 宽 {r[2]:5d} 高 {r[3]:5d}  质心 ({r[4]:7.1f}, {r[5]:7.1f})  面积 {r[6]:7d}"
              + (f"  位移 ({dx:+7.1f}, {dy:+7.1f})" if prev is not None else ""))
        prev = r
    ok = [(f, r) for f, r in rows if r is not None]
    if len(ok) >= 3:
        end = ok[-1][1]
        dist = [float(np.hypot(r[4] - end[4], r[5] - end[5])) for _, r in ok]
        print("  离终点的距离: " + " ".join(f"{d:.0f}" for d in dist))
        rat = [dist[k + 1] / dist[k] if dist[k] > 2 else float("nan") for k in range(len(dist) - 1)]
        print("  剩余距离之比: " + " ".join("—" if np.isnan(v) else f"{v:.2f}" for v in rat))
        print("  宽度÷终点宽度: " + " ".join(f"{r[2] / end[2]:.2f}" for _, r in ok))
        print("  面积÷终点面积: " + " ".join(f"{r[6] / end[6]:.2f}" for _, r in ok))
    if strip:
        n = len(ims); cw = min(260, 1560 // n); th = [im.resize((cw, max(1, int(round(im.size[1] * cw / im.size[0])))), Image.LANCZOS) for im in ims]
        sh = Image.new("RGB", (n * (cw + 2), th[0].size[1] + 16), (30, 30, 30)); d = ImageDraw.Draw(sh); ft = vis.font(11)
        for k, t in enumerate(th):
            sh.paste(t, (k * (cw + 2), 16)); d.text((k * (cw + 2) + 2, 1), f"f{f0 + k}", fill=(255, 235, 60), font=ft)
        sh.save(strip, quality=90); print("  条带:", strip, sh.size)


if __name__ == "__main__":
    main()
