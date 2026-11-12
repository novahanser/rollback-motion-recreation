"""python tools/cmp2.py TAG OUT f1 f2 ...  -> pairs (original above replica) from render/frames_TAG (png or jpg)"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
tag, out = sys.argv[1:3]; fs = [int(x) for x in sys.argv[3:]]
d = f'render/frames_{tag}'
cw, ch = 480, 270; cols = 4
rows = (len(fs) + cols - 1) // cols
font = ImageFont.truetype('arial.ttf', 16)
sheet = Image.new('RGB', (cols * cw + (cols + 1) * 4, rows * (2 * ch + 8) + 4), (255, 0, 80))
for i, f in enumerate(fs):
    x = 4 + (i % cols) * (cw + 4); y = 4 + (i // cols) * (2 * ch + 8)
    a = Image.open(f'frames_full/f_{f:04d}.jpg').convert('RGB').resize((cw, ch), Image.LANCZOS)
    p = next((q for q in (f'{d}/f_{f:04d}.png', f'{d}/f_{f:04d}.jpg') if os.path.exists(q)), None)
    b = Image.open(p).convert('RGB').resize((cw, ch), Image.LANCZOS) if p else Image.new('RGB', (cw, ch), (0, 0, 0))
    sheet.paste(a, (x, y)); sheet.paste(b, (x, y + ch + 2))
    dr = ImageDraw.Draw(sheet); dr.rectangle([x, y, x + 62, y + 20], fill=(0, 0, 0)); dr.text((x + 3, y + 1), f'f{f}', fill=(255, 255, 0), font=font)
sheet.save(out, quality=88); print(out, sheet.size)
