"""Per-frame ruler detection: line rows, thickness, tick period -> zoom scale."""
import numpy as np
from PIL import Image
import json, sys

P0 = 7.3333  # minor tick period at base scale (px)
N = 272


def box(v, k):
    k = int(k) | 1
    ker = np.ones(k) / k
    return np.convolve(np.pad(v, (k // 2, k // 2), mode='edge'), ker, 'valid')


def analyze(f):
    im = Image.open(f'frames_full/f_{f:04d}.jpg').convert('L')
    a = np.asarray(im).astype(np.float32)
    H, W = a.shape
    d = a[1:, :] - a[:-1, :]          # d[y] = a[y+1]-a[y]
    thr = 22.0
    lo, hi = 380, 700
    best = None
    for t in range(1, 70):
        # line occupying rows y+1..y+t : edges at d[y] and d[y+t], opposite sign
        top = d[lo:hi]
        bot = d[lo + t:hi + t]
        m = (top * bot < 0) & (np.abs(top) > thr) & (np.abs(bot) > thr)
        frac = m.mean(axis=1)
        y = int(np.argmax(frac))
        sc = float(frac[y])
        # prefer thicker lines when score similar (thin sub-edges may match too)
        if best is None or sc > best[0] + 0.02:
            best = (sc, y + lo, t)
    sc, y1, t = best
    if sc < 0.12:
        return dict(f=f, ok=False, linescore=round(sc, 3))
    yc = y1 + 0.5 + t / 2.0           # center of the line in pixel coords (row index + 0.5)
    s_guess = t / 2.0
    # tick band inside minor tick height: from 1.6s to 4.5s away from center
    r0 = max(1, int(round(1.6 * s_guess)))
    r1 = max(r0 + 1, int(round(4.5 * s_guess)))
    yci = int(round(yc - 0.5))
    rows = list(range(yci - r1, yci - r0)) + list(range(yci + r0 + 1, yci + r1 + 1))
    rows = [r for r in rows if 0 <= r < H]
    prof = a[rows, :].mean(axis=0)
    hp = prof - box(prof, max(31, int(P0 * s_guess * 6)))
    hp = hp - hp.mean()
    n = 1 << 14
    F = np.fft.rfft(hp, n=n)
    ac = np.fft.irfft(np.abs(F) ** 2)[:W]
    ac = ac / (ac[0] + 1e-9)
    pexp = P0 * s_guess
    cands = []
    for mult in (1.0,):
        a0 = max(2, int(pexp * 0.62))
        a1 = min(W - 2, int(pexp * 1.55) + 2)
        if a1 <= a0 + 1:
            continue
        seg = ac[a0:a1]
        j = int(np.argmax(seg)) + a0
        cands.append(j)
    if not cands:
        return dict(f=f, ok=False, linescore=round(sc, 3), t=t)
    j = cands[0]
    per = float(j)
    acpk = float(ac[j])
    for m in (2, 3, 5, 10, 15, 20, 30, 40):
        c = per * m
        w = max(2, int(round(0.3 * per)))
        lo2, hi2 = int(round(c)) - w, int(round(c)) + w + 1
        if hi2 >= W - 2 or lo2 < 1:
            break
        jj = int(np.argmax(ac[lo2:hi2])) + lo2
        if ac[jj] > 0.12:
            y0_, y1_, y2_ = ac[jj - 1], ac[jj], ac[jj + 1]
            den = (y0_ - 2 * y1_ + y2_)
            off = 0.5 * (y0_ - y2_) / den if abs(den) > 1e-9 else 0
            per = (jj + off) / m
    return dict(f=f, ok=True, y1=int(y1), t=int(t), yc=round(yc, 2), linescore=round(sc, 3),
                per=round(per, 3), acpk=round(acpk, 3), s=round(per / P0, 4))


if __name__ == '__main__':
    out = []
    for f in range(N):
        r = analyze(f)
        out.append(r)
        if r['ok']:
            print(f"{f:3d} yc={r['yc']:7.2f} t={r['t']:2d} ls={r['linescore']:.2f} per={r['per']:8.3f} ac={r['acpk']:.2f} s={r['s']:.3f}")
        else:
            print(f"{f:3d} FAIL ls={r.get('linescore')}")
    json.dump(out, open('track_ruler.json', 'w'))
