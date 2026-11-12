"""python tools/pair.py TAG OUT CELLW f1 f2 ...   -> rows of (original | replica) with a 200px grid; TAG='-' = original only (2 per row)"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
tag, out, cw = sys.argv[1], sys.argv[2], int(sys.argv[3]); fs = [int(x) for x in sys.argv[4:]]
ch = cw * 9 // 16
font = ImageFont.truetype('arial.ttf', 14)


def cell(path, label):
    if not os.path.exists(path):
        return Image.new('RGB', (cw, ch), (60, 0, 0))
    im = Image.open(path).convert('RGB').resize((cw, ch), Image.LANCZOS)
    d = ImageDraw.Draw(im); sc = cw / 1920
    for gx in range(200, 1920, 200):
        d.line([gx * sc, 0, gx * sc, 6], fill=(0, 200, 0)); d.line([gx * sc, ch - 6, gx * sc, ch], fill=(0, 200, 0))
        d.text((gx * sc + 2, ch - 16), str(gx), fill=(0, 170, 0), font=font)
    for gy in range(200, 1080, 200):
        d.line([0, gy * sc, 6, gy * sc], fill=(0, 200, 0)); d.text((8, gy * sc - 8), str(gy), fill=(0, 170, 0), font=font)
    d.rectangle([0, 0, 74, 18], fill=(0, 0, 0)); d.text((3, 1), label, fill=(255, 255, 0), font=font)
    return im


if tag == '-':
    cols = 2; rows = (len(fs) + 1) // 2
    sheet = Image.new('RGB', (cols * cw + 2, rows * ch), (255, 0, 80))
    for i, f in enumerate(fs):
        sheet.paste(cell(f'frames_full/f_{f:04d}.jpg', f'f{f}'), ((i % 2) * (cw + 2), (i // 2) * ch))
else:
    sheet = Image.new('RGB', (2 * cw + 2, len(fs) * (ch + 2)), (255, 0, 80))
    for i, f in enumerate(fs):
        sheet.paste(cell(f'frames_full/f_{f:04d}.jpg', f'f{f} org'), (0, i * (ch + 2)))
        sheet.paste(cell(f'render/frames_{tag}/f_{f:04d}.jpg', f'f{f} {tag}'), (cw + 2, i * (ch + 2)))
sheet.save(out, quality=90); print(out, sheet.size)
