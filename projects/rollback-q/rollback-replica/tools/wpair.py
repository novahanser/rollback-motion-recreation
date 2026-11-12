"""python tools/wpair.py TAG OUT wx0 wy0 wx1 wy1 PXPERWORLD f1 f2 ...
clean (no grid) world-rectangle crops: for every frame the ORIGINAL on top and the replica TAG below (TAG = none -> original only).
Cells of several frames are laid out left to right."""
import sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, r'C:\Users\bg931\Documents\New project\rollback-replica\scripts')
from gen_util import w2s

tag, out = sys.argv[1:3]
wx0, wy0, wx1, wy1 = [float(v) for v in sys.argv[3:7]]
ppw = float(sys.argv[7])
fs = [int(x) for x in sys.argv[8:]]
cw, ch = int((wx1 - wx0) * ppw), int((wy1 - wy0) * ppw)
rows = 1 if tag == 'none' else 2
font = ImageFont.truetype('arial.ttf', 13)
sheet = Image.new('RGB', (len(fs) * (cw + 4) + 4, rows * (ch + 4) + 4), (255, 0, 80))
for i, f in enumerate(fs):
    a = w2s(f, wx0, wy0); b = w2s(f, wx1, wy1)
    for r in range(rows):
        p = 'frames_full/f_%04d.jpg' % f if r == 0 else 'render/frames_%s/f_%04d.jpg' % (tag, f)
        im = Image.open(p).convert('RGB')
        cell = im.transform((cw, ch), Image.EXTENT, (a[0], a[1], b[0], b[1]), Image.BICUBIC, fillcolor=(40, 0, 40))
        d = ImageDraw.Draw(cell)
        d.rectangle([0, 0, 70, 17], fill=(0, 0, 0)); d.text((3, 2), ('O ' if r == 0 else 'R ') + 'f%d' % f, fill=(255, 255, 0), font=font)
        sheet.paste(cell, (4 + i * (cw + 4), 4 + r * (ch + 4)))
sheet.save(out, quality=93)
print(out, sheet.size)
