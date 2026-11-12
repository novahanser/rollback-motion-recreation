"""camera audit: horizontal offset between the ruler ticks of the original and of a render, per frame.
python tools/ruler_shift.py TAG f0 f1   -> shift in screen px (positive: original ticks are to the RIGHT of the replica's)
and the implied correction of cx (world px) = -shift / s"""
import sys
import numpy as np
from PIL import Image
sys.path.insert(0, r'C:\Users\bg931\Documents\New project\rollback-replica\scripts')
from gen_util import zoom

tag = sys.argv[1]
f0, f1 = int(sys.argv[2]), int(sys.argv[3])


def prof(a, s, lo, hi):
    """tick comb: mean |deviation from the row median| in the band lo..hi (fractions of the major half height)"""
    h = 11.0 * s
    rows = [r for r in range(1080) if lo * h <= abs(r - 540) <= hi * h]
    if not rows:
        return None
    b = a[rows, :].astype(float)
    med = np.median(b, axis=1, keepdims=True)
    p = np.abs(b - med).mean(0)
    k = max(5, int(36.33 * s * 2) | 1)
    sm = np.convolve(p, np.ones(k) / k, 'same')
    p = p - sm
    return p


def best_shift(po, pr, maxs):
    best = (-1e9, 0)
    n = len(po)
    res = []
    for d in range(-maxs, maxs + 1):
        if d >= 0:
            a, b = po[d:], pr[:n - d]
        else:
            a, b = po[:n + d], pr[-d:]
        den = np.sqrt((a * a).sum() * (b * b).sum()) + 1e-9
        c = float((a * b).sum() / den)
        res.append((c, d))
    res.sort(reverse=True)
    return res[0], res


for f in range(f0, f1 + 1):
    s = zoom(f)
    try:
        o = np.asarray(Image.open('frames_full/f_%04d.jpg' % f).convert('L'))
        r = np.asarray(Image.open('render/frames_%s/f_%04d.jpg' % (tag, f)).convert('L'))
    except Exception as e:
        print(f, 'missing'); continue
    out = '%3d s=%.3f' % (f, s)
    # coarse: major ticks only (period 36.33 world px)
    po, pr = prof(o, s, 0.66, 0.92), prof(r, s, 0.66, 0.92)
    if po is None:
        print(out, 'band too thin'); continue
    maxs = int(min(300, 18.0 * s + 2))
    (c1, d1), _ = best_shift(po, pr, maxs)
    # fine: all ticks (period 7.27 world px) around the coarse result
    po2, pr2 = prof(o, s, 0.2, 0.5), prof(r, s, 0.2, 0.5)
    fine = None
    if po2 is not None:
        (c2, d2), allr = best_shift(po2, pr2, maxs)
        cand = [(c, d) for c, d in allr if abs(d - d1) <= max(2, 3.7 * s)]
        fine = max(cand) if cand else None
    out += ' major: shift=%+d px corr=%.2f' % (d1, c1)
    if fine:
        out += ' | fine: shift=%+d px corr=%.2f -> dcx=%+.1f world' % (fine[1], fine[0], -fine[1] / s)
    print(out)
