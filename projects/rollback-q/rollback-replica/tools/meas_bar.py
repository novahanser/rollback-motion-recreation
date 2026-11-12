"""extent of a coloured horizontal bar in a world band, per frame.
python tools/meas_bar.py SRC f0 f1 wy0 wy1 wx0 wx1 kind   (kind: crimson | black | white)"""
import sys
import numpy as np
from PIL import Image
sys.path.insert(0, r'C:\Users\bg931\Documents\New project\rollback-replica\scripts')
from gen_util import s2w, w2s, zoom

src = sys.argv[1]; f0, f1 = int(sys.argv[2]), int(sys.argv[3])
wy0, wy1, wx0, wx1 = [float(v) for v in sys.argv[4:8]]
kind = sys.argv[8]
for f in range(f0, f1 + 1):
    p = 'frames_full/f_%04d.jpg' % f if src == 'orig' else 'render/frames_%s/f_%04d.jpg' % (src, f)
    a = np.asarray(Image.open(p).convert('RGB')).astype(int)
    X0, Y0 = w2s(f, wx0, wy0); X1, Y1 = w2s(f, wx1, wy1)
    X0, X1 = int(max(0, X0)), int(min(1920, X1)); Y0, Y1 = int(max(0, Y0)), int(min(1080, Y1))
    if X1 <= X0 or Y1 <= Y0:
        print(f, 'off'); continue
    b = a[Y0:Y1, X0:X1]
    R, G, B = b[..., 0], b[..., 1], b[..., 2]
    if kind == 'crimson':
        m = (R > 110) & (G < 70) & (B < 125) & (R - G > 80)
    elif kind == 'black':
        m = (R < 40) & (G < 40) & (B < 40)
    else:
        m = (R > 236) & (G > 236) & (B > 236)
    col = m.mean(0)
    xs = np.nonzero(col > 0.45)[0]
    if len(xs) == 0:
        print(f, 'none'); continue
    # longest run
    runs, s0 = [], xs[0]
    for i in range(1, len(xs)):
        if xs[i] != xs[i - 1] + 1:
            runs.append((s0, xs[i - 1])); s0 = xs[i]
    runs.append((s0, xs[-1]))
    out = []
    for a_, b_ in runs:
        if b_ - a_ >= 6:
            out.append('%.0f..%.0f' % (s2w(f, X0 + a_, 0)[0], s2w(f, X0 + b_ + 1, 0)[0]))
    print(f, ' '.join(out))
