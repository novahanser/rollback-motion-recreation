"""python tools/crop2.py TAG OUT x0 y0 x1 y1 SCALE f1 f2 ...  -> crops (original above replica) of the same screen region"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
tag, out = sys.argv[1:3]
x0, y0, x1, y1 = [int(v) for v in sys.argv[3:7]]
sc = float(sys.argv[7])
fs = [int(x) for x in sys.argv[8:]]
d = 'render/frames_%s' % tag
cw, ch = int((x1 - x0) * sc), int((y1 - y0) * sc)
font = ImageFont.truetype('arial.ttf', 16)
sheet = Image.new('RGB', (len(fs) * (cw + 4) + 4, 2 * ch + 12), (255, 0, 80))
for i, f in enumerate(fs):
    x = 4 + i * (cw + 4)
    a = Image.open('frames_full/f_%04d.jpg' % f).convert('RGB').crop((x0, y0, x1, y1)).resize((cw, ch), Image.LANCZOS)
    p = next((q for q in ('%s/f_%04d.png' % (d, f), '%s/f_%04d.jpg' % (d, f)) if os.path.exists(q)), None)
    b = Image.open(p).convert('RGB').crop((x0, y0, x1, y1)).resize((cw, ch), Image.LANCZOS) if p else Image.new('RGB', (cw, ch), (0, 0, 0))
    sheet.paste(a, (x, 4)); sheet.paste(b, (x, ch + 8))
    dr = ImageDraw.Draw(sheet); dr.rectangle([x, 4, x + 62, 24], fill=(0, 0, 0)); dr.text((x + 3, 5), 'f%d' % f, fill=(255, 255, 0), font=font)
sheet.save(out, quality=90); print(out, sheet.size)
