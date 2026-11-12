"""Hough tracking of the vinyl record (pink label disc, radius known in world px) per frame.
python tools/track_vinyl.py SRC f0 f1 [R_LABEL]"""
import sys
import numpy as np
from PIL import Image
sys.path.insert(0, r'C:\Users\bg931\Documents\New project\rollback-replica\scripts')
from gen_util import s2w, w2s, zoom, CAM

src = sys.argv[1]
f0, f1 = int(sys.argv[2]), int(sys.argv[3])
RL = float(sys.argv[4]) if len(sys.argv) > 4 else 92.0
WIN = (780.0, 330.0, 1220.0, 960.0)          # world window searched for the centre


def load(f):
    p = 'frames_full/f_%04d.jpg' % f if src == 'orig' else 'render/frames_%s/f_%04d.jpg' % (src, f)
    return np.asarray(Image.open(p).convert('RGB')).astype(int)


def edges(m):
    e = np.zeros_like(m)
    e[1:-1, 1:-1] = m[1:-1, 1:-1] & ~(m[:-2, 1:-1] & m[2:, 1:-1] & m[1:-1, :-2] & m[1:-1, 2:])
    return e


def hough(m, r_px, f):
    """best centre (screen px) of a circle of radius r_px through the edge pixels of mask m"""
    ys, xs = np.nonzero(edges(m))
    if len(xs) < 20:
        return None
    acc = np.zeros((1080 // 2 + 400, 1920 // 2 + 400), np.int32)          # half-res accumulator with a 200 px margin
    th = np.linspace(0, 2 * np.pi, 240, endpoint=False)
    cx = (xs[:, None] + r_px * np.cos(th)[None, :]) / 2.0 + 200
    cy = (ys[:, None] + r_px * np.sin(th)[None, :]) / 2.0 + 200
    ok = (cx >= 0) & (cx < acc.shape[1]) & (cy >= 0) & (cy < acc.shape[0])
    np.add.at(acc, (cy[ok].astype(int), cx[ok].astype(int)), 1)
    # restrict to the world window
    a = w2s(f, WIN[0], WIN[1]); b = w2s(f, WIN[2], WIN[3])
    x0, x1 = int(a[0] / 2 + 200), int(b[0] / 2 + 200)
    y0, y1 = int(a[1] / 2 + 200), int(b[1] / 2 + 200)
    x0, y0 = max(0, x0), max(0, y0)
    sub = acc[y0:y1, x0:x1]
    if sub.size == 0:
        return None
    # smooth 3x3
    s = sub.astype(float)
    s[1:-1, 1:-1] = (sub[:-2, :-2] + sub[:-2, 1:-1] + sub[:-2, 2:] + sub[1:-1, :-2] + sub[1:-1, 1:-1] + sub[1:-1, 2:] +
                     sub[2:, :-2] + sub[2:, 1:-1] + sub[2:, 2:]) / 9.0
    iy, ix = np.unravel_index(np.argmax(s), s.shape)
    return ((ix + x0 - 200) * 2.0, (iy + y0 - 200) * 2.0, float(s[iy, ix]))


for f in range(f0, f1 + 1):
    a = load(f)
    z = zoom(f)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    pk = (R > 190) & (G < 90) & (B > 60) & (B < 180)
    h = hough(pk, RL * z, f)
    out = '%d z=%.3f ' % (f, z)
    if h:
        wx, wy = s2w(f, h[0], h[1])
        out += 'label c=(%.0f, %.0f) score=%.0f (max %.0f) ' % (wx, wy, h[2], 2 * np.pi * RL * z / 2 * 240 / 240)
    # blue centre dot: small compact blue blob near the label centre
    bl = (R < 110) & (G > 90) & (G < 190) & (B > 190)
    if h:
        yy, xx = np.mgrid[0:1080, 0:1920]
        near = np.hypot(xx - h[0], yy - h[1]) < 40 * z
        m = bl & near
        if m.sum() > 8:
            ys, xs = np.nonzero(m)
            wx, wy = s2w(f, xs.mean(), ys.mean())
            out += '| dot c=(%.1f, %.1f) n=%d r~%.1f' % (wx, wy, m.sum(), np.sqrt(m.sum() / np.pi) / z)
    print(out)
