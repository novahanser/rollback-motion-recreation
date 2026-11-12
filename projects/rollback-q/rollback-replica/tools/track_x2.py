"""Second pass: constrained registration per segment."""
import numpy as np, json, sys
from PIL import Image
import track_x as T

tr = json.load(open('track_ruler.json'))
first = {r['f']: r for r in json.load(open('track_x.json'))}

def match_range(im, s, yc, cx0, cx1):
    # reimplement using T.match internals but constrained: call T.match on masked pano copy via monkeypatch
    w = max(8, int(round(1920 / s / T.DS)))
    h = max(8, int(round(1080 / s / T.DS)))
    fr = im.resize((w, h), Image.LANCZOS)
    a = np.asarray(fr).astype(np.float32)
    g = T.gradmag(a)
    cyf = yc / 1080.0 * h
    ci = int(round(cyf))
    g[max(0, ci - 8):ci + 8, :] = 0
    top = int(round(T.PH / T.DS / 2 - cyf))
    r0 = max(0, -top); r1 = min(h, T.PH // T.DS - top)
    if r1 - r0 < 8: return None
    gsub = g[r0:r1]; prow0 = top + r0; nrows = r1 - r0
    Ff = np.fft.rfft(gsub, n=T.NFFT, axis=1)
    cc = np.fft.irfft(T.FP[prow0:prow0 + nrows] * np.conj(Ff), n=T.NFFT, axis=1).sum(axis=0)
    L = T.GP.shape[1] - w
    xs = np.arange(1, L)
    A = T.CS2[prow0 + nrows - 1, xs + w - 1]; C = T.CS2[prow0 + nrows - 1, xs - 1]
    if prow0 > 0:
        B = T.CS2[prow0 - 1, xs + w - 1]; D = T.CS2[prow0 - 1, xs - 1]
    else:
        B = 0; D = 0
    en = A - B - C + D
    ef = float((gsub.astype(np.float64) ** 2).sum())
    ncc = cc[1:L] / np.sqrt(np.maximum(en, 1e-3) * max(ef, 1e-3))
    ncc = np.where(en > 0.02 * ef, ncc, 0)
    # cx for index j: xl=(j+1-PAD)*DS ; cx = xl+960/s
    cxs = (np.arange(len(ncc)) + 1 - T.PAD) * T.DS + 960.0 / s
    m = (cxs >= cx0) & (cxs <= cx1)
    if not m.any(): return None
    nc = np.where(m, ncc, -1)
    j = int(np.argmax(nc)); sc = float(nc[j])
    if 1 <= j < len(ncc) - 1:
        y0_, y1_, y2_ = ncc[j - 1], ncc[j], ncc[j + 1]
        den = y0_ - 2 * y1_ + y2_
        off = 0.5 * (y0_ - y2_) / den if abs(den) > 1e-9 else 0
    else: off = 0
    cx = (j + 1 + off - T.PAD) * T.DS + 960.0 / s
    nc2 = nc.copy(); nc2[max(0, j - 30):j + 31] = -1
    return cx, sc, float(nc2.max())

segs = [
    # (f0, f1, cx0, cx1, scales or None(use ruler))
    (0, 56, -600, 2600, None),
    (73, 97, 300, 4800, list(np.exp(np.linspace(np.log(0.3), np.log(1.2), 40))) + [2.874]),
    (104, 122, 3000, 5200, None),
    (127, 136, 3800, 5600, list(np.linspace(0.6, 0.82, 23))),
    (165, 177, 5700, 7000, None),
    (202, 226, 7000, 10300, list(np.linspace(3.0, 5.2, 23)) + [1.0, 1.1, 1.2, 1.4, 1.7, 2.0, 2.4]),
    (237, 237, 9700, 10000, [1.0, 1.003]),
    (257, 271, 9700, 10300, [1.0, 1.01, 1.02, 1.03, 1.05, 1.088]),
]
out = dict(first)
for (f0, f1, cx0, cx1, scales) in segs:
    for f in range(f0, f1 + 1):
        r = tr[f]
        im = Image.open(f'frames_full/f_{f:04d}.jpg').convert('L')
        ruler_ok = r['ok'] and 0.3 < r['s'] < 30 and r['acpk'] > 0.5 and abs(r['yc'] - 539.5) < 2
        sc_list = [r['s']] if (ruler_ok and scales is None) else (scales if scales is not None else list(np.exp(np.linspace(np.log(0.5), np.log(6), 50))))
        if ruler_ok and scales is not None:
            sc_list = [r['s']] + list(sc_list)
        best = None
        for s in sc_list:
            m = match_range(im, s, 539.5, cx0, cx1)
            if m and (best is None or m[1] > best[2]): best = (s, m[0], m[1], m[2])
        s, cx, sc, sc2 = best
        if not (ruler_ok and abs(s - r['s']) < 1e-6):
            for s2 in np.linspace(s * 0.97, s * 1.03, 13):
                m = match_range(im, s2, 539.5, cx0, cx1)
                if m and m[1] > sc: s, cx, sc, sc2 = s2, m[0], m[1], m[2]
        out[f] = dict(f=f, s=round(float(s), 4), cx=round(float(cx), 1), score=round(sc, 3), second=round(sc2, 3), ruler=ruler_ok)
        print(f"{f:3d} s={s:6.3f} cx={cx:8.1f} score={sc:.3f} 2nd={sc2:.3f} ratio={sc/max(sc2,1e-6):.2f} {'ruler' if ruler_ok else 'search'}", flush=True)
json.dump([out[f] for f in range(272)], open('track_x2.json', 'w'))
