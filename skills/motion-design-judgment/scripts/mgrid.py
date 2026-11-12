# -*- coding: utf-8 -*-
"""把不同视频的若干帧（可各自裁切）拼成一张对照图。

用法: python -I mgrid.py <输出.jpg> <列数> <每格宽> <编号:位置[:x0,y0,x1,y1]> ...
位置写秒数或 fN 帧号；裁切用 0—1 的比例。每格左上角标编号、帧号和时间。
"""
import os, sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
import vis


def main():
    out, cols, cw = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    cells = []
    for s in sys.argv[4:]:
        p = s.split(":")
        vid, pos = p[0], p[1]
        crop = vis.parse_crop(p[2]) if len(p) > 2 and p[2] else None
        m = vis.meta(vid)
        n, t = vis.parse_pos(m, pos)
        im = vis.read_frames(m, n, 1, cw, crop)[0]
        if im.size[0] != cw:
            im = im.resize((cw, int(round(im.size[1] * cw / im.size[0]))), Image.LANCZOS)
        cells.append((f"{vid} f{n} {vis.tc(t)}", im))
    ch = max(im.size[1] for _, im in cells); gap = 3
    rows = (len(cells) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cw + (cols + 1) * gap, rows * ch + (rows + 1) * gap), (40, 40, 40))
    d = ImageDraw.Draw(sheet); fnt = vis.font(13)
    for i, (lab, im) in enumerate(cells):
        x = gap + (i % cols) * (cw + gap); y = gap + (i // cols) * (ch + gap)
        sheet.paste(im, (x, y)); vis.label(d, (x + 3, y + 2), lab, fnt)
    sheet.save(out, quality=90)
    print(out, sheet.size, len(cells), "cells")


if __name__ == "__main__":
    main()
