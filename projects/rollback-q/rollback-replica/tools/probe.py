"""python tools/probe.py SRC f0 f1 wx,wy [wx,wy ...]  -> median RGB of a 5x5 screen patch at world points, per frame"""
import sys
import numpy as np
from PIL import Image
sys.path.insert(0, r'C:\Users\bg931\Documents\New project\rollback-replica\scripts')
from gen_util import w2s

src = sys.argv[1]; f0, f1 = int(sys.argv[2]), int(sys.argv[3])
pts = [tuple(float(v) for v in a.split(',')) for a in sys.argv[4:]]
for f in range(f0, f1 + 1):
    p = 'frames_full/f_%04d.jpg' % f if src == 'orig' else 'render/frames_%s/f_%04d.jpg' % (src, f)
    a = np.asarray(Image.open(p).convert('RGB')).astype(int)
    out = []
    for wx, wy in pts:
        X, Y = w2s(f, wx, wy)
        X, Y = int(round(X)), int(round(Y))
        if 3 <= X < 1917 and 3 <= Y < 1077:
            m = np.median(a[Y - 2:Y + 3, X - 2:X + 3].reshape(-1, 3), axis=0)
            out.append('(%3d,%3d,%3d)' % tuple(m))
        else:
            out.append('   off-screen ')
    print('%3d ' % f + ' '.join(out))
