"""Section A, part 1 (world x 0..1400): opening shapes, holographic paper, ring / vinyl, pole, tube, houses."""
import math
import numpy as np
from lib import *
from gen_util import s2w, pin, pin_keys, zoom, gen, quadrant, fit, gray
import shapes0 as S0
import horn

K = 2
RC = (700.0, 540.0)                 # ring centre
VIN_C, VIN_R = (980.0, 436.5), 215.0       # vinyl record: resting centre / radius
CRES_C, CRES_R0, CRES_R1 = (750.0, 540.0), 177.0, 276.0    # grey half ring under the ruler
PK = (232, 8, 109)                  # video pink
BL = (31, 134, 240)                 # video blue
HOLO_C = (378.0, 393.0)
CARD_C = (64.0, 539.0)
PERI = (138, 140, 240)


# ----------------------------------------------------------------------------- generic shapes
def ring_sector(R0, R1, a0, a1, color, k=K):
    """sector of a ring centred in a (2*R1+4) canvas; angles CCW from +x"""
    size = int((2 * R1 + 4) * k)
    c = size / 2.0
    x, y = grid(size, size)
    a = cov(sd_ring(x, y, c, c, R0 * k, R1 * k)) * sector_mask(x, y, c, c, a0, a1)
    return from_arr(color, a)


def circle_outline(r, stroke, color, k=K):
    size = int((2 * r + stroke + 4) * k)
    c = size / 2.0
    x, y = grid(size, size)
    a = cov(sd_ring(x, y, c, c, (r - stroke / 2) * k, (r + stroke / 2) * k))
    return from_arr(color, a)


def ball(r, c_in=(70, 100, 215), c_out=(6, 14, 66), k=K):
    size = int((2 * r + 4) * k)
    c = size / 2.0
    x, y = grid(size, size)
    d = np.hypot(x - c * 0.82, y - c * 0.74) / (r * k * 1.25)
    rgb = lerp_color(c_in, c_out, np.clip(d, 0, 1) ** 0.8)
    return from_arr(rgb, cov(np.hypot(x - c, y - c) - r * k))


def solid_rect(w, h, color, k=K):
    return new(max(2, int(w * k)), max(2, int(h * k)), rgba(color))


def hgrad_rect(w, h, c0, c1, k=K, hl=True):
    W_, H_ = int(w * k), int(h * k)
    x, y = grid(W_, H_)
    rgb = lerp_color(c0, c1, x / W_)
    if hl:
        m = np.clip(1 - np.abs(y / H_ - 0.78) / 0.05, 0, 1)[..., None] * 0.7
        rgb = rgb * (1 - m) + 255.0 * m
    return from_arr(rgb, np.ones((H_, W_), np.float32))


def text_asset(s, fname, size, color=(0, 0, 0), k=K, tracking=0.0, sx=1.0, rot=0.0, blur_x=0.0):
    im = text_img(s, font(fname, size * k), rgba(color), pad=3, tracking=tracking * k)
    if sx != 1.0:
        im = im.resize((max(1, int(im.width * sx)), im.height), Image.LANCZOS)
    if blur_x:
        im = im.resize((im.width, im.height), Image.LANCZOS).filter(ImageFilter.BoxBlur(0))
        a = np.asarray(im).astype(np.float32)
        kx = int(blur_x * k) | 1
        ker = np.ones(kx) / kx
        for ch in range(4):
            a[..., ch] = np.apply_along_axis(lambda r: np.convolve(r, ker, 'same'), 1, a[..., ch])
        im = Image.fromarray(a.astype(np.uint8), 'RGBA')
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    return im


# ----------------------------------------------------------------------------- photos
def pole_photo(part='all'):
    """leaning utility pole with cross-arm, disc insulators and a mass of foliage (GPT redraw 'pole-lean.png' of frames 24 / 32):
    world (228, 410) .. (410, 776).  part 'top' = the cross-arm region only, as a flat black silhouette (what is left from 74)"""
    a = np.asarray(gen('pole-lean.png').convert('RGBA')).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0).astype(np.uint8)
    a = a[1:1533, 73:990]
    if part == 'top':
        a = a[60:700, 330:917].copy()
        a[..., :3] = 10
        im = Image.fromarray(a, 'RGBA')
        return im.resize((int(104 * K), int(196 * K)), Image.LANCZOS)
    im = Image.fromarray(a, 'RGBA')
    return im.resize((int(182 * K), int(366 * K)), Image.LANCZOS)


def sunset_photo():
    """dusk city photo (GPT image redrawn from frame 46) between two black posts; the upper third is washed out and two thin
    white lines cross it, as in the source.  175 x 172 world px, top-left at (647, 500)."""
    W_, H_ = 175 * K, 172 * K
    bar = int(12.5 * K)
    a = np.asarray(fit(gen('sunset-city.png').convert('RGB'), W_ - 2 * bar, H_)).astype(np.float32)
    g = a.mean(axis=2, keepdims=True)
    a = g + (a - g) * 0.80                                        # the source is less saturated ...
    a[..., 1] = np.clip(a[..., 1] * 1.05 + 5, 0, 255)             # ... and its glow is more yellow than orange
    h, w = a.shape[:2]
    t = np.clip(np.linspace(0, 1, h)[:, None] / 0.38, 0, 1)
    wash = (0.52 + 0.48 * t)[..., None]
    a = a * wash + np.array((234, 242, 240), np.float32) * (1 - wash)
    out = Image.new('RGBA', (W_, H_), (8, 8, 8, 255))
    out.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGB'), (bar, 0))
    d = ImageDraw.Draw(out)
    for yy in (589.0, 653.0):
        py = int((yy - 500.0) * K)
        d.line([(0, py), (W_, py)], fill=(246, 246, 246, 235), width=max(1, K // 2))
    return out


def wires():
    """four parallel power lines (fine dotted hairlines rising to the right) with pairs of dark insulators"""
    c = Canvas(420, 260, 1110, 500, k=K, ss=3)
    col = (56, 56, 62, 255)
    lines = [((430, 363), (900, 279), (727, 762)), ((430, 440), (1090, 280), (655, 690)), ((560, 454), (1095, 335), (835, 870)),
             ((610, 481), (1095, 377), (912,))]
    for (p0, p1, blobs) in lines:
        c.dashed(p0, p1, col, 0.9, 2.2, 1.8)
        ang_ = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
        for bx in blobs:
            t = (bx - p0[0]) / float(p1[0] - p0[0])
            by = p0[1] + (p1[1] - p0[1]) * t
            blob = Image.new('RGBA', (int(15 * c.f), int(5.2 * c.f)), (0, 0, 0, 0))
            ImageDraw.Draw(blob).rounded_rectangle([0, 0, blob.width - 1, blob.height - 1], radius=2.2 * c.f, fill=(30, 30, 36, 255))
            blob = blob.rotate(-ang_, resample=Image.BICUBIC, expand=True)
            px_, py_ = c.P(bx, by)
            c.paste(blob, px_ - blob.width / 2, py_ - blob.height / 2)
    return c


# ----------------------------------------------------------------------------- holographic paper
def holo_big():
    return S0.holo_disc(830.0, k=1, seed=11, rim=True, sat=0.2)


SHEET_C = (228.0, -70.0)            # final centre of the quarter-annulus paper sheet (world)
SHEET_R0, SHEET_R1 = 359.0, 934.0
PINW = (522.0, 155.0)               # pastel pinwheel centre, relative to the sheet centre


def _sheet_alpha(wx, wy, k):
    """quarter annulus around the origin: radial sides point right (0 deg) and down (90 deg)"""
    d = np.hypot(wx, wy)
    return cov((d - SHEET_R1) * k) * cov((SHEET_R0 - d) * k) * cov(-wx * k) * cov(-wy * k)


def sheet(k=1.5):
    """the white 'paper': a quarter ring with a slightly brighter embossed rim"""
    n = int((SHEET_R1 + 4) * k)
    x, y = grid(n, n)
    wx, wy = x / k - 2, y / k - 2
    d = np.hypot(wx, wy)
    e = np.minimum(np.minimum(d - SHEET_R0, SHEET_R1 - d), np.minimum(wx, wy))
    rim = np.clip(1 - e / 34.0, 0, 1)
    v = 241.0 + 11.0 * rim + 3.0 * np.clip((d - SHEET_R0) / (SHEET_R1 - SHEET_R0), 0, 1)
    rgb = np.dstack([v, v, v + 1.0]) + noise(n, n, 5, 1.0)[..., None]
    return from_arr(rgb, _sheet_alpha(wx, wy, k))


def holo2(k=1.0):
    """pastel conic 'pinwheel' printed on the sheet + the lavender crescent hugging its inner arc"""
    n = int((SHEET_R1 + 4) * k)
    x, y = grid(n, n)
    wx, wy = x / k - 2, y / k - 2
    d = np.hypot(wx, wy)
    px_, py_ = PINW
    dp = np.hypot(wx - px_, wy - py_)
    t = (ang(wx, wy, px_, py_) / 360.0 + 0.035 * np.sin(dp / 55.0)) % 1.0
    stops = [(0.00, (250, 206, 226)), (0.07, (252, 226, 214)), (0.16, (226, 236, 252)), (0.30, (214, 216, 250)), (0.44, (236, 246, 246)),
             (0.56, (156, 236, 226)), (0.68, (206, 246, 238)), (0.80, (240, 244, 250)), (0.90, (172, 238, 232)), (1.00, (250, 206, 226))]
    rgb = grad_stops(t, stops)
    al = np.clip((600.0 - dp) / 330.0, 0, 1) ** 1.25 * 0.92
    cres = np.clip(1 - (d - SHEET_R0) / 96.0, 0, 1) * np.clip((d - SHEET_R0) / 6.0, 0, 1)
    th = np.degrees(np.arctan2(wy, wx))                       # 0 = +x, 90 = down
    cres = cres * np.clip((th - 16) / 14.0, 0, 1) * np.clip((87 - th) / 10.0, 0, 1)
    cm = cres[..., None]
    rgb = rgb * (1 - cm) + np.array((150, 150, 240), np.float32) * cm
    al = np.maximum(al, cres * 0.9)
    rgb = rgb + noise(n, n, 9, 3.2)[..., None]
    return from_arr(rgb, al * _sheet_alpha(wx, wy, k))


def lav_disc(R=310.0, k=1.0):
    """soft lavender disc that the holographic print starts from (frames 25-30)"""
    n = int((2 * R + 8) * k)
    c = n / 2.0
    x, y = grid(n, n)
    d = np.hypot(x - c, y - c) / k
    rgb = lerp_color((178, 170, 250), (130, 126, 240), np.clip(d / R, 0, 1) ** 1.5)
    return from_arr(rgb + noise(n, n, 4, 2.5)[..., None], np.clip((R - d) / 26.0, 0, 1) * 0.95)


def vgrad_rect(w, h, c0, c1, k=K):
    W_, H_ = int(w * k), int(h * k)
    x, y = grid(W_, H_)
    return from_arr(lerp_color(c0, c1, y / H_), np.ones((H_, W_), np.float32))


def zigzag():
    """the pink bar crumples into a zigzag for one frame (27)"""
    c = Canvas(428, 578, 682, 728, k=K, ss=3)
    pts = [(437, 715), (470, 594), (503, 702), (536, 602), (569, 702), (602, 602), (635, 702), (668, 612)]
    c.line(pts, rgba(PK), 13.0)
    return c


# ----------------------------------------------------------------------------- opening extras
DECK_W, DECK_H = 416.4, 239.0          # = 770 x 442 screen px at the zoom of the opening (1.849)


def _deck():
    """the opening photo: view from a ferry deck (GPT image rebuilt from frames 6 / 10 of the source).  As in the source the sky is
    cut away and the white railing tubes are keyed out, so only the pale sea shows between them; tones lifted to the washed mint."""
    a = np.asarray(gen('deck-view.png').convert('RGBA')).astype(np.float32)
    h, w = a.shape[:2]
    yy = np.mgrid[0:h, 0:w][0]
    al = (a[..., 3] >= 200).astype(np.float32)
    al = al * (1.0 - ((a[..., :3].min(axis=2) > 222) & (yy > 0.795 * h)).astype(np.float32))
    rgb = a[..., :3]
    rgb = rgb + (255.0 - rgb) * (np.clip((rgb - 110.0) / 60.0, 0, 1) * 0.42)
    rgb = rgb * np.array((0.985, 1.0, 0.985), np.float32)
    im = from_arr(rgb, al)
    im = im.crop(im.getbbox())
    return im.resize((int(DECK_W * K), int(DECK_H * K)), Image.LANCZOS)


def mint_shapes():
    """flat mint silhouette of the deck photo (frames 3-6), wiped away from the left as the photo itself appears"""
    a = np.asarray(_deck()).copy()
    a[..., 0], a[..., 1], a[..., 2] = 104, 250, 190
    a[..., 3] = np.where(a[..., 3] > 110, 255, 0).astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


def pale_photo():
    """the washed-out deck photo (frames 5-11)"""
    return _deck()


def stamp(R=39.4):
    """round physics diagram next to the sphere (frames 3-25): a circle, two dotted shells, radius arrows, M(r) / rho(r) / dr labels"""
    c = Canvas(-R - 3, -R - 3, R + 3, R + 3, k=4, ss=3)
    g = (16, 16, 18, 255)
    c.circle(0, 0, R, outline=g, width=0.8)
    for rr in (0.80, 0.70):
        n = int(2 * math.pi * R * rr / 1.8)
        for i in range(n):
            a_ = 2 * math.pi * i / n
            c.circle(R * rr * math.cos(a_), R * rr * math.sin(a_), 0.44, fill=g)

    def arrow(p, q, head=3.0):
        c.line([p, q], g, 0.8)
        a_ = math.atan2(q[1] - p[1], q[0] - p[0])
        for da in (2.6, -2.6):
            c.line([q, (q[0] + head * math.cos(a_ + da), q[1] + head * math.sin(a_ + da))], g, 0.8)
    v0 = (-R * 0.07, -R * 0.02)
    arrow(v0, (R * 0.44, -R * 0.56))
    arrow(v0, (R * 0.55, R * 0.66))
    arrow((R * 0.30, R * 0.01), (R * 0.69, R * 0.01), 2.4)
    arrow((R * 0.99, R * 0.01), (R * 0.81, R * 0.01), 2.4)
    f = 'timesbi.ttf'
    c.text(-R * 0.30, -R * 0.27, 'M(r)', f, R * 0.185, g, anchor='mm')
    c.text(-R * 0.20, R * 0.27, '\u03c1(r)', f, R * 0.185, g, anchor='mm')
    c.text(R * 0.47, -R * 0.09, 'r', f, R * 0.17, g, anchor='mm')
    c.text(R * 0.90, -R * 0.11, 'dr', f, R * 0.17, g, anchor='mm')
    c.text(R * 0.50, R * 0.80, 'M,R', f, R * 0.17, g, anchor='mm')
    return c


def wedge_light(L=520.0, half=16.0):
    """soft light sector pointing up from the holo centre (frames 2-14)"""
    c = Canvas(-L, -L, L, 8, k=1, ss=2)
    c.pie(0, 0, L, 90 - half, 90 + half, (250, 250, 250, 236))
    return blur(c.done(), 1.2)


# ----------------------------------------------------------------------------- ring group
def vinyl():
    """the record: a full disc in a square canvas centred on VIN_C (it orbits the ring centre, so nothing is clipped here)"""
    x0, y0 = VIN_C[0] - VIN_R - 2, VIN_C[1] - VIN_R - 2
    w = h = int((2 * VIN_R + 4) * K)
    x, y = grid(w, h)
    wx, wy = x / K + x0, y / K + y0
    d = np.hypot(wx - VIN_C[0], wy - VIN_C[1])
    a = cov((d - VIN_R) * K)
    th = np.radians(ang(wx, wy, VIN_C[0], VIN_C[1]))
    g = 13 + 9 * (0.5 + 0.5 * np.sin(d * 2.1)) + 7 * (0.5 + 0.5 * np.sin(d * 0.41 + 1.0))
    g = g + 26 * np.clip(np.cos(2 * (th - 0.75)), 0, 1) ** 8
    rgb = np.dstack([g, g, g + 1])
    lab = cov((d - 92) * K)[..., None]
    seg = (((np.degrees(th) + 18.0) % 90.0) < 40.0)[..., None]             # four lighter blades (pinwheel)
    labc = np.where(seg, np.array((246, 94, 152), np.float32), np.array((226, 28, 112), np.float32))
    ringm = (cov((np.abs(d - 74) - 1.0) * K) + cov((np.abs(d - 30) - 0.8) * K))[..., None] * 0.5
    labc = labc * (1 - ringm) + np.array((150, 14, 70), np.float32) * ringm
    rgb = rgb * (1 - lab) + labc * lab
    dot = cov((d - 10) * K)[..., None]
    rgb = rgb * (1 - dot) + np.array(BL, np.float32) * dot
    img = from_arr(rgb, a)
    # label lettering along a circle
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    fnt = font('georgia.ttf', 15 * K)
    txt = 'rollback(Q)  .  floating  cap  .  '
    for i, ch in enumerate(txt):
        if ch == ' ':
            continue
        ang_ = -90 + i * (360.0 / len(txt))
        gi = text_img(ch, fnt, (120, 8, 60, 255), pad=1)
        gi = gi.rotate(-ang_ - 90, resample=Image.BICUBIC, expand=True)
        cx_ = (VIN_C[0] - x0) * K + 56 * K * math.cos(math.radians(ang_))
        cy_ = (VIN_C[1] - y0) * K + 56 * K * math.sin(math.radians(ang_))
        lay.alpha_composite(gi, (int(cx_ - gi.width / 2), int(cy_ - gi.height / 2)))
    la = np.asarray(lay).copy()
    la[..., 3] = (la[..., 3] * np.asarray(img)[..., 3] / 255.0).astype(np.uint8)
    img.alpha_composite(Image.fromarray(la, 'RGBA'))
    return img


def ring_inner():
    x0, y0, x1, y1 = 500, 340, 900, 542
    w, h = (x1 - x0) * K, (y1 - y0) * K
    x, y = grid(w, h)
    wx, wy = x / K + x0, y / K + y0
    a = cov((np.hypot(wx - 700, wy - 540) - 197) * K) * cov((wy - 540) * K)
    t = np.clip(((wx - 520) / 360.0) * 0.6 + (1 - (wy - 345) / 195.0) * 0.4, 0, 1)
    rgb = grad_stops(t, [(0, (247, 244, 247)), (0.45, (248, 248, 250)), (1, (243, 246, 250))])
    rgb = rgb + noise(h, w, 21, 2.0)[..., None]
    return from_arr(rgb, a)


def inner_low():
    """white paper inside the grey ring, below the ruler (hides the record where it passes behind)"""
    r = CRES_R0 + 2.0
    w, h = int((2 * r + 4) * K), int((r + 4) * K)
    x, y = grid(w, h)
    wx, wy = x / K - r - 2, y / K - 2                       # relative to CRES_C
    a = cov((np.hypot(wx, wy) - r) * K) * cov(-wy * K)
    return from_arr(np.dstack([np.full_like(wx, 249.0)] * 3) + noise(h, w, 22, 1.5)[..., None], a)


def crescent(mode=0):
    """half ring below the ruler, centre CRES_C, radii CRES_R0..CRES_R1, in a square canvas centred on CRES_C.
    mode 0: light head at the right end fading to a black tail (the ring is turned out from under the ruler head first);
    mode 1: plain black (the head goes dark after frame 58)."""
    x0, y0 = CRES_C[0] - CRES_R1 - 2, CRES_C[1] - CRES_R1 - 2
    w = h = int((2 * CRES_R1 + 4) * K)
    x, y = grid(w, h)
    wx, wy = x / K + x0, y / K + y0
    d = np.hypot(wx - CRES_C[0], wy - CRES_C[1])
    a = cov((d - CRES_R1) * K) * cov((CRES_R0 - d) * K) * cov((CRES_C[1] - wy) * K)
    if mode == 1:
        return from_arr((3, 3, 3), a)
    phi = np.degrees(np.arctan2(wy - CRES_C[1], wx - CRES_C[0]))           # 0 = right end, 90 = bottom, 180 = left end
    g = [(0.0, 152.0), (15 / 180.0, 124.0), (35 / 180.0, 74.0), (55 / 180.0, 24.0), (66 / 180.0, 4.0), (1.0, 3.0)]
    v = grad_stops(np.clip(phi / 180.0, 0, 1), [(p, (q, q, q)) for p, q in g])
    v = v + noise(h, w, 8, 1.6)[..., None]
    return from_arr(v, a)


def curl():
    """dark page curl: a square corner with a quarter disc bitten out of it (two thin tips)"""
    cw, chh = 147.0, 147.0
    w, h = int(cw * K), int(chh * K)
    x, y = grid(w, h)
    wx, wy = x / K, y / K
    dist = np.hypot(wx - cw, (wy - chh) * cw / chh)
    rgb = lerp_color((30, 30, 32), (126, 126, 128), np.clip(np.hypot(wx, wy) / 150.0, 0, 1) ** 1.4)
    return from_arr(rgb, cov((0.95 * cw - dist) * K))


def road():
    c = Canvas(945, 640, 1100, 752, k=K, ss=3)
    top = [(955, 700), (1052, 652), (1090, 673), (1000, 733)]
    c.poly([(x_, y_ + 7) for x_, y_ in top], (236, 236, 236, 255))
    c.poly(top, (44, 46, 44, 255))
    c.dashed((978, 716), (1071, 664), (222, 196, 60, 255), 1.6, 9, 6)
    c.line([(966, 708), (1060, 659)], (200, 200, 200, 120), 0.8)
    return c


def horn_sprite(f, ver, lw_w=0.5, nl=66, val=92.0, al=0.62, fan_mul=2):
    """the wire horn at frame f (see horn.py); `ver` only keys the asset cache to the pose tables"""
    return horn.horn_frame(f, 1, lw_w, nl, val, al, fan_mul)


# ----------------------------------------------------------------------------- small graphics
def pin_icon(label=None):
    c = Canvas(-28, -36, 28, 22, k=4, ss=3)
    g = (24, 140, 44, 255)
    c.poly([(-8.2, -17), (8.2, -17), (0, 0)], g)
    c.circle(0, -20, 9.5, fill=g)
    c.circle(0, -20, 4.0, fill=(240, 246, 240, 255))
    if label:
        c.text(0, 4, label, 'Montserrat-Regular.ttf', 12.5, (20, 120, 40, 255), anchor='ma')
    return c


def _smooth(pts, n=14):
    """Catmull-Rom through the points"""
    out = []
    P = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            t = j / float(n)
            out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t * t
                                    + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t ** 3) for k in (0, 1)))
    out.append(pts[-1])
    return out


def lines_a():
    """two dark-green hairlines: a long thin 'lasso' loop that ends on the 2030 pin, and a curve that rises over the photo and
    drops to a small ringed end"""
    c = Canvas(560, 440, 1130, 640, k=K, ss=3)
    gr = (26, 104, 40, 255)
    top = _smooth([(634, 478), (646, 470), (700, 465), (800, 470), (900, 485), (1000, 505), (1110, 527)])
    bot = _smooth([(1110, 527), (1000, 517), (900, 507), (800, 497), (700, 490), (646, 486), (634, 478)])
    c.line(top + bot, gr, 1.0)
    low = _smooth([(575, 590), (660, 560), (740, 543), (830, 556), (900, 580), (948, 603)])
    c.line(low, gr, 1.0)
    c.circle(953, 607, 5.0, outline=(34, 34, 38, 255), width=0.9)
    return c


def bracket_a():
    c = Canvas(376, 165, 470, 615, k=K, ss=3)
    bk = (20, 20, 20, 255)
    c.line([(398, 178), (383, 178), (383, 606), (398, 606)], bk, 1.0)
    c.text(403, 172, '4月26日', 'Deng.ttf', 10, bk)
    c.text(403, 599, '6月21日', 'Deng.ttf', 10, bk)
    return c


def label_2030():
    c = Canvas(1036, 540, 1106, 574, k=4, ss=3)
    c.text(1040, 549, '2030', 'Montserrat-Light.ttf', 15, (20, 20, 20, 255))
    c.ellipse(1084, 547, 1096, 569, fill=rgba(PK))
    return c


def icons_a():
    c = Canvas(436, 748, 506, 784, k=4, ss=3)
    dg = (74, 74, 74, 255)
    c.text(452, 766, '♻', 'seguisym.ttf', 24, dg, anchor='mm')
    c.poly([(487, 753), (494, 764), (492, 776), (482, 776), (480, 766), (484, 760), (485, 766)], dg)
    c.poly([(487, 766), (490, 772), (485, 774)], (230, 230, 230, 255))
    return c


def quotes():
    c = Canvas(0, 498, 136, 548, k=6, ss=2)
    for (x_, ch) in ((20, '“'), (113, '”')):
        c.text(x_, 505, ch, 'georgiab.ttf', 62, (120, 120, 120, 255), anchor='ma')
        c.text(x_, 505.6, ch, 'georgiab.ttf', 59, (252, 252, 252, 255), anchor='ma')
    return c


def card():
    c = Canvas(33, 508, 95, 570, k=6, ss=2)
    c.rect(35, 510, 93, 568, fill=(255, 255, 255, 255), outline=(150, 150, 150, 255), width=0.5)
    return c


def watch():
    c = Canvas(35, 510, 93, 568, k=6, ss=3)
    cx_, cy_ = 62.0, 541.5
    c.line([(cx_ + 12, cy_ - 14), (cx_ + 17, cy_ - 20)], (150, 140, 150, 255), 3.0)
    c.circle(cx_ + 19.5, cy_ - 22.5, 4.6, outline=(150, 140, 150, 255), width=1.6)
    c.circle(cx_, cy_, 21.5, fill=(168, 160, 172, 255))
    c.circle(cx_, cy_, 19.4, fill=(224, 220, 226, 255))
    c.circle(cx_, cy_, 17.6, fill=(250, 250, 250, 255))
    for i in range(12):
        th = math.radians(i * 30)
        c.line([(cx_ + 14.2 * math.cos(th), cy_ + 14.2 * math.sin(th)), (cx_ + 16.6 * math.cos(th), cy_ + 16.6 * math.sin(th))],
               (60, 60, 60, 255), 0.7)
    c.circle(cx_ - 4, cy_ + 7, 4.6, outline=(120, 120, 120, 255), width=0.5)
    c.line([(cx_, cy_), (cx_ - 9, cy_ - 4)], (40, 40, 40, 255), 1.0)
    c.line([(cx_, cy_), (cx_ + 11, cy_ + 2)], (40, 40, 40, 255), 0.8)
    c.circle(cx_, cy_, 1.3, fill=(40, 40, 40, 255))
    return c


def tube():
    """glossy pink rope with a blue cap (GPT image redrawn from frames 46/50 of the source); 515 x 205 world px"""
    im = gen('pink-tube2.png')
    a = np.asarray(im).copy()
    a[..., 3] = np.where(a[..., 3] > 40, a[..., 3], 0).astype(np.uint8)
    im = Image.fromarray(a, 'RGBA')
    im = im.crop(im.getbbox())
    return im.resize((515 * K, 205 * K), Image.LANCZOS)


def buildings():
    """white paper-model houses (GPT image redrawn from frames 42 / 46); 501 world px wide, top-left at (852, 419)"""
    im = gen('buildings2.png')
    a = np.asarray(im).copy()
    a[..., 3] = np.where(a[..., 3] > 40, a[..., 3], 0).astype(np.uint8)
    im = Image.fromarray(a, 'RGBA')
    im = im.crop(im.getbbox())
    w = 501 * K
    return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)


def hill():
    x0, y0, x1, y1 = 1376, 484, 1556, 541
    w, h = (x1 - x0) * K, (y1 - y0) * K
    x, y = grid(w, h)
    wx, wy = x / K + x0, y / K + y0
    top = 506 - 12 * np.sin((wx - 1380) / 170.0 * math.pi) - 3.0 * np.sin(wx * 0.31) - 2.0 * np.sin(wx * 0.83 + 1.0) - 1.5 * np.sin(wx * 2.3)
    a = cov((top - wy) * K) * cov((wy - 540) * K) * cov((1382 - wx) * K) * cov((wx - 1550) * K)
    n = noise(h, w, 31, 9.0)
    rgb = np.dstack([24 + n, 32 + n * 1.2, 22 + n])
    return from_arr(rgb, a)


def lamp():
    c = Canvas(1335, 440, 1390, 542, k=K, ss=3)
    dg = (40, 40, 44, 255)
    c.line([(1345, 540), (1345, 458), (1352, 452), (1378, 450)], dg, 1.6)
    c.rect(1370, 449, 1382, 453, dg)
    c.line([(1345, 470), (1337, 466)], dg, 1.2)
    c.rect(1354, 506, 1368, 524, (232, 196, 40, 255))
    c.line([(1357, 511), (1365, 511)], (30, 30, 30, 255), 1.0)
    c.line([(1357, 516), (1365, 516)], (30, 30, 30, 255), 1.0)
    c.line([(1361, 524), (1361, 540)], dg, 1.2)
    return c


def red_lines():
    c = Canvas(1130, 320, 1570, 775, k=K, ss=3)
    rd = (150, 28, 44, 255)
    c.line([(1345, 430), (1185, 765), (1560, 335)], rd, 0.9)
    c.line([(1140, 548), (1185, 765)], rd, 0.9)
    return c


def kaishi_big():
    return text_asset('开始', 'simsun.ttc', 30, (10, 10, 10), sx=3.4)


# ----------------------------------------------------------------------------- build
def _two_wipes(L, x0, W_, heads, tails):
    """show only [tail, head] of a horizontal bar: heads/tails = [(frame, world x)] (hold keys)"""
    L.fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': [(f, 100.0 * (1 - (h - x0) / W_), HOLD) for f, h in heads],
                                'ADBE Linear Wipe-0002': -90.0, 'ADBE Linear Wipe-0003': 0.0})
    L.fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': [(f, 100.0 * (t - x0) / W_, HOLD) for f, t in tails],
                                'ADBE Linear Wipe-0002': 90.0, 'ADBE Linear Wipe-0003': 0.0})
    return L


def build(sc):
    sc.sec = 'A'
    sc.kdef = K
    hc = HOLO_C
    WHITE = [1.0, 1.0, 1.0, 1.0]

    # ---------------- holographic disc (opening) ----------------
    hp = [(2, s2w(2, 1270, 310), 0.405), (3, s2w(3, 1260, 440), 0.978), (5, s2w(5, 1225, 310), 1.11),
          (7, s2w(7, 1195, 310), 1.69), (9, s2w(9, 1155, 300), 1.77), (12, s2w(12, 1114, 310), 1.77),
          (14, s2w(14, 1085, 310), 1.76), (15, s2w(15, 650, 310), 0.94), (16, hc, 1.0)]
    pos_k = [(f, [p[0], p[1]], LIN) for f, p, s_ in hp]
    sca_k = [(f, [s_ * 100, s_ * 100], LIN) for f, p, s_ in hp]

    def hs(f):                                   # disc scale at frame f
        for (f0, _, a), (f1, _, b) in zip(hp[:-1], hp[1:]):
            if f0 <= f <= f1:
                return a + (b - a) * (f - f0) / float(f1 - f0)
        return hp[-1][2]

    L = sc.add('A_halo', S0.halo_ring, hc[0] - 320 * 1.42 - 2, hc[1] - 320 * 1.42 - 2, 320.0, k=K, pivot=hc, crop=False)
    L.span(3, 4).key('position', pos_k[1:3]).key('scale', sca_k[1:3]).set(pano=False)
    L = sc.add('A_holo', S0.holo_disc, hc[0] - 320 - 2, hc[1] - 320 - 2, 320.0, k=K, pivot=hc, crop=False)
    L.span(2, 24).key('position', pos_k).key('scale', sca_k).set(pano=False)
    # frame 2: almost white; 22-23: washes out to white before the soft white disc of frame 24
    L.fx('ADBE Tint', **{'ADBE Tint-0001': WHITE, 'ADBE Tint-0002': WHITE,
                         'ADBE Tint-0003': [(2, 80.0, HOLD), (3, 0.0, HOLD), (22, 30.0, HOLD), (23, 86.0, HOLD)]})

    # mint two-tone blocks (3-6) that turn into a washed-out photo (5-11), both glued to the screen
    # (photo: screen box 580..1349 x 311..753 on 5-11; silhouette: 258 px further right on 3-4, then on the photo, wiped off)
    L = sc.add('A_palephoto', pale_photo, 300, 400)
    L.span(5, 12).set(pano=False).key('opacity', [(5, 100.0, HOLD), (10, 86.0, HOLD), (11, 62.0, HOLD)])
    pin(L, [(5, 964.5, 532), (11, 964.5, 532)], [(5, 1.0), (11, 1.0)])
    L = sc.add('A_mint', mint_shapes, 300, 400)
    L.span(3, 7).set(pano=False)
    pin(L, [(3, 1222.5, 533), (4, 1222.5, 533), (5, 964.5, 532), (6, 964.5, 532)], [(3, 1.0), (6, 1.0)])
    L.fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': [(3, 0.0, HOLD), (5, 55.0, HOLD), (6, 63.0, HOLD)], 'ADBE Linear Wipe-0002': 90.0,
                                'ADBE Linear Wipe-0003': 0.0})

    # light wedge between two rays of the disc: white (2-8), then mint (9-14); stepped rotation
    w0 = sc.add('A_wedge0', wedge_light, hc[0] - 520, hc[1] - 520, k=1, pivot=hc, crop=False)
    wk = {2: (1.0, 7), 3: (2.44, 36), 4: (1.5, 20), 5: (0.68, -4), 6: (0.7, 0), 7: (0.7, 6), 8: (0.8, 15)}
    w0.span(2, 9).set(pano=False).key('position', pos_k)
    w0.key('scale', [(f, [kx * 100 * max(hs(f), 0.9), 125 * max(hs(f), 0.9)], HOLD) for f, (kx, r) in wk.items()])
    w0.key('rotation', [(f, float(r), HOLD) for f, (kx, r) in wk.items()])
    w0.flashes([(2, (236, 208, 250)), (3, None)])
    w1 = sc.clone('A_wedge1', w0)
    w1.pivot = hc
    wk = {9: (274, 221, 26), 10: (212, 221, 40), 11: (10, 60, -83), 12: (15, 50, -115), 13: (15, 50, -108), 14: (14, 48, -100)}   # (sx %, sy %, rotation)
    w1.span(9, 15).set(pano=False).key('position', pos_k)
    w1.key('scale', [(f, [float(sx_), float(sy_)], HOLD) for f, (sx_, sy_, r) in wk.items()])
    w1.key('rotation', [(f, float(r), HOLD) for f, (sx_, sy_, r) in wk.items()])
    MINT_ = [150 / 255.0, 240 / 255.0, 225 / 255.0, 1.0]
    w1.fx('ADBE Tint', **{'ADBE Tint-0001': MINT_, 'ADBE Tint-0002': MINT_, 'ADBE Tint-0003': 100.0})

    # thin rays from the disc centre.  5-9: a narrow fan in the upper sector; from 10 the lines spread out to
    # -88 / 0 / 60 / 110 / 136 / 155 deg (clockwise from 'up', measured on 11-13).  From 53 a fan from far left of the frame.
    L = sc.add('A_raysA', S0.rays, -1150 + hc[0], -1150 + hc[1], 1150.0, 1, (-36, -17, 5, 40, 60), pivot=hc, k=1, crop=False)
    L.span(5, 10).set(pano=False).key('position', pos_k[2:])
    L = sc.add('A_raysB', S0.rays, -1150 + hc[0], -1150 + hc[1], 1150.0, 1, (-88, 0, 60, 110, 136, 155), pivot=hc, k=1, crop=False)
    L.span(10, 25).set(pano=False).key('position', pos_k[2:] + [(24, [hc[0], hc[1]], LIN)]).key(
        'rotation', [(10, 8.0, HOLD), (11, 3.0, HOLD), (12, 0.0, HOLD)])
    L = sc.add('A_rays', S0.rays, -171.0 - 1150, 270.0 - 1150, pivot=(-171.0, 270.0), k=1, crop=False)
    L.span(53)

    # ---------------- the paper sheet: quarter annulus that fans open (25-31) and slides up (26-36) ----------------
    L = sc.add('A_holo_big', holo_big, 320 - 834, 200 - 834, k=1, pivot=(320, 200), crop=False)
    L.span(36, 57).set(pano=False).key('scale', [(36, [55, 55], LIN), (39, [100, 100], LIN)]).key('opacity', [(52, 100.0, LIN), (56, 0.0, LIN)])
    sk = [(25, 229, 160), (26, 230, 168), (27, 229, 160), (28, 226, 150), (29, 229, 113), (30, 229, 23), (31, 229, -14), (32, 229, -35),
          (33, 229, -50), (34, 229, -60), (35, 229, -66), (36, SHEET_C[0], SHEET_C[1])]
    sheet_pos = [(f, [x_, y_], HOLD) for f, x_, y_ in sk]
    L = sc.add('A_sheet', sheet, SHEET_C[0] - 2, SHEET_C[1] - 2, k=1.5, pivot=SHEET_C, crop=False)
    L.span(25).key('position', sheet_pos)
    L.fx('ADBE Radial Wipe', **{'ADBE Radial Wipe-0001': [(25, 6.67, HOLD), (26, 3.39, HOLD), (27, 2.14, HOLD), (28, 1.25, HOLD),
                                                          (29, 0.75, HOLD), (30, 0.44, HOLD), (31, 0.25, HOLD), (32, 0.0, HOLD)],
                                'ADBE Radial Wipe-0002': 90.0, 'ADBE Radial Wipe-0003': [3.0, 3.0], 'ADBE Radial Wipe-0004': 1})
    lav = sc.add('A_lav', lav_disc, 697 - 314, 478 - 314, k=1, crop=False, pivot=(697.0, 478.0))
    shrink = [(25, [100, 100], HOLD), (26, [96, 96], HOLD), (27, [92.7, 92.7], HOLD), (28, [88, 88], HOLD), (29, [83, 83], HOLD)]
    lav.span(25, 30).set(pano=False).key('scale', shrink).key('opacity', [(25, 100.0, HOLD), (29, 22.0, HOLD)])
    lav.fx('ADBE Radial Wipe', **{'ADBE Radial Wipe-0001': 50.0, 'ADBE Radial Wipe-0002': 270.0, 'ADBE Radial Wipe-0004': 1})
    lav2 = sc.clone('A_lav_up', lav)
    lav2.pivot = (697.0, 478.0)
    lav2.span(26, 31).set(pano=False).key('scale', shrink[1:] + [(30, [78, 78], HOLD)])
    fan = [(26, 12), (27, 25), (28, 40), (29, 52), (30, 20)]
    lav2.fx('ADBE Radial Wipe', **{'ADBE Radial Wipe-0001': [(f, 100.0 * (360 - 2 * h) / 360.0, HOLD) for f, h in fan],
                                   'ADBE Radial Wipe-0002': [(f, float(h), HOLD) for f, h in fan], 'ADBE Radial Wipe-0004': 1})
    L = sc.add('A_holo2', holo2, SHEET_C[0] - 2, SHEET_C[1] - 2, k=1, pivot=SHEET_C, crop=False)
    L.span(27).key('position', [k_ for k_ in sheet_pos if k_[0] >= 27]).key('opacity', [(27, 0.0, LIN), (31, 48.0, LIN)])

    # ---------------- gradient streaks along the ruler (21-29): head / tail positions measured per frame ----------------
    L = sc.add('A_gbar_mag', hgrad_rect, 96, 405, 934, 67, (124, 54, 236), (240, 62, 150))
    L.span(21, 29).set(pano=False)
    _two_wipes(L, 96.0, 934.0, [(21, 783), (22, 890), (23, 943), (24, 974), (25, 994), (26, 1008), (27, 1017), (28, 1024)],
               [(21, 705), (22, 697), (23, 677), (24, 621), (25, 96), (26, 332), (27, 568), (28, 802)])
    L = sc.add('A_gbar_cyan', vgrad_rect, -200, 472, 1230, 64, (96, 228, 228), (238, 150, 206))
    L.span(22, 30).set(pano=False)
    _two_wipes(L, -200.0, 1230.0, [(22, 120), (23, 151), (24, 152), (25, 957), (26, 979), (27, 992), (28, 1011), (29, 1018)],
               [(22, -200), (27, 121), (28, 428), (29, 733)])
    L = sc.add('A_gbar_violet', solid_rect, 96, 405, 40, 67, (118, 52, 236), pivot=(96, 438.5))
    L.span(22, 25).set(pano=False).key('scale', [(22, [23, 100], HOLD), (23, [100, 100], HOLD), (24, [90, 100], HOLD)])
    L = sc.add('A_whitedisc', S0.white_disc, 384 - 309, 299 - 309, 247.0, k=K, crop=False)
    L.span(24, 25).set(pano=False)

    # ---------------- pole (cut-out photo) ----------------
    L = sc.add('A_pole', pole_photo, 228, 410, crop=False)
    L.span(16, 73).flashes([(16, (255, 255, 255)), (18, (90, 108, 240)), (20, None)])
    sc.add('A_pole_top', pole_photo, 218, 432, 'top', crop=False).span(74).set(pano=False)

    # ---------------- text / bracket ----------------
    L = sc.add('A_farewell', text_asset, 0, 0, 'Farewell', 'Josefin Sans|Thin Italic', 82, (12, 12, 12), rot=78.0)
    L.x, L.y = 492 - L.ww / 2, -27 - L.wh / 2
    L.pivot = (492, -27)
    fk = [(27, 500), (28, 392), (29, 372), (30, 355), (31, 340), (32, 325), (33, 316), (34, 308), (35, 300), (36, 294), (37, 240), (38, 191),
          (39, 189), (40, 187), (41, 164), (48, 110), (54, 60), (56, 34), (58, -24), (60, -27), (64, -60), (74, -290)]
    L.span(27).key('position', [(f, [492, y_], LIN) for f, y_ in fk])
    L = sc.addc('A_bracket', bracket_a)
    L.span(28).fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': [(28, 30.0, LIN), (29, 19.4, LIN), (31, 11.7, LIN), (33, 10.6, LIN), (36, 5.6, LIN), (40, 0.0, LIN)],
                                         'ADBE Linear Wipe-0002': 180.0, 'ADBE Linear Wipe-0003': 0.0})

    # ---------------- sunset photo: a squashed strip that unfolds in steps (22-28), blue bar riding its lower edge ----------------
    L = sc.add('A_sunset', sunset_photo, 647, 500, pivot=(647, 500), crop=False)
    L.span(22, 64).set(pano=False)
    L.key('position', [(22, [736, 473], HOLD), (24, [666, 474], HOLD), (25, [666, 477], HOLD), (26, [656, 479], HOLD), (27, [654, 472], HOLD),
                       (28, [647, 489], HOLD), (30, [647, 500], HOLD)])
    L.key('scale', [(22, [106, 5], HOLD), (23, [106, 11], HOLD), (24, [147, 22], HOLD), (25, [148, 50], HOLD), (26, [155, 75], HOLD),
                    (27, [110, 88], HOLD), (28, [100, 100], HOLD)])
    L.fx('ADBE Wave Warp', **{'ADBE Wave Warp-0001': 2, 'ADBE Wave Warp-0002': [(22, 0.0, HOLD), (25, 14.0, HOLD), (26, 18.0, HOLD), (27, 10.0, HOLD), (28, 0.0, HOLD)],
                              'ADBE Wave Warp-0003': 46.0, 'ADBE Wave Warp-0004': 0.0, 'ADBE Wave Warp-0005': 0.0})
    # 57-63: eaten from the top down at 21.7 world px per frame (the city strip at the bottom goes last)
    L.fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': [(22, 0.0, HOLD), (57, 13.0, HOLD), (58, 26.0, HOLD), (59, 38.7, HOLD), (60, 51.6, HOLD),
                                                          (61, 63.8, HOLD), (62, 75.8, HOLD), (63, 89.3, HOLD)],
                                'ADBE Linear Wipe-0002': 180.0, 'ADBE Linear Wipe-0003': 0.0})
    L = sc.add('A_bluebar', solid_rect, 742, 471, 173, 20, (80, 120, 245), pivot=(742, 471))
    L.span(22, 30).set(pano=False).key('position', [(22, [742, 471], HOLD), (23, [743, 490], HOLD), (24, [741, 513], HOLD), (25, [747, 538], HOLD),
                                                    (26, [745, 548], HOLD), (27, [745, 557], HOLD), (28, [745, 582], HOLD), (29, [745, 617], HOLD)])

    # ---------------- houses: behind the ring group; the tube, the pins and the ruler pass in front ----------------
    L = sc.add('A_buildings', buildings, 852, 419)
    L.span(37).flash(37, PK, 2)

    # ---------------- ring group (stepped on the 6-frame grid, measured from the source) ----------------
    # blue sector: inner strip first (57-59), full radial width from 60, snaps at 65 then drifts home
    L = sc.add('A_ring_blue_in', ring_sector, RC[0] - 278, RC[1] - 278, 197.0, 276.0, 42.0, 90.0, BL, pivot=RC)
    L.span(57, 60).set(pano=False).key('rotation', [(57, 46.0, HOLD), (58, 37.0, HOLD), (59, 31.0, HOLD)])
    L = sc.add('A_ring_blue', ring_sector, RC[0] - 427, RC[1] - 427, 197.0, 425.0, 42.0, 90.0, BL, pivot=RC)
    L.span(60).key('rotation', [(60, 27.0, LIN), (64, 16.0, HOLD), (65, 13.0, LIN), (69, 10.0, LIN), (75, 3.0, LIN)])
    L.static['rotation'] = 3.0

    # record: it rides the ring group - its centre orbits the ring centre at radius 298.5 (tracked on the blue dot of the label),
    # easing from 51 deg below its resting place to rest on 87.  51-56 it is only seen through a wedge that opens upwards from
    # (975, 862); the wedge is a 'both ways' radial wipe expressed in the layer's own (turned) space.
    L = sc.add('A_vinyl', vinyl, VIN_C[0] - VIN_R - 2, VIN_C[1] - VIN_R - 2, pivot=RC, crop=False)
    vrot = {51: 51.1, 57: 32.8, 58: 30.3, 59: 27.0, 60: 22.6, 61: 18.2, 62: 16.7, 63: 14.6, 64: 13.3, 65: 11.9, 66: 10.6, 67: 9.5, 68: 8.5,
            69: 7.55, 70: 6.75, 71: 5.95, 72: 5.3, 73: 4.6, 74: 3.9, 75: 3.35, 76: 2.8, 77: 2.5, 78: 2.15, 79: 1.7, 80: 1.5, 81: 1.05,
            82: 0.9, 83: 0.7, 84: 0.5, 86: 0.2, 87: 0.0}
    L.span(51).key('rotation', [(f, r_, HOLD) for f, r_ in sorted(vrot.items())])
    th_ = math.radians(-51.1)
    vx_, vy_ = 975.0 - RC[0], 862.0 - RC[1]
    apx, apy = RC[0] + vx_ * math.cos(th_) - vy_ * math.sin(th_), RC[1] + vx_ * math.sin(th_) + vy_ * math.cos(th_)
    # the wedge (half angle 25 -> 37 deg) stays attached to the record while it turns and only opens up on 60-62
    L.fx('ADBE Radial Wipe', **{'ADBE Radial Wipe-0001': [(51, 100.0 * (1 - 25 / 180.0), HOLD), (52, 100.0 * (1 - 30 / 180.0), HOLD),
                                                          (53, 100.0 * (1 - 34 / 180.0), HOLD), (54, 100.0 * (1 - 37 / 180.0), HOLD),
                                                          (60, 100.0 * (1 - 60 / 180.0), HOLD), (61, 100.0 * (1 - 110 / 180.0), HOLD), (62, 0.0, HOLD)],
                                'ADBE Radial Wipe-0002': 180.0 - 51.1, 'ADBE Radial Wipe-0003': [(apx - L.x) * K, (apy - L.y) * K],
                                'ADBE Radial Wipe-0004': 3})
    # 51-56: nothing of it shows above the ruler (a half-plane through the pivot = a 180 deg radial wipe around the ring centre)
    L.fx('ADBE Radial Wipe', **{'ADBE Radial Wipe-0001': [(51, 50.0, HOLD), (57, 0.0, HOLD)], 'ADBE Radial Wipe-0002': 270.0 - 51.1,
                                'ADBE Radial Wipe-0003': [(RC[0] - L.x) * K, (RC[1] - L.y) * K], 'ADBE Radial Wipe-0004': 1})
    # On the source nothing of the record shows right of world x = 1119 (a fixed vertical edge while the record turns): a linear
    # wipe whose direction is counter-rotated with the layer; completion = share of the layer's extent along that direction.
    XE = 1119.0
    wa, wc = [], []
    for f_, r_ in sorted(vrot.items()):
        rr_ = math.radians(r_)
        d_ = (-math.cos(rr_), math.sin(rr_))
        cs_ = [d_[0] * cx_ + d_[1] * cy_ for cx_, cy_ in ((0.0, 0.0), (L.ww, 0.0), (0.0, L.wh), (L.ww, L.wh))]
        se_ = -(XE - RC[0]) + d_[0] * (RC[0] - L.x) + d_[1] * (RC[1] - L.y)
        wc.append((f_, max(0.0, min(100.0, 100.0 * (se_ - min(cs_)) / (max(cs_) - min(cs_)))), HOLD))
        wa.append((f_, -90.0 - r_, HOLD))
    L.fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': wc, 'ADBE Linear Wipe-0002': wa, 'ADBE Linear Wipe-0003': 0.0})

    # white paper inside the ring: below the ruler (inside the grey ring) and above it (radius 197 around the ring centre)
    sc.add('A_inner_low', inner_low, CRES_C[0] - CRES_R0 - 4, CRES_C[1] - 2, crop=False).span(51)
    sc.add('A_ring_inner', ring_inner, 500, 340).span(57)

    # grey ring: a half ring with a light head that is turned out from under the ruler in steps (swept angle per frame);
    # the piece that arrives on 40 is white for that frame; from 59 the head darkens (a black copy underneath shows through)
    cres = {34: 60, 35: 75, 36: 65, 40: 100, 41: 105, 42: 115, 43: 125, 47: 145, 51: 180}
    ks = sorted(cres.items())
    for nm, mode in (('A_cres_blk', 1), ('A_crescent', 0)):
        L = sc.add(nm, crescent, CRES_C[0] - CRES_R1 - 2, CRES_C[1] - CRES_R1 - 2, mode, pivot=CRES_C, crop=False)
        L.span(34 if mode == 0 else 37).key('rotation', [(f, 180.0 - s_, HOLD) for f, s_ in ks])
        L.fx('ADBE Radial Wipe', **{'ADBE Radial Wipe-0001': [(f, 100.0 * (1 - s_ / 360.0), HOLD) for f, s_ in ks],
                                    'ADBE Radial Wipe-0002': [(f, 90.0 + s_, HOLD) for f, s_ in ks],
                                    'ADBE Radial Wipe-0003': [(CRES_C[0] - L.x) * K, (CRES_C[1] - L.y) * K], 'ADBE Radial Wipe-0004': 1})
    L.flashes([(34, (255, 255, 255)), (35, (118, 118, 118)), (36, (190, 190, 190)), (37, None)])
    L.key('opacity', [(34, 100.0, HOLD), (59, 100.0, LIN), (60, 56.0, LIN), (64, 50.0, LIN), (66, 38.0, LIN), (70, 32.0, LIN), (76, 28.0, LIN),
                      (88, 10.0, LIN)])
    L = sc.add('A_cres_flash', ring_sector, CRES_C[0] - CRES_R1 - 2, CRES_C[1] - CRES_R1 - 2, CRES_R0, CRES_R1, 245.0, 280.0, (255, 255, 255),
               pivot=CRES_C, crop=False)
    L.span(40, 41).set(pano=False)
    sc.add('A_curl', curl, 819, 672).span(25)
    sc.addc('A_road', road).span(27).flash(27, (0, 0, 0), 1)

    # pink sector: a quarter ring wiped in from 0 deg (51-59: leading edge 4, 7, 12, 20, 54, 73, 79, 85, 91 deg), then it steps round
    L = sc.add('A_pink_sliver', ring_sector, RC[0] - 431, RC[1] - 431, 278.5, 429.0, 0.0, 25.0, PK, pivot=RC)
    L.span(51, 55).set(pano=False).fx('ADBE Radial Wipe', **{
        'ADBE Radial Wipe-0001': [(f, (25.0 - w) / 3.6, HOLD) for f, w in ((51, 4), (52, 7), (53, 12), (54, 20))],
        'ADBE Radial Wipe-0002': 65.0, 'ADBE Radial Wipe-0003': [(RC[0] - L.x) * K, (RC[1] - L.y) * K], 'ADBE Radial Wipe-0004': 1})
    L = sc.add('A_ring_pink', ring_sector, RC[0] - 431, RC[1] - 431, 278.5, 429.0, 90.0, 180.0, PK, pivot=RC)
    L.span(55).key('rotation', [(55, 90.0, HOLD), (60, 40.0, LIN), (64, 36.0, HOLD), (65, 6.0, LIN), (70, 0.0, LIN)])
    L.fx('ADBE Radial Wipe', **{
        'ADBE Radial Wipe-0001': [(f, 100.0 * (1 - w / 360.0), HOLD) for f, w in ((55, 54), (56, 73), (57, 79), (58, 85), (59, 90))] + [(60, 0.0, HOLD)],
        'ADBE Radial Wipe-0002': 0.0, 'ADBE Radial Wipe-0003': [(RC[0] - L.x) * K, (RC[1] - L.y) * K], 'ADBE Radial Wipe-0004': 1})

    # wire horn: one sprite per frame while it tumbles (30-73), then the resting pose
    hv = horn.version()
    for f in range(horn.F0, horn.F1):
        L = sc.add('A_horn_%02d' % f, horn_sprite, horn.HW[0], horn.HW[1], f, hv, k=horn.HK)
        L.span(f, f + 1).set(pano=False)
    # Resting pose.  On the far shots (zoom 0.47) the source keeps its strings about a pixel wide, so the bundle reads much
    # denser there: a heavier sprite on 74-83 and 86-97, the fine one on the close shots (84-85, 98+).
    thin = sc.add('A_horn_end', horn_sprite, horn.HW[0], horn.HW[1], horn.F1, hv, k=horn.HK)
    thin.span(98)
    sc.clone('A_horn_end84', thin).span(84, 86).set(pano=False)
    far = sc.add('A_horn_far', horn_sprite, horn.HW[0], horn.HW[1], horn.F1, hv, 1.3, 100, 58.0, 0.74, k=horn.HK)
    far.span(horn.F1, 84).set(pano=False)
    sc.clone('A_horn_far2', far).span(86, 98).set(pano=False)

    L = sc.addc('A_wires', wires)
    L.span(16).flashes([(16, (255, 255, 255)), (18, (90, 108, 240)), (20, None)])

    # ---------------- pins / thin lines ----------------
    for (nm, x_, y_, lab, f0) in (('A_pin1', 655, 447, '2026', 22), ('A_pin2', 1112, 528, None, 31), ('A_pin3', 850, 672, None, 37)):
        L = sc.addc(nm, pin_icon, lab)
        L.x += x_
        L.y += y_
        L.pivot = (x_, y_)
        L.span(f0).pop(f0, 3, 0.2, over=1.25)
    sc.addc('A_lines', lines_a).span(30).wipe(30, 5, angle=-90)
    sc.addc('A_2030', label_2030).span(37)

    # ---------------- transient markers of frames 15-39 ----------------
    L = sc.add('A_pinko0', circle_outline, 621.5 - 33, 544 - 33, 24.5, 13.0, PK, pivot=(621.5, 544), crop=False)
    L.span(15, 16).set(pano=False)                                   # frame 15: small but already thick
    L = sc.add('A_pinko', circle_outline, 621 - 80.5, 543 - 80.5, 72.0, 13.0, PK, pivot=(621, 543), crop=False)
    L.span(16, 40).set(pano=False).key('position', [(16, [621, 543], HOLD), (28, [620, 751], HOLD)]).fx(
        'ADBE Radial Wipe', **{'ADBE Radial Wipe-0001': [(34, 0.0, LIN), (40, 100.0, LIN)], 'ADBE Radial Wipe-0002': 0.0,
                               'ADBE Radial Wipe-0004': 1})
    L = sc.add('A_navy', ball, 692 - 33, 608 - 33, 31.0, crop=False)
    L.span(16, 34).set(pano=False).pop(16, 2, 0.3)
    L = sc.add('A_pinkbar', solid_rect, 435, 638, 209, 39, PK, pivot=(435, 657))
    L.span(16, 27).set(pano=False).key('scale', [(16, [10.5, 100], HOLD), (17, [50, 100], HOLD), (18, [92, 100], HOLD), (19, [100, 100], HOLD),
                                                  (25, [114, 104], HOLD)])
    sc.addc('A_zig', zigzag).span(27, 28).set(pano=False)
    L = sc.add('A_blackbar', solid_rect, 574, 459, 150, 8, (10, 10, 10))
    L.span(16, 26).set(pano=False).key('position', [(16, [649, 463], HOLD), (25, [401, 463], HOLD)]).key(
        'scale', [(16, [100, 100], HOLD), (25, [133, 100], HOLD)])
    L = sc.add('A_graybar', hgrad_rect, 724, 459, 150, 8, (150, 150, 150), (250, 250, 250), hl=False, pivot=(724, 463))
    L.span(16, 26).set(pano=False).key('position', [(16, [724, 463], HOLD), (25, [501, 463], HOLD)]).key(
        'scale', [(16, [20, 100], HOLD), (17, [55, 100], HOLD), (18, [85, 100], HOLD), (20, [97, 100], HOLD), (23, [110, 100], HOLD), (25, [136, 100], HOLD)])

    # ---------------- blue bar on the ruler + icon row ----------------
    sc.addc('A_icons', icons_a).span(9)

    # ---------------- quote card + stopwatch ----------------
    cpath = [(5, s2w(5, 1362, 510)), (7, s2w(7, 1332, 525)), (9, s2w(9, 1285, 565)), (12, s2w(12, 1105, 600)),
             (14, s2w(14, 981, 669)), (15, s2w(15, 885, 776))]
    ck = [(f, [p[0], p[1]], LIN) for f, p in cpath]
    ck[-1] = (15, ck[-1][1], HOLD)
    ck.append((16, [CARD_C[0], CARD_C[1]], HOLD))
    sk = [(5, [220, 220], HOLD), (16, [100, 100], HOLD)]
    for nm, fn, f0 in (('A_quotes', quotes, 5), ('A_card', card, 6), ('A_watch', watch, 7)):
        L = sc.addc(nm, fn, pivot=CARD_C)
        L.span(f0).key('position', ck).key('scale', sk)
    sc.get('A_watch').flashes([(7, (44, 0, 92)), (9, None)])           # flat dark-violet silhouette first

    # ---------------- opening shapes ----------------
    R = S0.px(197)
    p0 = s2w(0, 463, 328)
    L = sc.add('A_sphere', S0.sphere, p0[0] - R - 2, p0[1] - R - 2, R, pivot=p0, crop=False)
    L.span(0, 3).set(pano=False).key('rotation', [(0, 0.0, HOLD), (2, 80.0, HOLD)])
    pin(L, [(0, 463, 328), (2, 463, 328)])
    # 3-7: black core with a white glow, the lower-right half under a grey half disc whose diagonal tilts a little each frame;
    # (core radius px, diagonal angle, rim darkness, screen centre) fitted to the outline of the source
    R2 = S0.px(198)
    for f_, (rc_, al_, dk_, sx_, sy_) in {3: (146, 47, 0.25, 452.0, 327.5), 4: (134, 32, 1.0, 448.5, 327.5), 5: (131, 38, 1.0, 444.5, 327.5),
                                          6: (128, 46, 1.0, 442.5, 328.0), 7: (129, 42, 1.0, 445.5, 328.0)}.items():
        pw = s2w(f_, sx_, sy_)
        L = sc.add('A_donut%d' % f_, S0.donut2, pw[0] - R2 - 2, pw[1] - R2 - 2, R2, S0.px(rc_), al_, dk_, crop=False)
        L.span(f_, f_ + 1).set(pano=False)
    # 8-15: the two-tone ball again, small, spinning clockwise by one turn (light-side direction measured per frame)
    L = sc.add('A_ball', S0.sphere, p0[0] - R - 2, p0[1] - R - 2, R, pivot=p0, crop=False)
    L.span(8, 16).set(pano=False)
    pin(L, [(8, 433.5, 328), (9, 430, 328), (10, 426, 328), (11, 424, 328), (12, 424.5, 327), (13, 507, 358), (14, 596.5, 384), (15, 812, 415.5)],
        [(8, 0.419), (9, 0.218), (10, 0.198), (11, 0.188), (12, 0.188), (13, 0.16), (14, 0.132), (15, 0.117)])
    L.key('rotation', [(f_, r_, HOLD) for f_, r_ in ((8, 120.2), (9, 132.5), (10, 174.6), (11, 259.4), (12, 367.3), (13, 450.1), (14, 503.6), (15, 522.4))])
    kb = sc.add('A_kaishi', kaishi_big, 0, 0)
    pk_ = s2w(0, 1150, 160)
    kb.x, kb.y = pk_[0] - kb.ww / 2, pk_[1] - kb.wh / 2
    kb.pivot = pk_
    kb.span(0, 1).set(pano=False, scale=[140, 46])                    # frame 0: squashed flat and wide

    # small labels around the sphere (1-6): white while the field is black
    for nm, txt, fnt_, size, sx_, path in (('A_lab_start', 'START', 'timesbd.ttf', 10.5, 1.0, [(1, 306, 133), (2, 303, 135), (3, 299, 164), (4, 296, 164)]),
                                           ('A_lab_kaishi', '开始', 'simsun.ttc', 9.5, 2.2, [(1, 716, 160), (3, 710, 162), (4, 708, 290), (5, 702, 316), (6, 700, 334)])):
        L = sc.add(nm, text_asset, 0, 0, txt, fnt_, size, (20, 20, 20), sx=sx_)
        pw = s2w(path[0][0], path[0][1], path[0][2])
        L.x, L.y = pw[0] - L.ww / 2, pw[1] - L.wh / 2
        L.pivot = pw
        L.span(1, path[-1][0] + 1).set(pano=False).flashes([(1, (255, 255, 255)), (2, None)])
        pin(L, path)
    # tiny pixel-font captions that flash for one frame each
    for nm, txt, f_, sx_, sy_, size, col in (('A_set0', 'set 0', 3, 276, 511, 9.4, (60, 132, 132)), ('A_set1', 'set 1', 7, 964, 612, 8.2, (52, 52, 54))):
        L = sc.add(nm, text_asset, 0, 0, txt, 'Press Start 2P|Regular', size, col, tracking=-0.4)
        pw = s2w(f_, sx_, sy_)
        L.x, L.y = pw[0] - L.ww / 2, pw[1] - L.wh / 2
        L.pivot = pw
        L.span(f_, f_ + 1).set(pano=False)
    # small grey gradient tab (4-15): a stub on 4, full length from 6; it jumps to the right on 8
    L = sc.add('A_gradtab', hgrad_rect, 0, 0, 60.5, 17.3, (40, 40, 40), (232, 232, 232), hl=False)
    pw = s2w(5, 518.5, 592)
    L.x, L.y = pw[0] - L.ww / 2, pw[1] - L.wh / 2
    L.pivot = pw
    L.span(4, 16).set(pano=False)
    pin(L, [(4, 571, 592), (5, 518.5, 592), (6, 534, 592), (7, 528, 592), (8, 848, 593), (10, 838, 593), (12, 828, 590), (14, 860, 582), (15, 880, 558)])
    L.key('scale', [(4, [34, 100], HOLD), (5, [76, 100], HOLD), (6, [100, 100], HOLD), (14, [96, 96], HOLD), (15, [91, 91], HOLD)])
    # '2025'
    L = sc.add('A_2025', text_asset, 0, 0, '2025', 'Montserrat-Medium.ttf', 7.5, (20, 20, 20))
    pw = s2w(5, 613, 746)
    L.x, L.y = pw[0] - L.ww / 2, pw[1] - L.wh / 2
    L.pivot = pw
    L.span(5, 27).set(pano=False)
    pin(L, [(5, 613, 746), (9, 600, 746), (12, 587, 746), (13, 600, 740)])
    L.key('position', [(16, [474, 613], LIN), (20, [483, 615], LIN)])
    # round gauge / stamp (5-25)
    L = sc.addc('A_stamp', stamp, pivot=(0, 0))
    L.span(4, 26).set(pano=False)
    pin(L, [(4, 236, 230), (5, 253.6, 229.6), (6, 257.6, 229.6), (7, 268.4, 232), (8, 281, 232), (9, 588, 228), (10, 582, 231.6), (12, 576, 228),
            (14, 684, 312), (15, 738, 365)],
        [(4, 0.78), (5, 0.86), (6, 1.0), (12, 1.0), (14, 0.727), (15, 0.576)])
    L.key('position', [(18, [475.5, 425.0], LIN), (22, [486.0, 426.0], LIN), (23, [483.4, 424.0], LIN), (24, [439.0, 409.0], LIN), (25, [164.0, 386.0], LIN)])
    # it arrives as a horizontal smear: a flat wide copy on 3, a stretched tail behind it on 4
    for nm, f_, sx_, (kx, ky) in (('A_stamp_in', 3, 104, (260.0, 62.0)), ('A_stamp_tail', 4, 74, (300.0, 76.0))):
        t_ = sc.clone(nm, L)
        t_.pivot = (0, 0)
        pw = s2w(f_, sx_, 230)
        t_.x += pw[0]
        t_.y += pw[1]
        t_.pivot = pw
        t_.span(f_, f_ + 1).set(pano=False, scale=[kx, ky])

    L = sc.addc('A_tripod', S0.tripod, pivot=(0, 0))
    L.span(1, 14).set(pano=False)
    pin(L, [(1, 965, 872), (3, 965, 868), (5, 965, 850), (7, 965, 755), (12, 965, 735), (13, 965, 735)])
    tri = sc.addc('A_tri', S0.tri_down, S0.px(274), S0.px(342), pivot=(0, S0.px(342) / 2))
    tri.span(4, 26).set(pano=False)
    pin(tri, [(4, 620, 445), (5, 616, 504), (6, 613, 528), (8, 607, 528), (10, 598, 533), (12, 605, 527), (14, 691, 498), (15, 741, 510), (16, 735, 499)],
        [(4, 1.0), (12, 1.0), (14, 0.655), (15, 0.52), (16, 0.52)])
    tri.key('position', [(23, list(s2w(16, 735, 499)), HOLD), (24, [430.0, 512.0], HOLD), (25, [153.0, 517.0], HOLD)])
    t2 = sc.clone('A_tri2', tri)                                     # second triangle below the ruler (13-25)
    t2.pivot = (tri.x + tri.ww / 2, tri.y + tri.wh / 2)
    s_tri = 0.52 * zoom(4) / zoom(16) * 100.0
    t2.span(13, 26).set(pano=False, scale=[s_tri, s_tri]).key('position', [(13, [437.7, 682.0], LIN), (16, [472.0, 660.0], LIN), (20, [483.0, 661.0], LIN),
                                                                          (23, [476.0, 667.0], HOLD), (24, [415.0, 686.0], HOLD), (25, [153.0, 713.0], HOLD)])
    for i, path in enumerate(([(1, 385, 465), (3, 405, 445), (5, 440, 450), (7, 460, 480)],
                              [(1, 432, 565), (3, 478, 558), (5, 450, 595), (7, 400, 612), (8, 400, 612)],
                              [(3, 360, 548), (5, 330, 530), (7, 325, 495), (10, 315, 495)])):
        L = sc.addc('A_marker%d' % i, S0.marker, pivot=(0, 0))
        L.span(path[0][0], path[-1][0] + 1).set(pano=False)
        pin(L, path)
        if path[0][0] == 1:
            L.flashes([(1, (255, 255, 255)), (2, None)])
    # thick black arc right of the sphere (circle centre (896,135) px, radius 338 px): its lower end retracts frame by frame;
    # it runs over the triangle
    for f_, (a0_, a1_) in {4: (87.7, 169.6), 5: (117.1, 175.2), 6: (139.7, 180.0), 7: (154.1, 180.0), 8: (167.0, 180.0)}.items():
        L = sc.addc('A_arc%d' % f_, S0.black_arc, a0_, a1_, S0.px(338), S0.px(27), pivot=(0, 0))
        pw = s2w(f_, 896, 135)
        L.x += pw[0]
        L.y += pw[1]
        L.span(f_, f_ + 1).set(pano=False)
    # thick black line above the ruler (1-5): its right end retracts; drawn over the sphere and the triangle
    L = sc.add('A_blackline', solid_rect, 222, 500.8, 707, 4.9, (16, 16, 16), pivot=(222, 503.25))
    L.span(1, 6).set(pano=False).key('position', [(1, [222, 503.25], HOLD), (2, [157, 503.25], HOLD), (3, [135, 503.25], HOLD), (4, [127.8, 503.25], HOLD),
                                                  (5, [125, 503.25], HOLD)]).key(
        'scale', [(1, [94.5, 100], HOLD), (2, [100, 100], HOLD), (3, [95.5, 100], HOLD), (4, [83.1, 100], HOLD), (5, [54.2, 100], HOLD)])
    L.flashes([(1, (70, 70, 70)), (2, None)])
    # blue / cyan / navy bar on the ruler (world x 194.2 .. 425.5, y 508 .. 512.9; the blue part grows on 2-4) and the red stub
    L = sc.add('A_bar_b1', solid_rect, 194.2, 508.0, 118.3, 4.9, (0, 0, 224), pivot=(194.2, 510.45))
    L.span(2).key('scale', [(2, [83.6, 100], HOLD), (3, [95.4, 100], HOLD), (4, [100, 100], HOLD)])
    sc.add('A_bar_b2', solid_rect, 312.5, 508.0, 65.5, 4.9, (125, 224, 232)).span(4)
    sc.add('A_bar_b3', solid_rect, 378.0, 508.0, 47.5, 4.9, (12, 12, 60)).span(6)
    sc.add('A_redbar', solid_rect, 100, 508.0, 28, 4.9, (222, 20, 60)).span(9)

    # ---------------- tube / houses / hill ----------------
    # the rope grows along its own length: the tangle first (uncovered towards the left, 29-36), then the tail runs out to the
    # right (40-46); a blue cap rides on the growing end until the cap of the picture itself is uncovered
    L = sc.add('A_tube', tube, 971, 541)
    L.span(29, 104).set(pano=False)
    _two_wipes(L, 971.0, 515.0, [(29, 1140), (30, 1136), (32, 1212), (38, 1218), (40, 1250), (42, 1320), (44, 1400), (45, 1445), (46, 1486)],
               [(29, 1120), (30, 1055), (32, 1048), (34, 1000), (36, 962), (37, 971)])
    L = sc.add('A_tubecap', hgrad_rect, 1050, 627, 28, 15, (24, 40, 236), (60, 96, 250), hl=False)
    L.span(30, 46).set(pano=False)
    L.key('position', [(f, [float(x_), float(y_)], HOLD) for f, x_, y_ in ((30, 1065, 635), (31, 1110, 650), (32, 1150, 665), (33, 1080, 660),
                                                                           (34, 1020, 650), (35, 1090, 655), (36, 1172, 655), (37, 1210, 690),
                                                                           (38, 1150, 740), (40, 1139, 720), (42, 1305, 716), (44, 1388, 727),
                                                                           (45, 1432, 731))])
    # crimson bar (39-47): 847 -> 1238, head first, the tail follows it out
    L = sc.add('A_crimson', vgrad_rect, 847, 502, 392, 18, (226, 22, 92), (120, 8, 48))
    L.span(39, 48).set(pano=False)
    _two_wipes(L, 847.0, 392.0, [(39, 1124), (40, 1172), (41, 1195), (42, 1209), (43, 1218), (44, 1224), (45, 1229), (46, 1232), (47, 1238)],
               [(39, 847), (44, 925), (45, 1030), (46, 1133), (47, 1234)])
    return sc
