"""Film-run elements (frames 203-225) that live in the world comp but stay glued to the screen:
flickering giant Courier digits, horizontal glitch bars and the chibi parade.
They are inserted *below* every film strip, so the strips sweep over them like in the source.

Chibi parade (measured on the source, see 拆解分析.md):
  * 17-19 copies of the girl stand in one overlapping row; later copies sit in front of earlier ones
  * the row is revealed by a solid front that advances to the right, and beyond that front only a comb of
    vertical strips is visible - strip set A on odd frames, set B on even frames
"""
import numpy as np
from lib import *
from gen_util import s2w, zoom, gen

K = 2
S_RUN = 4.8862                                    # zoom during the film run
PARADE_H = 555.0                                  # on-screen height of one chibi (px)
PARADE_TOP = 262.0                                # on-screen y of the top of the hair
# screen x of the left edge of each chibi's left eye (frame 223), left -> right = back -> front
PARADE_L = [153, 295, 400, 501, 573, 679, 758, 883, 1023, 1148, 1239, 1331, 1427, 1530, 1665, 1770]
# vertical strips of the reveal comb (screen x) and their names
SEG_X = [0, 270, 360, 390, 407, 495, 560, 600, 698, 815, 877, 1000, 1090, 1259, 1353, 1500, 1640, 1760, 1920]
SEG_N = ['s0', 's1', 's2', 'A1', 'B1', 'A2', 'B2', 'A3', 'B3', 'A4', 'B4', 'A5', 'B5', 'A6', 'B6', 'A7', 'B7', 'B8']


def _upto(name):
    return SEG_N[:SEG_N.index(name) + 1]


# which strips are visible on which frame
PARADE_VIS = {
    203: ['s0'], 204: [], 205: ['s0', 's1'], 206: [], 207: ['s0', 's1', 's2', 'A1'], 208: ['s0', 's1', 'B1'],
    209: _upto('A1') + ['A2'], 210: _upto('s2') + ['B1', 'B2'], 211: _upto('A1') + ['A2', 'A3'], 212: _upto('B1') + ['B2', 'B3'],
    213: _upto('A2') + ['A3', 'A4'], 214: _upto('B2') + ['B3', 'B4'], 215: _upto('A3') + ['A4', 'A5'], 216: _upto('B3') + ['B4', 'B5'],
    217: _upto('A4') + ['A5', 'A6'], 218: _upto('B4') + ['B5', 'B6'], 219: _upto('A5') + ['A6', 'A7'], 220: _upto('A5') + ['B5', 'B6', 'B7'],
    221: _upto('B5') + ['A6', 'A7'], 222: _upto('B6') + ['B7', 'B8'], 223: _upto('B6') + ['A7'],
}


def _chibi_src():
    """generated sprite, hard alpha, cropped to its bounding box"""
    im = gen('chibi2.png')
    a = np.asarray(im).copy()
    a[..., 3] = np.where(a[..., 3] > 200, 255, 0).astype(np.uint8)
    im = Image.fromarray(a, 'RGBA')
    return im.crop(im.getbbox())


def chibi(h_world=240.0, pix=2):
    """the girl sprite (GPT image, redrawn from the source frames) with chunky aliased edges"""
    im = _chibi_src()
    h = int(h_world * K)
    w = int(im.width * h / im.height)
    small = im.resize((max(1, w // pix), max(1, h // pix)), Image.BOX)
    a = np.asarray(small).copy()
    a[..., 3] = np.where(a[..., 3] > 110, 255, 0).astype(np.uint8)
    return Image.fromarray(a, 'RGBA').resize((w, h), Image.NEAREST)


def parade_row():
    """the whole parade as one 1920 x 600 screen-pixel image (y 240..840 of the frame)"""
    src = _chibi_src()
    h = int(PARADE_H)
    w = int(src.width * h / src.height)
    spr = src.resize((max(1, w // 2), max(1, h // 2)), Image.BOX)
    a = np.asarray(spr).copy()
    a[..., 3] = np.where(a[..., 3] > 110, 255, 0).astype(np.uint8)
    spr = Image.fromarray(a, 'RGBA').resize((w, h), Image.NEAREST)
    a = np.asarray(spr).astype(int)
    eye = (a[..., 0] > 190) & (a[..., 1] < 90) & (a[..., 2] > 60) & (a[..., 3] > 0)
    cols = np.where(eye[: h // 2].sum(0) > 4)[0]
    ex = int(cols.min()) if len(cols) else int(w * 0.32)          # left edge of the left eye inside the sprite
    row = Image.new('RGBA', (1920, 600), (0, 0, 0, 0))
    for L in PARADE_L:
        row.alpha_composite(spr, (int(L - ex), int(PARADE_TOP - 240)))
    return row


def parade_seg(i, ver=2):
    return parade_row().crop((SEG_X[i], 0, SEG_X[i + 1], 600))


def big_digits(seed=3, n=30, thin=5):
    """hairline Courier digits; one digit = 98 world px tall = ~480 px at the film-run zoom, pitch 435 px"""
    rng = np.random.default_rng(seed)
    k = 3
    pitch, hgt = 89.0, 98.0
    c = Canvas(0, 0, n * pitch + 20, hgt + 40, k=k, ss=1)
    fnt = font('cour.ttf', hgt / 0.69 * k)
    prev = -1
    for i in range(n):
        d = int(rng.integers(0, 10))
        while d == prev:
            d = int(rng.integers(0, 10))
        prev = d
        im = text_img(str(d), fnt, (47, 47, 47, 255), pad=6)
        a = np.asarray(im).copy()
        a[..., 3] = np.asarray(Image.fromarray(a[..., 3]).filter(ImageFilter.MinFilter(thin)))      # thin the strokes
        im = Image.fromarray(a, 'RGBA')
        px_, py_ = c.P(10 + i * pitch + pitch / 2, 20 + hgt / 2)
        c.paste(im, px_ - im.width / 2, py_ - im.height / 2)
    return c


def hbars(seed=6):
    """horizontal 'pixel stretch' bars that tear in from the left edge (216-223); dark so the global invert turns them light"""
    rng = np.random.default_rng(seed)
    c = Canvas(0, 0, 300, 130, k=3, ss=1)
    y = 4.0
    while y < 126:
        h = 1.5 + rng.random() ** 2 * 9
        w = 300 * (0.25 + 0.75 * rng.random())
        v = int(20 + rng.random() * 110)
        if rng.random() < 0.75:
            c.rect(0, y, w, y + h, fill=(v, v, v, 255))
        y += h + 1 + rng.random() * 5
    return c


def build_under(sc):
    sec0 = sc.sec
    sc.sec = 'D'

    # ---- digits: a long strip; every 2-3 frames it jumps three digits further (new numbers), plus a slow drift left
    L = sc.addc('F_digits', big_digits)
    L.pivot = (L.x, L.y + L.wh / 2)
    wins = [205, 207, 210, 213, 216, 219, 222, 224, 226]
    path = []
    for j, f0 in enumerate(wins[:-1]):
        for f in range(f0, wins[j + 1]):
            path.append((f, -40.0 - j * 3 * 435.0 - 22.0 * (f - 205), 540.0))
    L.span(205, 226).set(pano=False)
    L.key('position', [(f, list(s2w(f, xs, ys)), HOLD) for f, xs, ys in path])
    L.key('scale', [(f, [S_RUN / zoom(f) * 100.0] * 2, HOLD) for f, xs, ys in path])

    # ---- glitch bars from the left edge
    L = sc.addc('F_hbars', hbars)
    L.pivot = (L.x, L.y + L.wh / 2)
    fr = list(range(216, 224))
    L.span(216, 224).set(pano=False)
    L.key('position', [(f, list(s2w(f, 0.0, 600.0)), HOLD) for f in fr])
    L.key('scale', [(f, [(1.0 if f >= 219 else 0.34) * 300.0 / zoom(f), (1.0 if f >= 219 else 0.85) * 300.0 / zoom(f)], HOLD) for f in fr])
    L.key('opacity', [(216, 100.0, HOLD), (218, 0.0, HOLD), (219, 100.0, HOLD)])

    # ---- chibi parade: one row image cut into the strips of the reveal comb, each strip glued to the screen
    frames = list(range(203, 224))
    for i, nm in enumerate(SEG_N):
        vis = [f for f in frames if nm in PARADE_VIS[f]]
        if not vis:
            continue
        L = sc.add('F_par_%s' % nm, parade_seg, 0, 0, i, 2, k=1, crop=False)
        L.pano = False
        L.pivot = (0.0, 300.0)                                   # left edge, vertical centre of the strip image
        L.span(vis[0], 224)
        L.key('position', [(f, list(s2w(f, float(SEG_X[i]), 540.0)), HOLD) for f in frames])
        L.key('scale', [(f, [100.0 / zoom(f)] * 2, HOLD) for f in frames])
        L.key('opacity', [(f, 100.0 if nm in PARADE_VIS[f] else 0.0, HOLD) for f in frames])
        # keep the natural colours under the global invert of 205-225 (pre-invert)
        L.fx('ADBE Invert', **{'ADBE Invert-0002': [(203, 100.0, HOLD), (205, 0.0, HOLD)] if vis[0] < 205 else 0.0})
    sc.sec = sec0
    return sc
