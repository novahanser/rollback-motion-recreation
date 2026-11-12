"""Base layers: background colour timeline + the world ruler."""
import numpy as np
from lib import *
import shapes0 as S0

P0 = 7.2654          # minor tick period (world px)
PHASE = 2.93         # minor tick centre phase
MAJOR_MOD = 4        # tick index n is major when n % 5 == MAJOR_MOD
RULER_Y = 540.0


def ruler_tile(x0, x1, k=4, color=(8, 8, 8)):
    """one tile of the ruler covering world [x0, x1), 30 world px tall centred on the line"""
    hw = 15.0
    w, h = int((x1 - x0) * k), int(2 * hw * k)
    x, y = grid(w, h)
    wx = x / k + x0
    wy = y / k - hw                      # 0 at the line centre
    a = cov((np.abs(wy) - 1.0) * k)      # 2px line
    n = np.round((wx - PHASE) / P0)
    tx = PHASE + n * P0
    major = (np.mod(n, 5) == MAJOR_MOD)
    half_h = np.where(major, 11.0, 6.0)
    tick = np.minimum(cov((np.abs(wx - tx) - 1.0) * k), cov((np.abs(wy) - half_h) * k))
    a = np.maximum(a, tick)
    return from_arr(color, a)


def build(sc):
    sc.sec = 'BG'
    # ---- background colour timeline (screen-space solids, hold-keyed opacity)
    sc.solid('BG_gray', (230, 230, 230))
    sc.solid('BG_black', (0, 0, 0)).blink([0, 1, 3, 104, 137], on=0, off=100).set(pano=False)
    sc.solid('BG_pink', (235, 4, 109)).blink([0, 3, 15, 95, 104], on=0, off=100)
    sc.solid('BG_gray2', (221, 221, 221)).span(15, 24)
    sc.solid('BG_blue', (105, 130, 246)).blink([0, 70, 72, 74, 79, 81, 85], on=0, off=100)
    L = sc.add('BG_vignette', S0.vignette, 0, 0, k=0.5, screen=True, crop=False)
    L.span(2, 3)
    L.pano = False
    return sc


RULER_UNDER = [(7200, 9000), (9000, 10030)]


def _ruler_keys(L, x0):
    """The ticks of the source ruler do not stay on one grid relative to the artwork: the offset changes from shot to shot
    (the panorama registration drifts between the sections) and by a few px inside a shot.  ruler_off.RULER_OFF is that offset
    per frame, measured by matching the major ticks of every source frame against the ideal grid; applied as hold keys."""
    from ruler_off import RULER_OFF
    L.pivot = (float(x0), RULER_Y)
    keys, prev = [], None
    for f, off in enumerate(RULER_OFF):
        if prev is None or abs(off - prev) > 0.04:
            keys.append((f, [x0 + off, RULER_Y], HOLD))
            prev = off
    L.key('position', keys)
    return L


def build_ruler_under(sc):
    """the stretch of ruler that lies below the film frames, the chibi parade and the lens rings"""
    sec0 = sc.sec
    sc.sec = 'RULER'
    for j, (x0, x1) in enumerate(RULER_UNDER):
        _ruler_keys(sc.add('ruler_u%d' % j, ruler_tile, x0, RULER_Y - 15, x0, x1, k=4, crop=False), x0)
    sc.sec = sec0
    return sc


def build_ruler(sc):
    sc.sec = 'RULER'
    tile = 1800
    for i, x0 in enumerate(range(-1800, 12600, tile)):
        x1 = x0 + tile
        if (x0, x1) == RULER_UNDER[0]:
            continue                      # 7200..10030 is added earlier (build_ruler_under): there the ruler runs under film / chibis / lens
        if x0 == 9000:
            x0 = RULER_UNDER[1][1]
        L = sc.add('ruler_%02d' % i, ruler_tile, x0, RULER_Y - 15, x0, x1, k=4, crop=False)
        _ruler_keys(L, x0)
        L.pano = True
        if i in (0, 1):      # frame 1 sits on black: the ruler is white there (frame 2 keeps it black, lost in the dark)
            L.fx('ADBE Invert', **{'ADBE Invert-0002': [(0, 100.0, HOLD), (1, 0.0, HOLD), (2, 100.0, HOLD)]})
    return sc
