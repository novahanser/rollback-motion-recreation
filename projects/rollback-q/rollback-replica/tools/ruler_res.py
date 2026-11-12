"""per-frame residual of the ORIGINAL ruler's major ticks against the ideal world grid used by the replica.
For every frame: detect major tick peaks on screen, map to world with the camera table, compare with PHASE + n*P0 (n%5==MAJOR_MOD).
Prints: median residual (world px), linear slope of residual across the frame (=> zoom error), tick count.
python tools/ruler_res.py f0 f1 [dump]"""
import sys
import numpy as np
from PIL import Image
sys.path.insert(0, r'C:\Users\bg931\Documents\New project\rollback-replica\scripts')
from gen_util import zoom, CAM
import base

f0, f1 = int(sys.argv[1]), int(sys.argv[2])
dump = len(sys.argv) > 3
P0, PHASE, MM = base.P0, base.PHASE, base.MAJOR_MOD
PM = 5 * P0


def major_peaks(g, s):
    h = 11.0 * s
    rows = [r for r in range(1080) if 0.66 * h <= abs(r - 540) <= 0.92 * h]
    if len(rows) < 2:
        return []
    b = g[rows, :].astype(float)
    med = np.median(b, axis=1, keepdims=True)
    p = np.abs(b - med).mean(0)
    k = max(5, int(PM * s * 1.5) | 1)
    p = p - np.convolve(p, np.ones(k) / k, 'same')
    w = max(1, int(1.0 * s))
    thr = max(8.0, p.std() * 1.2)
    pk = []
    for x in range(3, 1917):
        if p[x] > thr and p[x] >= p[x - 1] and p[x] >= p[x + 1] and p[x] == p[max(0, x - 3 * w - 2):x + 3 * w + 3].max():
            # sub-pixel centroid
            lo, hi = max(0, x - w - 2), min(1920, x + w + 3)
            ww = np.clip(p[lo:hi], 0, None)
            pk.append(float((np.arange(lo, hi) * ww).sum() / max(ww.sum(), 1e-6)))
    return pk


allpts = []
for f in range(f0, f1 + 1):
    c = CAM[f]; s = c['s']
    g = np.asarray(Image.open('frames_full/f_%04d.jpg' % f).convert('L'))
    pk = major_peaks(g, s)
    if len(pk) < 4:
        print('%3d s=%.3f cx=%.1f  ticks=%d' % (f, s, c['cx'], len(pk))); continue
    X = np.array(pk)
    wx = c['cx'] + (X - 960.0) / s
    n = np.round((wx - PHASE - MM * P0) / PM)
    res = wx - (PHASE + MM * P0 + n * PM)
    # robust: keep the dominant cluster (circular median)
    ang = res / PM * 2 * np.pi
    m = np.angle(np.exp(1j * ang).mean()) / (2 * np.pi) * PM
    d = (res - m + PM / 2) % PM - PM / 2
    keep = np.abs(d) < 3.5
    if keep.sum() >= 4:
        A = np.vstack([wx[keep] - c['cx'], np.ones(keep.sum())]).T
        sl, ic = np.linalg.lstsq(A, (m + d)[keep], rcond=None)[0]
        print('%3d s=%.3f cx=%7.1f  ticks=%2d kept=%2d  res=%+6.2f  slope=%+.4f/1000px  rms=%.2f' % (
            f, s, c['cx'], len(pk), keep.sum(), ic, sl * 1000, float(np.sqrt(((m + d)[keep] - (A @ [sl, ic])) ** 2).mean()) if False else float(np.std((m + d)[keep] - A @ np.array([sl, ic])))))
        for x_, r_ in zip(wx[keep], (m + d)[keep]):
            allpts.append((f, x_, r_))
    else:
        print('%3d s=%.3f cx=%7.1f  ticks=%2d kept=%2d  (m=%.2f)' % (f, s, c['cx'], len(pk), keep.sum(), m))
if dump:
    np.save('sheets/ruler_res.npy', np.array(allpts))
