"""Sub-pixel camera x from ruler major-tick phase. Combines with coarse registration."""
import numpy as np, json
from PIL import Image

def box(v, k):
    k = int(k) | 1
    return np.convolve(np.pad(v, (k // 2, k // 2), mode='edge'), np.ones(k) / k, 'valid')

def tickness(prof):
    # ticks are thin deviations from local background (either polarity)
    bg = box(prof, 41)
    return np.abs(prof - bg)

def demod(w, periods, x0=0.0):
    x = np.arange(len(w)) + x0
    best = None
    for P in periods:
        C = (w * np.exp(-2j * np.pi * x / P)).sum()
        if best is None or abs(C) > best[0]:
            best = (abs(C), P, np.angle(C))
    mag, P, ang = best
    phi = (ang / (2 * np.pi)) * P   # tick positions x = phi + n*P  (since C ~ sum exp(-2pi i (x)/P) -> peak when x = phi)
    return P, phi % P, mag / (w.sum() + 1e-9)

# ---- pano lattice
pano = np.asarray(Image.open('pano/pano.png').convert('L')).astype(np.float32)
pm = (pano[528:533].mean(axis=0) + pano[547:552].mean(axis=0)) / 2
wm = tickness(pm)
Pm, phim, qm = demod(wm, np.arange(36.50, 36.90, 0.0005))
print('pano major period', Pm, 'phase', phim, 'quality', qm)
P0 = Pm / 5

tr = json.load(open('track_ruler.json'))
cx2 = json.load(open('track_x2.json'))
out = []
for f in range(272):
    r = tr[f]; c = cx2[f]
    rec = dict(f=f, s=c['s'], cx=c['cx'], ratio=round(c['score'] / max(c['second'], 1e-6), 2), ruler=bool(r['ok'] and r.get('acpk', 0) > 0.5 and abs(r.get('yc', 0) - 539.5) < 2 and 0.3 < r.get('s', 0) < 30))
    if rec['ruler']:
        a = np.asarray(Image.open(f'frames_full/f_{f:04d}.jpg').convert('L')).astype(np.float32)
        s = r['s'] * 7.3333 / P0  # rescale to calibrated P0
        yc = r['yc']
        # major-only band: 6.6s..10.5s from centre
        r0 = int(round(6.6 * s)); r1 = max(r0 + 1, int(round(10.5 * s)))
        yci = int(round(yc - 0.5))
        rows = list(range(yci - r1, yci - r0 + 1)) + list(range(yci + 1 + r0, yci + r1 + 2))
        rows = [y for y in rows if 0 <= y < a.shape[0]]
        prof = a[rows].mean(axis=0)
        w = tickness(prof)
        P, phi, q = demod(w, Pm * s * np.linspace(0.985, 1.015, 121))
        s_ref = P / Pm
        # cx ≡ phim - (phi-960)/s  (mod Pm)   [pixel centre conventions cancel]
        base = phim - (phi - 960.0) / s_ref
        n = np.round((c['cx'] - base) / Pm)
        cxr = base + n * Pm
        rec.update(s_ref=round(float(s_ref), 5), cx_ref=round(float(cxr), 2), resid=round(float(c['cx'] - cxr), 2), q=round(float(q), 3))
    out.append(rec)
json.dump(dict(P0=P0, Pm=Pm, phim=phim, frames=out), open('track_phase.json', 'w'))
for rec in out:
    if rec['ruler']:
        print(f"{rec['f']:3d} s={rec['s']:.4f} sref={rec['s_ref']:.4f} cx={rec['cx']:8.1f} cxref={rec['cx_ref']:9.2f} resid={rec['resid']:6.2f} q={rec['q']:.2f} ratio={rec['ratio']}")
    else:
        print(f"{rec['f']:3d} s={rec['s']:.4f} cx={rec['cx']:8.1f} (no ruler) ratio={rec['ratio']}")
