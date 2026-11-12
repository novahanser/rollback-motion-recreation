"""Section B (world x 2750..5500): mirrored circles, chrome shape, checker disc, black window with clouds,
ribbons, streak burst, cloud cards, dictionary text."""
import math
import numpy as np
from lib import *
from PIL import ImageOps
from gen_util import s2w, pin, zoom, gen, quadrant, fit, gray, components, w2s
from sec_a import solid_rect, hgrad_rect, text_asset, circle_outline, PK, BL
from sec_a2 import ocr_text, OCR

K = 2
ROYAL = (13, 62, 216)
RIB = (232, 36, 110)
RIB_D = (186, 16, 86)
DISC_C = (3976.0, 420.0)
DISC_R = 790.0
WIN = (3653, 362, 4722, 992)          # the black 'window'
PLATE = (3803, 412)                   # picture plate inside the window (final position)
PLATE_W, PLATE_H = 770, 538


# ----------------------------------------------------------------------------- B1 mirrored circles / curves
DXB = 59.5        # the 2750-3560 stretch is only ever seen from the 86-103 shots, whose registration sits 59 px further right


def circles_b(mirror=False):
    col = (28, 120, 230, 255) if mirror else (20, 20, 20, 255)
    y0, y1 = (545, 1085) if mirror else (-5, 535)
    c = Canvas(2745 + DXB, y0, 3560 + DXB, y1, k=K, ss=3)

    def Y(v):
        return 1080 - v if mirror else v
    c.circle(3013 + DXB, Y(240), 140, outline=col, width=1.0)
    c.circle(3013 + DXB, Y(240), 13, outline=col, width=1.0)
    c.circle(3082 + DXB, Y(310), 62, outline=col, width=1.0)
    c.circle(2872 + DXB, Y(350), 9, outline=col, width=1.0)
    c.circle(3300 + DXB, Y(492) if not mirror else 612, 42, outline=col, width=1.0)
    pts = []
    for i in range(121):
        t = i / 120.0
        x = 2750 + DXB + 900 * t
        if t < 0.33:
            y = 330 - 65 * math.sin(t / 0.33 * math.pi)
        elif t < 0.78:
            y = 330 + 110 * (1 - math.cos((t - 0.33) / 0.45 * math.pi)) / 2
        else:
            y = 440
        pts.append((x, Y(y)))
    c.line(pts, col, 1.0)
    c.text(3013 + DXB, Y(180), '[*]', OCR, 15, col, anchor='mm')
    return c


def thick_line(w, h, col):
    return new(int(w * K), int(h * K), rgba(col))


# ----------------------------------------------------------------------------- B2 chrome
def chrome():
    """liquid-chrome calligraphic shape (GPT image redrawn from frame 84 of the source)"""
    im = gen('chrome-shape2.png')
    a = np.asarray(im).copy()
    a[..., 3] = np.where(a[..., 3] > 40, a[..., 3], 0).astype(np.uint8)
    im = Image.fromarray(a, 'RGBA')
    im = im.crop(im.getbbox())
    w = 300 * 3
    return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)


def chrome_frame():
    c = Canvas(2931, 357, 3300, 725, k=K, ss=3)
    c.rect(2936, 362, 3295, 720, outline=(170, 170, 170, 255), width=0.8)
    for (x_, ch) in ((2963, '“'), (3272, '”')):
        c.text(x_, 382, ch, 'georgiab.ttf', 44, (130, 130, 130, 255), anchor='ma')
        c.text(x_, 382.5, ch, 'georgiab.ttf', 42, (250, 250, 250, 255), anchor='ma')
    return c


def _serif_line(parts, width, track=-9.0):
    """tight high-contrast serif line (Playfair Display, upright / italic parts) scaled to `width` world px"""
    S = 200
    im = Image.new('RGBA', (3200, 460), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 30.0
    for (txt, italic, col) in parts:
        fnt = font('PlayfairDisplay-Italic.ttf' if italic else 'PlayfairDisplay-Regular.ttf', S)
        for ch in txt:
            d.text((x, 60), ch, font=fnt, fill=rgba(col))
            x += fnt.getlength(ch) + track
        x -= 2
    im = im.crop(im.getbbox())
    w = int(width * K)
    return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)


def waiting_text():
    """'Waitingfor(connect)' - 754 world px wide in the source (86-97)"""
    return _serif_line([('Waitingfor', False, (186, 188, 188)), ('(connect)', True, (172, 184, 180))], 754.0)


def connect_text():
    """'(connect)' alone, 280 world px wide (98-103)"""
    return _serif_line([('(connect)', True, (150, 172, 166))], 280.0)


# ----------------------------------------------------------------------------- B3 big disc (three skins)
def disc_checker(k=1):
    size = int((2 * DISC_R + 4) * k)
    cc = size / 2.0
    x, y = grid(size, size)
    cell = 20.0 * k
    v = np.where(((np.floor(x / cell) + np.floor(y / cell)) % 2) > 0, 238.0, 205.0)
    d = np.hypot(x - cc, y - cc)
    edge = cov(np.abs(d - DISC_R * k + 1.5) - 1.5)[..., None]
    rgb = np.dstack([v, v, v]) * (1 - edge) + np.array((150, 170, 220), np.float32) * edge
    return from_arr(rgb, cov(d - DISC_R * k))


def disc_silver(k=1):
    size = int((2 * DISC_R + 4) * k)
    cc = size / 2.0
    x, y = grid(size, size)
    a = np.radians(ang(x, y, cc, cc))
    v = 128 + 118 * np.cos(2 * a + 0.7) * (0.75 + 0.25 * np.cos(4 * a + 1.3))
    v = np.clip(v, 0, 255)
    return from_arr(np.dstack([v, v, v]), cov(np.hypot(x - cc, y - cc) - DISC_R * k))


def disc_blue(k=1):
    size = int((2 * DISC_R + 4) * k)
    cc = size / 2.0
    x, y = grid(size, size)
    return from_arr(ROYAL, cov(np.hypot(x - cc, y - cc) - DISC_R * k))


# ----------------------------------------------------------------------------- B4 labels / tree
def label_2100():
    c = Canvas(3470, 544, 3580, 594, k=4, ss=2)
    c.text(3478, 548, '2/00', 'Montserrat-Regular.ttf', 24, (10, 10, 10, 255), tracking=-1.2)
    c.text(3479, 575, '22 CENTURY', 'Montserrat-Medium.ttf', 8.5, (10, 10, 10, 255), tracking=-0.2)
    return c


def pixel_text(s, px=12, color=(0, 0, 0), fname='simsun.ttc', up=2):
    """bitmap-looking text: render without anti-aliasing at `px`, upscale with nearest"""
    fnt = font(fname, px)
    w = int(fnt.getlength(s)) + 4
    im = Image.new('L', (w, px + 6), 0)
    d = ImageDraw.Draw(im)
    d.fontmode = '1'
    d.text((2, 2), s, font=fnt, fill=255)
    bb = im.getbbox()
    if bb:
        im = im.crop((0, 0, bb[2] + 2, im.height))
    im = im.resize((im.width * up, im.height * up), Image.NEAREST)
    out = Image.new('RGBA', im.size, rgba(color, 0))
    out.putalpha(im)
    arr = np.asarray(out).copy()
    arr[..., 0], arr[..., 1], arr[..., 2] = color
    return Image.fromarray(arr, 'RGBA')


def ascii_tree(color=(240, 240, 240)):
    rows = [('ASCII-Art/', None), None, ('index.html', None), ('style.css', None), ('sketch.js', '// 主程序'),
            ('template.js', '// 字符模板生成'), ('matcher.js', '// SSD块匹配'), ('edge.js', '// Sobel边缘'),
            ('dithering.js', '// Floyd抖动'), ('ui.js', '// 滑块与上传'), ('renderer.js', '// 绘制输出')]
    W_, H_ = 230 * K, 310 * K
    im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y = 4 * K
    for i, r in enumerate(rows):
        if r is None:
            y += 34 * K
            continue
        name, cm = r
        if i == 0:
            im.alpha_composite(pixel_text(name, 12, color), (2 * K, y))
            y += 0
            continue
        d.line([(4 * K, y + 9 * K), (30 * K, y + 9 * K)], fill=rgba(color), width=K)
        d.line([(4 * K, y - 18 * K), (4 * K, y + 9 * K)], fill=rgba(color), width=K)
        im.alpha_composite(pixel_text(name, 12, color), (36 * K, y))
        if cm:
            im.alpha_composite(pixel_text(cm, 12, color), (118 * K, y))
        y += 28.4 * K
        y = int(y)
    return im


# ----------------------------------------------------------------------------- B5 window: clouds, girl, ribbons
def window_black():
    x0, y0, x1, y1 = WIN
    c = Canvas(x0, y0, x1, y1, k=1, ss=2)
    c.rect(x0, y0, x1, y1, fill=(0, 0, 0, 255))
    for i, col in enumerate(((232, 40, 40), (40, 190, 80), (40, 110, 230))):
        c.rect(x1 - 62 + i * 19, y0 + 2, x1 - 46 + i * 19, y0 + 16, fill=rgba(col), outline=(240, 240, 240, 255), width=0.8)
    return c


def clouds_photo():
    im = fit(gen('clouds.png'), PLATE_W, PLATE_H)
    return im


def clouds_sil():
    """white-on-blue two tone silhouette of the cloud photo (frames 104-105)"""
    im = fit(gen('clouds.png'), PLATE_W, PLATE_H).convert('RGB')
    a = np.asarray(im).astype(np.float32)
    white = (a.mean(axis=2) > 150) & ((a.max(axis=2) - a.min(axis=2)) < 90)
    out = np.zeros(a.shape[:2] + (4,), np.uint8)
    out[..., :3] = np.where(white[..., None], 255, np.array(ROYAL)).astype(np.uint8)
    out[..., 3] = 255
    return Image.fromarray(out, 'RGBA')


def clouds_sil_silver(a0=35.0):
    """the cloud region as a conic gradient around an apex inside the window: black at angle a0 (degrees, clockwise from 'right'),
    rising linearly to white one full turn later, with a hard edge (measured on 106-112: the edge turns from 39 to -47 deg);
    the sky stays royal blue"""
    im = fit(gen('clouds.png'), PLATE_W, PLATE_H).convert('RGB')
    a = np.asarray(im).astype(np.float32)
    white = (a.mean(axis=2) > 150) & ((a.max(axis=2) - a.min(axis=2)) < 90)
    h, w = white.shape
    x, y = grid(w, h)
    an = np.degrees(np.arctan2(y - 375.0, x - 230.0))              # apex measured in plate coordinates
    v = 0.71 * ((an - a0) % 360.0)
    out = np.zeros(a.shape[:2] + (4,), np.uint8)
    for i in range(3):
        out[..., i] = np.where(white, np.clip(v, 0, 255), ROYAL[i]).astype(np.uint8)
    out[..., 3] = 255
    return Image.fromarray(out, 'RGBA')


def girl_plate():
    im = gen('girl-gray.png')
    w, h = im.size
    im = im.crop((int(w * 0.18), 0, w, h))
    im = fit(im, 520, PLATE_H)
    a = np.asarray(im).copy()
    x = np.linspace(0, 1, a.shape[1])[None, :]
    a[..., 3] = (np.clip((x - 0.28) / 0.22, 0, 1) ** 1.6 * 255).astype(np.uint8)   # soft edge; the sky stays clear up to ~55 % of the plate
    return Image.fromarray(a, 'RGBA')


def ribbon(p0, p1, w0, w1, seed, bend=0.0, k=1, jag=0.35):
    """a crumpled paper ribbon from p0 to p1 (world), width w0->w1; returns Canvas"""
    rng = np.random.default_rng(seed)
    x0, y0 = p0
    x1, y1 = p1
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux
    n = max(6, int(L / 55))
    top, bot, mid = [], [], []
    for i in range(n + 1):
        t = i / n
        off = bend * math.sin(t * math.pi) + (rng.random() - 0.5) * 14
        cx_, cy_ = x0 + (x1 - x0) * t + nx * off, y0 + (y1 - y0) * t + ny * off
        w = (w0 + (w1 - w0) * t) * (1 + (rng.random() - 0.5) * jag)
        top.append((cx_ + nx * w / 2, cy_ + ny * w / 2))
        bot.append((cx_ - nx * w / 2, cy_ - ny * w / 2))
        mid.append((cx_, cy_))
    xs = [p[0] for p in top + bot]
    ys = [p[1] for p in top + bot]
    c = Canvas(min(xs) - 4, min(ys) - 4, max(xs) + 4, max(ys) + 4, k=k, ss=3)
    c.poly(top + bot[::-1], rgba(RIB))
    for i in range(n):
        if rng.random() < 0.45:           # darker facet
            a_, b_ = top[i], top[i + 1]
            m_ = mid[i] if rng.random() < 0.5 else mid[i + 1]
            c.poly([a_, b_, m_], rgba(RIB_D))
        if rng.random() < 0.3:
            c.poly([bot[i], bot[i + 1], mid[i + 1]], (246, 70, 140, 255))
    c.line(top, (255, 150, 190, 200), 0.8)
    return c


def white_wire(seed, x0, y0, x1, y1, n=26, col=(245, 245, 245, 230)):
    rng = np.random.default_rng(seed)
    c = Canvas(x0, y0, x1, y1, k=1, ss=3)
    p = (x0 + (x1 - x0) * rng.random(), y0 + (y1 - y0) * rng.random())
    pts = [p]
    for i in range(n):
        p = (min(max(p[0] + (rng.random() - 0.5) * (x1 - x0) * 0.5, x0 + 4), x1 - 4),
             min(max(p[1] + (rng.random() - 0.5) * (y1 - y0) * 0.5, y0 + 4), y1 - 4))
        pts.append(p)
    c.line(pts, col, 0.9)
    return c


# ----------------------------------------------------------------------------- B6 cluster / chain / icons
def cluster():
    c = Canvas(3595, 210, 3890, 505, k=K, ss=3)
    g = (218, 216, 216, 255)
    c.circle(3685, 335, 84, fill=g)
    c.circle(3800, 300, 84, fill=g)
    c.circle(3762, 412, 88, fill=g)
    im = c.done()
    # blue stippled ring on the top-right disc
    w, h = im.size
    x, y = grid(w, h)
    d = np.hypot(x - (3800 - 3595) * K, y - (300 - 210) * K) / K
    dens = np.clip((76 - d) / 34.0, 0, 1) * (d > 42)
    rng = np.random.default_rng(4)
    dots = (rng.random((h, w)) < dens * 0.9).astype(np.float32)
    a = np.asarray(im).astype(np.float32)
    for i, v in enumerate(ROYAL):
        a[..., i] = a[..., i] * (1 - dots) + v * dots
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def sprite(i, target_w):
    sheet = gen('y2k-sheet.png')
    boxes = components(sheet, min_area=6000)
    boxes.sort(key=lambda b: (b[1] > sheet.height * 0.45, b[0]))
    im = sheet.crop(boxes[i])
    w = int(target_w * K)
    return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)


def _bead(r):
    """one glassy bead sprite of radius r px"""
    n = int(2 * r + 6)
    c = n / 2.0
    x, y = grid(n, n)
    d = np.hypot(x - c, y - c)
    dl = np.hypot(x - (c - 0.28 * r), y - (c - 0.32 * r)) / (1.25 * r)
    rgb = lerp_color((196, 214, 255), (26, 56, 206), np.clip(dl, 0, 1) ** 1.3)
    ring = cov(np.abs(d - 0.56 * r) - 0.085 * r)[..., None] * 0.92
    rgb = rgb * (1 - ring) + 255.0 * ring
    spec = cov(np.hypot((x - (c - 0.36 * r)) / 1.4, y - (c - 0.40 * r)) - 0.13 * r)[..., None]
    rgb = rgb * (1 - spec) + 255.0 * spec
    edge = cov(np.abs(d - r + 1.6) - 1.6)[..., None]
    rgb = rgb * (1 - edge) + np.array((10, 22, 128), np.float32) * edge
    return from_arr(rgb, cov(d - r))


CHAIN_W, CHAIN_H = 199.9, 113.7        # = 306 x 174 screen px at the zoom of frames 105-122


def bead_chain2():
    """the bracelet alone: 13 pearl beads with white centres (GPT image redrawn from frame 107 of the source)"""
    im = gen('bead-chain2.png').convert('RGBA')
    a = np.asarray(im).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0).astype(np.uint8)
    im = Image.fromarray(a, 'RGBA')
    im = im.crop(im.getbbox())
    return im.resize((int(CHAIN_W * K), int(CHAIN_H * K)), Image.LANCZOS)


_CL = {}


def _cl_src():
    """the GPT sheet 'chain-cluster.png' (redrawn from frame 118): hard alpha, the glyph on the small blue badge painted over"""
    if 'a' not in _CL:
        a = np.asarray(gen('chain-cluster.png').convert('RGBA')).copy()
        a[..., 3] = np.where(a[..., 3] >= 235, 255, 0).astype(np.uint8)
        yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
        inb = (((xx - 792) / 34.0) ** 2 + ((yy - 433) / 48.0) ** 2) < 1.0
        m = inb & (a[..., :3].min(axis=2) > 150)
        a[m, 0], a[m, 1], a[m, 2] = 24, 84, 216
        _CL['a'] = a
    return _CL['a']


def _cl_mask(kind):
    a = _cl_src()
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]

    def poly(pts):
        im = Image.new('L', (w, h), 0)
        ImageDraw.Draw(im).polygon(pts, fill=255)
        return np.asarray(im) > 0

    def rect(x0, y0, x1, y1):
        return (xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)

    def circ(cx, cy, r):
        return (xx - cx) ** 2 + (yy - cy) ** 2 < r * r

    badge = ((xx - 792) / 41.0) ** 2 + ((yy - 433) / 55.0) ** 2 < 1.0
    win = (rect(791, 210, 1062, 414) | circ(795, 188, 83) | circ(1018, 497, 97) | rect(824, 541, 942, 759)) & ~badge
    bar = (poly([(374, 433), (835, 433), (925, 438), (925, 548), (598, 543), (374, 530)]) & ~win) | badge
    star = poly([(1167, 583), (1212, 688), (1314, 708), (1247, 772), (1232, 892), (1140, 812), (1033, 888), (1080, 768), (1013, 705), (1120, 688)])
    shard = poly([(1136, 786), (1528, 798), (1472, 874), (1213, 866)])
    m = {'bar': bar, 'win': win, 'monitor': rect(1056, 238, 1332, 432) & ~win, 'gbadge': circ(1340, 390, 37),
         'folder': rect(953, 598, 1114, 752) & ~rect(824, 541, 942, 759), 'star': star, 'shard': shard,
         'network': rect(1303, 618, 1457, 762) & ~star, 'pen': rect(1393, 483, 1492, 607)}[kind]
    return m & (a[..., 3] > 0)


def cl_bbox(kind):
    m = _cl_mask(kind)
    ys, xs = np.nonzero(m)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def cluster_piece(kind, tw, th):
    """one object (group) of the cluster sheet, resized to tw x th world px"""
    a = _cl_src().copy()
    a[..., 3] = np.where(_cl_mask(kind), 255, 0).astype(np.uint8)
    x0, y0, x1, y1 = cl_bbox(kind)
    im = Image.fromarray(a, 'RGBA').crop((x0, y0, x1, y1))
    return im.resize((max(2, int(round(tw * K))), max(2, int(round(th * K)))), Image.LANCZOS)


def info_dot():
    c = Canvas(4279, 334, 4297, 352, k=4, ss=3)
    c.circle(4288, 343, 6.5, fill=(250, 250, 250, 255), outline=(40, 40, 44, 255), width=0.7)
    c.text(4288, 343, 'i', 'georgiab.ttf', 9.5, (30, 30, 34, 255), anchor='mm')
    return c


def ruler_bar():
    c = Canvas(3628, 538, 3852, 567, k=K, ss=3)
    c.rect(3630, 540, 3850, 565, fill=(246, 246, 246, 255))
    for i in range(31):
        x_ = 3636 + i * 7.0
        c.line([(x_, 540), (x_, 546 if i % 5 else 551)], (40, 40, 40, 255), 0.8)
    im = c.done()
    w, h = im.size
    rng = np.random.default_rng(9)
    x, y = grid(w, h)
    dens = np.clip(1 - np.abs(x / w - 0.42) / 0.07, 0, 1)
    dots = (rng.random((h, w)) < dens * 0.8).astype(np.float32) * (np.asarray(im)[..., 3] > 0)
    a = np.asarray(im).astype(np.float32)
    for i, v in enumerate(ROYAL):
        a[..., i] = a[..., i] * (1 - dots) + v * dots
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def folders(n=11):
    c = Canvas(4284, 572, 4322, 1090, k=K, ss=3)
    for i in range(n):
        y = 580 + i * 47.0
        c.poly([(4290, y + 3), (4301, y + 3), (4304, y + 7), (4316, y + 7), (4316, y + 22), (4290, y + 22)], (236, 200, 60, 255), (150, 120, 20, 255), 0.6)
        c.rect(4290, y + 10, 4316, y + 22, fill=(250, 224, 110, 255))
    return c


# ----------------------------------------------------------------------------- B7 streaks
def streak(length, width, kind, seed=1):
    """long thin band; kind: 'blue' (grainy royal blue), 'white', 'navy'"""
    W_, H_ = int(length), max(2, int(round(width)))
    if kind == 'blue':
        rng = np.random.default_rng(seed)
        n = rng.random((H_, W_))
        v = np.where(n < 0.28, 1.0, 0.0)[..., None]
        rgb = np.array(ROYAL, np.float32) * (1 - v) + np.array((235, 240, 255), np.float32) * v
        return from_arr(rgb, np.ones((H_, W_), np.float32))
    col = (250, 250, 250) if kind == 'white' else (26, 36, 150)
    return from_arr(col, np.ones((H_, W_), np.float32))


# ----------------------------------------------------------------------------- B8 right side
def torn_paper():
    c = Canvas(4575, 425, 4960, 578, k=K, ss=3)
    rng = np.random.default_rng(12)
    top = [(4580, 500)]
    x = 4580.0
    while x < 4950:
        x += 8 + rng.random() * 16
        top.append((min(x, 4950), 440 + rng.random() * 22 + 30 * abs(math.sin((x - 4580) / 60.0))))
    c.poly(top + [(4950, 570), (4580, 570)], (246, 246, 246, 255))
    # paper plane
    c.poly([(4800, 492), (4915, 468), (4860, 508)], (226, 226, 220, 255), (90, 90, 80, 255), 0.6)
    c.poly([(4800, 492), (4860, 508), (4838, 512)], (190, 190, 180, 255), (90, 90, 80, 255), 0.6)
    c.poly([(4860, 508), (4915, 468), (4905, 500)], (206, 206, 196, 255), (90, 90, 80, 255), 0.6)
    c.text(4750, 515, '[cloud1]', 'Montserrat-Bold.ttf', 8.5, rgba(ROYAL), anchor='mm')
    return c


def cloud_card(qx, qy, w, h, label, blue=0.0):
    q = quadrant('photos-sheet.png', qx, qy)
    im = fit(q, w * K, h * K)
    if blue:
        a = np.asarray(im).astype(np.float32)
        lum = a[..., :3].mean(axis=2, keepdims=True)
        duo = np.array(ROYAL, np.float32) * (1 - lum / 255.0) + 255.0 * (lum / 255.0)
        a[..., :3] = a[..., :3] * (1 - blue) + duo * blue
        im = Image.fromarray(a.astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(im)
    f = font('Montserrat-Bold.ttf', 8.5 * K)
    d.text((im.width / 2, im.height / 2), label, font=f, fill=(250, 250, 250, 255), anchor='mm')
    return im


def kioku():
    c = Canvas(5050, 560, 5152, 598, k=K, ss=3)
    fnt = font('Source Han Sans SC|Heavy', 22 * c.f)
    im = text_img('【記憶】', fnt, (250, 250, 250, 255), pad=6, stroke=int(1.3 * c.f), stroke_fill=(16, 16, 16, 255))
    px_, py_ = c.P(5052, 562)
    c.paste(im, px_, py_)
    return c


def dict_text(color):
    c = Canvas(4572, 596, 5215, 812, k=K, ss=2)
    col = rgba(color)
    f = 'simsun.ttc'
    c.text(4580, 600, '記', f, 15, col)
    c.text(4580, 656, '英    /      m    e    m', f, 12, col)
    for x_, s in ((4580, '簡明釋義'), (4672, '牛津詞典'), (4762, '柯林斯詞典'), (5060, '詞根詞綴')):
        c.text(x_, 692, s, f, 12, col, tracking=6)
    for x_, s in ((4580, '記憶力'), (4648, '記憶'), (4706, '回憶'), (4764, '存儲器'), (4832, '記性'), (4888, '對死者的記憶'), (4985, '記憶所及的時期'), (5090, '回憶所及的範圍')):
        c.text(x_, 727, s, f, 11, col, tracking=1.5)
    c.text(4580, 760, '記', f, 12, col)
    c.text(5148, 760, '憶', f, 12, col)
    for x_, s in ((4580, 'memor-'), (4722, '記憶'), (4860, '+'), (4980, '-y'), (5110, '名詞后綴')):
        c.text(x_, 792, s, f, 11, col, tracking=1.0)
    return c


def counter_strip():
    c = Canvas(5075, 560, 5455, 648, k=K, ss=3)
    c.poly([(5080, 600), (5446, 566), (5446, 610), (5080, 642)], (18, 18, 20, 255))
    for i in range(8):
        x_ = 5100 + i * 43.0
        y_ = 608 - i * 4.0
        c.rect(x_, y_, x_ + 12, y_ + 12, fill=(60, 150, 230, 255))
        c.text(x_ + 6, y_ + 17, 'Counter opens at', 'arial.ttf', 3.6, (230, 230, 230, 255), anchor='ma')
        c.text(x_ + 6, y_ + 23, '05:30', 'arialbd.ttf', 5.0, (240, 240, 240, 255), anchor='ma')
        c.text(x_ + 20, y_ - 10, 'C%d' % (8 - i), 'arialbd.ttf', 6.0, (240, 150, 30, 255), anchor='ma')
    return c


def box_one():
    c = Canvas(5275, 436, 5482, 572, k=K, ss=3)
    c.rrect(5280, 476, 5445, 565, 4, fill=(214, 214, 214, 255), outline=(140, 140, 140, 255), width=0.6)
    fnt = font('georgiab.ttf', 30 * c.f)
    im = text_img('(1)', fnt, (236, 236, 236, 255), pad=6, stroke=int(1.2 * c.f), stroke_fill=(20, 20, 20, 255))
    px_, py_ = c.P(5288, 478)
    c.paste(im, px_, py_)
    # glove hand
    c.rrect(5378, 492, 5412, 548, 8, fill=(250, 250, 250, 255), outline=(30, 30, 30, 255), width=0.8)
    for i in range(4):
        c.rrect(5378 + i * 8.6, 480, 5385 + i * 8.6, 508, 3, fill=(250, 250, 250, 255), outline=(30, 30, 30, 255), width=0.7)
    c.rect(5376, 478, 5414, 484, fill=(60, 60, 60, 255))
    c.poly([(5415, 442), (5476, 442), (5445, 495)], (168, 168, 168, 255))
    c.circle(5283, 578 - 8, 6, fill=(40, 110, 230, 255))
    c.text(5283, 570, 'i', 'georgiab.ttf', 8, (255, 255, 255, 255), anchor='mm')
    return c


def red_arc():
    c = Canvas(5365, 625, 5475, 815, k=K, ss=3)
    c.arc(5460, 720, 85, 100, 250, (170, 28, 40, 255), 5.0)
    return c


def definete():
    c = Canvas(4716, 848, 4960, 900, k=K, ss=3)
    c.text(4722, 852, 'Definete', 'Abril Fatface|Regular', 17, (10, 10, 10, 255))
    c.line([(4820, 866), (4880, 866)], (10, 10, 10, 255), 1.0)
    c.poly([(4880, 862), (4888, 866), (4880, 870)], (10, 10, 10, 255))
    c.text(4905, 852, 'memory', 'Abril Fatface|Regular', 17, (10, 10, 10, 255))
    c.text(4760, 882, '3 小时 30 分钟', 'Deng.ttf', 6, (40, 40, 40, 255))
    return c


def arc_text_disc():
    c = Canvas(4486, 828, 4690, 1006, k=K, ss=3)
    c.pie(4585, 955, 96, 0, 180, (220, 220, 220, 255))
    txt = 'SHE BACK  •  YOU CAN’T BRING  '
    fnt = font('Montserrat-Medium.ttf', 9.5 * c.f)
    for i, ch in enumerate(txt):
        if ch == ' ':
            continue
        a_ = 176 - i * (172.0 / len(txt))
        gi = text_img(ch, fnt, (16, 16, 16, 255), pad=1).rotate(a_ - 90, resample=Image.BICUBIC, expand=True)
        px_, py_ = c.P(4585 + 82 * math.cos(math.radians(a_)), 955 - 82 * math.sin(math.radians(a_)))
        c.paste(gi, px_ - gi.width / 2, py_ - gi.height / 2)
    c.rect(4572, 836, 4640, 886, fill=(250, 250, 250, 255))
    c.poly([(4590, 836), (4640, 836), (4640, 886)], rgba(ROYAL))
    c.rect(4572, 872, 4608, 880, fill=(60, 60, 200, 255))
    c.arc(4592, 900, 16, 90, 300, (40, 40, 40, 255), 5.0)
    return c


def pink_arc():
    """big pink->white gradient arc on the far right (centre 5415,200 r 250)"""
    x0, y0, x1, y1 = 5150, -60, 5440, 470
    w, h = (x1 - x0) * K, (y1 - y0) * K
    x, y = grid(w, h)
    wx, wy = x / K + x0, y / K + y0
    d = np.hypot(wx - 5415, wy - 200)
    a = cov((np.abs(d - 250) - 12) * K) * sector_mask(x, y, (5415 - x0) * K, (200 - y0) * K, 105, 255)
    t = np.clip((wy - (-30)) / 430.0, 0, 1)
    rgb = grad_stops(t, [(0, (236, 20, 110)), (0.45, (244, 90, 150)), (0.8, (236, 200, 214)), (1, (190, 190, 190))])
    a2 = cov((np.abs(d - 224) - 2.5) * K) * sector_mask(x, y, (5415 - x0) * K, (200 - y0) * K, 110, 250)
    rgb = rgb * (1 - a2[..., None]) + 255.0 * a2[..., None]
    return from_arr(rgb, np.maximum(a, a2))


def blue_ellipse():
    c = Canvas(5200, 170, 5480, 290, k=K, ss=3)
    c.ellipse(5207, 182, 5363, 274, fill=rgba(ROYAL))
    fnt = font('SourceHanSerifSC-Heavy.otf', 62 * c.f)
    im = text_img('雲', fnt, (236, 236, 240, 255), pad=6, stroke=int(1.0 * c.f), stroke_fill=(90, 90, 100, 255))
    px_, py_ = c.P(5252, 176)
    c.paste(im, px_, py_)
    c.circle(5445, 220, 27, fill=rgba(PK))
    return c


def wire_mesh(seed=5):
    rng = np.random.default_rng(seed)
    c = Canvas(4740, 350, 5500, 850, k=1, ss=3)
    pts = [(4760 + rng.random() * 720, 370 + rng.random() * 460) for _ in range(46)]
    col = (150, 150, 150, 220)
    for i, p in enumerate(pts):
        d = sorted(range(len(pts)), key=lambda j: (pts[j][0] - p[0]) ** 2 + (pts[j][1] - p[1]) ** 2)
        for j in d[1:4]:
            c.line([p, pts[j]], col, 0.8)
    return c


def spiky_outline():
    c = Canvas(5290, -10, 5505, 420, k=1, ss=3)
    rng = np.random.default_rng(3)
    pts = []
    for i in range(22):
        a_ = i / 22.0 * 2 * math.pi
        r = 150 if i % 2 == 0 else 60 + rng.random() * 40
        pts.append((5420 + r * math.cos(a_) * 0.75, 210 + r * math.sin(a_) * 1.2))
    c.line(pts + [pts[0]], (150, 150, 150, 255), 0.9)
    return c


# ----------------------------------------------------------------------------- build
def build(sc):
    sc.sec = 'B'
    sc.kdef = K

    # ---------------- big disc behind everything: silver (122-130) -> blue (131-136) -> checker (137+) ----------------
    cx_, cy_ = DISC_C
    L = sc.add('B_disc_checker', disc_checker, cx_ - DISC_R - 2, cy_ - DISC_R - 2, k=1, crop=False)
    L.span(137)
    L = sc.add('B_disc_silver', disc_silver, cx_ - DISC_R - 2, cy_ - DISC_R - 2, k=1, crop=False, pivot=DISC_C)
    L.span(122, 133).set(pano=False).key('rotation', [(122, 0.0, LIN), (130, 28.0, LIN)]).key(
        'scale', [(122, [300, 300], HOLD), (124, [70, 70], HOLD), (125, [100, 100], HOLD)])       # fills the frame, snaps small, settles
    L = sc.add('B_disc_blue', disc_blue, cx_ - DISC_R - 2, cy_ - DISC_R - 2, k=1, crop=False, pivot=DISC_C)
    L.span(131, 137).set(pano=False).key('position', [(131, [cx_ + 75, cy_ + 20], HOLD), (132, [cx_ + 38, cy_ - 8], HOLD), (133, [cx_, cy_], HOLD)])

    # ---------------- mirrored circles ----------------
    sc.addc('B_circ_top', circles_b, False).span(86).wipe(86, 3, angle=-90)
    sc.addc('B_circ_bot', circles_b, True).span(90).wipe(90, 3, angle=-90)
    sc.add('B_grayline', thick_line, 2432, 362, 1101, 8, (120, 120, 120), pivot=(2432, 366)).span(88).key(
        'scale', [(88, [0, 100], LIN), (91, [100, 100], LIN)])
    sc.add('B_blueline', thick_line, 2548, 739, 988, 9, BL, pivot=(2548, 743)).span(91).key(
        'scale', [(91, [0, 100], LIN), (94, [100, 100], LIN)])
    sc.add('B_lab5921', ocr_text, 3405, 348, '[5921]', 13.0, BL).span(91)

    # ---------------- chrome shape ----------------
    # 82: flat blue silhouette on the ruler, 83: black, 84-85: close-up, 86: chrome, 87-88: blue again - all near x 2150 at about
    # full size; 89-90 it jumps to its frame 1.6x too large, then settles (centres / widths tracked on the source)
    sc.addc('B_chrome_frame', chrome_frame).span(96)
    ch = sc.add('B_chrome', chrome, 2959, 0, k=3)
    ch.y = 534 - ch.wh / 2
    ch.pivot = (3109.0, 534.0)
    ch.span(82).key('position', [(82, [2175, 541], HOLD), (83, [2156, 545], HOLD), (84, [2146, 541], HOLD), (86, [2133, 564], HOLD), (87, [2160, 536], HOLD),
                                 (88, [2165, 543], HOLD), (89, [3103, 527], HOLD), (91, [3118, 540], HOLD), (92, [3113, 540], HOLD), (95, [3109, 534], HOLD)])
    ch.key('scale', [(82, [89, 89], HOLD), (83, [96, 96], HOLD), (84, [100, 100], HOLD), (86, [102, 102], HOLD), (87, [97, 97], HOLD), (89, [160, 160], HOLD),
                     (91, [97, 97], HOLD), (95, [98, 98], HOLD)])
    ch.flashes([(82, BL), (83, (10, 10, 10)), (84, None), (87, BL), (89, None)])
    # 'Waitingfor(connect)': 86-88 at x 2272, 90-97 168 px further right, off on 89 and 92, white on the pink field (95-97)
    L = sc.add('B_waiting', waiting_text, 2272, 617)
    wx_, wy_ = L.pivot
    L.span(86, 98).set(pano=False)
    L.key('position', [(86, [wx_, wy_], HOLD), (90, [wx_ + 168.0, wy_], HOLD)])
    L.key('opacity', [(86, 100.0, HOLD), (89, 0.0, HOLD), (90, 100.0, HOLD), (92, 0.0, HOLD), (93, 100.0, HOLD)])
    L.flashes([(86, None), (95, (250, 250, 250))])
    L = sc.add('B_connect', connect_text, 2742, 603)
    L.span(98, 104).set(pano=False)

    # ---------------- labels / tree ----------------
    # (these two are also seen from the 98-103 shots, 58-60 px further right than from the black section)
    L = sc.addc('B_2100', label_2100)
    lx_, ly_ = L.pivot
    L.span(98).key('position', [(98, [lx_ + 58.0, ly_], HOLD), (104, [lx_, ly_], HOLD)])
    L = sc.add('B_tree_w', ascii_tree, 3466, 624, (240, 240, 240))
    lx_, ly_ = L.pivot
    L.span(103, 137).set(pano=False).key('position', [(103, [lx_ + 60.0, ly_], HOLD), (104, [lx_, ly_], HOLD)])
    sc.add('B_tree', ascii_tree, 3466, 624, (24, 24, 24)).span(137)

    # ---------------- the black window: slides in from the upper right on 100-103 ----------------
    WIN_IN = {100: (244.0, -142.0), 101: (233.0, -142.0), 102: (219.0, -142.0), 103: (208.0, -142.0)}
    L = sc.addc('B_window', window_black)
    lx_, ly_ = L.pivot
    L.span(100).key('position', [(f, [lx_ + dx, ly_ + dy], HOLD) for f, (dx, dy) in sorted(WIN_IN.items())] + [(104, [lx_, ly_], HOLD)])
    L = sc.add('B_clouds_pre', clouds_photo, PLATE[0], PLATE[1], k=1)
    lx_, ly_ = L.pivot
    L.span(100, 104).set(pano=False).key('position', [(f, [lx_ + dx + 3.0, ly_ + dy - 3.0], HOLD) for f, (dx, dy) in sorted(WIN_IN.items())])
    # the picture plate drifts in from the right (104-116) and then sinks to its place (115-122)
    DX = {104: 143, 105: 128, 106: 114, 107: 110, 108: 106, 109: 86, 110: 67, 111: 52, 112: 37, 113: 23, 114: 10, 115: 4}
    DY = {115: -130, 116: -117, 117: -95, 118: -72, 119: -50, 120: -29, 121: -14}
    slide = [(f, DX.get(f, 0.0), DY.get(f, -144.0 if f < 115 else 0.0)) for f in range(104, 123)]

    def plate_keys(L):
        px_, py_ = L.pivot
        L.key('position', [(f, [px_ + dx, py_ + dy], HOLD) for f, dx, dy in slide])
        return L

    L = plate_keys(sc.add('B_clouds_sil', clouds_sil, PLATE[0], PLATE[1], k=1))
    L.span(104, 106).set(pano=False)
    for f_, a0_ in ((106, 39.0), (107, 35.0), (108, 31.0), (109, 13.5), (110, -0.5), (111, -19.0), (112, -47.5), (113, -80.0)):
        L = sc.add('B_clouds_silver%d' % f_, clouds_sil_silver, PLATE[0] + DX.get(f_, 0.0), PLATE[1] - 144.0, a0_, k=1)
        L.span(f_, f_ + 1).set(pano=False)
    plate_keys(sc.add('B_clouds', clouds_photo, PLATE[0], PLATE[1], k=1)).span(114)
    L = plate_keys(sc.add('B_girl', girl_plate, PLATE[0] + PLATE_W - 520, PLATE[1], k=1))
    # dark and out of focus at first, sharpening in steps until the clouds photo lands (114)
    L.span(104).fx('ADBE Tint', **{'ADBE Tint-0001': [0.02, 0.02, 0.02, 1.0], 'ADBE Tint-0002': [0.42, 0.42, 0.44, 1.0],
                                   'ADBE Tint-0003': [(104, 100.0, HOLD), (110, 70.0, HOLD), (112, 40.0, HOLD), (114, 0.0, HOLD)]})
    L.fx('ADBE Gaussian Blur 2', **{'ADBE Gaussian Blur 2-0001': [(104, 46.0, HOLD), (106, 38.0, HOLD), (108, 28.0, HOLD), (110, 16.0, HOLD),
                                                                (112, 7.0, HOLD), (114, 0.0, HOLD)]})
    # white ruler strip: starts 531 px long further right (3875..4406 on 105) and slides / shrinks to its place by 112
    L = sc.add('B_rulerbar', ruler_bar, 3628, 538)
    L.pivot = (L.x, L.y + L.wh / 2)
    rb = {105: (3875, 4406), 106: (3840, 4033), 107: (3805, 3978), 108: (3770, 3947), 109: (3735, 3932), 110: (3700, 3917), 111: (3665, 3885),
          112: (L.x, L.x + L.ww)}
    L.span(105).key('position', [(f, [float(a_), L.pivot[1]], HOLD) for f, (a_, b_) in sorted(rb.items())]).key(
        'scale', [(f, [(b_ - a_) / L.ww * 100.0, 100.0], HOLD) for f, (a_, b_) in sorted(rb.items())])

    # ribbons: (name, p0 (near the focus), p1 (far end), w0, w1, seed, bend, start frame, white frames)
    F = (4390.0, 560.0)
    ribs = [((4550, 480), (3560, 1075), 26, 70, 1, -40, 110, 2), ((4540, 495), (3340, 1090), 22, 58, 2, 30, 113, 0),
            ((4570, 505), (3760, 1085), 20, 50, 3, -25, 113, 0), ((4520, 470), (3420, 930), 18, 44, 4, 46, 116, 0),
            ((4575, 515), (3960, 1090), 18, 40, 5, 12, 117, 0), ((4530, 478), (3300, 1010), 14, 34, 6, -60, 120, 0),
            ((4580, 500), (4120, 1085), 16, 34, 7, -14, 120, 0), ((4500, 462), (3560, 800), 12, 30, 8, 30, 122, 0)]
    for i, (p0, p1, w0, w1, seed, bend, f0, nw) in enumerate(ribs):
        L = sc.addc('B_rib%d' % i, ribbon, p0, p1, w0, w1, seed, bend)
        ang_ = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))        # travel direction (screen coords)
        L.span(f0).wipe(f0, 3, angle=ang_ - 90.0)
        if nw:
            L.flashes([(f0, (255, 255, 255)), (f0 + nw, None)])
    # crumpled arc over the top-left corner of the window
    arc = [((3500, 150), (3545, 250), 34, 40, 21), ((3545, 250), (3640, 292), 40, 50, 22), ((3640, 292), (3790, 300), 46, 40, 23),
           ((3790, 300), (3960, 318), 38, 44, 24), ((3960, 318), (4130, 340), 40, 36, 25), ((4130, 340), (4290, 420), 34, 30, 26),
           ((3545, 400), (3620, 470), 30, 40, 27), ((3520, 300), (3545, 400), 30, 30, 28)]
    for i, (p0, p1, w0, w1, seed) in enumerate(arc):
        L = sc.addc('B_arc%d' % i, ribbon, p0, p1, w0, w1, seed, 0.0)
        L.span(120).flashes([(120, (255, 255, 255)), (122, None)]).key('opacity', [(120, 100.0, HOLD), (121, 12.0, HOLD), (122, 100.0, HOLD)])
    top = [((3850, 428), (4050, 416), 104, 112, 31), ((4050, 416), (4300, 432), 112, 100, 32), ((4300, 432), (4575, 486), 100, 78, 33)]
    for i, (p0, p1, w0, w1, seed) in enumerate(top):
        L = sc.addc('B_arcT%d' % i, ribbon, p0, p1, w0, w1, seed, 0.0)
        L.set(pano=False)
        L.span(120, 124 if i == 0 else 122).flashes([(120, (255, 255, 255)), (122, None)]).key('opacity', [(120, 100.0, HOLD), (121, 12.0, HOLD), (122, 100.0, HOLD)])
    for i in range(3):
        L = sc.addc('B_wwire%d' % i, white_wire, 30 + i, 3700 + i * 250, 440 + i * 60, 4300 + i * 150, 1000)
        L.span(113 + i * 3)

    # cluster, chain, icons
    sc.add('B_cluster', cluster, 3595, 210).span(105)
    # The bracelet is a ring of 13 fused chrome pearls that TURNS (chain3d.py: 0.194 bead pitch per 30-fps source frame, conformed
    # to 24 fps, near row to the right).  Placement, fitted to the highlight blobs of the source (tools/chain_track.py):
    # glued to the SCREEN at (842,422) and full size on 105-131, shrinking to 0.913 and sliding on 132-136, and from 137 fixed in
    # the WORLD at about (4125,390).  It is uncovered from the right on 105-107.  One layer per frame (each a different pose).
    import chain3d
    place = {132: (850.0, 429.6, 0.973), 133: (850.5, 433.8, 0.937), 134: (846.5, 436.7, 0.913), 135: (830.2, 436.7, 0.913),
             136: (806.4, 436.4, 0.912)}
    trk = {137: 249.5, 138: 234.3, 139: 222.1, 140: 212.1, 141: 203.5, 142: 196.1, 143: 189.6, 144: 113.1, 145: 107.8, 146: 103.2,
           147: 99.0, 148: 95.0, 149: 91.4, 150: 87.8}
    wlast = sum(s2w(f, trk[f], 436.7)[0] for f in range(146, 151)) / 5.0
    BW, BH = chain3d.BOX[2], chain3d.BOX[3]
    wipe = {105: 41.6, 106: 20.5, 107: 5.7}
    for f in range(105, 164):
        if f <= 131:
            cx_, cy_, s_ = 842.0, 422.0, 1.0
        elif f <= 136:
            cx_, cy_, s_ = place[f]
        else:
            s_ = 0.913
            wx_ = s2w(f, trk[f], 436.7)[0] if f in trk else wlast
            cx_, cy_ = w2s(f, wx_, s2w(140, 0.0, 436.7)[1])
        z_ = zoom(f)
        wx0, wy0 = s2w(f, cx_ - BW * s_ / 2.0, cy_ - BH * s_ / 2.0)
        L = sc.add('B_chain_%03d' % f, chain3d.chain_frame, wx0, wy0, chain3d.src_index(f), chain3d.version(), k=chain3d.OUTK * z_ / s_, crop=False)
        L.span(f, f + 1).set(pano=(f == 140))
        if f in wipe:
            L.fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': wipe[f], 'ADBE Linear Wipe-0002': 90.0, 'ADBE Linear Wipe-0003': 0.0})
    # The desktop-icon group stays in the WORLD.  'bar' / 'win' share one mapping of the sheet (377,106)-(1114,757) -> world
    # (4101,364.3)-(4286,517.8); the other objects are fitted to the boxes measured on frames 110-118.
    GX0, GY0, GSX, GSY = 377.0, 106.0, 185.0 / 737.0, 153.5 / 651.0
    for kind, f0 in (('bar', 107), ('win', 110)):
        bx0, by0, bx1, by1 = cl_bbox(kind)
        sc.add('B_cl_' + kind, cluster_piece, 4101.0 + (bx0 - GX0) * GSX, 364.3 + (by0 - GY0) * GSY, kind, (bx1 - bx0) * GSX, (by1 - by0) * GSY,
               crop=False).span(f0)
    for kind, (x0_, y0_, x1_, y1_), f0 in (('monitor', (4273, 393, 4335, 435), 112), ('folder', (4283, 482, 4317, 512), 112),
                                           ('gbadge', (4340, 420, 4354, 434), 114), ('star', (4304, 484.5, 4377, 553), 116),
                                           ('shard', (4335, 522, 4456, 538), 116), ('network', (4384, 496, 4414, 522), 116),
                                           ('pen', (4433, 448, 4448, 469), 118)):
        L = sc.add('B_cl_' + kind, cluster_piece, x0_, y0_, kind, float(x1_ - x0_), float(y1_ - y0_), crop=False)
        L.span(f0)
    sc.add('B_icon4', sprite, 4382, 437, 4, 78.0).span(125).pop(125, 2, 0.4, over=1.2)
    sc.addc('B_info', info_dot).span(116)
    sc.addc('B_folders', folders).span(119).wipe(119, 3, angle=0)

    # ---------------- streak burst (120-126), pivot = where each band crosses the focus ----------------
    streaks = [(24, (4565, 500), 26, 'blue', 120), (56, (4565, 470), 14, 'white', 121), (22, (4580, 430), 9, 'blue', 122),
               (28, (4565, 445), 8, 'white', 123), (68, (4600, 420), 6, 'blue', 123), (40, (4565, 430), 5, 'navy', 124),
               (60, (4590, 420), 4, 'white', 124), (74, (4640, 400), 3, 'navy', 126), (13.5, (4565, 471), 4, 'navy', 126),
               (33, (4565, 455), 3, 'white', 126)]
    for i, (th, P_, wd, kind, f0) in enumerate(streaks):
        Lg = 3400
        L = sc.add('B_streak%d' % i, streak, P_[0] - Lg / 2, P_[1] - wd / 2.0, Lg, wd, kind, i, k=1, crop=False, pivot=P_)
        L.span(f0).set(rotation=-th)
        if i == 1:
            L.key('scale', [(f0, [8, 260], HOLD), (f0 + 1, [60, 200], HOLD), (f0 + 2, [100, 130], HOLD), (124, [100, 620], HOLD), (125, [100, 100], HOLD),
                            (127, [100, 520], HOLD), (128, [100, 100], HOLD)])
        else:
            L.key('scale', [(f0, [8, 300], LIN), (f0 + 2, [100, 170], LIN), (f0 + 4, [100, 100], LIN)])

    # ---------------- right side ----------------
    sc.addc('B_mesh', wire_mesh).span(127).wipe(127, 3, angle=-90)
    sc.add('B_cloud3', cloud_card, 4982, 262, 1, 1, 268, 248, '[cloud3]').span(130).pop(130, 2, 0.6)
    sc.add('B_cloud2', cloud_card, 4755, 560, 1, 1, 305, 150, '[cloud2]', blue=0.85).span(129).pop(129, 2, 0.6)
    sc.addc('B_torn', torn_paper).span(127).pop(127, 2, 0.6)
    L = sc.addc('B_dict_w', dict_text, (236, 236, 236))
    L.span(128, 137).set(pano=False)
    sc.addc('B_dict', dict_text, (70, 70, 70)).span(137)
    sc.addc('B_kioku', kioku).span(132)
    sc.addc('B_counter', counter_strip).span(137).wipe(137, 3, angle=-90).flashes([(137, PK), (139, None)])
    sc.addc('B_box1', box_one).span(137).pop(137, 2, 0.6)
    L = sc.addc('B_redarc', red_arc, pivot=(5460, 720))
    L.span(138).key('scale', [(138, [30, 30], LIN), (141, [100, 100], LIN)]).flashes([(138, PK), (146, None)])
    sc.addc('B_definete', definete).span(124)
    sc.addc('B_arctext', arc_text_disc).span(123).pop(123, 2, 0.6)
    sc.addc('B_spiky', spiky_outline).span(150)
    L = sc.add('B_pinkarc', pink_arc, 5150, -60, pivot=(5415, 200))
    L.span(137).flashes([(137, (255, 255, 255)), (152, None)]).key('rotation', [(137, -70.0, LIN), (150, -20.0, LIN), (153, 0.0, LIN)])
    sc.addc('B_ellipse', blue_ellipse).span(132)
    return sc
