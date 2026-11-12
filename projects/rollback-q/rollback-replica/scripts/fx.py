"""Global / screen-space effects: invert + 1-bit flashes, grain, flip glitch, the ending (dark field, pink bands)."""
import math
import numpy as np
from lib import *

K = 2
N_BANDS = 10
BAND_H = 108


def pink_band(h=BAND_H):
    """one horizontal band of the ending: bright pink at the top fading to near black"""
    W_, H_ = 1920, h
    x, y = grid(W_, H_)
    rgb = grad_stops(y / H_, [(0.0, (236, 12, 110)), (0.45, (200, 10, 92)), (0.8, (96, 8, 44)), (1.0, (24, 8, 12))])
    return from_arr(rgb, np.ones((H_, W_), np.float32))


def dark_streaks(seed=3):
    """vertical 'pixel stretch' columns that eat the grey field on 260-263 (screen space, half resolution)"""
    rng = np.random.default_rng(seed)
    W_, H_ = 960, 540
    img = np.zeros((H_, W_, 4), np.float32)
    x = int(W_ * 0.40)
    while x < W_:
        wcol = int(rng.integers(5, 60))
        v = float(rng.integers(16, 100))
        top = int(H_ * (0.22 + 0.6 * rng.random()))
        img[top:, x:x + wcol, 0:3] = v
        img[top:, x:x + wcol, 3] = (0.55 + 0.4 * rng.random()) * 255
        x += wcol
    return Image.fromarray(img.astype(np.uint8), 'RGBA')


def white_chevron():
    c = Canvas(0, 0, 420, 520, k=1, ss=3)
    c.line([(60, 20), (60, 500)], (250, 250, 250, 255), 46)
    c.line([(380, 20), (90, 260), (380, 500)], (250, 250, 250, 255), 46)
    return c


def band_extent(i, f, f_on, rng):
    """[left, right] of band i on frame f: arrive from the right (<=263), fill (264-266), recede as a staircase (267+)"""
    if f <= 263:
        a = max(0.0, 1300.0 - (f - f_on) * 420.0 - rng.random() * 300.0)
        b = 1920.0
    elif f <= 266:
        a = 0.0 if rng.random() < 0.7 else float(rng.integers(1, 6)) * 180.0
        b = 1920.0 if rng.random() < 0.75 else 1920.0 - float(rng.integers(1, 5)) * 160.0
    else:
        k = f - 266
        b = min(1920.0, 700.0 + i * 135.0 + rng.random() * 220.0 - k * 60.0)
        a = max(0.0, (9 - i) * 150.0 * (k / 5.0) + rng.random() * 200.0 - 100.0) if i < 8 else 0.0
    if b - a < 80.0:
        b = min(1920.0, a + 80.0)
        a = b - 80.0
    return a, b


def gray_dot(r=55.0):
    n = int(2 * r + 6)
    x, y = grid(n, n)
    return from_arr((200, 200, 204), cov(np.hypot(x - n / 2.0, y - n / 2.0) - r))


def build_bands(sc):
    """pink gradient bands of the ending. They are glued to the screen but sit *inside* the world stack
    (above the title panel and the lens rings, below the film frames), so they get inverse-camera keys."""
    from gen_util import s2w, zoom
    sc.sec = 'FX'
    rng = np.random.default_rng(7)
    on = {0: 258, 1: 259, 2: 260, 3: 261, 4: 261, 5: 262, 6: 262, 7: 263, 8: 263, 9: 264}
    off = {0: 267, 1: 269, 2: 270, 3: 270, 4: 270, 5: 271, 6: 271, 7: 272, 8: 272, 9: 272}
    for i in range(N_BANDS):
        yc = i * BAND_H + BAND_H / 2.0
        L = sc.add('FX_band%d' % i, pink_band, 0, 0, k=1, crop=False, pivot=(0, BAND_H / 2.0))
        L.pano = False
        f0, f1 = on[i], off[i]
        ks_s, ks_p = [], []
        for f in range(f0, f1):
            a, b = band_extent(i, f, f0, rng)
            z = zoom(f)
            ks_s.append((f, [(b - a) / 1920.0 * 100.0 / z, 101.0 / z], HOLD))
            ks_p.append((f, list(s2w(f, a, yc)), HOLD))
        L.span(f0, f1).key('scale', ks_s).key('position', ks_p)
    return sc


def build(sc):
    sc.sec = 'FX'

    # ---------------- ending: the grey field sinks to near black (under the world layer) ----------------
    L = sc.solid('FX_black', (17, 13, 12))
    L.below = True
    L.span(256).key('opacity', [(256, 8, HOLD), (257, 14, HOLD), (258, 37, HOLD), (260, 52, HOLD), (261, 74, HOLD),
                                (262, 82, HOLD), (263, 90, HOLD), (264, 100, HOLD)])
    L = sc.add('FX_streaks', dark_streaks, 0, 0, k=0.5, screen=True, crop=False)
    L.below = True
    L.pano = False
    L.span(260, 264).key('opacity', [(260, 55, HOLD), (261, 75, HOLD), (262, 90, HOLD), (263, 70, HOLD)])

    # ---------------- screen-space layers above the world ----------------
    # global invert for the film run (205-225); digits / film strips are dark in the world so they come out light
    L = sc.adjust('FX_invert', 205, 226)
    L.fx('ADBE Invert')

    # two white 'K' chevrons that flash on frames 69-70 (left of centre, mirrored top / bottom)
    L = sc.addc('FX_chev1', white_chevron, screen=True)
    L.pano = False
    L.x, L.y = 415, -65
    L.pivot = (625, 195)
    L.span(69, 71).set(scale=[95, 62])
    L = sc.addc('FX_chev2', white_chevron, screen=True)
    L.pano = False
    L.x, L.y = 415, 660
    L.pivot = (625, 920)
    L.span(69, 71).set(scale=[95, -62])

    # grey bar that wipes down the frame at x 1125-1240 (86-93), shrinks to a square (94-96) and a dot (97)
    L = sc.solid('FX_graybar', (200, 200, 204), w=115, h=1080, x=1125, y=0)
    L.pivot = (1182.5, 0.0)
    bar = [(86, 0, 220), (87, 0, 400), (88, 0, 600), (89, 0, 880), (90, 0, 1080), (91, 120, 1080), (92, 320, 1080), (93, 640, 1080),
           (94, 948, 1048), (95, 860, 970)]
    L.span(86, 97).key('position', [(f, [1182.5, float(t)], HOLD) for f, t, b in bar]).key(
        'scale', [(f, [100.0, (b - t) / 1080.0 * 100.0], HOLD) for f, t, b in bar])
    L = sc.add('FX_graydot', gray_dot, 1176 - 58, 750 - 58, k=1, screen=True, crop=False)
    L.pano = False
    L.span(97, 98)

    # frame 96: plain luminance threshold over the pink field (pink / blue -> black, light things -> white).
    # NB: in this 16/32-bpc project the Threshold level runs 0..1
    L = sc.adjust('FX_thr96', 96, 97)
    L.fx('ADBE Threshold2', **{'ADBE Threshold2-0001': 0.53})
    # ... and the left 430 px smeared sideways (Transform effect: 12000 % wide around x = 430).
    # effect points of a non-comp-sized adjustment layer are remapped layer->comp, hence 430 * 430 / 1920
    L = sc.solid('FX_stretch96', (255, 255, 255), w=430, h=1080, x=0, y=0, kind='adjust')
    L.span(96, 97)
    px_ = 430.0 * 430.0 / 1920.0
    L.fx('ADBE Geometry2', **{'ADBE Geometry2-0001': [px_, 540.0], 'ADBE Geometry2-0002': [px_, 540.0], 'ADBE Geometry2-0011': 0,
                              'ADBE Geometry2-0003': 100.0, 'ADBE Geometry2-0004': 12000.0})

    # frame 165: |picture - field grey| thresholded -> every element (dark or coloured) turns white on black, whites drop out
    L = sc.solid('FX_diff165', (231, 231, 231))
    L.blend = 'difference'
    L.span(165, 166)
    L = sc.adjust('FX_thr165', 165, 166)
    L.fx('ADBE Threshold2', **{'ADBE Threshold2-0001': 0.10})

    # flip glitch on the title panel: rows torn sideways over the right part of the frame (238-241)
    L = sc.solid('FX_tear', (255, 255, 255), w=840, h=1080, x=1080, y=0, kind='adjust')
    L.pivot = (1500, 540)
    L.span(240, 242)
    L.fx('ADBE Wave Warp', **{'ADBE Wave Warp-0001': 9, 'ADBE Wave Warp-0002': [(240, 9.0, HOLD), (241, 4.0, HOLD)],
                              'ADBE Wave Warp-0003': 26.0, 'ADBE Wave Warp-0004': 0.0, 'ADBE Wave Warp-0005': 3.0})

    # film grain over everything
    L = sc.adjust('FX_grain', 0, NFRAMES)
    L.fx('ADBE Noise', **{'ADBE Noise-0001': 3.0, 'ADBE Noise-0002': 0, 'ADBE Noise-0003': 1})
    return sc
