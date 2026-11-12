"""perspective (Blaschke) warp fit: beads evenly spaced on the 3-D circle -> eccentric angle on the image ellipse"""
import re, math
import numpy as np
rows = {}
for ln in open('sheets/beads_o.txt'):
    m = re.match(r'\s*(\d+) n=', ln)
    if m:
        rows[int(m.group(1))] = [(float(a), float(b), int(c)) for a, b, c in re.findall(r'\((\d+),(\d+)\|(\d+)\)', ln)]
cx, cy, a, b, tilt = np.load('sheets/beads_fit.npy')
u = np.array([math.cos(math.radians(tilt)), math.sin(math.radians(tilt))]); v = np.array([-u[1], u[0]])
P = np.array([(f, x, y, n) for f in range(107, 124) for (x, y, n) in rows[f] if 150 < n < 560 and x < 985])
du = (P[:, 1] - cx) * u[0] + (P[:, 2] - cy) * u[1]; dv = (P[:, 1] - cx) * v[0] + (P[:, 2] - cy) * v[1]
zeta = np.exp(1j * np.arctan2(dv / b, du / a))
pitch = 2 * math.pi / 13
fr = P[:, 0].astype(int)
def cost(w):
    z = (zeta + w) / (1 + np.conj(w) * zeta)
    ph = np.angle(z) % pitch
    tot = 0.0; phases = {}
    for f in range(107, 124):
        s = fr == f
        ang = ph[s] / pitch * 2 * math.pi
        C, S = np.cos(ang).mean(), np.sin(ang).mean()
        tot += (1 - math.hypot(C, S)) * s.sum()
        phases[f] = (math.atan2(S, C) % (2 * math.pi)) / (2 * math.pi)
    return tot / len(fr), phases
best = (9, None)
for wr in np.arange(-0.4, 0.401, 0.02):
    for wi in np.arange(-0.4, 0.401, 0.02):
        c, _ = cost(complex(wr, wi))
        if c < best[0]:
            best = (c, complex(wr, wi))
w0 = best[1]
for wr in np.arange(w0.real - 0.02, w0.real + 0.0201, 0.002):
    for wi in np.arange(w0.imag - 0.02, w0.imag + 0.0201, 0.002):
        c, _ = cost(complex(wr, wi))
        if c < best[0]:
            best = (c, complex(wr, wi))
w = best[1]
c, phases = cost(w)
print('w = %.3f%+.3fj  |w|=%.3f arg=%.1f deg   circ.var=%.4f (w=0: %.4f)' % (w.real, w.imag, abs(w), math.degrees(np.angle(w)), c, cost(0j)[0]))
prev = None
for f in range(107, 124):
    d = '' if prev is None else '  step %.2f fifths' % ((((phases[f] - prev + 0.5) % 1.0) - 0.5) * 5)
    print('f%d phase %.3f (%.2f fifths)%s' % (f, phases[f], phases[f] * 5, d)); prev = phases[f]
z = (zeta + w) / (1 + np.conj(w) * zeta)
pred = 1.0 / np.abs(1 - np.conj(w) * z) ** 2
rh = np.sqrt(P[:, 3] / math.pi)
k = (pred * rh).sum() / (pred ** 2).sum()
print('highlight radius ~ %.2f * 1/|1-conj(w)z|^2 ; rms err %.2f px (range %.1f..%.1f)' % (k, np.sqrt(((rh - k * pred) ** 2).mean()), rh.min(), rh.max()))
for t0 in range(0, 360, 30):
    th = np.degrees(np.angle(zeta)) % 360
    s = (th >= t0) & (th < t0 + 30)
    if s.sum():
        print('  theta %3d-%3d: rh %.1f  model %.1f' % (t0, t0 + 30, rh[s].mean(), (k * pred[s]).mean()))
np.save('sheets/beads_w.npy', np.array([w.real, w.imag]))
