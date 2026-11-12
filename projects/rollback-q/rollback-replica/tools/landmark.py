"""Landmark tracker: locate a settled pano rect inside a frame over (s, x).
usage: python tools/landmark.py X0 X1 Y0 Y1 SMIN SMAX NS F0 F1"""
import numpy as np, sys, json
from PIL import Image

def gradmag(a):
    gx = np.zeros_like(a); gy = np.zeros_like(a)
    gx[:, 1:-1] = a[:, 2:] - a[:, :-2]; gy[1:-1, :] = a[2:, :] - a[:-2, :]
    return np.sqrt(gx * gx + gy * gy)

PANO = Image.open('pano/pano.png').convert('L')

def locate(f, rect, scales, DS=2):
    X0, X1, Y0, Y1 = rect
    fr = Image.open(f'frames_full/f_{f:04d}.jpg').convert('L')
    fr = fr.resize((1920 // DS, 1080 // DS), Image.LANCZOS)
    F = gradmag(np.asarray(fr).astype(np.float32))
    H, W = F.shape
    best = None
    patch0 = PANO.crop((X0, Y0, X1, Y1))
    for s in scales:
        w = max(8, int(round((X1 - X0) * s / DS))); h = max(8, int(round((Y1 - Y0) * s / DS)))
        p = gradmag(np.asarray(patch0.resize((w, h), Image.LANCZOS)).astype(np.float32))
        # mask ruler band inside the patch
        yr = (540 - Y0) * s / DS
        if 0 <= yr < h:
            p[max(0, int(yr - 6)):int(yr + 7), :] = 0
        ytop = int(round(((Y0 - 540) * s + 540) / DS))
        r0 = max(0, -ytop); r1 = min(h, H - ytop)
        if r1 - r0 < 10: continue
        ps = p[r0:r1]; fs = F[ytop + r0: ytop + r1].copy()
        yrf = int(round(540 / DS)) - (ytop + r0)
        if 0 <= yrf < fs.shape[0]:
            fs[max(0, yrf - 6):yrf + 7, :] = 0
        n = 1 << int(np.ceil(np.log2(W + w + 2)))
        # pad frame on both sides by w so the patch may be partially outside
        fp = np.zeros((fs.shape[0], W + 2 * w), np.float32); fp[:, w:w + W] = fs
        n = 1 << int(np.ceil(np.log2(fp.shape[1] + w)))
        cc = np.fft.irfft(np.fft.rfft(fp, n=n, axis=1) * np.conj(np.fft.rfft(ps, n=n, axis=1)), n=n, axis=1).sum(axis=0)[:W + w]
        e2 = np.cumsum((fp.astype(np.float64) ** 2).sum(axis=0)); e2 = np.concatenate([[0], e2])
        en = e2[np.arange(W + w) + w] - e2[np.arange(W + w)]
        ep = float((ps.astype(np.float64) ** 2).sum())
        ncc = cc / np.sqrt(np.maximum(en, 1e-3) * ep)
        ncc = np.where(en > 0.15 * ep * 0.2, ncc, 0)
        j = int(np.argmax(ncc)); sc = float(ncc[j])
        xl = (j - w) * DS            # screen x of patch left edge
        cx = X0 - (xl - 960) / s
        if best is None or sc > best[0]: best = (sc, s, cx, xl)
    return best

if __name__ == '__main__':
    X0, X1, Y0, Y1 = [int(v) for v in sys.argv[1:5]]
    smin, smax = float(sys.argv[5]), float(sys.argv[6]); ns = int(sys.argv[7])
    f0, f1 = int(sys.argv[8]), int(sys.argv[9])
    scales = list(np.exp(np.linspace(np.log(smin), np.log(smax), ns)))
    for f in range(f0, f1 + 1):
        sc, s, cx, xl = locate(f, (X0, X1, Y0, Y1), scales)
        # refine
        sc2, s2, cx2, xl2 = locate(f, (X0, X1, Y0, Y1), list(np.linspace(s * 0.97, s * 1.03, 13)), DS=1)
        print(f"{f:3d} s={s2:.4f} cx={cx2:8.1f} score={sc2:.3f} (coarse s={s:.3f} cx={cx:.0f} sc={sc:.3f})", flush=True)
