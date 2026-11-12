"""The bead bracelet as a rotating 3-D ring of fused 'liquid chrome' pearls (frames 105-162).

Measured on the source (highlight blobs of frames 107-123, tools/fit_beads*.py, tools/bead_fit3.py):
  * the 13 highlights run on an ellipse (centre 853.8,409.4  a 125.5  b 42.7  tilt 15.5 deg, screen px at the frame-105 size);
  * the beads are evenly spaced on a circle seen in perspective: eccentric angle = Blaschke warp of the circle angle with
    w = 0.004+0.078j (near side = bottom row), so the near beads are larger and further apart;
  * the ring turns 0.194 bead pitch per SOURCE frame (30 fps, one turn in 67 frames) and the clip was conformed to 24 fps by
    dropping every fifth frame: source index = floor(1.25 (f-107) + 0.5)  ->  steps of 1, 2, 1, 1 per four frames;
  * near row moves right, far row moves left;
  * the beads are not separate discs: neighbours fuse, one white outline + black contour runs round the union, every highlight
    (white core, lavender double ring) stays visible and close highlights merge - the look of a posterised chrome render.
The picture is therefore rendered here per frame: spheres on the fitted ring -> shading field -> colour ramp.
(A single GPT bead, 'gen/bead-sprite.png', was tried first; separate stickers cannot fuse like the source.)
"""
import cmath
import math
import numpy as np
from PIL import Image

N = 13
PITCH = 2 * math.pi / N
HC = (853.8, 409.4)
HA, HB, TILT = 125.5, 42.7, 15.52
WARP = complex(0.004, 0.078)
PH0, PHSTEP = 0.286, 0.194              # phase (in pitches) on frame 107 and per source frame
BOX = (842.0, 422.0, 336.0, 204.0)      # asset canvas in screen px of frames 105-124: centre x, centre y, width, height
OUTK = 2                                # asset px per screen px
SS = 2                                  # supersampling while drawing
ZAMP = 118.0                            # depth amplitude of the ring (screen px), only used for the occlusion order

_U = (math.cos(math.radians(TILT)), math.sin(math.radians(TILT)))
_V = (-_U[1], _U[0])


def src_index(f):
    return int(math.floor(1.25 * (f - 107) + 0.5))


def core_radius(theta):
    """area-equivalent radius of the white highlight core (px), smooth fit of the binned measurements"""
    t = math.radians(theta)
    return 10.25 + 2.05 * math.cos(t - math.radians(52.0)) + 0.35 * math.cos(2 * (t - math.radians(40.0)))


def highlights(n30, ph0=PH0):
    """[(hx, hy, core radius, theta deg, circle angle rad)] of the 13 highlights for source frame n30, reference screen px"""
    out = []
    phi0 = (ph0 - PHSTEP * n30) * PITCH
    for i in range(N):
        phi = phi0 + i * PITCH
        z = cmath.exp(1j * phi)
        zeta = (z - WARP) / (1 - WARP.conjugate() * z)
        th = math.atan2(zeta.imag, zeta.real)
        ca, sa = HA * math.cos(th), HB * math.sin(th)
        out.append((HC[0] + ca * _U[0] + sa * _V[0], HC[1] + ca * _U[1] + sa * _V[1], core_radius(math.degrees(th)), math.degrees(th) % 360.0, phi))
    return out


def beads(n30, ph0=PH0):
    """[(cx, cy, r, hx, hy, rh, theta, z)]: bead discs (outer radius incl. the white outline) fitted to the source silhouettes"""
    out = []
    for (hx, hy, rh, th, phi) in highlights(n30, ph0):
        t = math.radians(th)
        r = 31.6 + 4.6 * math.sin(t) + 0.8 * math.cos(t)
        ox = 9.5 + 1.5 * math.sin(t) - 1.65 * math.cos(t)
        oy = -8.86 - 3.59 * math.sin(t) - 2.34 * math.cos(t)
        out.append((hx - ox, hy - oy, r, hx, hy, rh, th, ZAMP * math.sin(phi)))
    return out


def _blur(a, sigma):
    """separable gaussian on a float array"""
    n = max(1, int(3 * sigma))
    k = np.exp(-0.5 * (np.arange(-n, n + 1) / float(sigma)) ** 2)
    k /= k.sum()
    p = np.pad(a, ((n, n), (0, 0)), mode='edge')
    out = sum(k[i] * p[i:i + a.shape[0]] for i in range(2 * n + 1))
    p = np.pad(out, ((0, 0), (n, n)), mode='edge')
    return sum(k[i] * p[:, i:i + a.shape[1]] for i in range(2 * n + 1))


def _ramp(v, stops):
    v = np.clip(v, stops[0][0], stops[-1][0])
    out = np.zeros(v.shape + (3,), np.float32)
    for (a, ca), (b, cb) in zip(stops[:-1], stops[1:]):
        m = (v >= a) & (v <= b)
        t = ((v[m] - a) / float(b - a))[:, None]
        out[m] = np.array(ca, np.float32) * (1 - t) + np.array(cb, np.float32) * t
    return out


BODY = [(-0.60, (0, 0, 8)), (-0.28, (0, 0, 8)), (-0.12, (4, 10, 96)), (0.04, (12, 28, 186)), (0.20, (40, 68, 226)), (0.38, (104, 130, 240)),
        (0.54, (172, 188, 246)), (0.68, (224, 230, 250)), (1.00, (242, 244, 252))]


def _step(v, edge, w):
    """anti-aliased v >= edge (w = half width of the transition)"""
    return np.clip((v - edge) / (2.0 * w) + 0.5, 0.0, 1.0)


def chain_frame(n30, ver=1, ph0=PH0):
    """RGBA image of the bracelet for source frame n30; canvas = BOX, OUTK px per screen px"""
    f = OUTK * SS
    W, H = int(round(BOX[2] * f)), int(round(BOX[3] * f))
    x0, y0 = BOX[0] - BOX[2] / 2.0, BOX[1] - BOX[3] / 2.0
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    X, Y = (xx + 0.5) / f + x0, (yy + 0.5) / f + y0            # screen px
    bl = beads(n30, ph0)
    aa = 0.5 / f                                               # half a drawing pixel in screen px

    # ---- union silhouette (smooth max of the signed distances) and the front-most bead per pixel
    k = 0.85
    acc = np.zeros((H, W), np.float32)
    front = np.full((H, W), -1e9, np.float32)
    lum = np.zeros((H, W), np.float32)
    smax = np.full((H, W), -1e9, np.float32)
    lum_out = np.zeros((H, W), np.float32)
    for (cx, cy, r, hx, hy, rh, th, z) in bl:
        d = np.hypot(X - cx, Y - cy)
        s = r - d
        acc += np.exp(np.clip(k * s, -60, 60))
        near_t = min(1.0, max(0.0, (r - 28.0) / 9.5))
        # shading: bright centre shifted to the lower left, dark limb (thicker on the upper right)
        u, v = (X - cx) / r, (Y - cy) / r
        u0 = -0.16 * near_t - 0.04 * (1 - near_t)
        v0 = 0.20 * near_t + 0.30 * (1 - near_t)
        rho = np.hypot(u - u0, v - v0) / 0.95
        L = (0.86 + 0.14 * near_t) * (1.0 - np.clip(rho, 0, 1.6))
        zf = z + np.sqrt(np.clip(r * r - d * d, 0, None))
        inside = d < r
        take = inside & (zf > front)
        front = np.where(take, zf, front)
        lum = np.where(take, L, lum)
        t2 = s > smax
        smax = np.where(t2, s, smax)
        lum_out = np.where(t2, L, lum_out)
    S = np.log(acc) / k
    lum = np.where(front > -1e8, lum, lum_out)
    lum = _blur(lum, 0.9 * f)

    rgb = _ramp(lum, BODY)
    # black contour just inside the white outline
    cont = _step(S, 2.2, aa) * (1 - _step(S, 4.0, aa * 3))
    rgb = rgb * (1 - cont[..., None]) + np.array((0, 0, 10), np.float32) * cont[..., None]
    outl = 1 - _step(S, 2.2, aa)
    rgb = rgb * (1 - outl[..., None]) + np.array((250, 250, 252), np.float32) * outl[..., None]
    alpha = _step(S, 0.0, aa)

    # ---- small black tear-drops with a white rim in the creases between neighbours
    order = sorted(bl, key=lambda b: b[6])
    for i in range(N):
        a_, b_ = order[i], order[(i + 1) % N]
        if abs(((b_[6] - a_[6] + 180) % 360) - 180) > 40:
            continue
        mx, my = (a_[0] + b_[0]) / 2.0, (a_[1] + b_[1]) / 2.0
        ox_, oy_ = mx - HC[0], my - HC[1] + 6.0
        nrm = math.hypot(ox_, oy_) or 1.0
        rr = (a_[2] + b_[2]) / 2.0
        px, py = mx + ox_ / nrm * rr * 0.30, my + oy_ / nrm * rr * 0.30 + rr * 0.10
        sz = rr / 37.0
        ang = math.atan2(b_[1] - a_[1], b_[0] - a_[0]) + math.pi / 2
        du = (X - px) * math.cos(ang) + (Y - py) * math.sin(ang)
        dv = -(X - px) * math.sin(ang) + (Y - py) * math.cos(ang)
        q = np.hypot(du / (3.4 * sz), dv / (2.0 * sz))
        rim = _step(-q, -1.55, aa / 2.4) * _step(S, 5.0, aa)
        rgb = rgb * (1 - rim[..., None]) + np.array((244, 246, 252), np.float32) * rim[..., None]
        dot = _step(-q, -1.0, aa / 2.4) * _step(S, 5.0, aa)
        rgb = rgb * (1 - dot[..., None]) + np.array((0, 0, 12), np.float32) * dot[..., None]

    # ---- highlights: white core, lavender double ring with a thin light line, navy hair line; neighbours merge
    kg = 1.1
    accg = np.zeros((H, W), np.float32)
    for (cx, cy, r, hx, hy, rh, th, z) in bl:
        near_t = min(1.0, max(0.0, (rh - 8.3) / (12.4 - 8.3)))
        asp = 1.0 + 0.26 * near_t
        ra, rb = rh * math.sqrt(asp), rh / math.sqrt(asp)
        c45, s45 = math.cos(math.radians(45.0)), math.sin(math.radians(45.0))
        du = (X - hx) * c45 + (Y - hy) * s45
        dv = -(X - hx) * s45 + (Y - hy) * c45
        g = rh * (1.0 - np.hypot(du / ra, dv / rb))            # ~ signed distance to the core edge (px), positive inside
        accg += np.exp(np.clip(kg * g, -60, 60))
    G = np.log(accg) / kg
    inner = _step(S, 4.6, aa)
    for edge, col in ((-7.0, (24, 36, 150)), (-6.2, (126, 131, 190)), (-3.6, (214, 217, 240)), (-2.8, (150, 153, 206)), (0.0, (250, 250, 246))):
        m = _step(G, edge, aa) * inner
        rgb = rgb * (1 - m[..., None]) + np.array(col, np.float32) * m[..., None]

    out = np.dstack([np.clip(rgb, 0, 255), alpha * 255.0]).astype(np.uint8)
    im = Image.fromarray(out, 'RGBA')
    if SS > 1:
        im = im.resize((W // SS, H // SS), Image.LANCZOS)
    return im


def version():
    return 'chain3d-5'
