"""Register each video frame to the panorama: find camera center x (pano coords) given scale s.
World->screen:  Xs = (Xp - cx)*s + 960 ; Ys = (Yp - 540)*s + yc
"""
import numpy as np
from PIL import Image
import json, sys

DS = 2            # work at 1/DS of pano resolution
PADX = 1400       # padding (in pano px) on both sides
PW, PH = 11000, 1080


def gradmag(a):
    gx = np.zeros_like(a)
    gy = np.zeros_like(a)
    gx[:, 1:-1] = a[:, 2:] - a[:, :-2]
    gy[1:-1, :] = a[2:, :] - a[:-2, :]
    return np.sqrt(gx * gx + gy * gy)


def load_pano():
    p = Image.open('pano/pano.png').convert('L')
    p = p.resize((PW // DS, PH // DS), Image.LANCZOS)
    a = np.asarray(p).astype(np.float32)
    g = gradmag(a)
    # mask the ruler band
    c = PH // DS // 2
    g[c - 8:c + 8, :] = 0
    pad = PADX // DS
    gp = np.zeros((g.shape[0], g.shape[1] + 2 * pad), np.float32)
    gp[:, pad:pad + g.shape[1]] = g
    return gp, pad


GP, PAD = load_pano()
NFFT = 1 << int(np.ceil(np.log2(GP.shape[1] + 1200)))
FP = np.fft.rfft(GP, n=NFFT, axis=1)
CS2 = np.cumsum(np.cumsum(GP.astype(np.float64) ** 2, axis=0), axis=1)


def match(frame_gray, s, yc=539.5):
    """frame_gray: PIL L image 1920x1080. returns (cx, score, second)"""
    w = max(8, int(round(1920 / s / DS)))
    h = max(8, int(round(1080 / s / DS)))
    fr = frame_gray.resize((w, h), Image.LANCZOS)
    a = np.asarray(fr).astype(np.float32)
    g = gradmag(a)
    # frame row r corresponds to pano(DS) row: (r+0.5)*(1080/s/DS)/h - yc/s/DS + 270
    cyf = yc / 1080.0 * h         # ruler row in resized frame
    ci = int(round(cyf))
    g[max(0, ci - 8):ci + 8, :] = 0
    top = int(round(PH / DS / 2 - cyf))      # pano row of frame row 0
    r0 = max(0, -top)
    r1 = min(h, PH // DS - top)
    if r1 - r0 < 8:
        return None
    gsub = g[r0:r1]
    prow0 = top + r0
    nrows = r1 - r0
    Ff = np.fft.rfft(gsub, n=NFFT, axis=1)
    cc = np.fft.irfft(FP[prow0:prow0 + nrows] * np.conj(Ff), n=NFFT, axis=1).sum(axis=0)
    # normalisation by pano energy in window
    L = GP.shape[1] - w
    cc = cc[:L]
    # energy of pano window [x, x+w) x rows
    def rect(x0, x1, y0, y1):
        # sum over rows y0..y1-1, cols x0..x1-1 using CS2
        A = CS2[y1 - 1, x1 - 1]
        B = CS2[y0 - 1, x1 - 1] if y0 > 0 else 0
        C = CS2[y1 - 1, x0 - 1] if True else 0
        D = CS2[y0 - 1, x0 - 1] if y0 > 0 else 0
        return A - B - C + D
    xs = np.arange(1, L)
    A = CS2[prow0 + nrows - 1, xs + w - 1]
    C = CS2[prow0 + nrows - 1, xs - 1]
    if prow0 > 0:
        B = CS2[prow0 - 1, xs + w - 1]
        D = CS2[prow0 - 1, xs - 1]
    else:
        B = 0
        D = 0
    en = A - B - C + D
    ef = float((gsub.astype(np.float64) ** 2).sum())
    ncc = cc[1:L] / np.sqrt(np.maximum(en, 1e-3) * max(ef, 1e-3))
    # require decent overlap energy: penalise windows with tiny pano energy
    ncc = np.where(en > 0.05 * ef, ncc, 0)
    j = int(np.argmax(ncc))
    sc = float(ncc[j])
    # sub-pixel
    if 1 <= j < len(ncc) - 1:
        y0_, y1_, y2_ = ncc[j - 1], ncc[j], ncc[j + 1]
        den = y0_ - 2 * y1_ + y2_
        off = 0.5 * (y0_ - y2_) / den if abs(den) > 1e-9 else 0
    else:
        off = 0
    xl = (j + 1 + off - PAD) * DS          # pano x of frame left edge
    cx = xl + 960.0 / s
    # second best away from peak
    m = ncc.copy()
    lo, hi = max(0, j - 40), min(len(m), j + 41)
    m[lo:hi] = 0
    sc2 = float(m.max())
    return cx, sc, sc2


if __name__ == '__main__':
    tr = json.load(open('track_ruler.json'))
    out = []
    frames = range(272) if len(sys.argv) < 2 else [int(x) for x in sys.argv[1:]]
    for f in frames:
        r = tr[f]
        im = Image.open(f'frames_full/f_{f:04d}.jpg').convert('L')
        cands = []
        if r['ok'] and 0.3 < r['s'] < 30 and r['acpk'] > 0.5 and abs(r['yc'] - 539.5) < 2:
            scales = [r['s']]
            yc = r['yc']
            reliable = True
        else:
            scales = list(np.exp(np.linspace(np.log(0.5), np.log(6.0), 60)))
            yc = 539.5
            reliable = False
        best = None
        for s in scales:
            m = match(im, s, yc)
            if m is None:
                continue
            if best is None or m[1] > best[2]:
                best = (s, m[0], m[1], m[2])
        s, cx, sc, sc2 = best
        if not reliable:
            # refine scale locally
            for s2 in np.linspace(s * 0.96, s * 1.04, 17):
                m = match(im, s2, yc)
                if m and m[1] > sc:
                    s, cx, sc, sc2 = s2, m[0], m[1], m[2]
        out.append(dict(f=f, s=round(float(s), 4), cx=round(float(cx), 1), score=round(sc, 3), second=round(sc2, 3), reliable=reliable))
        print(f"{f:3d} s={s:6.3f} cx={cx:8.1f} score={sc:.3f} 2nd={sc2:.3f} {'R' if reliable else 'search'}", flush=True)
    if len(sys.argv) < 2:
        json.dump(out, open('track_x.json', 'w'))
