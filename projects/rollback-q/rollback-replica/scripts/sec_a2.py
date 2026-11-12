"""Section A, part 2 (world x 1100..2760): code circle, QR circle, mint blocks, data table, mirrored blue bars, target."""
import math
import numpy as np
from lib import *
from PIL import ImageOps
from gen_util import s2w, pin, zoom, gen, quadrant, fit, gray, threshold
from sec_a import solid_rect, hgrad_rect, text_asset, circle_outline, PK, BL

K = 2
MINT = (20, 232, 184)
OCR = 'OCRAEXT.TTF'


# ----------------------------------------------------------------------------- code / QR circles
CODE_C, CODE_R = (1253.0, -118.0), 315.0


def code_circle():
    """big white disc (centre (1253, -118), radius 315 when fully grown) holding a code-editor screenshot (small text, upper
    part) and a few larger code lines below it"""
    cx_, cy_, R_ = CODE_C[0], CODE_C[1], CODE_R
    c = Canvas(cx_ - R_ - 2, cy_ - R_ - 2, cx_ + R_ + 2, cy_ + R_ + 2, k=K, ss=2)
    c.circle(cx_, cy_, R_, fill=(250, 251, 252, 255))
    kw, tx, num = (26, 58, 150, 255), (30, 34, 40, 255), (150, 152, 156, 255)
    # editor panel with a tab bar and a line-number gutter
    c.rect(1083, -402, 1422, -80, fill=(255, 255, 255, 255), outline=(206, 208, 212, 255), width=0.7)
    c.rect(1083, -402, 1422, -386, fill=(236, 237, 240, 255))
    c.rect(1090, -398, 1140, -389, fill=(250, 250, 250, 255))
    c.line([(1146, -394), (1158, -394)], (70, 70, 74, 255), 1.2)
    lines = ['let cellSize = 20;', 'let cols, rows;', '', 'let grid = [];', 'let ant;', '', 'let running = true;', 'let stepsPerFrame = 30;', '',
             'function setup() {', '  createCanvas(800, 800);', '', '  cols = floor(width / cellSize);', '  rows = floor(height / cellSize);', '',
             '  resetSimulation();', '}', '', 'function resetSimulation() {', '  grid = [];']
    fs = 9.4
    for i, ln in enumerate(lines):
        y = -378.0 + i * 14.3
        c.text(1101, y, str(i + 1), 'consola.ttf', fs * 0.9, num, anchor='ra')
        x = 1108.0
        for tok in ('let', 'function'):
            if ln.startswith(tok):
                c.text(x, y, tok, 'consola.ttf', fs, kw)
                x += font('consola.ttf', fs * c.f).getlength(tok) / c.f
                ln = ln[len(tok):]
                break
        if ln:
            c.text(x, y, ln, 'consola.ttf', fs, tx)
    for (y, s_) in ((-66, '0; x < cols; x++){'), (-40, '= 0; y < rows; y++) {'), (-14, 'y] = 0;'), (48, 'cols / 2),'), (67, 'rows / 2),'),
                    (86, '// 0上 1右 2下 3左'), (136, 'at(255);')):
        c.text(1172, y, s_, 'consola.ttf', 13.0, tx)
    # keep only what is inside the circle, then the outline
    im = c.im
    w, h = im.size
    xx, yy = grid(w, h)
    m = cov(np.hypot(xx - (cx_ - c.x0) * c.f, yy - (cy_ - c.y0) * c.f) - (R_ + 0.5) * c.f)
    a = np.asarray(im).copy()
    a[..., 3] = (a[..., 3] * m).astype(np.uint8)
    c.im = Image.fromarray(a, 'RGBA')
    c.d = ImageDraw.Draw(c.im)
    c.circle(cx_, cy_, R_, outline=(20, 20, 20, 255), width=1.0)
    return c


def qr_circle(seed=7, n=15, frac=1.0):
    """white disc (r 132) with a black / white cell pattern that has grown to `frac` of the disc (one red cell)"""
    r = 132.0
    size = int((2 * r + 4) * K)
    cc = size / 2.0
    rng = np.random.default_rng(seed)
    cells = rng.random((n, n)) < 0.52
    # a few big solid blocks, like the reference
    for _ in range(5):
        i, j = rng.integers(0, n - 3, 2)
        cells[i:i + rng.integers(2, 4), j:j + rng.integers(2, 4)] = bool(rng.integers(0, 2))
    x, y = grid(size, size)
    cs = 2 * r * K / n
    ix = np.clip(((x - (cc - r * K)) / cs).astype(int), 0, n - 1)
    iy = np.clip(((y - (cc - r * K)) / cs).astype(int), 0, n - 1)
    # the pattern spreads from a point left of / below the centre
    gx, gy = (n - 1) / 2.0 - 2.2 * (1 - frac), (n - 1) / 2.0 + 0.8 * (1 - frac)
    grown = np.maximum(np.abs(ix - gx), np.abs(iy - gy)) <= frac * (n / 2.0 + 2.5) + rng.random((n, n))[iy, ix] * 1.4 * (frac < 1.0)
    on = cells[iy, ix] & grown
    rgb = np.dstack([np.where(on, 6.0, 246.0)] * 3)
    red = (ix == int(round(gx)) + 1) & (iy == int(round(gy)))
    rgb = np.where(red[..., None], np.array((214, 30, 54), np.float32), rgb)
    d = np.hypot(x - cc, y - cc)
    edge = cov(np.abs(d - r * K) - 1.0)[..., None]
    rgb = rgb * (1 - edge) + 10.0 * edge
    return from_arr(rgb, cov(d - r * K - 1.0))


def top_marks():
    """three slanted ticks above the QR disc (74-77)"""
    c = Canvas(1618, -400, 1670, -236, k=K, ss=3)
    for i in range(3):
        y = -386 + i * 50.0
        c.line([(1660, y), (1632, y + 34)], (24, 24, 28, 255), 7.0)
    return c


def top_glyph():
    """the black glyph that replaces the ticks from 78"""
    return text_asset('再', 'A-OTF-RyuminPr5-Regular.otf', 118, (14, 14, 16))


def cursor():
    """big pixelated arrow pointer"""
    px = ['X..........', 'XX.........', 'XoX........', 'XooX.......', 'XoooX......', 'XooooX.....', 'XoooooX....', 'XooooooX...',
          'XoooooooX..', 'XooooooooX.', 'XoooooXXXXX', 'XooXooX....', 'XoX.XooX...', 'XX..XooX...', 'X....XooX..', '.....XooX..', '......XX...']
    u = 4 * K
    im = Image.new('RGBA', (11 * u, 17 * u), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for j, row in enumerate(px):
        for i, ch in enumerate(row):
            if ch == 'X':
                d.rectangle([i * u, j * u, i * u + u - 1, j * u + u - 1], fill=(150, 150, 156, 230))
            elif ch == 'o':
                d.rectangle([i * u, j * u, i * u + u - 1, j * u + u - 1], fill=(252, 252, 252, 235))
    return im


# ----------------------------------------------------------------------------- mint blocks
def mint_block(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    c = Canvas(min(xs) - 2, min(ys) - 2, max(xs) + 2, max(ys) + 2, k=K, ss=3)
    c.poly(pts, rgba(MINT))
    return c


def wide_label(s, size=20.0):
    return text_asset(s, 'arial.ttf', size, (8, 8, 8), sx=1.36)


def plus_button():
    r = 40.0
    size = int((2 * r + 6) * K)
    cc = size / 2.0
    x, y = grid(size, size)
    d = np.hypot(x - cc, y - cc) / (r * K)
    hl = np.hypot(x - cc * 0.86, y - cc * 0.62) / (r * K)
    rgb = lerp_color((120, 200, 255), (16, 96, 226), np.clip(hl, 0, 1) ** 0.9)
    rim = np.clip((d - 0.9) / 0.1, 0, 1)[..., None]
    rgb = rgb * (1 - rim) + np.array((10, 54, 150), np.float32) * rim
    img = from_arr(rgb, cov((d - 1.0) * r * K))
    dr = ImageDraw.Draw(img)
    t, l = 5.0 * K, 23.0 * K
    dr.rectangle([cc - l, cc - t, cc + l, cc + t], fill=(255, 255, 255, 255))
    dr.rectangle([cc - t, cc - l, cc + t, cc + l], fill=(255, 255, 255, 255))
    return img


def bw_photo(qx, qy, w, h, box=(0.2, 0.1, 0.8, 0.9), contrast=1.6, border=3):
    q = quadrant('photos-sheet.png', qx, qy)
    W_, H_ = q.size
    q = gray(q.crop((int(box[0] * W_), int(box[1] * H_), int(box[2] * W_), int(box[3] * H_))))
    q = fit(q, w * K, h * K)
    a = np.asarray(q).astype(np.float32)
    a[..., :3] = np.clip((a[..., :3] - 128) * contrast + 138, 0, 255)
    im = Image.fromarray(a.astype(np.uint8), 'RGBA')
    if border:
        out = Image.new('RGBA', (im.width + 2 * border * K, im.height + 2 * border * K), (250, 250, 250, 255))
        out.paste(im, (border * K, border * K))
        return out
    return im


def thumbs_row():
    c = Canvas(1340, 444, 1872, 540, k=K, ss=3)
    c.rect(1749, 470, 1798, 498, fill=(122, 150, 112, 255), outline=(60, 60, 60, 255), width=0.5)        # green landscape thumb
    c.rect(1756, 484, 1791, 498, fill=(96, 124, 84, 255))
    c.rect(1812, 479, 1862, 500, fill=(246, 246, 246, 255), outline=(130, 130, 130, 255), width=0.6)     # empty frame
    c.text(1773, 501, 'QQ截图', 'msyh.ttc', 6.5, (20, 20, 20, 255), anchor='ma')
    c.text(1773, 510, '2026080521 57', 'msyh.ttc', 6.5, (20, 20, 20, 255), anchor='ma')
    c.text(1773, 519, '05', 'msyh.ttc', 6.5, (20, 20, 20, 255), anchor='ma')
    c.text(1837, 503, '时间线_00543', 'msyh.ttc', 6.5, (20, 20, 20, 255), anchor='ma')
    items = [(1345, 448, 1418, 498, (14, 150, 130)), (1438, 450, 1470, 498, (96, 140, 60)), (1553, 462, 1608, 498, (20, 20, 24)),
             (1628, 452, 1658, 498, (40, 40, 44)), (1690, 452, 1720, 498, (70, 76, 70))]
    for (x0, y0, x1, y1, col) in items:
        c.rect(x0, y0, x1, y1, fill=rgba(col), outline=(60, 60, 60, 255), width=0.5)
    # video file icon + pink ring play mark
    c.poly([(1500, 452), (1528, 452), (1538, 462), (1538, 498), (1500, 498)], (246, 246, 246, 255), (120, 120, 120, 255), 0.6)
    c.circle(1522, 478, 9, fill=(40, 40, 46, 255), outline=rgba(PK), width=1.6)
    c.poly([(1519, 473), (1519, 483), (1527, 478)], (255, 255, 255, 255))
    for i in range(6):
        c.rect(1556 + i * 9, 464, 1561 + i * 9, 468, fill=(230, 230, 230, 255))
        c.rect(1556 + i * 9, 492, 1561 + i * 9, 496, fill=(230, 230, 230, 255))
    for (x_, a, b) in ((1580, '2026080521 56', '57'), (1643, '2026080521 57', '00'), (1705, '2026080521 57', '02')):
        c.text(x_, 501, 'QQ截图', 'msyh.ttc', 6.5, (20, 20, 20, 255), anchor='ma')
        c.text(x_, 510, a, 'msyh.ttc', 6.5, (20, 20, 20, 255), anchor='ma')
        c.text(x_, 519, b, 'msyh.ttc', 6.5, (20, 20, 20, 255), anchor='ma')
    return c


def jp_line():
    return text_asset('人間の時間に対する感知は、周囲の物事の変化に由来する。', 'A-OTF-RyuminPr5-Regular.otf', 10.5, (16, 16, 16), tracking=2.1)


def data_table(seed=3):
    c = Canvas(1136, 544, 1740, 668, k=K, ss=3)
    rng = np.random.default_rng(seed)
    cols = [(196, 60, 60), (60, 90, 200), (200, 150, 40), (60, 160, 120), (150, 150, 160), (120, 80, 170)]
    for r in range(17):
        y = 549 + r * 6.6
        c.rect(1141, y, 1146, y + 4, fill=(10, 10, 10, 255))
        c.rect(1149, y, 1154, y + 4, fill=(10, 10, 10, 255))
        c.rect(1160, y, 1165, y + 4, fill=rgba(cols[int(rng.integers(0, len(cols)))]))
        c.rect(1170, y + 0.5, 1170 + float(rng.integers(18, 46)), y + 3.2, fill=(120, 120, 124, 255))
        for bx in (1226, 1246):
            c.rect(bx, y, bx + 5, y + 4, fill=(10, 10, 10, 255))
            c.rect(bx + 7, y, bx + 12, y + 4, fill=(10, 10, 10, 255))
        for bx in (1276, 1310, 1346):
            c.rrect(bx, y - 0.4, bx + 26, y + 4.6, 1.2, fill=(12, 12, 12, 255))
            c.rect(bx + 3, y + 1.2, bx + 3 + float(rng.integers(8, 18)), y + 2.8, fill=(235, 235, 235, 255))
        for bx in (1392, 1440, 1472):
            c.rect(bx, y + 0.8, bx + float(rng.integers(16, 26)), y + 3.0, fill=(40, 70, 130, 255))
        if rng.random() < 0.3:
            c.rect(1418, y, 1436, y + 4, fill=(60, 200, 150, 255))
    # gantt-like bars
    c.line([(1520, 546), (1520, 664)], (40, 80, 200, 255), 1.0)
    bars = [(1522, 548, 1560, (40, 60, 150)), (1548, 554, 1592, (90, 110, 110)), (1522, 566, 1530, (40, 60, 150)), (1524, 578, 1540, (110, 80, 60)),
            (1556, 590, 1576, (60, 70, 160)), (1540, 598, 1556, (50, 60, 140)), (1522, 606, 1556, (120, 70, 60)), (1522, 613, 1552, (110, 60, 60)),
            (1522, 620, 1548, (40, 50, 120)), (1524, 627, 1728, (90, 110, 110)), (1524, 634, 1540, (250, 250, 250)), (1546, 634, 1728, (250, 250, 250)),
            (1524, 642, 1544, (250, 250, 250)), (1524, 650, 1536, (60, 70, 130))]
    for (x0, y0, x1, col) in bars:
        c.rect(x0, y0, x1, y0 + 5, fill=rgba(col), outline=(40, 40, 40, 255), width=0.4)
    return c


def spaced_text():
    c = Canvas(1122, 704, 1384, 856, k=K, ss=3)
    rows = ['As one grows older', 'Increased experience', 'People will become calm and silent',
            'But even though you appear calm and indifferent on the surface',
            'Memories piled up but bring you wounds that cannot be washed away', 'Hidden beneath silence is eternal chaos']
    for i, row in enumerate(rows):
        words = row.split(' ')
        y = 712 + i * 26.4
        n = len(words)
        fnt = font('courbd.ttf', 5.6 * c.f)
        widths = [fnt.getlength(w_) / c.f for w_ in words]
        gap = (250.0 - sum(widths)) / max(n - 1, 1)
        x = 1128.0
        for w_, ww_ in zip(words, widths):
            c.text(x, y, w_, 'courbd.ttf', 5.6, (20, 20, 20, 255))
            x += ww_ + gap
    return c


def red_lines2():
    c = Canvas(1178, 150, 1560, 772, k=K, ss=3)
    rd = (150, 28, 44, 255)
    c.line([(1185, 590), (1185, 765), (1550, 160)], rd, 0.9)
    c.line([(1185, 590), (1550, 160)], rd, 0.9)
    c.line([(1185, 520), (1185, 478), (1548, 478)], rd, 0.9)
    return c


def hill2():
    """wooded double hill behind the lamp: two rounded crowns (peaks 495 / 499, saddle at x 1438) with a clumpy dark canopy"""
    x0, y0, x1, y1 = 1224, 484, 1562, 541
    w, h = (x1 - x0) * K, (y1 - y0) * K
    x, y = grid(w, h)
    wx, wy = x / K + x0, y / K + y0
    b1 = 540 - 45 * np.sqrt(np.clip(1 - ((wx - 1335) / 105.0) ** 2, 0, 1))
    b2 = 540 - 41 * np.sqrt(np.clip(1 - ((wx - 1493) / 64.0) ** 2, 0, 1))
    top = np.minimum(b1, b2) + 1.8 * np.sin(wx * 0.55) + 1.4 * np.sin(wx * 1.3 + 1.0) + 1.0 * np.sin(wx * 2.9 + 0.4)
    a = cov((top - wy) * K) * cov((wy - 540) * K)
    rng = np.random.default_rng(31)
    small = rng.normal(0, 1, (h // 6 + 2, w // 6 + 2)).astype(np.float32)
    clump = np.asarray(Image.fromarray(small).resize((w, h), Image.BICUBIC))
    n = noise(h, w, 32, 6.0) + clump * 9.0
    shade = np.clip((wy - top) / 30.0, 0, 1)
    rgb = np.dstack([36 + n - 10 * shade, 46 + n * 1.15 - 12 * shade, 32 + n * 0.9 - 9 * shade])
    return from_arr(rgb, a)


def lamp2():
    c = Canvas(1340, 360, 1470, 542, k=K, ss=3)
    dg = (34, 34, 38, 255)
    c.line([(1367, 540), (1367, 392), (1375, 385), (1452, 381)], dg, 2.6)
    c.rect(1438, 378, 1458, 384.5, dg)
    c.line([(1367, 424), (1424, 392)], dg, 1.5)
    for (bx, by) in ((1368, 388), (1404, 381), (1431, 378)):               # birds sitting on the arm
        c.ellipse(bx - 4.5, by - 6, bx + 4.5, by - 1, fill=dg)
        c.circle(bx + 3.6, by - 7, 2.0, fill=dg)
    c.rect(1354, 498, 1378, 534, (232, 196, 40, 255))
    for yy in (504, 510, 516, 522, 528):
        c.line([(1357, yy), (1375, yy)], (150, 60, 30, 255), 1.0)
    return c


def jura(size, wght=400):
    """Jura (variable font) at a given weight - the rounded-square face of the 'dotnet build' line and of the text panel"""
    f = ImageFont.truetype(font_path('Jura|Light'), int(round(size)))
    try:
        f.set_variation_by_axes([wght])
    except Exception:
        pass
    return f


def jura_fit(s, width, color, wght=500, flip=False):
    """one line of Jura scaled so that the text is `width` world px wide"""
    w100 = jura(100, wght).getlength(s)
    size = 100.0 * width / w100
    im = text_img(s, jura(size * K, wght), rgba(color), pad=3)
    return im.transpose(Image.FLIP_TOP_BOTTOM) if flip else im


def dots4():
    c = Canvas(1705, 352, 1788, 370, k=K, ss=3)
    for i in range(4):
        c.circle(1713 + i * 22.0, 361, 5.2, outline=(40, 40, 44, 255), width=1.0)
    return c


def none_label():
    """small grey pill 'None will revive' that blinks below / above the ruler on 91-92"""
    c = Canvas(2560, 418, 2792, 456, k=K, ss=3)
    c.rrect(2563, 420, 2789, 454, 8, fill=(150, 150, 152, 255))
    fnt = jura(19.0 * c.f, 480)
    im = text_img('None will revive', fnt, (250, 250, 250, 255), pad=2)
    px_, py_ = c.P(2676, 437)
    c.paste(im, px_ - im.width / 2, py_ - im.height / 2)
    return c


# ----------------------------------------------------------------------------- bars group
def vgrad_rect(w, h, stops, k=K, grain_amt=3.0, seed=5):
    W_, H_ = int(w * k), int(h * k)
    x, y = grid(W_, H_)
    rgb = grad_stops(y / H_, stops) + noise(H_, W_, seed, grain_amt)[..., None]
    return from_arr(rgb, np.ones((H_, W_), np.float32))


def gray_rect():
    """grey tower: flat grey with a dark->white 'cylinder' gradient in its lowest third"""
    return vgrad_rect(100, 334, [(0.0, (168, 168, 168)), (0.52, (186, 186, 186)), (0.70, (176, 176, 176)), (0.705, (36, 36, 36)),
                                 (0.86, (150, 150, 150)), (1.0, (250, 250, 250))])


def violet_rect():
    return vgrad_rect(97, 342, [(0.0, (88, 92, 244)), (0.45, (98, 100, 236)), (1.0, (164, 166, 196))])


def cone():
    w, h = 72, 64
    W_, H_ = w * K, h * K
    x, y = grid(W_, H_)
    u = (x / W_ - 0.5) / np.maximum(y / H_, 1e-3) * 2.0            # -1..1 across the cone at this height
    a = cov((np.abs(u) - 1.0) * (y / H_) * W_ / 2.0)
    t = np.clip(u * 0.5 + 0.5, 0, 1)
    rgb = grad_stops(t, [(0, (20, 20, 20)), (0.3, (190, 190, 190)), (0.5, (250, 250, 250)), (0.68, (120, 120, 120)), (1, (16, 16, 16))])
    return from_arr(rgb, a)


def glyph_tile(ch, fname, w, h, size, dx=0.0, dy=0.0, rot=0.0, outline=False):
    c = Canvas(0, 0, w, h, k=K, ss=3)
    c.rect(0, 0, w, h, fill=(6, 6, 6, 255))
    if outline:
        fnt = font(fname, size * c.f)
        im = text_img(ch, fnt, (6, 6, 6, 255), pad=6, stroke=int(1.2 * c.f), stroke_fill=(250, 250, 250, 255))
        c.paste(im, w * c.f / 2 - im.width / 2 + dx * c.f, h * c.f / 2 - im.height / 2 + dy * c.f)
    else:
        c.text(w / 2 + dx, h / 2 + dy, ch, fname, size, (250, 250, 250, 255), anchor='mm', rot=rot)
    return c


def ocr_text(s, size, color, tracking=-1.2, flip=False):
    im = text_asset(s, OCR, size, color, tracking=tracking)
    return im.transpose(Image.FLIP_TOP_BOTTOM) if flip else im


def circles_set(mirror=False):
    """thin circles above the ruler (black) / mirrored below (blue)"""
    col = (28, 120, 230, 255) if mirror else (20, 20, 20, 255)
    y0, y1 = (545, 1085) if mirror else (-5, 535)
    c = Canvas(1880, y0, 2700, y1, k=K, ss=3)

    def Y(v):
        return 1080 - v if mirror else v
    c.circle(1940, Y(215), 48, outline=col, width=1.0)
    c.circle(2140, Y(180), 90, outline=col, width=1.0)
    c.circle(2140, Y(57), 45, outline=col, width=1.0)
    c.circle(2140, Y(57), 11, fill=(28, 120, 230, 255) if mirror else (130, 130, 130, 255))
    c.arc(2395, Y(250), 245, 95 if not mirror else -180, 180 if not mirror else -95, col, 1.0)
    return c


def cyl_bar():
    """black-white-black metallic bar under the ruler (world x 1390..2552), frames 75-83"""
    w, h = 1162, 64
    x, y = grid(w, h)
    wx = 1390.0 + x
    # black up to 1790, a long ramp to white at 2140, a glossy black cap 2143-2365, then white fading to light grey
    v = grad_stops(x / w, [(0.0, (3, 3, 3)), (0.344, (3, 3, 3)), (0.643, (250, 250, 250)), (0.6465, (250, 250, 250)), (0.648, (4, 4, 4)),
                           (0.838, (4, 4, 4)), (0.8395, (246, 246, 246)), (1.0, (224, 224, 224))])
    hl = np.exp(-((wx - 2254.0) / 70.0) ** 2) * np.exp(-((y - 50.0) / 9.0) ** 2) * 70.0 * ((wx > 2150) & (wx < 2358))
    return from_arr(v + hl[..., None], np.ones((h, w), np.float32))


def text_bar():
    """grey panel sitting on the ruler (1883..2432 x 478.5..532) with four justified rows of black Jura (row pitch 14.65)"""
    c = Canvas(1880, 476, 2436, 536, k=K, ss=3)
    c.rect(1883, 478.5, 2432, 532, fill=(126, 126, 126, 255))
    rows = ['Dreams are the only place we can escape from reality.', 'In dreams, consciousness collapses onto the timeline.',
            'Slowly it drifts towards the future.', 'The journey in dreams follows the law of time, it can only move forward.']
    fnt = jura(11.6 * c.f, 440)
    asc = fnt.getmetrics()[0]
    for i, row in enumerate(rows):
        words = row.split(' ')
        widths = [fnt.getlength(w_) / c.f for w_ in words]
        gap = (540.0 - sum(widths)) / max(len(words) - 1, 1)
        x = 1888.0
        base = 486.4 + i * 14.65                                   # baseline of the row
        for w_, ww_ in zip(words, widths):
            px_, py_ = c.P(x, base)
            c.d.text((px_, py_ - asc), w_, font=fnt, fill=(12, 12, 12, 255))
            x += ww_ + gap
    return c


# target: GPT cutout 'target-cutout.png' (redrawn from frames 100 / 103 of the source): transparent ground, dirt strip with
# animal-shaped holes, cream / purple / red / orange / yellow rings, dark marks scattered over everything
TGT_S = 0.3272                        # world px per sheet px (white ring radius 463 px = 151.5 world px)
TGT_X0, TGT_Y0 = 2234.3, 194.1        # world position of the sheet's top-left: disc centre (504.8, 559.8) px -> (2399.5, 377.3)
TGT_C = (2399.5, 377.3)
_TG = {}


def _tgt():
    if 'a' not in _TG:
        a = np.asarray(gen('target-cutout.png').convert('RGBA')).copy()
        a[..., 3] = np.where(a[..., 3] >= 128, 255, 0).astype(np.uint8)
        a[:, 1399:, 3] = 0                                  # the picture ends at world x 2692 on the source
        hh, ww = a.shape[:2]
        yy, xx = np.mgrid[0:hh, 0:ww]
        op = a[..., 3] > 0
        strip = op & (yy < 136 + 0.144 * xx)                # everything above the lower edge of the log
        marks = op & ~strip & (a[..., :3].max(axis=2) < 108)
        mm = Image.fromarray((marks * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(5))
        marks = np.asarray(mm) > 0                           # opening: drops the thin dark rim line of the rings
        _TG.update(a=a, strip=strip, marks=marks, d=np.hypot(xx - 504.8, yy - 559.8), op=op)
    return _TG


def _tgt_out(arr):
    im = Image.fromarray(arr, 'RGBA')
    return im.resize((int(round(im.width * TGT_S * K)), int(round(im.height * TGT_S * K))), Image.LANCZOS)


def target_photo(ver=2):
    return _tgt_out(_tgt()['a'])


def target_flip(ver=2):
    """the cutout upside down (the full-colour copy that appears 510 px to the left on frames 88-89)"""
    return _tgt_out(_tgt()['a'][::-1].copy())


def target_part(kind, col=None):
    """pieces of the cutout for the glitch frames 86-88: 'strip' / 'marks', in their own colours or as a flat silhouette"""
    t = _tgt()
    m = t['strip'] if kind == 'strip' else t['marks']
    if kind == 'marks':                                     # close pin holes
        mm = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
        m = np.asarray(mm) > 0
    out = t['a'].copy()
    if col is not None:
        out[..., 0], out[..., 1], out[..., 2] = col
    out[..., 3] = np.where(m, 255, 0).astype(np.uint8)
    return _tgt_out(out)


def target_disc(mode=0):
    """flat rings without the white one, centred on (0, 0): mode 0 = frame 88 (dark rim), mode 1 = frame 86 (plain red)"""
    R_ = 113.0
    c = Canvas(-R_ - 2, -R_ - 2, R_ + 2, R_ + 2, k=K, ss=3)
    if mode == 0:
        rings = [(1.0, (90, 40, 92)), (0.975, (197, 46, 60)), (0.78, (233, 63, 71)), (0.435, (236, 140, 72)), (0.22, (234, 214, 70))]
    else:
        rings = [(1.0, (227, 64, 87)), (0.435, (240, 150, 72)), (0.24, (238, 220, 74))]
    for fr, col in rings:
        c.circle(0, 0, R_ * fr, fill=rgba(col))
    return c


def target_sil(col):
    """the whole cutout as a flat silhouette (disc filled to the rim of the white ring), flipped top-bottom: the twin below the ruler"""
    t = _tgt()
    m = t['op'] | (t['d'] < 463.0)
    out = np.zeros(t['a'].shape, np.uint8)
    out[..., 0], out[..., 1], out[..., 2] = col
    out[..., 3] = np.where(m, 255, 0).astype(np.uint8)
    return _tgt_out(out[::-1].copy())


def stripes():
    """screen-filling vertical hairlines used on frames 85-88 (world space, tiles the area around the bars)"""
    x0, y0, x1, y1 = 1300, -400, 3900, 1500
    k = 1
    w, h = (x1 - x0) * k, (y1 - y0) * k
    x, y = grid(w, h)
    a = cov((np.abs(((x / k) % 22.0) - 11.0) - 0.8) * k) * 0.55
    return from_arr((120, 120, 124), a)


def guide(w, h, col=(40, 110, 230)):
    return new(max(2, int(w)), max(2, int(h)), rgba(col, 230))


def scrollbar(w, h):
    W_, H_ = int(w * K), int(h * K)
    x, y = grid(W_, H_)
    rgb = lerp_color((214, 214, 214), (168, 172, 174), np.clip(y / H_, 0, 1))
    a = cov(sd_box(x, y, W_ / 2, H_ / 2, W_ / 2, H_ / 2, 8 * K))
    return from_arr(rgb, a * 0.9)


# ----------------------------------------------------------------------------- build
def build(sc):
    sc.sec = 'A'
    sc.kdef = K

    # ---------------- hill behind the mint blocks (the lamp stands in front of them, see below) ----------------
    sc.add('A_hill', hill2, 1224, 484).span(44).flash(44, PK, 1)

    # ---------------- code + QR circles (frame 71, QR pattern flickers) ----------------
    # code disc: grows from 43 % (71) to full size (radius 137 -> 242 -> 272 -> 298 -> 315, fitted on the source)
    L = sc.addc('A_codecircle', code_circle, pivot=CODE_C, crop=False)
    L.span(71).key('scale', [(71, [43.5, 43.5], HOLD), (72, [77.0, 77.0], HOLD), (73, [82.0, 82.0], HOLD), (74, [86.5, 86.5], LIN), (78, [94.7, 94.7], LIN),
                             (82, [97.1, 97.1], LIN), (90, [100.0, 100.0], LIN)])
    # QR disc: full size from the start, the cell pattern spreads over it
    for i, (f0, f1, frac) in enumerate(((71, 72, 0.16), (72, 74, 0.3), (74, 78, 0.6), (78, 82, 0.84), (82, 272, 1.0))):
        L = sc.add('A_qr%d' % i, qr_circle, 1508 - 134, 135 - 134, 7, 15, frac, pivot=(1508, 135), crop=False)
        L.span(f0, f1)
        if i < 4:
            L.set(pano=False)
    sc.addc('A_topmarks', top_marks).span(74, 78).set(pano=False)
    sc.add('A_topglyph', top_glyph, 1596, -306).span(78)
    L = sc.add('A_cursor', cursor, 1118, 60)
    L.span(56).key('position', [(56, [1030, 30], LIN), (59, [L.pivot[0], L.pivot[1]], LIN)])

    # ---------------- mint blocks: 53 (slides up), 59, 65 ----------------
    b3 = sc.addc('A_mint3', mint_block, [(1326, 444), (1647, 430), (1647, 505), (1326, 512)])
    p3 = b3.pivot
    b3.span(53).key('position', [(53, [p3[0], p3[1] + 40], HOLD), (54, [p3[0], p3[1] + 16], HOLD), (55, [p3[0], p3[1]], HOLD)])
    sc.addc('A_mint2', mint_block, [(1340, 350), (1645, 344), (1645, 420), (1340, 424)]).span(59)
    sc.addc('A_mint1', mint_block, [(1324, 256), (1631, 238), (1631, 326), (1324, 330)]).span(65)
    L = sc.add('A_lab_cant', wide_label, 1320, 425, '(CANT-1)')
    L.span(53).key('position', [(53, [L.pivot[0], L.pivot[1] + 40], HOLD), (54, [L.pivot[0], L.pivot[1] + 16], HOLD), (55, [L.pivot[0], L.pivot[1]], HOLD)])
    sc.add('A_lab_sleep', wide_label, 1535, 323, '(SLEEP-2)').span(59)
    sc.add('A_lab_well', wide_label, 1320, 233, '(WELL-3)').span(65)
    sc.add('A_ph1', bw_photo, 1622, 214, 1, 0, 70, 78, box=(0.1, 0.2, 0.6, 0.95)).span(65)
    sc.add('A_ph2', bw_photo, 1542, 276, 0, 0, 66, 46, box=(0.45, 0.25, 0.85, 0.6)).span(59)
    sc.add('A_ph3', bw_photo, 1478, 308, 0, 1, 54, 72, box=(0.3, 0.05, 0.7, 0.75)).span(54).pop(54, 2, 0.5)
    sc.add('A_plus', plus_button, 1375 - 43, 350 - 43, pivot=(1375, 350), crop=False).span(74).pop(74, 2, 0.3, over=1.15)
    sc.addc('A_thumbs', thumbs_row).span(59).wipe(59, 3, angle=-90)
    sc.addc('A_lamp', lamp2).span(44).flashes([(44, PK), (45, None), (46, (226, 20, 60)), (47, None)])
    # caption line: appears with the paper sheet on 27, 367 px left of its place, creeps right (27-31), jumps home on 38
    L = sc.add('A_jp', jp_line, 1137, 296)
    jx, jy = L.pivot
    L.span(27).key('position', [(27, [jx - 367.0, jy], HOLD), (28, [jx - 354.0, jy], HOLD), (29, [jx - 339.0, jy], HOLD), (30, [jx - 324.0, jy], HOLD),
                                (31, [jx - 277.5, jy], HOLD), (38, [jx, jy], HOLD)])

    # ---------------- data table / text ----------------
    sc.addc('A_table', data_table).span(54).wipe(54, 3, angle=180)
    sc.addc('A_spaced', spaced_text).span(56).blink([56, 57, 58])
    sc.addc('A_redlines2', red_lines2).span(47).wipe(47, 3, angle=-90)

    # ================= mirrored bars group =================
    T_CMD = r'C:\World\CE\<File2xxx> dotnet build'
    # ---- phase 1 (70-83): a flickering sketch of the group around x 1640-2030, doubled in a mirror below the ruler.
    #      None of it is where the finished group ends up; every element was read off world-aligned crops of the source.
    P1 = range(70, 86)

    def vis(L, frames):
        L.key('opacity', [(f, 100.0 if f in frames else 0.0, HOLD) for f in P1])
        return L

    def mirrored(name, fn, x, y, *args, frames=None, rot=0.0, **kw):
        top = sc.add(name, fn, x, y, *args, **kw)
        bot = sc.clone(name + '_m', top)
        bot.y = 1080.0 - (top.y + top.wh)
        bot.pivot = (top.pivot[0], 1080.0 - top.pivot[1])
        bot.set(scale=[100.0, -100.0])
        for L, r_ in ((top, rot), (bot, -rot)):
            if rot:
                L.set(rotation=r_)
            L.span(70, 84).set(pano=False)
            if frames is not None:
                vis(L, frames)
        return top, bot

    L = sc.add('A_p1_tower', solid_rect, 1696, 203, 100, 678, (252, 252, 252))
    vis(L.span(70, 84).set(pano=False), {75, 77, 79, 80, 81, 82})
    mirrored('A_p1_text', jura_fit, 1669, 266, T_CMD, 376.0, (40, 40, 44), 640, frames=set(range(71, 83)))
    mirrored('A_p1_brk', text_asset, 1676, 343, '[', 'arialbd.ttf', 30, (46, 34, 34), frames=set(range(70, 83)))
    mirrored('A_p1_dots', dots4, 1705, 352, frames=set(range(74, 83)))
    mirrored('A_p1_c1', circle_outline, 1789 - 93.6, 414 - 93.6, 91.0, 1.2, (24, 24, 28), frames={70, 72, 74, 75, 76, 77, 78, 79, 80, 82}, crop=False)
    mirrored('A_p1_c2', circle_outline, 1879 - 93.6, 414 - 93.6, 91.0, 1.2, (24, 24, 28), frames={74, 76, 78, 79, 81, 82}, crop=False)
    mirrored('A_p1_gray', gray_rect, 1823, 76, frames={78, 80, 82})
    mirrored('A_p1_violet', violet_rect, 1929, 68, frames={82})
    mirrored('A_p1_k', glyph_tile, 1826 - 39.5, 398 - 39.5, 'k', 'timesbi.ttf', 79, 79, 86, dy=-7, frames={79, 80, 81, 82}, rot=-25.0)
    mirrored('A_p1_ii', text_asset, 1731, 422, 'ii', 'arialbd.ttf', 24, (34, 34, 38), frames=set(range(77, 83)))
    # selection guides that jump from frame to frame (one vertical, a mirrored pair of horizontals)
    gcol = (24, 44, 170)
    vx = {73: 1675, 74: 1681, 75: 1681, 76: 1681, 77: 1745, 78: 1681, 79: 1827, 80: 1925, 81: 1906, 84: 1861, 85: 1861}
    L = sc.add('A_p1_vline', guide, 1675, -700, 1.8, 2500, gcol, k=1, crop=False)
    L.pivot = (1675.9, 550.0)
    L.span(70, 86).set(pano=False)
    L.key('position', [(f, [float(vx.get(f, 1675)), 550.0], HOLD) for f in P1])
    vis(L, set(vx))
    for nm, ys in (('A_p1_hline', {74: 204, 75: 204, 76: 204, 77: 204, 78: 204, 79: 397, 80: 361, 81: 361}),
                   ('A_p1_hline_m', {74: 849, 75: 849, 76: 849, 77: 849, 78: 849, 79: 685, 80: 719, 81: 719})):
        L = sc.add(nm, guide, 600, 397, 4200, 1.8, gcol, k=1, crop=False)
        L.pivot = (2700.0, 397.9)
        L.span(70, 84).set(pano=False)
        L.key('position', [(f, [2700.0, float(ys.get(f, 397))], HOLD) for f in P1])
        vis(L, set(ys))

    # ---- phase 2 (86-): the finished group
    # guides: thin blue lines that criss-cross while the camera is pulled far out
    for i, (x_, y_, w_, h_, f0, f1) in enumerate(((1690, -700, 1.6, 2500, 86, 98), (0, 330, 4800, 1.6, 86, 98), (0, 748, 4800, 1.6, 86, 98),
                                                  (2110, -700, 1.6, 2500, 86, 98), (0, 150, 4800, 1.6, 86, 98))):
        sc.add('A_guide%d' % i, guide, x_, y_, w_, h_, k=1, crop=False).span(f0, f1).set(pano=False)
    # on the source the guides run BEHIND the ring group (pink / blue sectors, record): move them down in the stack
    gl = [L_ for L_ in sc.layers if L_.name.startswith('A_guide')]
    for L_ in gl:
        sc.layers.remove(L_)
    gi = [i for i, L_ in enumerate(sc.layers) if L_.name == 'A_buildings'][0] + 1
    sc.layers[gi:gi] = gl
    L = sc.add('A_stripes', stripes, 1300, -400, k=1, crop=False)
    L.span(85, 89).set(pano=False)

    sc.addc('A_circ_top', circles_set, False).span(86)
    sc.addc('A_circ_bot', circles_set, True).span(86).wipe(86, 3, angle=-90)

    sc.addc('A_textbar', text_bar).span(82)
    # 75-82: a black-white metallic bar runs along the ruler first (head grows right, then the tail follows it out)
    from sec_a import _two_wipes
    L = sc.add('A_cylbar', cyl_bar, 1390, 543, k=1)
    L.span(75, 83).set(pano=False)
    _two_wipes(L, 1390.0, 1162.0, [(75, 2277), (76, 2414), (77, 2500), (78, 2540), (79, 2552)],
               [(75, 1390), (80, 1690), (81, 2000), (82, 2308)])
    sc.add('A_w1', solid_rect, 1715, 395, 98, 147, (255, 255, 255)).span(86)
    sc.add('A_w2', solid_rect, 1852, 326, 98, 216, (255, 255, 255), pivot=(1901, 540)).span(86)
    sc.add('A_grayrect', gray_rect, 1978, 198).span(86)
    sc.add('A_violet', violet_rect, 2115, 198).span(86)
    sc.addc('A_tile_z', glyph_tile, 'Z', 'Montserrat-BlackItalic.ttf', 50, 57, 84, dx=6, dy=-8, rot=0).span(86)
    sc.get('A_tile_z').x += 1793
    sc.get('A_tile_z').y += 338
    sc.get('A_tile_z').pivot = (1818, 366)
    sc.addc('A_tile_re', glyph_tile, 'Re', 'Press Start 2P|Regular', 34, 26, 11).span(86)
    sc.get('A_tile_re').x += 1716
    sc.get('A_tile_re').y += 388
    sc.get('A_tile_re').pivot = (1733, 401)
    sc.addc('A_tile_ce', glyph_tile, 'CE', 'timesbd.ttf', 62, 42, 46, dy=2).span(88)
    sc.get('A_tile_ce').x += 2152
    sc.get('A_tile_ce').y += 507
    sc.get('A_tile_ce').pivot = (2183, 528)
    sc.addc('A_tile_k', glyph_tile, 'k', 'timesbi.ttf', 76, 74, 92, dy=-8).span(86)
    sc.get('A_tile_k').x += 1954
    sc.get('A_tile_k').y += 470
    sc.get('A_tile_k').pivot = (1992, 507)
    L = sc.add('A_cone', cone, 1879, 470)
    cx_, cy_ = L.pivot
    L.span(72).key('position', [(72, [cx_ + 12.0, cy_ + 89.0], HOLD), (73, [cx_, cy_], HOLD)])       # first frame: hangs under the ruler
    sc.add('A_ocr', jura_fit, 1822, 397, T_CMD, 414.0, (56, 56, 60), 620).span(86)

    # blue bars: partial 87, more 88, OFF 89, all from 90
    blue = [('A_blueA', 1717, 510, 98, 198), ('A_blueA2', 1797, 706, 48, 62), ('A_blueC', 1853, 444, 100, 334),
            ('A_blueD', 1980, 572, 100, 336), ('A_blueE', 2115, 555, 98, 353)]
    first = {'A_blueA': 88, 'A_blueA2': 97, 'A_blueC': 97, 'A_blueD': 97, 'A_blueE': 97}       # the mirrored towers only turn up on 97
    for (nm, x_, y_, w_, h_) in blue:
        # 97-101: a white copy slides out from under every mirrored blue piece (same offsets as under the target's twin)
        Lw = sc.add(nm + '_w', solid_rect, x_, y_, w_, h_, (250, 250, 250))
        wx_, wy_ = Lw.pivot
        Lw.span(97, 102).set(pano=False).key('position', [(f, [wx_ + dx, wy_ + dy], HOLD) for f, dx, dy in (
            (97, 25.0, 6.0), (98, -45.0, -10.0), (99, -50.0, -10.0), (100, -17.0, -6.0), (101, -5.0, -2.0))])
        L = sc.add(nm, solid_rect, x_, y_, w_, h_, BL)
        f0 = first[nm]
        L.span(f0).blink([f0, 89, 90] if f0 < 89 else [f0])
    sc.add('A_ocr_mirror', jura_fit, 1822, 668, T_CMD, 414.0, BL, 620, True).span(90)
    sc.add('A_bluestrip', solid_rect, 2227, 556, 163, 18, BL).span(90)
    sc.add('A_2050', text_asset, 2316, 552, '2050', 'Montserrat-Regular.ttf', 19, (10, 20, 40), tracking=-1.0).span(84)
    sc.add('A_tinystrip', solid_rect, 2390, 560, 240, 7, (24, 24, 24)).span(90)

    # target: GPT cutout (transparent ground).  86-88 are glitch frames on the source: strip and marks as flat blue silhouettes,
    # the rings without the white one and larger (x1.27 on 86, x1.18 on 88, none on 87), only x < 2536 on 86 and x < 2667 on 87
    # (left part photographic with black marks, right part blue); the finished cutout from 89.
    TW = 1462 * TGT_S

    def clip(L, lo=None, hi=None):
        if lo is not None:
            L.fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': 100.0 * (lo - TGT_X0) / TW, 'ADBE Linear Wipe-0002': 90.0, 'ADBE Linear Wipe-0003': 0.0})
        if hi is not None:
            L.fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': 100.0 * (TGT_X0 + TW - hi) / TW, 'ADBE Linear Wipe-0002': -90.0, 'ADBE Linear Wipe-0003': 0.0})
        return L
    TB = (84, 92, 242)
    for f_, mode, sc_ in ((86, 1, 126.5), (88, 0, 117.7)):
        L = sc.addc('A_tgt_disc%d' % f_, target_disc, mode)
        L.x += TGT_C[0]
        L.y += TGT_C[1]
        L.pivot = TGT_C
        L.span(f_, f_ + 1).set(pano=False, scale=[sc_, sc_])
    clip(sc.add('A_tgt_strip', target_part, TGT_X0, TGT_Y0, 'strip', crop=False).span(87, 88).set(pano=False), hi=2536.0)
    clip(sc.add('A_tgt_marks', target_part, TGT_X0, TGT_Y0, 'marks', crop=False).span(87, 88).set(pano=False), hi=2536.0)
    for nm, kind in (('A_tgt_stripB', 'strip'), ('A_tgt_marksB', 'marks')):
        src_ = sc.add(nm, target_part, TGT_X0, TGT_Y0, kind, TB, crop=False)
        clip(src_.span(86, 87).set(pano=False), hi=2536.0)
        clip(sc.clone(nm + '87', src_).span(87, 88).set(pano=False), lo=2536.0, hi=2667.0)
        sc.clone(nm + '88', src_).span(88, 89).set(pano=False)
    sc.add('A_target', target_photo, TGT_X0, TGT_Y0, 2, crop=False).span(89)
    # The twin below the ruler is the flipped silhouette in flat blue (mirror line y = 558).  It sits 510 px further left at first
    # (88-96, a plain copy on 88-89) and jumps under the target on 97, where a white copy slides out from under it (97-101).
    TWY = 1116.0 - (TGT_Y0 + 1076 * TGT_S)
    L = sc.add('A_target_copy', target_flip, TGT_X0 - 510.0, TWY, 2, crop=False)
    L.span(88, 90).set(pano=False)
    # on 86 / 87 that copy is still on its way up from below the frame (screen boxes read off the source)
    for f_, (sx0, sy0, sx1, sy1) in ((86, (468, 844, 688, 1064)), (87, (632, 704, 832, 844))):
        w0, w1 = s2w(f_, sx0, sy0), s2w(f_, sx1, sy1)
        Lc = sc.clone('A_target_copy%d' % f_, L)
        Lc.x, Lc.y = (w0[0] + w1[0]) / 2.0 - 504.8 * TGT_S, (w0[1] + w1[1]) / 2.0 - (1076 - 559.8) * TGT_S
        Lc.pivot = (Lc.x + Lc.ww / 2.0, Lc.y + Lc.wh / 2.0)
        Lc.span(f_, f_ + 1).set(pano=False)
    L = sc.add('A_target_wht', target_sil, TGT_X0, TWY, (250, 250, 250), crop=False)
    wx_, wy_ = L.pivot
    L.span(97, 102).set(pano=False).key('position', [(f, [wx_ + dx, wy_ + dy], HOLD) for f, dx, dy in (
        (97, 25.0, 6.0), (98, -45.0, -10.0), (99, -50.0, -10.0), (100, -17.0, -6.0), (101, -5.0, -2.0))])
    L = sc.add('A_target_blue', target_sil, TGT_X0, TWY, (12, 137, 247), crop=False)
    tx, ty = L.pivot
    L.span(90).key('position', [(90, [tx - 510.0, ty], HOLD), (97, [tx, ty], HOLD)])
    L = sc.addc('A_none', none_label)
    nx_, ny_ = L.pivot
    # it climbs about 276 px per frame from below the frame (89) to above the ruler and off the top
    L.span(89, 96).set(pano=False).key('position', [(f, [nx_, ny_ + dy], HOLD) for f, dy in ((89, 825.0), (90, 551.0), (91, 273.0), (92, -3.0),
                                                                                          (93, -279.0), (94, -482.0), (95, -379.0))])
    sc.add('A_areyou', ocr_text, 2702, 196, 'Are you', 20.0, (60, 60, 64)).span(88)
    sc.add('A_areyou_m', ocr_text, 2704, 884, 'Are you', 20.0, BL, flip=True).span(90)

    # tall grey rounded block: drops in from the top (86-88), spans the whole frame height while it jumps sideways (89-91) and
    # sinks away (92-95); a narrower one tags along on 87-90.  Boxes (x0, x1, y0, y1) read off world-aligned crops of the source.
    for nm, (w_, h_), boxes in (
            ('A_scroll1', (240, 1100), {86: (2611, 2767, -212, 92), 87: (2707, 2922, -700, 325), 88: (2730, 2959, -700, 762),
                                        89: (2567, 2800, -700, 1214), 90: (2574, 2815, -700, 1500), 91: (3089, 3341, -700, 1500),
                                        92: (3100, 3341, 40, 1500), 93: (3107, 3348, 733, 1500), 94: (3133, 3381, 1410, 1500),
                                        95: (3160, 3408, 1355, 1500)}),
            ('A_scroll2', (110, 500), {87: (2922, 3026, 1066, 1281), 88: (2959, 3070, 888, 1325), 89: (2800, 2915, 677, 1355),
                                       90: (2815, 2926, 436, 1362)})):
        L = sc.add(nm, scrollbar, 2600, 0, w_, h_)
        L.pivot = (L.x, L.y)
        fr = sorted(boxes)
        L.span(fr[0], fr[-1] + 1).set(pano=False)
        L.key('position', [(f, [float(boxes[f][0]), float(boxes[f][2])], HOLD) for f in fr])
        L.key('scale', [(f, [(boxes[f][1] - boxes[f][0]) / float(w_) * 100.0, (boxes[f][3] - boxes[f][2]) / float(h_) * 100.0], HOLD) for f in fr])
    return sc
