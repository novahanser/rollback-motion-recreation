"""circle Hough on the dark contour pixels of the bead chain: python tools/bead_hough.py f"""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
f = int(sys.argv[1])
box = (670, 310, 1014, 534)
im = np.asarray(Image.open('frames_full/f_%04d.jpg' % f).convert('RGB').crop(box)).astype(float)
h, w = im.shape[:2]
dark = (im.max(axis=2) < 75)
ys, xs = np.nonzero(dark)
best = []
acc_all = {}
for r in np.arange(20, 41, 1.0):
    acc = np.zeros((h + 80, w + 80), np.float32)
    for t in np.arange(0, 360, 3):
        cx = np.round(xs - r * math.cos(math.radians(t))).astype(int) + 40
        cy = np.round(ys - r * math.sin(math.radians(t))).astype(int) + 40
        ok = (cx >= 0) & (cx < w + 80) & (cy >= 0) & (cy < h + 80)
        np.add.at(acc, (cy[ok], cx[ok]), 1.0)
    acc_all[r] = acc / (2 * math.pi * r)        # fraction of the circumference covered (approx)
cands = []
for r, acc in acc_all.items():
    a = sum(np.roll(np.roll(acc, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1)) / 9.0
    for _ in range(40):
        i = np.argmax(a); y, x = divmod(i, a.shape[1])
        if a[y, x] < 0.30: break
        cands.append((a[y, x], x - 40 + box[0], y - 40 + box[1], r))
        a = a.copy(); a[max(0, y - 6):y + 7, max(0, x - 6):x + 7] = 0
cands.sort(reverse=True)
keep = []
for c in cands:
    if all(math.hypot(c[1] - k[1], c[2] - k[2]) > 14 for k in keep):
        keep.append(c)
    if len(keep) >= 16: break
S = 3
vis = Image.open('frames_full/f_%04d.jpg' % f).convert('RGB').crop(box).resize((w * S, h * S), Image.LANCZOS)
d = ImageDraw.Draw(vis)
for sc, x, y, r in keep:
    X, Y = (x - box[0]) * S, (y - box[1]) * S
    d.ellipse([X - r * S, Y - r * S, X + r * S, Y + r * S], outline=(255, 255, 0), width=1)
    d.ellipse([X - 3, Y - 3, X + 3, Y + 3], fill=(255, 0, 0))
    print('score %.2f centre (%.0f, %.0f) r %.0f' % (sc, x, y, r))
vis.save('sheets/hough_%d.jpg' % f, quality=92)
dm = Image.fromarray((dark * 255).astype(np.uint8)).resize((w * S, h * S), Image.NEAREST); dm.save('sheets/dark_%d.png' % f)
