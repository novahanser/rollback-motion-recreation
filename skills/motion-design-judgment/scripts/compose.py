# -*- coding: utf-8 -*-
"""粗略量一帧的构图：东西占了多少地方、重心在哪、左右上下各有多重。

用法: python -I compose.py <输出.jpg> <列数> <每格宽> <编号:位置> ...
  位置写秒数或 fN 帧号。输出一张拼图：每帧上画出三分线（细）、中线（虚）、
  「分量」的重心（黄圈）和「细节」的重心（青色十字），并在终端打印数值。

量法（都在 640 像素宽的缩小图上做）:
  底色     取出现最多的颜色（4 bit/通道量化后最大的一箱）
  分量     每个像素与底色的差（RGB 距离），即「有多不像底」。它的重心是画面的视觉重心的一个近似
  细节     边缘强度。它的重心偏向小字、细线多的地方
  占用     把画面分成 32×18 格，分量的均值超过阈值的格子占多少；1 减去它就是留白
  左右、上下   分量在左半与右半、上半与下半之间的比例
  中心带   画面正中 1/3×1/3 区域里的分量占全部的多少（均匀分布时是 11%）
这些数只描述像素的分布，不知道哪个是主体、哪个是字。主次要靠看。
"""
import os, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
import vis


def measure(im):
    a = np.asarray(im).astype(np.float32); h, w = a.shape[:2]
    q = (a.astype(np.int32) >> 4)
    key = (q[..., 0] << 8) | (q[..., 1] << 4) | q[..., 2]
    cnt = np.bincount(key.ravel(), minlength=4096); b = int(cnt.argmax())
    bg = np.median(a.reshape(-1, 3)[key.ravel() == b], 0)
    mass = np.sqrt(((a - bg) ** 2).sum(2)) / 441.7
    g = cv2.cvtColor(a.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    det = (np.abs(cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)) + np.abs(cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3))) / 1020.0
    yy, xx = np.mgrid[0:h, 0:w]

    def cen(m):
        s = float(m.sum())
        return (float((m * xx).sum() / s / w), float((m * yy).sum() / s / h)) if s > 1e-6 else (0.5, 0.5)

    gx, gy = 32, 18
    cell = mass[:h // gy * gy, :w // gx * gx].reshape(gy, h // gy, gx, w // gx).mean((1, 3))
    occ = float((cell > 0.06).mean())
    tot = float(mass.sum()) + 1e-6
    lr = float(mass[:, :w // 2].sum() / tot); tb = float(mass[:h // 2].sum() / tot)
    mid = float(mass[h // 3:2 * h // 3, w // 3:2 * w // 3].sum() / tot)
    return dict(bg="#%02X%02X%02X" % tuple(int(v) for v in bg), bgshare=float(cnt[b] / key.size), mass=cen(mass), det=cen(det),
                occ=occ, left=lr, top=tb, mid=mid)


def main():
    out, cols, cw = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    cells = []
    for s in sys.argv[4:]:
        vid, pos = s.split(":")[:2]
        m = vis.meta(vid); n, t = vis.parse_pos(m, pos)
        im = vis.read_frames(m, n, 1, 640)[0]
        r = measure(im)
        print(f"{vid} f{n} {vis.tc(t)}  底 {r['bg']}（占 {r['bgshare'] * 100:.0f}%） 占用 {r['occ'] * 100:.0f}% 留白 {100 - r['occ'] * 100:.0f}%"
              f"  分量重心 ({r['mass'][0] * 100:.0f}%, {r['mass'][1] * 100:.0f}%)  细节重心 ({r['det'][0] * 100:.0f}%, {r['det'][1] * 100:.0f}%)"
              f"  左:右 {r['left'] * 100:.0f}:{100 - r['left'] * 100:.0f}  上:下 {r['top'] * 100:.0f}:{100 - r['top'] * 100:.0f}  中心带 {r['mid'] * 100:.0f}%")
        v = im.resize((cw, int(round(im.size[1] * cw / im.size[0]))), Image.LANCZOS); d = ImageDraw.Draw(v); W, Hh = v.size
        for k in (1, 2):
            d.line([(W * k // 3, 0), (W * k // 3, Hh)], fill=(255, 0, 255), width=1)
            d.line([(0, Hh * k // 3), (W, Hh * k // 3)], fill=(255, 0, 255), width=1)
        for x in range(0, W, 12):
            d.line([(x, Hh // 2), (x + 5, Hh // 2)], fill=(0, 255, 0), width=1)
        for y in range(0, Hh, 12):
            d.line([(W // 2, y), (W // 2, y + 5)], fill=(0, 255, 0), width=1)
        mx, my = r["mass"][0] * W, r["mass"][1] * Hh
        d.ellipse([mx - 9, my - 9, mx + 9, my + 9], outline=(255, 235, 0), width=3)
        dx, dy = r["det"][0] * W, r["det"][1] * Hh
        d.line([(dx - 10, dy), (dx + 10, dy)], fill=(0, 255, 255), width=3); d.line([(dx, dy - 10), (dx, dy + 10)], fill=(0, 255, 255), width=3)
        cells.append((f"{vid} f{n} {vis.tc(t)}", v))
    ch = max(v.size[1] for _, v in cells); gap = 3; rows = (len(cells) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cw + (cols + 1) * gap, rows * ch + (rows + 1) * gap), (40, 40, 40))
    d = ImageDraw.Draw(sheet); fnt = vis.font(12)
    for i, (lab, v) in enumerate(cells):
        x = gap + (i % cols) * (cw + gap); y = gap + (i // cols) * (ch + gap)
        sheet.paste(v, (x, y)); vis.label(d, (x + 3, y + 2), lab, fnt)
    sheet.save(out, quality=90); print(out, sheet.size)


if __name__ == "__main__":
    main()
