"""Section D (world x 8250..11000): nested film frames, pattern block, pixel chibi row, lens rings, Forward/Rollback title."""
import math
import numpy as np
from lib import *
from PIL import ImageOps
from gen_util import s2w, pin, zoom, gen, quadrant, fit, gray, threshold
from sec_a import solid_rect, hgrad_rect, text_asset, circle_outline, PK, BL
from sec_c import film_set, dot_text, FILM, REDBASE, GOLD, YEL, BGC, outlined
from filmrun import chibi

K = 2
LENS_C = (9548.0, 565.0)
FLIP_X = 10410.0                  # vertical axis the title panel flips around
TITLE_FONT = 'ROCKEB.TTF'

FILM_E = [                                            # left: dark-red outline + vertical KODAK / EBX band
    ('frame', 8250, 80, 8475, 960, 32, 35, 0, 35, REDBASE),
    ('dots', 8458, 285, 'FUJI RVP', YEL, -90, 3.2), ('dots', 8458, 605, 'CAFAAI-BEFB', YEL, -90, 2.6), ('dots', 8458, 900, 'FUJI RVP', YEL, -90, 3.2),
    ('frame', 8250, 355, 8360, 720, 22, 22, 0, 40, FILM), ('text', 8312, 366, '1', 'arialbd.ttf', 12, YEL, 0), ('text', 8312, 710, '1', 'arialbd.ttf', 12, YEL, 0),
    ('holes', [8322], 378, 400, 16, BGC, 4), ('holes', [8322], 676, 698, 16, BGC, 4),
    ('rect', 8535, 0, 8660, 1080, FILM),
    ('holes', [8626], 150, 215, 50, BGC, 12), ('holes', [8626], 275, 340, 50, BGC, 12), ('holes', [8626], 410, 475, 50, BGC, 12),
    ('holes', [8626], 535, 600, 50, BGC, 12), ('holes', [8626], 665, 730, 50, BGC, 12), ('holes', [8626], 790, 855, 50, BGC, 12),
    ('holes', [8626], 915, 980, 50, BGC, 12), ('holes', [8626], 25, 90, 50, BGC, 12),
    ('text', 8563, 115, 'KODAK', 'arialbd.ttf', 40, GOLD, 90), ('text', 8566, 388, '3', 'arialbd.ttf', 36, GOLD, 90),
    ('text', 8563, 962, 'EBX', 'arialbd.ttf', 40, GOLD, 90),
    ('frame', 8490, 335, 8540, 745, 8, 8, 8, 8, FILM),
]
FILM_F = [                                            # middle: big frame, cross bars, PORTRA frame, top/bottom dark-red bands
    ('frame', 8595, 55, 9495, 1010, 55, 55, 0, 0, FILM),
    ('rect', 8760, 0, 8795, 1080, FILM), ('rect', 8660, 295, 8915, 330, FILM),
    ('frame', 8685, 295, 8910, 760, 18, 18, 18, 0, FILM),
    ('text', 8696, 420, 'KODAK  PORTRA 400', 'arialbd.ttf', 8.5, (240, 240, 240), 90), ('text', 8696, 660, 'KODAK  PORTRA 400', 'arialbd.ttf', 8.5, (240, 240, 240), 90),
    ('text', 8696, 540, '43', 'arialbd.ttf', 8.5, (240, 240, 240), 90), ('dots', 8776, 418, 'RVP > 2', YEL, 90, 3.3),
    ('rect', 9040, 80, 9495, 112, REDBASE), ('dots', 9250, 96, 'FUJI RVP', YEL, 0, 3.2), ('dots', 9115, 72, 'RVP > 4', YEL, 180, 3.0),
    ('rect', 9090, 955, 9495, 990, REDBASE),
    ('rect', 9335, 0, 9415, 1080, FILM),
    ('holes', [9377], 150, 215, 62, BGC, 14), ('holes', [9377], 20, 85, 62, BGC, 14), ('holes', [9377], 790, 860, 62, BGC, 14),
    ('holes', [9377], 925, 995, 62, BGC, 14), ('holes', [9377], 285, 345, 62, BGC, 14), ('holes', [9377], 700, 760, 62, BGC, 14),
    ('text', 9452, 400, '3', 'arialbd.ttf', 40, GOLD, 90), ('text', 9440, 925, '2A', 'arialbd.ttf', 30, GOLD, 90), ('rect', 9460, 880, 9463, 990, GOLD),
]
FILM_G = [                                            # right: portrait strip + dark-red outline around the title edge
    ('rect', 9495, 80, 9970, 112, REDBASE), ('dots', 9565, 100, 'CAFAAI-BEFB', YEL, 0, 2.6), ('dots', 9868, 100, 'FUJI RVP', YEL, 0, 3.2),
    ('rect', 9935, 80, 9970, 1000, REDBASE), ('rect', 9495, 968, 9970, 1000, REDBASE), ('dots', 9552, 975, 'RVP > 2', YEL, 0, 3.0),
    ('frame', 9495, 355, 9725, 720, 30, 30, 22, 30, FILM),
    ('holes', [9506], 372, 390, 12, BGC, 3), ('holes', [9506], 420, 438, 12, BGC, 3), ('holes', [9506], 470, 488, 12, BGC, 3), ('holes', [9506], 520, 538, 12, BGC, 3),
    ('holes', [9506], 570, 588, 12, BGC, 3), ('holes', [9506], 620, 638, 12, BGC, 3), ('holes', [9506], 670, 688, 12, BGC, 3),
    ('text', 9648, 322, '21', 'arialbd.ttf', 22, YEL, 0), ('text', 9660, 745, '1', 'arialbd.ttf', 20, YEL, 0),
    ('frame', 9740, 345, 9830, 730, 0, 0, 30, 30, FILM), ('rect', 9740, 345, 9830, 365, FILM), ('rect', 9740, 710, 9830, 730, FILM),
    ('holes', [9790], 372, 392, 26, BGC, 4), ('holes', [9790], 410, 430, 26, BGC, 4), ('holes', [9790], 452, 472, 26, BGC, 4),
    ('holes', [9790], 495, 515, 26, BGC, 4), ('holes', [9790], 540, 560, 26, BGC, 4), ('holes', [9790], 584, 604, 26, BGC, 4),
    ('holes', [9790], 628, 648, 26, BGC, 4), ('holes', [9790], 672, 692, 26, BGC, 4),
    ('text', 9818, 396, '21', 'arialbd.ttf', 16, YEL, -90), ('text', 9820, 612, '20A', 'arialbd.ttf', 14, YEL, 90),
    ('frame', 9742, 262, 9997, 572, 6, 6, 6, 6, FILM), ('frame', 9873, 495, 9970, 575, 5, 5, 5, 5, FILM),
]


# ----------------------------------------------------------------------------- pattern block
def patterns(seed=5):
    rng = np.random.default_rng(seed)
    c = Canvas(8908, 188, 9340, 866, k=K, ss=2)
    bk, wh = (8, 8, 8, 255), (250, 250, 250, 255)
    c.rect(8912, 232, 9335, 862, fill=wh)
    # tiny grid of cells with triangles (top-left)
    for i in range(14):
        for j in range(10):
            x_, y_ = 8930 + i * 9.5, 250 + j * 9.5
            if rng.random() < 0.6:
                c.rect(x_, y_, x_ + 8, y_ + 8, outline=bk, width=0.5)
            if rng.random() < 0.3:
                c.poly([(x_, y_ + 8), (x_ + 4, y_), (x_ + 8, y_ + 8)], bk)
    # vertical stripes
    for i in range(12):
        c.rect(9130 + i * 7.2, 200, 9133.6 + i * 7.2, 270, fill=bk)
    # big pixel pattern (QR-like)
    for i in range(9):
        for j in range(7):
            if rng.random() < 0.5:
                c.rect(9112 + i * 12.5, 274 + j * 12.5, 9124.5 + i * 12.5, 286.5 + j * 12.5, fill=bk)
    for (qx, qy) in ((9112, 274), (9199.5, 274), (9112, 349)):                     # finder squares
        c.rect(qx, qy, qx + 25, qy + 25, fill=bk)
        c.rect(qx + 5, qy + 5, qx + 20, qy + 20, fill=wh)
        c.rect(qx + 9, qy + 9, qx + 16, qy + 16, fill=bk)
    # checkerboard
    for i in range(11):
        for j in range(5):
            if (i + j) % 2 == 0:
                c.rect(9204 + i * 12, 366 + j * 12, 9216 + i * 12, 378 + j * 12, fill=bk)
    # thick chevron rows
    for r in range(6):
        pts = []
        for i in range(17):
            pts.append((8926 + i * 9.0, 350 + r * 12 + (0 if i % 2 else 9)))
        c.line(pts, bk, 4.2, joint=None)
    # horizontal stripe blocks + fine grid (lower half, mostly behind the chibi row)
    for r in range(9):
        c.rect(8915, 610 + r * 8, 8945, 614 + r * 8, fill=bk)
    for r in range(7):
        c.rect(9100, 632 + r * 7, 9150, 635.5 + r * 7, fill=bk)
    for i in range(16):
        c.line([(8952 + i * 9, 640), (8952 + i * 9, 700)], bk, 0.6)
    for j in range(8):
        c.line([(8952, 640 + j * 8.5), (9087, 640 + j * 8.5)], bk, 0.6)
    for r in range(14):
        c.rect(8920 + r * 13, 708, 8926 + r * 13, 760, fill=bk)
    for i in range(22):
        if rng.random() < 0.55:
            c.rect(8950 + (i % 11) * 12, 770 + (i // 11) * 12, 8961 + (i % 11) * 12, 781 + (i // 11) * 12, fill=bk)
    # UI rulers
    for (x0_, y0_, x1_) in ((8930, 238, 9160), (8950, 818, 9165)):
        c.rect(x0_, y0_, x1_, y0_ + 12, fill=(60, 60, 60, 255))
        for i in range(int((x1_ - x0_) / 6)):
            c.line([(x0_ + i * 6, y0_ + 12), (x0_ + i * 6 - 5, y0_)], (220, 220, 220, 255), 0.6)
        c.rrect(x0_ + 70, y0_ + 2, x0_ + 96, y0_ + 10, 2, fill=wh)
    c.circle(9110, 300, 22, outline=bk, width=0.8)
    c.circle(9098, 656, 14, outline=bk, width=0.8)
    c.line([(9000, 420), (9230, 396)], bk, 0.7)
    c.line([(9250, 330), (9330, 350), (9300, 400)], bk, 0.7)
    for (nx, ny) in ((9000, 420), (9230, 396), (9250, 330), (9330, 350), (9300, 400)):
        c.circle(nx, ny, 2.6, fill=wh, outline=bk, width=0.7)
    # dark blocks
    c.rect(9160, 232, 9335, 250, fill=bk)
    c.rect(9080, 690, 9118, 840, fill=(30, 30, 30, 255))
    c.rect(8912, 700, 8935, 760, fill=bk)
    im = c.done()
    # gradient cylinder bottom-right
    x0_, y0_, x1_, y1_ = 9118, 660, 9332, 858
    w, h = (x1_ - x0_) * K, (y1_ - y0_) * K
    x, y = grid(w, h)
    v = grad_stops(y / h, [(0, (230, 230, 230)), (0.18, (30, 30, 30)), (0.5, (236, 236, 236)), (0.8, (60, 60, 60)), (1, (200, 200, 200))])
    cyl = from_arr(v, np.ones((h, w), np.float32))
    im.alpha_composite(cyl, (int((x0_ - 8908) * K), int((y0_ - 188) * K)))
    # light grey panel top-right
    d = ImageDraw.Draw(im)
    d.rectangle([int((9226 - 8908) * K), int((200 - 188) * K), int((9335 - 8908) * K), int((262 - 188) * K)], fill=(244, 244, 244, 255), outline=(60, 60, 60, 255))
    for i in range(5):
        yy = int((212 + i * 9 - 188) * K)
        d.line([int((9234 - 8908) * K), yy, int((9326 - 8908) * K), yy], fill=(90, 90, 90, 255), width=1)
    return im


def portrait():
    im = gen('girl-gray.png')
    w, h = im.size
    im = im.crop((int(w * 0.38), int(h * 0.05), int(w * 0.78), int(h * 0.95)))
    return fit(im, 176 * K, 300 * K)


# ----------------------------------------------------------------------------- lens rings
def lens_ring(r0, r1, seed, k=1):
    size = int((2 * r1 + 4) * k)
    cc = size / 2.0
    x, y = grid(size, size)
    d = np.hypot(x - cc, y - cc) / k
    a = np.radians(ang(x, y, cc, cc))
    rng = np.random.default_rng(seed)
    n = int(rng.integers(2, 5))
    ph = rng.random() * 6.28
    v = 156 + 72 * np.cos(n * a + ph) * (0.6 + 0.4 * np.cos((n + 1) * a + ph * 1.7))
    v = v + 10 * np.sin(d * 0.9)                     # fine concentric brushing
    v = np.clip(v, 52, 244)
    edge = cov(np.abs(d - r1 + 1.0) - 0.9) + cov(np.abs(d - r0 - 1.0) - 0.9)
    v = v * (1 - np.clip(edge, 0, 1)) + 20 * np.clip(edge, 0, 1)
    return from_arr(np.dstack([v, v, v]), cov(sd_ring(x, y, cc, cc, r0 * k, r1 * k)))


# ----------------------------------------------------------------------------- title panel
def _title_raw(s):
    fnt = font(TITLE_FONT, 131 * K)
    return text_img(s, fnt, (8, 8, 8, 255), pad=6, tracking=-3.0 * K, stroke=int(1.0 * K), stroke_fill=(8, 8, 8, 255))


def title(s):
    ref = _title_raw('Rollback')
    st = 739.0 * K / ref.width                                # same horizontal stretch for both words
    im = _title_raw(s)
    return im.resize((int(im.width * st), im.height), Image.LANCZOS)


def slab(s, size):
    fnt = font(TITLE_FONT, size * K)
    im = text_img(s, fnt, (8, 8, 8, 255), pad=4, stroke=max(1, int(0.3 * K)), stroke_fill=(8, 8, 8, 255))
    return im.resize((int(im.width * 1.2), im.height), Image.LANCZOS)


def q_glyph(w=172.0, h=100.0):
    fnt = font(TITLE_FONT, 150 * K)
    im = text_img('Q', fnt, (8, 8, 8, 255), pad=6, stroke=int(1.0 * K), stroke_fill=(8, 8, 8, 255))
    im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im.resize((int(w * K), int(h * K)), Image.LANCZOS)


def flip_ghost():
    """white disc with the hourglass (the panel's centre graphic) - shows up squeezed over the film during the flip"""
    R = 342.0
    c = Canvas(-R - 4, -R - 4, R + 4, R + 4, k=K, ss=2)
    c.circle(0, 0, R, fill=(250, 250, 250, 255), outline=(20, 20, 20, 255), width=1.2)
    c.circle(0, 0, 182, outline=(20, 20, 20, 255), width=1.0)
    bk = (8, 8, 8, 255)
    c.poly([(-127, -190), (127, -190), (0, 37)], bk)
    c.poly([(0, 13), (63, 125), (-60, 125)], bk)
    c.circle(0, -115, 72, fill=(250, 250, 250, 255))
    c.circle(0, 95, 38, fill=(250, 250, 250, 255))
    return c


def hourglass():
    x0, y0, x1, y1 = 10290, 200, 10552, 525
    w, h = (x1 - x0) * K, (y1 - y0) * K
    c = Canvas(x0, y0, x1, y1, k=K, ss=3)
    bk = (8, 8, 8, 255)
    c.poly([(10293, 205), (10547, 205), (10420, 432)], bk)
    c.poly([(10420, 408), (10483, 520), (10360, 520)], bk)
    im = c.done()
    x, y = grid(im.width, im.height)
    wx, wy = x / K + x0, y / K + y0
    hole = np.maximum(cov((np.hypot(wx - 10420, wy - 280) - 72) * K), cov((np.hypot(wx - 10420, wy - 490) - 38) * K))
    a = np.asarray(im).copy()
    a[..., 3] = (a[..., 3] * (1 - hole)).astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


def big_circles():
    c = Canvas(10070, 45, 10770, 745, k=K, ss=3)
    c.circle(10420, 395, 182, outline=(20, 20, 20, 255), width=0.9)
    c.circle(10420, 395, 342, outline=(20, 20, 20, 255), width=0.9)
    c.circle(10420, 395, 332, outline=(20, 20, 20, 255), width=0.6)
    return c


def word_columns():
    c = Canvas(10100, 278, 10800, 374, k=K, ss=3)
    rows = [('know', 'my', 'fall', 'is', 'a', '', 'mistake'), ('know', 'my', 'pain', 'is', 'a', '', 'disgrace'),
            ('know', 'my', 'prayer', 'is', 'hard', 'to', 'raise'), ('know', 'my', 'sins', 'are', 'mine', 'to', 'face'),
            ('know', 'my', 'faith', 'is', 'worn', 'and', 'frayed'), ('know', 'my', 'hope', '', 'begins', 'to', 'fade'),
            ('know', 'my', 'soul', '', 'longs', 'for', 'grace'), ('know', 'my', 'God', 'is', 'in', 'this', 'place')]
    xs = [10126, 10245, 10365, 10462, 10560, 10668, 10786]
    jit = [(-8, 0, 0, 0, 0, 0, 0), (-10, 0, 8, 0, 0, 0, 0), (-28, -34, -18, -70, 22, 4, 0), (-26, -32, -22, -84, 20, 6, 0),
           (-30, -36, -32, -92, 2, 0, 0), (2, 12, 24, 0, -50, -6, 0), (-30, -36, -34, 0, -24, 6, 0), (-26, -30, -10, 40, -22, 0, 0)]
    for r, (row, jj) in enumerate(zip(rows, jit)):
        for i, wd in enumerate(row):
            if wd:
                c.text(xs[i] + jj[i], 284 + r * 10.6, wd, 'arial.ttf', 10.5, (14, 14, 14, 255), anchor='ra' if i == 6 else 'la', tracking=-0.5)
    return c


def mirrored_code():
    words = ['fall', 'pain', 'prayer', 'sins', 'faith', 'hope', 'soul', 'grace']
    tails = ['is a mistake', 'is a disgrace', 'is hard to raise', 'are mine to face', 'is worn and frayed', 'begins to fade', 'still longs for grace', 'is in this place']
    widths = [750, 390, 390, 383, 583, 390, 390, 440]
    x0, x1 = 10028, 10830
    c = Canvas(x0, 720, x1, 1004, k=K, ss=3)
    col = (14, 14, 14, 255)
    fs = 9.8
    xr = x1 - 8.0                                              # every line ends here (-> left edge after the flip)

    def justified(y, toks, width):
        n = len(toks)
        for i, t in enumerate(toks):
            c.text(xr - width + width * i / float(max(n - 1, 1)), y, t, 'arial.ttf', fs, col, anchor='la' if i < n - 1 else 'ra')

    def plain(y, s):
        c.text(xr, y, s, 'arial.ttf', fs, col, anchor='ra', tracking=-0.3)

    y = 724.0
    for wd, tl, wj in zip(words, tails, widths):
        toks = ['#', 'I', 'know', 'my', wd if wd != 'grace' else 'God'] + tl.split(' ')
        justified(y, toks, wj)
        y += 11.8
        plain(y, 'self.record.append("%s")' % wd)
        y += 11.8
    y += 10
    justified(y, ['if', 'len(self.record)', '>=', '8:'], 250)
    y += 11.8
    plain(y, 'self.record.clear()')
    y += 11.8
    justified(y, ['#', 'rollback', 'complete', '\u2014', 'restart'], 253)
    y += 23.6
    justified(y, ['def', 'emit(self):'], 198)
    y += 11.8
    justified(y, ['return', "'-", 'rollback', 'Q', '-', '//', 'each', 'iteration', 'carries', 'the', 'same', "weight'"], 548)
    return c.done().transpose(Image.FLIP_LEFT_RIGHT)


def collage():
    c = Canvas(10194, 452, 10376, 676, k=K, ss=2)
    srcs = [(0, 0, (0.3, 0.1, 0.7, 0.6)), (0, 1, (0.1, 0.2, 0.9, 0.9)), (1, 0, (0.0, 0.3, 0.6, 0.9)), (0, 0, (0.0, 0.5, 0.5, 1.0)), (0, 1, (0.3, 0.0, 0.8, 0.5))]
    boxes = [(10197, 460, 10262, 512), (10245, 520, 10362, 578), (10247, 585, 10300, 668), (10305, 590, 10370, 668), (10200, 520, 10242, 575)]
    for (qx, qy, bx), (x0, y0, x1, y1) in zip(srcs, boxes):
        q = quadrant('photos-sheet.png', qx, qy)
        W_, H_ = q.size
        q = gray(q.crop((int(bx[0] * W_), int(bx[1] * H_), int(bx[2] * W_), int(bx[3] * H_))))
        a = np.asarray(q).astype(np.float32)
        a[..., :3] = np.clip((a[..., :3] - 120) * 1.9 + 130, 0, 255)
        q = Image.fromarray(a.astype(np.uint8), 'RGBA')
        c.rect(x0 - 2, y0 - 2, x1 + 2, y1 + 2, fill=(250, 250, 250, 255))
        c.image(q, x0, y0, w=x1 - x0, h=y1 - y0)
    c.rect(10297, 460, 10337, 505, fill=(96, 92, 40, 255), outline=(250, 250, 250, 255), width=1.5)
    c.text(10330, 672, 'PROGRESS REPORT', 'arialbd.ttf', 4.0, (20, 20, 20, 255), anchor='ma')
    return c


def small_bits():
    c = Canvas(9690, 255, 10220, 780, k=K, ss=3)
    bk = (20, 20, 20, 255)
    for r in (20, 40, 60):
        c.circle(9725, 630, r, outline=bk, width=0.7)
    c.dashed((10030, 282), (10030, 366), bk, 0.8, 4, 4)
    for i in range(18):
        c.rect(9990 + (i * 37 % 150), 566 + (i * 13 % 40), 9993 + (i * 37 % 150), 570 + (i * 13 % 40), fill=bk)
    return c


def tiny_para():
    c = Canvas(9862, 636, 9944, 736, k=K, ss=3)
    lines = ['iteration 07 / 08', 'restore from frame', 'checksum mismatch', 'retry in 0.25s', 'state: rollback', 'queue length 12', 'drop frame 148', 'who returns to the past.']
    for i, t in enumerate(lines):
        c.text(9866, 640 + i * 10.5, t, 'courbd.ttf', 5.0, (20, 20, 20, 255))
    return c.done().transpose(Image.FLIP_LEFT_RIGHT)


# ----------------------------------------------------------------------------- build
def _is_back(c):
    """the two wide sprocket strips (with their holes and gold edge print): they pass *behind* the chibi parade"""
    if c[0] == 'rect' and c[1] in (8535, 9335) and c[2] == 0:
        return True
    if c[0] == 'holes' and c[1] in ([8626], [9377]):
        return True
    return c[0] == 'text' and c[1] in (8563, 8566)


def build_lens(sc):
    """lens rings + the two wide sprocket strips: added early (from sec_c, before the film-run parade) so the chibis stay in front"""
    sec0 = sc.sec
    sc.sec = 'D'
    rng = np.random.default_rng(42)
    for i, (r0, r1) in enumerate(((400, 466), (330, 398), (252, 328), (178, 250), (90, 176))):
        L = sc.add('D_lens%d' % i, lens_ring, LENS_C[0] - r1 - 2, LENS_C[1] - r1 - 2, float(r0), float(r1), 20 + i, k=1, crop=False, pivot=LENS_C)
        ks = []
        a = float(rng.integers(0, 360))
        for f in range(224, 272):
            if f == 224 or rng.random() < 0.45:
                a = a + float(rng.integers(20, 140)) * (1 if i % 2 else -1)
            ks.append((f, a, HOLD))
        L.span(200).key('rotation', ks)
    sc.addc('D_filmE_back', film_set, [c for c in FILM_E if _is_back(c)], 8531, 0, 8664, 1084).span(200)
    sc.addc('D_filmF_back', film_set, [c for c in FILM_F if _is_back(c)], 9331, 0, 9419, 1084).span(200)
    sc.sec = sec0
    return sc


def build(sc):
    sc.sec = 'D'
    sc.kdef = K

    # ---------------- title panel (flips around FLIP_X on 237-242) ----------------
    panel = []
    panel.append(sc.addc('D_circles', big_circles).span(224))
    L = sc.add('D_forward', title, 10035, 38, 'Forward')
    L.span(224, 241).set(pano=False)
    panel.append(L)
    L = sc.add('D_rollback', title, 10035, 38, 'Rollback')
    L.span(241)
    panel.append(L)
    panel.append(sc.add('D_hourglass', hourglass, 10290, 200).span(224))
    panel.append(sc.addc('D_words', word_columns).span(224))
    panel.append(sc.add('D_q1', q_glyph, 10617, 161).span(224))
    panel.append(sc.add('D_pull1', slab, 10128, 493, 'Pull', 17).span(224))
    panel.append(sc.add('D_pull2', slab, 10716, 592, 'Pull', 28).span(224))
    panel.append(sc.add('D_pull3', slab, 10716, 968, 'Pull', 28).span(224))
    L = sc.add('D_rolback', text_asset, 10698, 634, 'ROLBACK..', 'georgiab.ttf', 21, (14, 14, 14))
    L.span(224).set(scale=[-100, -100])
    panel.append(L)
    panel.append(sc.add('D_code', mirrored_code, 10028, 720).span(224))
    panel.append(sc.addc('D_collage', collage).span(224))
    # ending: the panel smears out horizontally (anchor near its right end) -> (pivot world x, x-stretch) per frame
    # flip, measured per frame: (frame, world x of the panel's pivot, x-scale). Squeezed -> mirrored -> overshoot -> 1.6x -> settled
    FLIP = [(237, 10157.5, 0.13), (238, 10270.7, -0.23), (239, 10443.7, -0.43), (240, 10653.0, -1.28), (241, 10200.0, 1.6), (242, 10410.0, 1.0)]
    CLIP_X = 10139.0
    END = [(265, 10524.6, 1.234), (266, 10593.8, 1.276), (267, 10706.5, 1.459), (268, 10871.6, 1.694), (269, 11000.4, 2.215),
           (270, 10865.2, 3.4), (271, 10057.0, 6.0)]
    for L in panel:
        L.pivot = (FLIP_X, L.pivot[1])
        sx0 = L.static.get('scale', [100.0, 100.0])
        sy = sx0[1]
        sg = 1 if sx0[0] >= 0 else -1
        L.key('scale', [(236, [100 * sg, sy], HOLD)] + [(f, [100 * sg * st, sy], HOLD) for f, x_, st in FLIP + END])
        L.key('position', [(236, [FLIP_X, L.pivot[1]], HOLD)] + [(f, [x_, L.pivot[1]], HOLD) for f, x_, st in FLIP + END])
        # frame 241: the 1.6x panel overflows to the left and is cut off at CLIP_X
        left = 10200.0 + (L.x - FLIP_X) * 1.6
        frac = min(max((CLIP_X - left) / (L.ww * 1.6), 0.0), 1.0)
        if frac > 0.01 and sg > 0:
            L.fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': [(236, 0.0, HOLD), (241, 100.0 * frac, HOLD), (242, 0.0, HOLD)],
                                        'ADBE Linear Wipe-0002': 90.0, 'ADBE Linear Wipe-0003': 0.0})

    # ---------------- bits left of the panel ----------------
    sc.add('D_q2', q_glyph, 9833, 739, 111.0, 55.0).span(224)
    sc.addc('D_bits', small_bits).span(224)
    sc.add('D_para', tiny_para, 9862, 636).span(224)
    L = sc.add('D_rolback2', text_asset, 10115, 596, 'ROLBACK..', 'georgiab.ttf', 12, (14, 14, 14))
    L.span(224).set(scale=[-100, -100])

    # ---------------- ending: pink bands (screen-glued) cover the panel and the lens rings, but not the film ----------------
    import fx
    fx.build_bands(sc)
    sc.sec = 'D'

    # ---------------- film frames ----------------
    sc.addc('D_filmE', film_set, [c for c in FILM_E if not _is_back(c)], 8246, 0, 8664, 1084).span(200)
    sc.addc('D_filmF', film_set, [c for c in FILM_F if not _is_back(c)], 8591, 0, 9499, 1084).span(200)
    sc.add('D_portrait', portrait, 9518, 387).span(200)
    sc.addc('D_filmG', film_set, FILM_G, 9491, 76, 10001, 1004).span(200)

    # ---------------- pattern block + chibi row ----------------
    sc.add('D_patterns', patterns, 8908, 188).span(224)
    ROWX = [8948, 9017, 9089, 9126, 9199, 9244, 9303, 9344, 9385, 9435]            # centres measured on frame 227
    first = sc.add('D_chibi00', chibi, 0, 0, 200.0)
    for i, cx_ in enumerate(ROWX):
        L = first if i == 0 else sc.clone('D_chibi%02d' % i, first)
        L.x, L.y = cx_ - L.ww / 2, 526 - L.wh / 2
        L.pivot = (cx_, 526.0)
        # still under the global invert on 224-225: pre-invert so they keep their own colours
        L.span(224).fx('ADBE Invert', **{'ADBE Invert-0002': [(224, 0.0, HOLD), (226, 100.0, HOLD)]})

    # ---------------- flip, left side: the pattern block + chibi row jump to the right as a squeezed copy (237-239) ----------------
    GRP = [(236, 9124.0, 1.0), (237, 10434.0, 0.37), (238, 10622.0, 0.20), (239, 8977.0, 0.37), (240, 9124.0, 1.0)]
    for L in [sc.get('D_patterns')] + [sc.get('D_chibi%02d' % i) for i in range(len(ROWX))]:
        px_, py_ = L.pivot
        L.key('position', [(f, [cx_ + (px_ - 9124.0) * k_, py_], HOLD) for f, cx_, k_ in GRP])
        L.key('scale', [(f, [100.0 * k_, 100.0], HOLD) for f, cx_, k_ in GRP])

    # squeezed white disc + hourglass that flashes over the film (237-239), and a small copy top-left
    big = sc.addc('D_ghostA', flip_ghost, pivot=(0.0, 0.0))
    gk = [(237, 460, 360, 0.18, 1.0), (238, 465, 430, 0.28, 1.08), (239, 515, 350, 0.14, 1.02)]
    big.span(237, 240).set(pano=False)
    big.key('position', [(f, list(s2w(f, xs, ys)), HOLD) for f, xs, ys, sx_, sy_ in gk])
    big.key('scale', [(f, [100.0 * sx_ / zoom(f), 100.0 * sy_ / zoom(f)], HOLD) for f, xs, ys, sx_, sy_ in gk])
    small = sc.clone('D_ghostB', big)
    small.pivot = (0.0, 0.0)
    gk = [(237, 240, 170), (238, 220, 70), (239, 200, 95)]
    small.span(237, 240).set(pano=False)
    small.key('position', [(f, list(s2w(f, xs, ys)), HOLD) for f, xs, ys in gk])
    small.key('scale', [(f, [20.0 / zoom(f), 20.0 / zoom(f)], HOLD) for f, xs, ys in gk])
    return sc
