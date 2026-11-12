"""per-frame placement of the bracelet: fit translation + scale of the highlight model to the white blobs of the original
python tools/chain_track.py f0 f1"""
import sys, math
import numpy as np
from PIL import Image
sys.path.insert(0, r'C:\Users\bg931\Documents\New project\rollback-replica\scripts')
import chain3d
from gen_util import w2s, zoom

def blobs(f, box):
    a = np.asarray(Image.open('frames_full/f_%04d.jpg' % f).convert('RGB').crop(box)).astype(int)
    m = (a.min(axis=2) > 225)
    h, w = m.shape
    lab = np.zeros((h, w), np.int32); out = []; n = 0
    ys, xs = np.nonzero(m)
    for y0, x0 in zip(ys, xs):
        if lab[y0, x0]:
            continue
        n += 1; st = [(y0, x0)]; lab[y0, x0] = n; pts = []
        while st:
            cy, cx = st.pop(); pts.append((cy, cx))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < h and 0 <= nx < w and m[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = n; st.append((ny, nx))
            if len(pts) > 2500:
                break
        if 90 <= len(pts) <= 1300:
            p = np.array(pts); hgt = p[:, 0].max() - p[:, 0].min() + 1; wid = p[:, 1].max() - p[:, 1].min() + 1
            if 0.5 < wid / float(hgt) < 2.0 and len(pts) > 0.5 * wid * hgt:
                out.append((p[:, 1].mean() + box[0], p[:, 0].mean() + box[1], len(pts)))
    return out

def guess(f):
    box = {105: (842.0, 422.0), 125: (820.5, 424.5), 126: (824.5, 427.0), 127: (823.0, 424.0), 128: (826.5, 419.5), 132: (843.5, 431.0),
           134: (841.0, 439.5), 135: (830.5, 440.5), 136: (810.0, 440.5)}
    if f < 137:
        cur = box[105]
        for k in sorted(box):
            if k <= f: cur = box[k]
        return cur[0], cur[1], 0.92 if f >= 125 else 1.0
    wx = 4115.5 + (4140.0 - 4115.5) * min(1.0, (f - 137) / 13.0)
    sx, sy = w2s(f, wx, 392.0)
    return sx, sy, 0.9

f0, f1 = int(sys.argv[1]), int(sys.argv[2])
res = {}
for f in range(f0, f1 + 1):
    gx, gy, gs = guess(f)
    bx = (int(max(0, gx - 230)), int(max(0, gy - 150)), int(min(1920, gx + 230)), int(min(1080, gy + 150)))
    B = np.array([(x, y) for x, y, n in blobs(f, bx)])
    if len(B) < 4:
        print(f, 'too few blobs', len(B)); continue
    n30 = chain3d.src_index(f)
    best = None
    for dph in (0.0, -0.1, 0.1, -0.2, 0.2):
        M0 = np.array([(hx - chain3d.BOX[0], hy - chain3d.BOX[1]) for hx, hy, rh, th, phi in chain3d.highlights(n30, chain3d.PH0 + dph)])
        def cost(tx, ty, s):
            M = M0 * s + (tx, ty)
            d = np.hypot(B[:, None, 0] - M[None, :, 0], B[:, None, 1] - M[None, :, 1]).min(axis=1)
            return np.minimum(d, 12.0).sum() / len(B), int((d < 5).sum())
        cur = (gx, gy, gs); cc = cost(*cur)[0]
        for tx in np.arange(gx - 60, gx + 61, 6.0):
            for ty in np.arange(gy - 40, gy + 41, 6.0):
                for s in (0.80, 0.86, 0.92, 0.98, 1.04):
                    c = cost(tx, ty, s)[0]
                    if c < cc: cc, cur = c, (tx, ty, s)
        step = [3.0, 3.0, 0.03]
        for it in range(40):
            imp = False
            for i in range(3):
                for sg in (1, -1):
                    q = list(cur); q[i] += sg * step[i]
                    c = cost(*q)[0]
                    if c < cc - 1e-6: cc, cur, imp = c, tuple(q), True
            if not imp:
                step = [v * 0.5 for v in step]
                if step[0] < 0.05: break
        if best is None or cc < best[0]:
            best = (cc, cur, dph, cost(*cur)[1])
    cc, cur, dph, nin = best
    res[f] = cur
    print('f%d  centre (%.1f, %.1f) scale %.3f  dphase %+.1f  cost %.2f  inliers %d/%d   guess (%.0f,%.0f)  world c (%.1f)' % (
        f, cur[0], cur[1], cur[2], dph, cc, nin, len(B), gx, gy, (cur[0] - 960) / zoom(f)))
np.save('sheets/chain_track_%d_%d.npy' % (f0, f1), np.array([(f,) + tuple(v) for f, v in sorted(res.items())]))
