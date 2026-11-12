"""python tools/ogrid.py SRC OUT x0 y0 x1 y1 SCALE COLS f1 f2 ...
grid of crops of one source: SRC = 'orig' (frames_full) or a render tag (render/frames_TAG)"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
src, out = sys.argv[1:3]
x0, y0, x1, y1 = [int(v) for v in sys.argv[3:7]]
sc = float(sys.argv[7]); cols = int(sys.argv[8])
fs = [int(x) for x in sys.argv[9:]]
cw, ch = int((x1 - x0) * sc), int((y1 - y0) * sc)
rows = (len(fs) + cols - 1) // cols
font = ImageFont.truetype('arial.ttf', 16)
sheet = Image.new('RGB', (cols * (cw + 4) + 4, rows * (ch + 4) + 4), (255, 0, 80))
for i, f in enumerate(fs):
    x = 4 + (i % cols) * (cw + 4); y = 4 + (i // cols) * (ch + 4)
    if src == 'orig':
        p = 'frames_full/f_%04d.jpg' % f
    else:
        p = next((q for q in ('render/frames_%s/f_%04d.png' % (src, f), 'render/frames_%s/f_%04d.jpg' % (src, f)) if os.path.exists(q)), None)
    a = Image.open(p).convert('RGB').crop((x0, y0, x1, y1)).resize((cw, ch), Image.LANCZOS)
    sheet.paste(a, (x, y))
    dr = ImageDraw.Draw(sheet); dr.rectangle([x, y, x + 62, y + 20], fill=(0, 0, 0)); dr.text((x + 3, y + 1), 'f%d' % f, fill=(255, 255, 0), font=font)
sheet.save(out, quality=90); print(out, sheet.size)
