"""python tools/band.py OUT Y0 Y1 SCALE f1 f2 ... [--rep TAG] : horizontal band of the original frames stacked (optionally interleaved with the replica)"""
import sys, os
from PIL import Image, ImageDraw
args = sys.argv[1:]
rep = None
if '--rep' in args:
    i = args.index('--rep'); rep = args[i + 1]; args = args[:i] + args[i + 2:]
out, y0, y1, sc = args[0], int(args[1]), int(args[2]), float(args[3]); fs = [int(v) for v in args[4:]]
w, h = int(1920 * sc), int((y1 - y0) * sc)
rows = []
for f in fs:
    srcs = [('org', 'frames_full/f_%04d.jpg' % f)]
    if rep:
        p = next((q for q in ('render/frames_%s/f_%04d.png' % (rep, f), 'render/frames_%s/f_%04d.jpg' % (rep, f)) if os.path.exists(q)), None)
        if p: srcs.append((rep, p))
    for tag, p in srcs:
        im = Image.open(p).convert('RGB').crop((0, y0, 1920, y1)).resize((w, h), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        for gx in range(0, 1920, 100):
            d.line([gx * sc, 0, gx * sc, 5], fill=(0, 255, 0))
            if gx % 200 == 0: d.text((gx * sc + 2, 6), str(gx), fill=(0, 255, 0))
        d.rectangle([0, h - 13, 58, h], fill=(0, 0, 0)); d.text((2, h - 12), 'f%d %s' % (f, tag), fill=(255, 255, 0))
        rows.append(im)
sheet = Image.new('RGB', (w, len(rows) * (h + 2)), (255, 0, 80))
for i, im in enumerate(rows): sheet.paste(im, (0, i * (h + 2)))
sheet.save(out, quality=88); print(out, sheet.size)
