"""vertical position of the ruler's base line per frame, original vs a render tag: python tools/ruler_y.py TAG [f0 f1]"""
import sys
import numpy as np
from PIL import Image
tag = sys.argv[1]
f0, f1 = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 271)
def ry(path):
    a = np.asarray(Image.open(path).convert('L')).astype(np.float32)
    band = a[440:640]
    dark = band < 70
    # the base line is the row with the longest total run of dark pixels; require long horizontal runs: use a horizontal erosion
    run = dark[:, :-24]
    for k in range(1, 24):
        run = run & dark[:, k:dark.shape[1] - 24 + k]
    cnt = run.sum(axis=1)
    if cnt.max() < 40:
        return None, 0
    rows = np.nonzero(cnt > 0.6 * cnt.max())[0]
    w = cnt[rows]
    return 440 + float((rows * w).sum() / w.sum()), int(cnt.max())
out = []
for f in range(f0, f1 + 1):
    o, no = ry('frames_full/f_%04d.jpg' % f)
    r, nr = ry('render/frames_%s/f_%04d.jpg' % (tag, f))
    out.append((f, o, r))
    if o is not None and r is not None:
        print('f%3d  orig %.1f (%d)  %s %.1f (%d)   d=%+.1f' % (f, o, no, tag, r, nr, o - r))
    else:
        print('f%3d  orig %s  %s %s' % (f, o, tag, r))
