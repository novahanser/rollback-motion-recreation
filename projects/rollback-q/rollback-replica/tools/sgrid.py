"""python tools/sgrid.py TAG OUT x0 y0 x1 y1 SCALE STEP f1 f2 ...  screen crops with a labelled pixel grid; original row above, replica TAG row below (TAG=none: original only)"""
import sys
from PIL import Image, ImageDraw, ImageFont
tag, out = sys.argv[1:3]
x0, y0, x1, y1 = [int(v) for v in sys.argv[3:7]]
S = float(sys.argv[7]); step = int(sys.argv[8]); fs = [int(v) for v in sys.argv[9:]]
font = ImageFont.truetype('arial.ttf', 12)
cw, ch = int((x1 - x0) * S), int((y1 - y0) * S)
rows = 1 if tag == 'none' else 2
sheet = Image.new('RGB', (len(fs) * (cw + 4) + 4, rows * (ch + 4) + 4), (255, 0, 80))
for i, f in enumerate(fs):
    for r in range(rows):
        p = 'frames_full/f_%04d.jpg' % f if r == 0 else 'render/frames_%s/f_%04d.jpg' % (tag, f)
        im = Image.open(p).convert('RGB').crop((x0, y0, x1, y1)).resize((cw, ch), Image.LANCZOS)
        d = ImageDraw.Draw(im, 'RGBA')
        for x in range((x0 // step + 1) * step, x1, step):
            d.line([((x - x0) * S, 0), ((x - x0) * S, ch)], fill=(255, 255, 0, 70), width=1)
            if x % (2 * step) == 0: d.text(((x - x0) * S + 2, 20), str(x), fill=(255, 230, 0, 255), font=font)
        for y in range((y0 // step + 1) * step, y1, step):
            d.line([(0, (y - y0) * S), (cw, (y - y0) * S)], fill=(0, 255, 255, 70), width=1)
            if y % (2 * step) == 0: d.text((2, (y - y0) * S + 1), str(y), fill=(0, 240, 255, 255), font=font)
        d.rectangle([0, 0, 64, 17], fill=(0, 0, 0, 255)); d.text((3, 2), ('O ' if r == 0 else 'R ') + 'f%d' % f, fill=(255, 255, 0, 255), font=font)
        sheet.paste(im, (4 + i * (cw + 4), 4 + r * (ch + 4)))
sheet.save(out, quality=92); print(out, sheet.size)
