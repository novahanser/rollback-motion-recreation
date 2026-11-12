"""Reusable shape generators (gradient sphere, holographic disc, tripod, markers ...)."""
import math
import numpy as np
from lib import *
from gen_util import s2w, pin, pin_keys, zoom

K = 2
SI = 1.852                       # intro zoom
HOLO_C = (378.0, 393.0)          # where the holographic disc settles (frames 16-23)
HOLO_R = 320.0
CARD_C = (64.0, 539.0)           # final centre of the quote/stopwatch card


def px(v):
    return v / SI


# ----------------------------------------------------------------------------- assets
def sphere(R, k=K, tilt=16.0):
    size = int(2 * R * k) + 8
    c = size / 2.0
    x, y = grid(size, size)
    ph = math.radians(tilt)
    t = ((y - c) * math.cos(ph) - (x - c) * math.sin(ph)) / (R * k)      # -1 .. 1 across the split line
    top = lerp_color((238, 238, 238), (140, 140, 140), np.clip(-t, 0, 1))
    bot = lerp_color((4, 4, 4), (74, 74, 74), np.clip(t, 0, 1))
    rgb = np.where((t < 0)[..., None], top, bot)
    d = np.hypot(x - c, y - c)
    a = cov(d - R * k)
    edge = cov(np.abs(d - R * k + 1.0) - 1.0)
    rgb = rgb * (1 - edge[..., None]) + np.array((30, 30, 30), np.float32) * edge[..., None]
    return from_arr(rgb, a)


def donut(R, k=K):
    """the sphere's second state: gradient ring, black core, diagonal grey band, black arc on the right"""
    size = int(2.9 * R * k)
    c = (size * 0.40, size / 2.0)
    x, y = grid(size, size)
    d = np.hypot(x - c[0], y - c[1]) / (R * k)
    a_ang = ang(x, y, c[0], c[1])
    ring_t = 0.5 + 0.5 * np.cos(np.radians(a_ang - 135.0))
    rgb = lerp_color((250, 250, 250), (40, 40, 40), ring_t)
    a = cov((d - 1.0) * R * k)
    core = cov((d - 0.72) * R * k)
    rgb = rgb * (1 - core[..., None])
    # diagonal band
    ph = math.radians(-42.0)
    t = ((y - c[1]) * math.cos(ph) - (x - c[0]) * math.sin(ph)) / (R * k)
    band = cov((np.abs(t - 0.30) - 0.26) * R * k) * a
    bandcol = lerp_color((120, 120, 120), (205, 205, 205), np.clip((x - c[0]) / (R * k) * 0.5 + 0.5, 0, 1))
    rgb = rgb * (1 - band[..., None]) + bandcol * band[..., None]
    img = from_arr(rgb, a)
    # black arc to the right
    cv = Image.new('RGBA', (size * 2, size * 2), (0, 0, 0, 0))
    dr = ImageDraw.Draw(cv)
    cc = (c[0] * 2 - 0.45 * R * k * 2, c[1] * 2 - 0.2 * R * k * 2)
    rr = 1.75 * R * k * 2
    dr.arc([cc[0] - rr, cc[1] - rr, cc[0] + rr, cc[1] + rr], start=-38, end=22, fill=(0, 0, 0, 255), width=int(0.16 * R * k * 2))
    img.alpha_composite(cv.resize((size, size), Image.LANCZOS))
    return img


def donut2(R, rc, alpha, dark=1.0, k=K):
    """frames 3-7: black core (radius rc) with a white glow that falls off to a dark rim, and a flat grey half disc covering
    everything below the diagonal through the centre (the diagonal rises to the right at `alpha` degrees).
    dark < 1 keeps the rim light (frame 3)."""
    size = int(2 * R * k) + 8
    c = size / 2.0
    x, y = grid(size, size)
    d = np.hypot(x - c, y - c) / k
    phi = np.degrees(np.arctan2(y - c, x - c))                       # 0 = right, 90 = down
    t = np.clip((d - rc) / float(R - rc), 0, 1)
    edge = np.clip(12.0 + 290.0 * (0.5 - 0.5 * np.cos(np.radians(phi + 105.0))), 0, 236)      # darkest up / upper left
    edge = 216.0 + (edge - 216.0) * dark
    v = 252.0 - (252.0 - edge) * t ** 0.75
    core = cov((d - rc) * k)
    v = v * (1 - core) + 6.0 * core
    rgb = np.dstack([v, v, v])
    al = math.radians(alpha)
    s = ((x - c) * math.sin(al) + (y - c) * math.cos(al)) / k         # > 0 on the lower-right side of the diagonal
    half = cov(-s * k)
    g = 206.0 - 72.0 * np.clip((x - c) / (R * k) * 0.5 + 0.5, 0, 1)
    rgb = rgb * (1 - half[..., None]) + np.dstack([g, g, g]) * half[..., None]
    line = cov((np.abs(s) - 0.45) * k)[..., None] * 0.8
    rgb = rgb * (1 - line) + 34.0 * line
    a = cov((d - R) * k)
    rim = cov((np.abs(d - R + 0.6) - 0.6) * k)[..., None]
    rgb = rgb * (1 - rim) + 34.0 * rim
    return from_arr(rgb, a)


def black_arc(a0, a1, r, w, k=K):
    """thick black arc piece: angles in degrees clockwise from 'right' (90 = down, 180 = left), centre (0, 0)"""
    c = Canvas(-r - w, -r - w, r + w, r + w, k=k, ss=3)
    n = max(8, int(abs(a1 - a0) / 1.5))
    outer = [((r + w / 2.0) * math.cos(math.radians(a0 + (a1 - a0) * i / n)), (r + w / 2.0) * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    inner = [((r - w / 2.0) * math.cos(math.radians(a0 + (a1 - a0) * i / n)), (r - w / 2.0) * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    c.poly(outer + inner[::-1], (12, 12, 12, 255))
    return c


def holo_disc(R, k=K, seed=3, rim=True, sat=1.0):
    size = int(2 * R * k) + 8
    c = size / 2.0
    x, y = grid(size, size)
    d = np.hypot(x - c, y - c) / k
    u = d / R
    a_ang = ang(x, y, c, c)
    stops = [(0.00, (246, 196, 240)), (0.12, (212, 204, 252)), (0.25, (168, 246, 226)), (0.38, (224, 252, 204)),
             (0.50, (252, 212, 228)), (0.63, (182, 238, 248)), (0.76, (236, 204, 252)), (0.88, (178, 248, 210)),
             (1.00, (246, 196, 240))]
    t = (a_ang / 360.0 + 0.07 * np.sin(u * 7.0) + 0.03 * np.sin(u * 19.0 + 1.3)) % 1.0
    rgb = grad_stops(t, stops)
    wc = np.clip(1.0 - u * 1.25, 0, 1)[..., None] * 0.45
    rgb = rgb * (1 - wc) + 255.0 * wc
    if rim:
        def bandw(u0, u1):
            return np.clip(np.minimum((u - u0) / 0.012, (u1 - u) / 0.012), 0, 1)[..., None]
        for (u0, u1, col, amt) in ((0.775, 0.84, (250, 250, 250), 0.85), (0.865, 0.915, (250, 198, 206), 0.75),
                                   (0.93, 0.965, (232, 248, 236), 0.8), (0.975, 1.0, (196, 238, 206), 0.9)):
            b = bandw(u0, u1) * amt
            rgb = rgb * (1 - b) + np.array(col, np.float32) * b
    if sat < 1.0:
        rgb = rgb * sat + np.array((236, 238, 238), np.float32) * (1 - sat)
    rgb = rgb + noise(size, size, seed, 2.5)[..., None]
    a = np.clip((R - d) * k / 2.5, 0, 1)
    return from_arr(rgb, a)


def halo_ring(R, k=K):
    """black -> white radial ring that flashes around the disc on frames 3-4"""
    R2 = R * 1.42
    size = int(2 * R2 * k) + 8
    c = size / 2.0
    x, y = grid(size, size)
    u = np.hypot(x - c, y - c) / k / R
    t = np.clip((u - 1.0) / 0.42, 0, 1)
    v = np.clip((t - 0.25) / 0.45, 0, 1) * 255.0
    a = np.clip((u - 0.98) / 0.02, 0, 1) * np.clip((1.42 - u) / 0.14, 0, 1)
    return from_arr(np.dstack([v, v, v]), a)


def white_disc(R, k=K):
    size = int(2.5 * R * k)
    c = size / 2.0
    x, y = grid(size, size)
    d = np.hypot(x - c, y - c) / k
    a = np.clip((R * 1.2 - d) / (R * 0.22), 0, 1) ** 1.6
    return from_arr((255, 255, 255), a)


def vignette():
    """frame-2 flash: black field with a white glow pushing in from the left edge only (screen space, 960x540 upscaled in AE)"""
    w, h = 960, 540
    x, y = grid(w, h)
    d = np.hypot((x - w * 0.66) / (w * 0.60), (y - h * 0.5) / (h * 1.5))
    v = np.clip((d - 0.60) / 0.28, 0, 1) * 255.0
    return from_arr(np.dstack([v, v, v]), np.ones((h, w), np.float32))


def rays(L=1150.0, k=1, cw=None):
    """thin lines from one centre; `cw` = angles in degrees clockwise from 'up' (default: the late set of frames 53+)"""
    c = Canvas(-L, -L, L, L, k=k, ss=3)
    for a in ((90, 37, 180, -68, -42, 120) if cw is None else [90.0 - v for v in cw]):
        r = math.radians(a)
        c.line([(0, 0), (L * math.cos(r), -L * math.sin(r))], (10, 10, 10, 255), 1.0)
    return c


def tripod():
    c = Canvas(-160, -8, 160, 100, k=K, ss=3)
    g1, g2 = (214, 214, 214, 255), (176, 176, 176, 255)
    c.line([(0, 4), (-150, 88)], g2, 9)
    c.line([(0, 4), (150, 88)], g2, 9)
    c.line([(0, 0), (0, 92)], g1, 9)
    c.rect(-151, -5, 151, 5, g1)
    return c


def tri_down(w, h, col=(176, 176, 176)):
    c = Canvas(-w / 2 - 2, -2, w / 2 + 2, h + 2, k=K, ss=3)
    c.poly([(-w / 2, 0), (w / 2, 0), (0, h)], rgba(col))
    return c


def marker(r=8.1, col=(0, 0, 0), w=6.3):
    c = Canvas(-r - w / 2 - 2, -r - w / 2 - 2, r + w / 2 + 2, r + w / 2 + 2, k=4, ss=3)
    c.circle(0, 0, r + w / 2.0, outline=rgba(col), width=w)          # r = centre line of the ring
    return c


def bar(w, h, col):
    return new(max(2, w * K), max(2, h * K), rgba(col))
