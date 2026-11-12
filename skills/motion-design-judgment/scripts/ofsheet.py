# -*- coding: utf-8 -*-
"""把若干个「一帧画面」前后的连续帧排成一张对照图，每个事件一行。

用法: python -I ofsheet.py <输出.jpg> <每格宽> <前几帧> <后几帧> <编号:帧号[:说明]> ...
每行: 事件帧之前的若干帧、事件帧（黄框）、之后的若干帧。行首写编号、帧号、时间和说明。
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
import vis


def main():
    out, cw, nb, na = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    specs = sys.argv[5:]
    rows = []
    for s in specs:
        parts = s.split(":", 2)
        vid, f = parts[0], int(parts[1]); note = parts[2] if len(parts) > 2 else ""
        m = vis.meta(vid)
        f0 = max(0, f - nb)
        ims = vis.read_frames(m, f0, nb + na + 1, cw)
        rows.append((vid, f, f0, note, ims, float(m["pts"][f])))
    ch = max(im.size[1] for r in rows for im in r[4]); lab = 16
    W = cw * (nb + na + 1) + 2 * (nb + na); H = (ch + lab + 2) * len(rows)
    sheet = Image.new("RGB", (W, H), (30, 30, 30)); dr = ImageDraw.Draw(sheet); ft = vis.font(12)
    y = 0
    for vid, f, f0, note, ims, t in rows:
        dr.text((3, y + 1), f"{vid} f{f} {vis.tc(t)}  {note}", fill=(255, 235, 60), font=ft)
        for k, im in enumerate(ims):
            x = k * (cw + 2)
            sheet.paste(im, (x, y + lab))
            if f0 + k == f:
                dr.rectangle([x, y + lab, x + im.size[0] - 1, y + lab + im.size[1] - 1], outline=(255, 230, 0), width=2)
        y += ch + lab + 2
    sheet.save(out, quality=88)
    print(out, sheet.size, len(rows), "rows")


if __name__ == "__main__":
    main()
