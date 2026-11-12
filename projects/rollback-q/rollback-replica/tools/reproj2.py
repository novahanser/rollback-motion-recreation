"""Reprojection grid using cam.json: python tools/reproj2.py OUT COLS CELLW f1 f2 ..."""
import sys, json, numpy as np
from PIL import Image, ImageDraw
cam = json.load(open(r'C:\Users\bg931\Documents\New project\rollback-replica\scripts\cam.json'))
PANO = Image.open('pano/pano.png').convert('RGB')
out = sys.argv[1]; cols = int(sys.argv[2]); cw = int(sys.argv[3]); fs = [int(x) for x in sys.argv[4:]]
ch = cw * 9 // 16
rows = (len(fs) + cols - 1) // cols
sheet = Image.new('RGB', (cols * cw, rows * ch))
for i, f in enumerate(fs):
    s = cam[f]['s']; cx = cam[f]['cx']
    fr = Image.open(f'frames_full/f_{f:04d}.jpg').convert('RGB')
    x0 = cx - 960 / s; y0 = 540 - 540 / s
    warped = PANO.transform((1920, 1080), Image.AFFINE, (1 / s, 0, x0, 0, 1 / s, y0), resample=Image.BILINEAR, fillcolor=(120, 0, 120))
    a = np.asarray(fr).copy(); b = np.asarray(warped)
    for ys in range(0, 1080, 270):
        a[ys + 135:ys + 270] = b[ys + 135:ys + 270]
    im = Image.fromarray(a).resize((cw, ch), Image.LANCZOS)
    d = ImageDraw.Draw(im); d.rectangle([0, 0, 250, 14], fill=(0, 0, 0)); d.text((3, 2), f'f{f} s={s:.3f} cx={cx:.0f} rows: frame/pano', fill=(255, 255, 0))
    sheet.paste(im, ((i % cols) * cw, (i // cols) * ch))
sheet.save(out, quality=88); print(out, sheet.size)
