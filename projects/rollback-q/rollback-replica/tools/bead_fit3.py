"""fit bead radius / centre offset functions to the silhouettes of the original"""
import sys, math
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
sys.path.insert(0, r'C:\Users\bg931\Documents\New project\rollback-replica\scripts')
import chain3d
BOXS = (660, 300, 1024, 544)
XMAX = 945          # ignore everything right of this screen x (the cyan bar covers the right end on some frames)
def silhouette(f, thr=212):
    im = np.asarray(Image.open('frames_full/f_%04d.jpg' % f).convert('RGB').crop(BOXS)).astype(int)
    h, w = im.shape[:2]
    white = (im.min(axis=2) > thr)
    barrier = np.asarray(Image.fromarray((white * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))) > 0
    reach = np.zeros((h, w), bool)
    stack = [(y, x) for y in range(h) for x in (0, w - 1)] + [(y, x) for x in range(w) for y in (0, h - 1)]
    while stack:
        y, x = stack.pop()
        if y < 0 or y >= h or x < 0 or x >= w or reach[y, x] or barrier[y, x]:
            continue
        reach[y, x] = True
        stack.extend(((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)))
    return ~reach
FR = [107, 108, 111, 112]
SIL = {f: silhouette(f) for f in FR}
h, w = SIL[107].shape
yy, xx = np.mgrid[0:h, 0:w]
X, Y = xx + BOXS[0] + 0.5, yy + BOXS[1] + 0.5
valid = (X < XMAX) & (X > 698)
_t = math.radians(15.52)
_du = (X - 853.8) * math.cos(_t) + (Y - 409.4) * math.sin(_t); _dv = -(X - 853.8) * math.sin(_t) + (Y - 409.4) * math.cos(_t)
valid &= (np.hypot(_du / 125.5, _dv / 42.7) > 0.72)          # the hole of the ring is not seeded: leave the inside out of the score
HL = {f: chain3d.highlights(chain3d.src_index(f)) for f in FR}
for f in FR:
    print(f, 'sil area', int((SIL[f] & valid).sum()))
def model(f, p):
    m = np.zeros((h, w), bool)
    for (hx, hy, rh, th) in HL[f]:
        t = math.radians(th)
        r = p[0] + p[1] * math.sin(t) + p[2] * math.cos(t)
        ox = p[3] + p[4] * math.sin(t) + p[5] * math.cos(t)
        oy = p[6] + p[7] * math.sin(t) + p[8] * math.cos(t)
        m |= ((X - (hx - ox)) ** 2 + (Y - (hy - oy)) ** 2) < r * r
    return m
def score(p):
    inter = uni = 0
    for f in FR:
        m = model(f, p)
        inter += (m & SIL[f] & valid).sum(); uni += ((m | SIL[f]) & valid).sum()
    return inter / float(uni)
p = [30.5, 4.5, 0.0, 9.5, 4.5, 0.0, -8.0, -4.5, 0.0]
best = score(p); print('start IoU %.4f' % best)
step = [2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0]
for it in range(7):
    for i in range(9):
        for sgn in (1, -1):
            while True:
                q = list(p); q[i] += sgn * step[i]
                s = score(q)
                if s > best + 1e-5:
                    p, best = q, s
                else:
                    break
    step = [s_ * 0.55 for s_ in step]
    print('it %d IoU %.4f  p=%s' % (it, best, ' '.join('%.2f' % v for v in p)))
np.save('sheets/bead_p.npy', np.array(p))
# preview: silhouette boundary + model circles on the original
cells = []
for f in (107, 108, 107, 108):
    S = 3
    o = Image.open('frames_full/f_%04d.jpg' % f).convert('RGB').crop(BOXS).resize((w * S, h * S), Image.LANCZOS)
    d = ImageDraw.Draw(o)
    for (hx, hy, rh, th) in HL[f]:
        t = math.radians(th)
        r = p[0] + p[1] * math.sin(t) + p[2] * math.cos(t)
        cx_ = hx - (p[3] + p[4] * math.sin(t) + p[5] * math.cos(t)); cy_ = hy - (p[6] + p[7] * math.sin(t) + p[8] * math.cos(t))
        XX, YY = (cx_ - BOXS[0]) * S, (cy_ - BOXS[1]) * S
        d.ellipse([XX - r * S, YY - r * S, XX + r * S, YY + r * S], outline=(255, 255, 0), width=1)
        d.ellipse([(hx - BOXS[0]) * S - 3, (hy - BOXS[1]) * S - 3, (hx - BOXS[0]) * S + 3, (hy - BOXS[1]) * S + 3], fill=(255, 0, 0))
    cells.append(o)
sheet = Image.new('RGB', (2 * (w * 3 + 4), 2 * (h * 3 + 4)), (255, 0, 80))
for i, c in enumerate(cells):
    sheet.paste(c, ((i % 2) * (w * 3 + 4), (i // 2) * (h * 3 + 4)))
sheet.save('sheets/bead_fit3.jpg', quality=90); print(sheet.size)
