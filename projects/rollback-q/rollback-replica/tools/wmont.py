"""python tools/wmont.py SRC OUT wx0 wy0 wx1 wy1 PXPERWORLD COLS STEP f1 f2 ...
montage of the same WORLD rectangle over several frames, each cell with a world grid (labels every 2*STEP).
SRC = orig or a render tag; out-of-screen parts are filled dark."""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, r'C:\Users\bg931\Documents\New project\rollback-replica\scripts')
from gen_util import s2w, w2s, zoom

src, out = sys.argv[1:3]
wx0, wy0, wx1, wy1 = [float(v) for v in sys.argv[3:7]]
ppw = float(sys.argv[7]); cols = int(sys.argv[8]); step = float(sys.argv[9])
fs = [int(x) for x in sys.argv[10:]]
cw, ch = int((wx1 - wx0) * ppw), int((wy1 - wy0) * ppw)
rows = (len(fs) + cols - 1) // cols
font = ImageFont.truetype('arial.ttf', 12)
sheet = Image.new('RGB', (cols * (cw + 4) + 4, rows * (ch + 4) + 4), (255, 0, 80))
for i, f in enumerate(fs):
    p = 'frames_full/f_%04d.jpg' % f if src == 'orig' else 'render/frames_%s/f_%04d.jpg' % (src, f)
    im = Image.open(p).convert('RGB')
    a = w2s(f, wx0, wy0); b = w2s(f, wx1, wy1)
    cell = im.transform((cw, ch), Image.EXTENT, (a[0], a[1], b[0], b[1]), Image.BICUBIC, fillcolor=(40, 0, 40))
    d = ImageDraw.Draw(cell, 'RGBA')
    x = np.ceil(wx0 / step) * step
    while x <= wx1:
        sx = (x - wx0) * ppw
        major = (round(x / step) % 2 == 0)
        d.line([(sx, 0), (sx, ch)], fill=(0, 160, 255, 140 if major else 60), width=1)
        if major:
            d.text((sx + 2, 22), '%d' % x, fill=(0, 90, 220, 255), font=font)
        x += step
    y = np.ceil(wy0 / step) * step
    while y <= wy1:
        sy = (y - wy0) * ppw
        major = (round(y / step) % 2 == 0)
        d.line([(0, sy), (cw, sy)], fill=(255, 120, 0, 140 if major else 60), width=1)
        if major:
            d.text((2, sy + 1), '%d' % y, fill=(220, 80, 0, 255), font=font)
        y += step
    d.rectangle([0, 0, 46, 18], fill=(0, 0, 0, 255)); d.text((3, 2), 'f%d' % f, fill=(255, 255, 0, 255), font=font)
    sheet.paste(cell, (4 + (i % cols) * (cw + 4), 4 + (i // cols) * (ch + 4)))
sheet.save(out, quality=92)
print(out, sheet.size)
