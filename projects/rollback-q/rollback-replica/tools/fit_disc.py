"""fit the big white 'code' disc on the blue-field frames: python tools/fit_disc.py SRC f1 f2 ..."""
import sys
import numpy as np
from PIL import Image
sys.path.insert(0, r'C:\Users\bg931\Documents\New project\rollback-replica\scripts')
from gen_util import s2w, zoom

src = sys.argv[1]
for f in [int(v) for v in sys.argv[2:]]:
    p = 'frames_full/f_%04d.jpg' % f if src == 'orig' else 'render/frames_%s/f_%04d.jpg' % (src, f)
    a = np.asarray(Image.open(p).convert('RGB')).astype(int)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    blue = (np.abs(R - 105) < 40) & (np.abs(G - 130) < 40) & (B > 200)
    pts = []
    for y in range(20, 430, 6):
        row = ~blue[y, 150:900]
        # longest run of non-blue
        best, cur, s0, bs = 0, 0, 0, 0
        for i, v in enumerate(row):
            if v:
                if cur == 0:
                    s0 = i
                cur += 1
                if cur > best:
                    best, bs = cur, s0
            else:
                cur = 0
        if best > 60:
            pts.append((150 + bs, y)); pts.append((150 + bs + best - 1, y))
    if len(pts) < 12:
        print(f, 'no disc'); continue
    P = np.array(pts, float)
    # algebraic circle fit, then drop outliers and refit
    for it in range(3):
        A = np.c_[2 * P[:, 0], 2 * P[:, 1], np.ones(len(P))]
        b = (P ** 2).sum(1)
        cx, cy, c = np.linalg.lstsq(A, b, rcond=None)[0]
        r = np.sqrt(c + cx * cx + cy * cy)
        d = np.abs(np.hypot(P[:, 0] - cx, P[:, 1] - cy) - r)
        keep = d < max(4.0, np.percentile(d, 70))
        if keep.sum() < 10:
            break
        P = P[keep]
    wx, wy = s2w(f, cx, cy)
    print('%3d screen c=(%.0f, %.0f) r=%.0f | world c=(%.0f, %.0f) r=%.0f  (pts %d, resid %.1f)' % (f, cx, cy, r, wx, wy, r / zoom(f), len(P), d[keep].mean()))
