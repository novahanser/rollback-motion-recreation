"""fit the highlight path of the bead chain (ellipse) and the per-frame phase from sheets/beads_o.txt"""
import re, sys, math
import numpy as np

rows = {}
for ln in open('sheets/beads_o.txt'):
    m = re.match(r'\s*(\d+) n=', ln)
    if not m:
        continue
    f = int(m.group(1))
    rows[f] = [(float(a), float(b), int(c)) for a, b, c in re.findall(r'\((\d+),(\d+)\|(\d+)\)', ln)]
pts = []
for f in range(107, 124):
    for (x, y, n) in rows[f]:
        if n < 560 and x < 985 and 150 < n:
            pts.append((f, x, y, n))
P = np.array(pts)
x, y = P[:, 1], P[:, 2]
# conic fit  A x^2 + B xy + C y^2 + D x + E y = 1
M = np.stack([x * x, x * y, y * y, x, y], axis=1)
co, *_ = np.linalg.lstsq(M, np.ones(len(x)), rcond=None)
A, B, C, D, E = co
den = B * B - 4 * A * C
cx = (2 * C * D - B * E) / den
cy = (2 * A * E - B * D) / den
F = -1.0
Fc = A * cx * cx + B * cx * cy + C * cy * cy + D * cx + E * cy + F
Q = np.array([[A, B / 2], [B / 2, C]]) / (-Fc)
w, v = np.linalg.eigh(Q)
a, b = 1 / math.sqrt(w[0]), 1 / math.sqrt(w[1])
u = v[:, 0]
if u[0] < 0:
    u = -u
tilt = math.degrees(math.atan2(u[1], u[0]))
print('centre %.1f %.1f  a %.1f b %.1f tilt %.2f deg' % (cx, cy, a, b, tilt))
vv = np.array([-u[1], u[0]])
du = (x - cx) * u[0] + (y - cy) * u[1]
dv = (x - cx) * vv[0] + (y - cy) * vv[1]
th = np.degrees(np.arctan2(dv / b, du / a)) % 360
rad = np.hypot(du / a, dv / b)
pitch = 360.0 / 13
for f in range(107, 124):
    sel = P[:, 0] == f
    ph = th[sel] % pitch
    ang = ph / pitch * 2 * math.pi
    mean = (math.atan2(np.sin(ang).mean(), np.cos(ang).mean()) % (2 * math.pi)) / (2 * math.pi)
    spread = np.abs(((ph / pitch - mean + 0.5) % 1.0) - 0.5).max()
    print('f%d  n=%2d  phase(frac of pitch)=%.3f  -> fifths %.2f  spread %.3f' % (f, sel.sum(), mean, mean * 5, spread))
# radial residual and area vs theta (binned)
print('theta-bin  n  mean radial  mean area')
for t0 in range(0, 360, 30):
    s = (th >= t0) & (th < t0 + 30)
    if s.sum():
        print('%3d-%3d %3d  %.3f  %.0f' % (t0, t0 + 30, s.sum(), rad[s].mean(), P[s, 3].mean()))
np.save('sheets/beads_fit.npy', np.array([cx, cy, a, b, tilt]))
