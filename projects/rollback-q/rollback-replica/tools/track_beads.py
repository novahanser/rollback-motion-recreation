"""track the white highlight blobs of the bead chain in a screen window: python tools/track_beads.py SRC f0 f1 [x0 y0 x1 y1]"""
import sys
import numpy as np
from PIL import Image

src = sys.argv[1]; f0, f1 = int(sys.argv[2]), int(sys.argv[3])
box = [int(v) for v in sys.argv[4:8]] if len(sys.argv) > 7 else [670, 310, 1010, 525]


def label(m):
    h, w = m.shape
    lab = np.zeros((h, w), np.int32)
    n = 0
    out = []
    for y in range(h):
        for x in range(w):
            if m[y, x] and not lab[y, x]:
                n += 1
                stack = [(y, x)]
                lab[y, x] = n
                pts = []
                while stack:
                    cy, cx = stack.pop()
                    pts.append((cy, cx))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and m[ny, nx] and not lab[ny, nx]:
                            lab[ny, nx] = n
                            stack.append((ny, nx))
                out.append(np.array(pts))
    return out


for f in range(f0, f1 + 1):
    p = 'frames_full/f_%04d.jpg' % f if src == 'orig' else 'render/frames_%s/f_%04d.jpg' % (src, f)
    a = np.asarray(Image.open(p).convert('RGB').crop(box)).astype(int)
    m = (a.min(axis=2) > 225)
    blobs = []
    for pts in label(m):
        if 120 <= len(pts) <= 1800:
            ys, xs = pts[:, 0], pts[:, 1]
            hgt, wid = ys.max() - ys.min() + 1, xs.max() - xs.min() + 1
            if 0.45 < wid / float(hgt) < 2.2 and len(pts) > 0.5 * wid * hgt:
                blobs.append((xs.mean() + box[0], ys.mean() + box[1], len(pts)))
    blobs.sort()
    print('%3d n=%2d ' % (f, len(blobs)) + ' '.join('(%.0f,%.0f|%d)' % b for b in blobs))
