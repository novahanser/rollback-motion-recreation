# -*- coding: utf-8 -*-
"""粗略测量一块文字的外形：字高、笔画粗细、字的宽窄、字距、行距。

用法: python -I typemetrics.py <编号> <帧号或秒> <x0,y0,x1,y1> [latin|cjk] [dark|light] [输出标注图.jpg]
  裁切用 0—1 的比例，只框住要量的那一块字，底色要干净。
  latin: 按连通域取字形，适合拉丁字母和数字（i、j 的点和分开的笔画会被当成小件丢掉）。
  cjk:   按投影切行、切字，适合汉字和假名（一个字有多个不相连的部件）。
  dark / light: 字比底暗还是亮。不写时取面积较小的一类。

输出（每行文字一行）:
  字高      占整幅画面高度的百分比（拉丁字母取大写高或连通域高度的中位数）
  粗细      笔画宽度 ÷ 字高。小于 0.08 算细，0.10—0.14 常规，0.18 以上粗（只是这里用的叫法）
  反差      笔画最粗处 ÷ 最细处（取 85 与 15 分位）。接近 1 是等线体，2 以上是衬线体或明朝体那一类
  宽窄      字形宽度的中位数 ÷ 字高。拉丁大写 0.5 以下算窄，0.9 以上算宽
  字距      相邻字形之间的空隙的中位数 ÷ 字高
  行距      相邻两行的行顶之间的距离 ÷ 字高
数值只对这一帧、这一块字成立；压缩、抗锯齿和字太小（字高不到 20 像素）都会让粗细偏大。字体名称量不出来。
"""
import os, sys
import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
import vis


def otsu(g):
    t, _ = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return t


def stroke_stats(fg):
    """fg: bool 图。返回 (笔画宽度中位数, 反差)。"""
    dt = cv2.distanceTransform(fg.astype(np.uint8), cv2.DIST_L2, 5)
    mx = cv2.dilate(dt, np.ones((3, 3), np.uint8))
    ridge = (dt >= mx - 1e-3) & (dt >= 1.0)
    v = dt[ridge]
    if len(v) < 10:
        return 0.0, 0.0
    w = 2.0 * v - 1.0
    return float(np.median(w)), float(np.percentile(w, 85) / max(np.percentile(w, 15), 1e-3))


def main():
    vid, pos = sys.argv[1], sys.argv[2]
    crop = vis.parse_crop(sys.argv[3])
    rest = sys.argv[4:]
    mode = "latin"; pol = None; outp = None
    for a in rest:
        if a in ("latin", "cjk"):
            mode = a
        elif a in ("dark", "light"):
            pol = a
        else:
            outp = a
    m = vis.meta(vid)
    n, t = vis.parse_pos(m, pos)
    im = vis.read_frames(m, n, 1, 99999, crop)[0]
    rgb = np.asarray(im); g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    H = m["height"]
    thr = otsu(g)
    dark = g < thr
    if pol is None:
        pol = "dark" if dark.mean() < 0.5 else "light"
    fg = dark if pol == "dark" else ~dark
    fg = cv2.morphologyEx(fg.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)).astype(bool)
    print(f"{vid} f{n} {vis.tc(t)} 裁切 {im.size[0]}×{im.size[1]} 像素, 模式 {mode}, 字比底{'暗' if pol == 'dark' else '亮'}, 前景占 {fg.mean() * 100:.1f}%")
    ann = rgb.copy()
    lines = []
    if mode == "latin":
        nlab, lab, st, cen = cv2.connectedComponentsWithStats(fg.astype(np.uint8), 8)
        comps = [(st[i, 0], st[i, 1], st[i, 2], st[i, 3], st[i, 4], i) for i in range(1, nlab)]
        if not comps:
            print("没有找到字形"); return
        hs = np.array([c[3] for c in comps])
        h90 = np.percentile(hs, 90)
        comps = [c for c in comps if c[3] >= 0.45 * h90 and c[4] >= 12]
        comps.sort(key=lambda c: c[1])
        for c in comps:
            placed = False
            for L in lines:
                y0 = min(q[1] for q in L); y1 = max(q[1] + q[3] for q in L)
                ov = min(y1, c[1] + c[3]) - max(y0, c[1])
                if ov >= 0.5 * min(c[3], y1 - y0):
                    L.append(c); placed = True; break
            if not placed:
                lines.append([c])
        lines = [sorted(L, key=lambda c: c[0]) for L in lines if len(L) >= 2]
        lines.sort(key=lambda L: min(q[1] for q in L))
        tops = []
        for L in lines:
            hh = np.array([q[3] for q in L]); ww = np.array([q[2] for q in L])
            cap = float(np.median(hh))
            gaps = np.array([L[k + 1][0] - (L[k][0] + L[k][2]) for k in range(len(L) - 1)])
            gaps = gaps[gaps > -0.2 * cap]
            mask = np.zeros_like(fg)
            for q in L:
                mask |= (lab == q[5])
                cv2.rectangle(ann, (q[0], q[1]), (q[0] + q[2], q[1] + q[3]), (255, 80, 0), 1)
            sw, con = stroke_stats(mask)
            top = float(np.median([q[1] for q in L])); tops.append((top, cap))
            print(f"  行: {len(L)} 个字形  字高 {cap:.0f}px = {cap / H * 100:.1f}%  粗细 {sw / cap:.3f}  反差 {con:.1f}"
                  f"  宽窄 {np.median(ww) / cap:.2f}  字距 {np.median(gaps) / cap if len(gaps) else 0:.2f}")
        for k in range(len(tops) - 1):
            print(f"  行距（第 {k + 1}→{k + 2} 行）: {(tops[k + 1][0] - tops[k][0]) / tops[k][1]:.2f} 倍字高")
    else:
        rows = fg.sum(1) > 0
        segs = []; y = 0; hh = fg.shape[0]
        while y < hh:
            if rows[y]:
                y1 = y
                while y1 < hh and rows[y1]:
                    y1 += 1
                if y1 - y >= 6:
                    segs.append((y, y1))
                y = y1
            else:
                y += 1
        tops = []
        for (ya, yb) in segs:
            band = fg[ya:yb]
            cols = band.sum(0) > 0
            cells = []; x = 0; ww = band.shape[1]; hgt = yb - ya
            while x < ww:
                if cols[x]:
                    x1 = x
                    while x1 < ww and cols[x1]:
                        x1 += 1
                    cells.append([x, x1]); x = x1
                else:
                    x += 1
            # 把间隙很小的相邻片段并成一个字（偏旁之间的空隙）
            merged = []
            for c in cells:
                if merged and c[0] - merged[-1][1] < 0.12 * hgt and (c[1] - merged[-1][0]) <= 1.25 * hgt:
                    merged[-1][1] = c[1]
                else:
                    merged.append(list(c))
            if len(merged) < 1:
                continue
            widths = np.array([c[1] - c[0] for c in merged]); gaps = np.array([merged[k + 1][0] - merged[k][1] for k in range(len(merged) - 1)])
            sw, con = stroke_stats(band)
            for c in merged:
                cv2.rectangle(ann, (c[0], ya), (c[1], yb), (255, 80, 0), 1)
            tops.append((ya, hgt))
            print(f"  行: {len(merged)} 个字  字高 {hgt}px = {hgt / H * 100:.1f}%  粗细 {sw / hgt:.3f}  反差 {con:.1f}"
                  f"  宽窄 {np.median(widths) / hgt:.2f}  字距 {np.median(gaps) / hgt if len(gaps) else 0:.2f}")
        for k in range(len(tops) - 1):
            print(f"  行距（第 {k + 1}→{k + 2} 行）: {(tops[k + 1][0] - tops[k][0]) / tops[k][1]:.2f} 倍字高")
    if outp:
        cv2.imwrite(outp, cv2.cvtColor(ann, cv2.COLOR_RGB2BGR))
        print("  标注图:", outp)


if __name__ == "__main__":
    main()
