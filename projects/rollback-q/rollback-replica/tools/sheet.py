"""Contact sheet: python tools/sheet.py START END STEP COLS CELLW OUT [dir] [pattern]"""
import sys
from PIL import Image, ImageDraw, ImageFont

start, end, step, cols, cw = [int(x) for x in sys.argv[1:6]]
out = sys.argv[6]
d = sys.argv[7] if len(sys.argv) > 7 else 'frames_full'
pat = sys.argv[8] if len(sys.argv) > 8 else 'f_%04d.jpg'
fr = list(range(start, end + 1, step))
ch = int(cw * 1080 / 1920)
rows = (len(fr) + cols - 1) // cols
pad = 4
sheet = Image.new('RGB', (cols * (cw + pad) + pad, rows * (ch + pad) + pad), (40, 40, 40))
try:
    font = ImageFont.truetype('arial.ttf', 18)
except Exception:
    font = ImageFont.load_default()
for i, f in enumerate(fr):
    im = Image.open(f'{d}/{pat % f}').convert('RGB').resize((cw, ch), Image.LANCZOS)
    x = pad + (i % cols) * (cw + pad)
    y = pad + (i // cols) * (ch + pad)
    sheet.paste(im, (x, y))
    dr = ImageDraw.Draw(sheet)
    lab = f'{f} ({f/24:.2f}s)'
    dr.rectangle([x, y, x + 9 * len(lab) + 8, y + 22], fill=(0, 0, 0))
    dr.text((x + 4, y + 2), lab, fill=(255, 255, 0), font=font)
sheet.save(out, quality=88)
print(out, sheet.size)
