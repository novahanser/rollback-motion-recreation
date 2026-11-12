"""Frame-to-frame camera dx from the ruler major-tick profile (unambiguous within +-18 world px)."""
import numpy as np, json
from PIL import Image
tr = json.load(open('track_ruler.json'))
PM = 36.6667

def box(v, k):
    k = int(k) | 1
    return np.convolve(np.pad(v, (k // 2, k // 2), mode='edge'), np.ones(k) / k, 'valid')

def prof(f):
    r = tr[f]
    if not (r['ok'] and r.get('acpk', 0) > 0.45 and abs(r.get('yc', 0) - 539.5) < 2 and 0.3 < r.get('s', 0) < 30):
        return None
    a = np.asarray(Image.open(f'frames_full/f_{f:04d}.jpg').convert('L')).astype(np.float32)
    s = r['s']
    r0 = int(round(6.8 * s)); r1 = max(r0 + 1, int(round(10.2 * s)))
    yci = int(round(r['yc'] - 0.5))
    rows = list(range(yci - r1, yci - r0 + 1)) + list(range(yci + 1 + r0, yci + r1 + 2))
    p = a[rows].mean(axis=0)
    w = np.abs(p - box(p, max(15, int(8 * s)) ))
    return s, w

res = []
prev = None
for f in range(272):
    cur = prof(f)
    if cur is not None and prev is not None:
        s1, w1 = prev; s2, w2 = cur
        # resample w1 to scale s2 about 960
        x = np.arange(1920)
        xs = (x - 960) * (s1 / s2) + 960
        w1r = np.interp(xs, x, w1, left=0, right=0)
        maxsh = int(PM * s2 / 2)
        best = None
        a_ = w1r - w1r.mean(); b_ = w2 - w2.mean()
        for sh in range(-maxsh, maxsh + 1):
            if sh >= 0:
                c = (a_[:1920 - sh] * b_[sh:]).sum()
            else:
                c = (a_[-sh:] * b_[:1920 + sh]).sum()
            if best is None or c > best[0]: best = (c, sh)
        c, sh = best
        nrm = np.sqrt((a_ ** 2).sum() * (b_ ** 2).sum()) + 1e-9
        res.append((f, s2, sh, -sh / s2, c / nrm))
    else:
        res.append((f, cur[0] if cur else None, None, None, None))
    prev = cur
json.dump(res, open('ruler_flow.json', 'w'))
acc = 0
for (f, s, sh, dcx, q) in res:
    if sh is None: print(f"{f:3d} s={s} --"); continue
    print(f"{f:3d} s={s:.3f} dx={sh:4d}px dcx={dcx:7.2f} q={q:.2f}")
