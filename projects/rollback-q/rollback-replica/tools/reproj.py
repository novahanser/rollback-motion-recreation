"""Reprojection check: python tools/reproj.py OUT F:S:CX [F:S:CX ...]  -> stacked rows: frame | pano warped (side by side, half res)"""
import sys, numpy as np
from PIL import Image, ImageDraw
PANO = Image.open('pano/pano.png').convert('RGB')
rows = []
for spec in sys.argv[2:]:
    f, s, cx = spec.split(':'); f = int(f); s = float(s); cx = float(cx)
    fr = Image.open(f'frames_full/f_{f:04d}.jpg').convert('RGB')
    # world rect visible
    x0 = cx - 960 / s; x1 = cx + 960 / s; y0 = 540 - 540 / s; y1 = 540 + 540 / s
    warped = PANO.transform((1920, 1080), Image.AFFINE, (1 / s, 0, x0, 0, 1 / s, y0), resample=Image.BILINEAR, fillcolor=(120, 0, 120))
    # mark out-of-pano
    a = np.asarray(fr).astype(np.float32); b = np.asarray(warped).astype(np.float32)
    # checker blend: alternate 120px vertical stripes frame/pano to judge alignment
    out = a.copy()
    for xs in range(0, 1920, 240):
        out[:, xs + 120:xs + 240] = b[:, xs + 120:xs + 240]
    im = Image.fromarray(out.astype(np.uint8)).resize((1280, 720), Image.LANCZOS)
    d = ImageDraw.Draw(im); d.rectangle([0, 0, 330, 22], fill=(0, 0, 0)); d.text((4, 4), f'f{f} s={s} cx={cx} (stripes: frame|pano)', fill=(255, 255, 0))
    rows.append(im)
sheet = Image.new('RGB', (1280, 720 * len(rows)))
for i, im in enumerate(rows): sheet.paste(im, (0, 720 * i))
sheet.save(sys.argv[1], quality=88); print(sys.argv[1], sheet.size)
