"""python tools/wgrid.py SRC OUT f X0 Y0 X1 Y1 SCALE [STEP]
crop of one frame (screen rect X0..X1, Y0..Y1) with a world-coordinate grid drawn over it.
SRC = orig or a render tag."""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, r'C:\Users\bg931\Documents\New project\rollback-replica\scripts')
from gen_util import s2w, w2s, zoom

src, out = sys.argv[1:3]
f = int(sys.argv[3])
X0, Y0, X1, Y1 = [int(v) for v in sys.argv[4:8]]
sc = float(sys.argv[8])
step = float(sys.argv[9]) if len(sys.argv) > 9 else 50.0
p = 'frames_full/f_%04d.jpg' % f if src == 'orig' else 'render/frames_%s/f_%04d.jpg' % (src, f)
im = Image.open(p).convert('RGB').crop((X0, Y0, X1, Y1))
im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
d = ImageDraw.Draw(im, 'RGBA')
font = ImageFont.truetype('arial.ttf', 13)
wx0, wy0 = s2w(f, X0, Y0)
wx1, wy1 = s2w(f, X1, Y1)
x = np.ceil(wx0 / step) * step
while x <= wx1:
    sx = (w2s(f, x, 540)[0] - X0) * sc
    major = (round(x / step) % 2 == 0)
    d.line([(sx, 0), (sx, im.height)], fill=(0, 160, 255, 150 if major else 70), width=1)
    if major:
        d.text((sx + 2, 2), '%d' % x, fill=(0, 90, 220, 255), font=font)
    x += step
y = np.ceil(wy0 / step) * step
while y <= wy1:
    sy = (w2s(f, 0, y)[1] - Y0) * sc
    major = (round(y / step) % 2 == 0)
    d.line([(0, sy), (im.width, sy)], fill=(255, 120, 0, 150 if major else 70), width=1)
    if major:
        d.text((2, sy + 1), '%d' % y, fill=(220, 80, 0, 255), font=font)
    y += step
d.rectangle([im.width - 150, 0, im.width, 18], fill=(0, 0, 0, 200))
d.text((im.width - 146, 2), '%s f%d z=%.3f' % (src, f, zoom(f)), fill=(255, 255, 0, 255), font=font)
im.save(out, quality=92)
print(out, im.size)
