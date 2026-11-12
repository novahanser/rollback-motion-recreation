"""overlay the procedural horn (red) on world-aligned crops of the source: python tools/horn_test.py OUT COLS f1 f2 ..."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, r'C:\Users\bg931\Documents\New project\rollback-replica\scripts')
from gen_util import w2s
import horn

out = sys.argv[1]; cols = int(sys.argv[2]); fs = [int(v) for v in sys.argv[3:]]
ppw = 0.62
wx0, wy0, wx1, wy1 = horn.HW
cw, ch = int((wx1 - wx0) * ppw), int((wy1 - wy0) * ppw)
rows = (len(fs) + cols - 1) // cols
sheet = Image.new('RGB', (cols * (2 * cw + 8) + 4, rows * (ch + 4) + 4), (255, 0, 80))
font = ImageFont.truetype('arial.ttf', 14)
for i, f in enumerate(fs):
    im = Image.open('frames_full/f_%04d.jpg' % f).convert('RGB')
    a = w2s(f, wx0, wy0); b = w2s(f, wx1, wy1)
    cell = im.transform((cw, ch), Image.EXTENT, (a[0], a[1], b[0], b[1]), Image.BICUBIC, fillcolor=(40, 0, 40)).convert('RGBA')
    spr = horn.horn_frame(f).resize((cw, ch), Image.LANCZOS)
    red = np.asarray(spr).copy()
    red[..., 0], red[..., 1], red[..., 2] = 255, 0, 0
    both = cell.copy()
    both.alpha_composite(Image.fromarray(red, 'RGBA'))
    plain = Image.new('RGBA', (cw, ch), (236, 236, 236, 255)); plain.alpha_composite(spr)
    x = 4 + (i % cols) * (2 * cw + 8); y = 4 + (i // cols) * (ch + 4)
    sheet.paste(both.convert('RGB'), (x, y)); sheet.paste(plain.convert('RGB'), (x + cw + 4, y))
    d = ImageDraw.Draw(sheet); d.rectangle([x, y, x + 46, y + 18], fill=(0, 0, 0)); d.text((x + 3, y + 1), 'f%d' % f, fill=(255, 255, 0), font=font)
sheet.save(out, quality=90); print(out, sheet.size)
