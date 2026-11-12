"""angular extent of the pink / blue ring sectors around RC, per frame (original, or a render tag)
python tools/meas_ring.py SRC f0 f1"""
import sys, os
import numpy as np
from PIL import Image
sys.path.insert(0, r'C:\Users\bg931\Documents\New project\rollback-replica\scripts')
from gen_util import s2w, zoom, CAM

src = sys.argv[1]
f0, f1 = int(sys.argv[2]), int(sys.argv[3])
RC = (700.0, 540.0)


def load(f):
    if src == 'orig':
        p = 'frames_full/f_%04d.jpg' % f
    else:
        p = 'render/frames_%s/f_%04d.jpg' % (src, f)
    return np.asarray(Image.open(p).convert('RGB')).astype(int)


def runs(mask):
    out = []
    start = None
    for i, v in enumerate(mask):
        if v and start is None:
            start = i
        if (not v) and start is not None:
            out.append((start, i - 1)); start = None
    if start is not None:
        out.append((start, len(mask) - 1))
    return out


yy, xx = np.mgrid[0:1080, 0:1920]
for f in range(f0, f1 + 1):
    a = load(f)
    c = CAM[f]
    wx = c['cx'] + (xx - 960.0) / c['s']
    wy = 540.0 + (yy - 540.0) / c['s']
    r = np.hypot(wx - RC[0], wy - RC[1])
    th = (np.degrees(np.arctan2(-(wy - RC[1]), wx - RC[0])) + 360.0) % 360.0      # CCW, y up
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    pk = (R > 200) & (G < 70) & (B > 70) & (B < 170)
    bl = (R < 90) & (G > 100) & (G < 170) & (B > 200)
    res = []
    for nm, m, (r0, r1) in (('pinkO', pk, (300, 415)), ('pinkI', pk, (210, 265)), ('blueO', bl, (300, 415)), ('blueI', bl, (210, 265))):
        band = (r > r0) & (r < r1)
        tb = th[band].astype(int)
        tot = np.bincount(tb, minlength=360).astype(float)
        hit = np.bincount(th[band & m].astype(int), minlength=360).astype(float)
        cov_ = np.where(tot > 30, hit / np.maximum(tot, 1), 0)
        rr = [(s, e) for s, e in runs(cov_ > 0.5) if e - s >= 2]
        res.append('%s %s' % (nm, rr))
    print(f, ' | '.join(res))
