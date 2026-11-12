"""The wire 'horn' of section A.

In the source it is a string-art hyperboloid - two rings joined by straight strings, so the bundle has a waist - plus a stack of
rings at the bell end, a lip of rings at the far end and a 'fan' (a hub with spokes to a row of small rings). It tumbles through
frames 30-73 and then rests inside the ring group for the remainder of the section.  The poses below were read off world-aligned
crops of the source (see 拆解分析.md); everything in between is linear interpolation.
"""
import math
import numpy as np
from PIL import Image, ImageDraw

HW = (250.0, -40.0, 1300.0, 960.0)          # world window every horn sprite is drawn in
HK = 1.5                                    # px per world px of the sprites
F0, F1 = 30, 74                             # animated range; the pose of F1 is the resting one

# frame: (A, ra, ea, B, rb, eb)   A = bell centre, B = far ring centre (world px), r = ring radius, e = minor / major axis
POSES = {
    30: ((1028, 488), 45, 1.00, (760, 498), 5, 1.0),
    32: ((1050, 514), 55, 1.00, (430, 500), 20, 1.0),
    34: ((1052, 535), 58, 1.00, (420, 495), 20, 1.0),
    36: ((1050, 556), 62, 0.97, (400, 487), 18, 1.0),
    38: ((1070, 552), 62, 0.90, (330, 410), 30, 0.9),
    39: ((900, 610), 70, 0.80, (350, 335), 40, 0.7),
    40: ((960, 690), 78, 0.65, (380, 245), 50, 0.5),
    42: ((920, 722), 95, 0.75, (632, 224), 24, 0.3),
    43: ((900, 740), 97, 0.74, (672, 224), 56, 0.3),
    44: ((900, 742), 99, 0.74, (628, 229), 75, 0.3),
    46: ((882, 750), 96, 0.74, (643, 229), 75, 0.3),
    48: ((868, 752), 99, 0.70, (647, 229), 65, 0.3),
    50: ((829, 756), 104, 0.55, (651, 229), 56, 0.3),
    51: ((795, 761), 104, 0.55, (701, 225), 38, 0.3),
    52: ((768, 761), 104, 0.55, (716, 225), 47, 0.3),
    53: ((720, 756), 104, 0.70, (772, 200), 47, 0.3),
    54: ((640, 690), 95, 0.80, (1005, 185), 42, 0.45),
    55: ((590, 640), 100, 0.70, (1108, 256), 45, 0.42),
    56: ((570, 600), 100, 0.60, (1143, 327), 50, 0.40),
    57: ((560, 565), 104, 0.50, (1173, 364), 52, 0.38),
    58: ((555, 550), 104, 0.50, (1183, 374), 52, 0.38),
    60: ((560, 520), 130, 0.42, (1177, 385), 55, 0.36),
    62: ((580, 518), 135, 0.40, (1168, 352), 58, 0.35),
    64: ((595, 490), 110, 0.50, (1150, 318), 58, 0.36),
    68: ((590, 480), 100, 0.60, (1110, 270), 60, 0.37),
    71: ((590, 475), 92, 0.68, (1091, 245), 62, 0.42),
    74: ((590, 470), 85, 0.75, (1058, 205), 62, 0.45),
}
# frame: (hub, arc centre, arc radius, a0, a1, rings, ring radius); angles in degrees, clockwise from +x on screen (270 = up)
FAN = {
    44: ((836, 520), (836, 520), 172, 262, 290, 5, 15),
    48: ((826, 520), (826, 520), 182, 262, 305, 7, 16),
    50: ((735, 520), (735, 520), 190, 265, 320, 9, 16),
    52: ((820, 516), (820, 516), 185, 255, 330, 11, 17),
    53: ((805, 520), (805, 520), 187, 200, 350, 16, 17),
    54: ((800, 500), (800, 500), 150, 240, 330, 10, 15),
    56: ((810, 460), (810, 460), 110, 235, 325, 9, 13),
    57: ((900, 538), (750, 540), 158, 30, 150, 15, 11),
    64: ((900, 535), (750, 540), 158, 30, 150, 15, 11),
    74: ((853, 535), (750, 540), 160, 35, 150, 15, 11),
}


def _flat(v):
    out = []
    for a in v:
        if isinstance(a, (tuple, list)):
            out += list(a)
        else:
            out.append(a)
    return out


def _interp(table, f):
    ks = sorted(table)
    if f <= ks[0]:
        return _flat(table[ks[0]])
    if f >= ks[-1]:
        return _flat(table[ks[-1]])
    for a, b in zip(ks[:-1], ks[1:]):
        if a <= f <= b:
            t = (f - a) / float(b - a)
            va, vb = _flat(table[a]), _flat(table[b])
            return [x + (y - x) * t for x, y in zip(va, vb)]


def pose(f):
    ax, ay, ra, ea, bx, by, rb, eb = _interp(POSES, f)
    return (ax, ay), ra, ea, (bx, by), rb, eb


def fan(f):
    if f < min(FAN):
        return None
    hx, hy, cx, cy, r, a0, a1, n, rr = _interp(FAN, f)
    return (hx, hy), (cx, cy), r, a0, a1, int(round(n)), rr


def _segments(f, tw=158.0, nl=66, fan_mul=1):
    """world-space polylines of the horn at frame f: (strings, rings)"""
    (A, ra, ea, B, rb, eb) = pose(f)
    L = math.hypot(B[0] - A[0], B[1] - A[1]) or 1.0
    u = ((B[0] - A[0]) / L, (B[1] - A[1]) / L)
    n = (-u[1], u[0])

    def P(C, r, e, th):
        return (C[0] + r * math.cos(th) * n[0] + r * e * math.sin(th) * u[0],
                C[1] + r * math.cos(th) * n[1] + r * e * math.sin(th) * u[1])

    strings = []
    if f > 30:
        for i in range(nl):
            th = 2 * math.pi * i / nl
            strings.append([P(A, ra, ea, th), P(B, rb, eb, th + math.radians(tw))])
    rings = []
    nb = 3 if f <= 30 else 11
    for k in range(nb):                       # bell: face-on -> concentric, side-on -> a stack
        Ck = (A[0] - u[0] * k * 7.5 * (1 - ea), A[1] - u[1] * k * 7.5 * (1 - ea))
        rk = ra * (1 - 0.055 * k * ea) * (1 + 0.012 * k * (1 - ea))
        rings.append([P(Ck, rk, ea, 2 * math.pi * j / 72.0) for j in range(73)])
    if f > 34:
        for k in range(6):                    # lip at the far end
            Ck = (B[0] + u[0] * k * 4.0 * (1 - eb), B[1] + u[1] * k * 4.0 * (1 - eb))
            rings.append([P(Ck, rb, eb, 2 * math.pi * j / 48.0) for j in range(49)])
    fn_ = fan(f)
    spokes = []
    if fn_:
        H, C, r, a0, a1, cnt, rr = fn_
        if fan_mul > 1 and f >= 57:                       # the settled fan has about twice as many spokes
            cnt = cnt * fan_mul - (fan_mul - 1)
        for i in range(cnt):
            a = math.radians(a0 + (a1 - a0) * i / max(cnt - 1, 1))
            q = (C[0] + r * math.cos(a), C[1] + r * math.sin(a))
            spokes.append([H, q])
            rings.append([(q[0] + rr * math.cos(2 * math.pi * j / 28.0), q[1] + rr * math.sin(2 * math.pi * j / 28.0)) for j in range(29)])
    return strings, rings, spokes


def horn_frame(f, ver=1, lw_w=0.5, nl=66, val=92.0, al=0.62, fan_mul=1):
    """RGBA sprite of the horn at frame f covering the world window HW (HK px per world px).
    lw_w = string width in world px, nl = number of strings, val / al = grey value and opacity of one string"""
    ss = 2
    kk = HK * ss
    W_, H_ = int((HW[2] - HW[0]) * kk), int((HW[3] - HW[1]) * kk)
    strings, rings, spokes = _segments(f, nl=nl, fan_mul=fan_mul)

    def px(p):
        return ((p[0] - HW[0]) * kk, (p[1] - HW[1]) * kk)

    acc = np.zeros((H_, W_), np.float32)
    lw = max(1, int(round(lw_w * kk)))
    # strings: accumulate so that the crossings of the bundle read darker, like the source
    for i in range(0, len(strings), 6):
        tmp = Image.new('L', (W_, H_), 0)
        d = ImageDraw.Draw(tmp)
        for s in strings[i:i + 6]:
            d.line([px(s[0]), px(s[1])], fill=255, width=lw)
        acc += np.asarray(tmp, np.float32) / 255.0
    for grp in (rings, spokes):
        tmp = Image.new('L', (W_, H_), 0)
        d = ImageDraw.Draw(tmp)
        for s in grp:
            d.line([px(p) for p in s], fill=255, width=lw)
        acc += np.asarray(tmp, np.float32) / 255.0
    alpha = 1.0 - np.power(1.0 - al, acc)
    v = val - 34.0 * np.clip(acc - 1.0, 0, 3) / 3.0               # denser -> darker
    out = np.zeros((H_, W_, 4), np.uint8)
    out[..., 0] = out[..., 1] = np.clip(v, 0, 255).astype(np.uint8)
    out[..., 2] = np.clip(v + 5, 0, 255).astype(np.uint8)
    out[..., 3] = np.clip(alpha * 255.0, 0, 255).astype(np.uint8)
    im = Image.fromarray(out, 'RGBA')
    return im.resize((W_ // ss, H_ // ss), Image.LANCZOS)


def version():
    """short hash of the pose tables + drawing code revision (keys the asset cache)"""
    import hashlib
    return hashlib.md5((repr(sorted(POSES.items())) + repr(sorted(FAN.items())) + 'draw-5').encode('utf-8')).hexdigest()[:8]
