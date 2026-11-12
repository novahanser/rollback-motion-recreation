# -*- coding: utf-8 -*-
"""粗略测量一帧里各行文字的字高（按原始分辨率），用来核对「字号分几档」。

用法: python -I typesize.py <id> <帧号|秒> [out.jpg]
做法: 大津阈值二值化，分别取深色和浅色连通域；把高度相近、基线接近、水平相邻的连通域串成「行」；
      报告每行的字高（行内连通域高度的 90 分位）和字符数。
局限: 只适合底色干净的版式；连笔手写体、被图形压住的字、极小的字（<5 px）检测不到；图形排成一行也会被当成字。
"""
import sys, os
import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
import vis  # noqa: E402


def lines_from(binimg, H, W):
    n, lab, stats, cent = cv2.connectedComponentsWithStats(binimg, connectivity=8)
    comps = []
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        if h < 5 or h > 0.7 * H or w < 2 or w > 0.5 * W:
            continue
        if w / h > 3.2 or w / h < 0.06:
            continue
        fill = area / (w * h)
        if fill < 0.10 or fill > 0.95:
            continue
        comps.append((x, y, w, h))
    comps.sort()
    used = [False] * len(comps); out = []
    for i, c in enumerate(comps):
        if used[i]:
            continue
        chain = [c]; used[i] = True; last = c
        for j in range(i + 1, len(comps)):
            if used[j]:
                continue
            d = comps[j]
            gap = d[0] - (last[0] + last[2])
            if gap > 1.6 * max(last[3], d[3]):
                if d[0] - last[0] > 4 * max(last[3], d[3]) + last[2]:
                    break
                continue
            if gap < -0.5 * last[2]:
                continue
            r = d[3] / last[3]
            cy1 = last[1] + last[3]; cy2 = d[1] + d[3]            # 基线（底边）
            if 0.45 <= r <= 2.2 and abs(cy1 - cy2) < 0.45 * max(last[3], d[3]):
                chain.append(d); used[j] = True; last = d
        if len(chain) >= 3:
            hs = np.array([k[3] for k in chain])
            x0 = min(k[0] for k in chain); y0 = min(k[1] for k in chain)
            x1 = max(k[0] + k[2] for k in chain); y1 = max(k[1] + k[3] for k in chain)
            out.append((float(np.percentile(hs, 90)), len(chain), x0, y0, x1, y1))
    return out


def main():
    vid, pos = sys.argv[1], sys.argv[2]
    m = vis.meta(vid)
    n, t = vis.parse_pos(m, pos if pos.startswith("f") or "." in pos else "f" + pos)
    im = np.array(vis.read_frames(m, n, 1, m["width"])[0])
    H, W = im.shape[:2]
    gray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    res = []
    for pol in (0, 1):
        _, b = cv2.threshold(gray, 0, 255, (cv2.THRESH_BINARY if pol else cv2.THRESH_BINARY_INV) + cv2.THRESH_OTSU)
        res += [(h, c, x0, y0, x1, y1, pol) for h, c, x0, y0, x1, y1 in lines_from(b, H, W)]
        # 局部自适应阈值补小字
        ad = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY if pol else cv2.THRESH_BINARY_INV, 31, 12)
        res += [(h, c, x0, y0, x1, y1, pol) for h, c, x0, y0, x1, y1 in lines_from(ad, H, W) if h < 60]
    # 去重：包围盒重叠的取字符多的
    res.sort(key=lambda r: -r[1]); keep = []
    for r in res:
        dup = False
        for k in keep:
            ix = max(0, min(r[4], k[4]) - max(r[2], k[2])); iy = max(0, min(r[5], k[5]) - max(r[3], k[3]))
            if ix * iy > 0.5 * (r[4] - r[2]) * (r[5] - r[3]):
                dup = True; break
        if not dup:
            keep.append(r)
    keep.sort(key=lambda r: -r[0])
    hs = np.array([r[0] for r in keep]) / H * 100
    print(f"{vid} f{n} {vis.tc(t)}  {W}x{H}  text-like lines: {len(keep)}")
    bins = [0, 0.8, 1.2, 1.8, 2.7, 4, 6, 9, 13.5, 20, 30, 100]
    cnt = np.histogram(hs, bins=bins)[0]
    print("  line height as % of frame height -> lines: " + "  ".join(f"{bins[i]:g}-{bins[i + 1]:g}%:{cnt[i]}" for i in range(len(cnt)) if cnt[i]))
    print("  tallest: " + ", ".join(f"{r[0] / H * 100:.1f}%({r[0]:.0f}px,{r[1]}ch)" for r in keep[:8]))
    if len(sys.argv) > 3:
        vis_im = im.copy()
        for h, c, x0, y0, x1, y1, pol in keep:
            cv2.rectangle(vis_im, (x0, y0), (x1, y1), (255, 0, 255) if h / H > 0.04 else (0, 200, 0), 2)
        s = 1568 / W
        cv2.imwrite(sys.argv[3], cv2.cvtColor(cv2.resize(vis_im, (1568, int(H * s))), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])


if __name__ == "__main__":
    main()
