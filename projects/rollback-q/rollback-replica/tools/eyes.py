import sys, numpy as np
from PIL import Image
src = sys.argv[1] if len(sys.argv) > 1 else 'frames_full/f_%04d.jpg'
for f in range(203, 227):
    a = np.asarray(Image.open(src % f).convert('RGB')).astype(int)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    m = (R > 190) & (G < 90) & (B > 60) & (B < 170)          # magenta eyes
    ys, xs = np.nonzero(m)
    if len(xs) < 40:
        print('f%d: none' % f); continue
    # vertical extent of the eye band (median) and x clusters
    col = m.sum(0)
    on = np.where(col >= 6)[0]
    runs = []
    st = pv = on[0]
    for x in on[1:]:
        if x > pv + 3:
            runs.append((st, pv)); st = x
        pv = x
    runs.append((st, pv))
    yb = (int(np.percentile(ys, 5)), int(np.percentile(ys, 95)))
    print('f%d y%s: ' % (f, yb) + ' '.join('%d-%d' % r for r in runs if r[1] - r[0] >= 3))
