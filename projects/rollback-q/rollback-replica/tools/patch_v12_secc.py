"""v12: section C (frames 144-196): GPT card / escalator / church / line art, wire blobs, thick RGB bars, sign, toggle, labels ..."""
import io
P = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts\sec_c.py'
s = io.open(P, encoding='utf-8').read()


def repl_func(src, name, new):
    i = src.index('\ndef %s(' % name) + 1
    j = src.index('\n\n\n', i)
    return src[:i] + new.strip('\n') + src[j:]


def repl(src, old, new):
    assert src.count(old) == 1, (old[:80], src.count(old))
    return src.replace(old, new)


# ---------------------------------------------------------------- assets
s = repl_func(s, 'tongue_card', '''
def tongue_card():
    """manga panel (GPT redraw 'tongue-card2.png' of frame 170): grey hair, two white spikes, black band, magenta tongue;
    the panel itself is world (5516.5, 174) .. (5756.5, 862.5)"""
    im = gen('tongue-card2.png').convert('RGB').crop((245, 8, 783, 1529))
    return im.resize((int(240.0 * K * 1.5), int(688.5 * K * 1.5)), Image.LANCZOS).convert('RGBA')
''')

s = repl(s, """    c.text(5648, 219, 'Blender has stopped working', 'segoeui.ttf', 11.6, (0, 51, 153, 255))
""", """    c.text(5648, 219, 'Blender has stopped working', 'seguisb.ttf', 11.4, (0, 40, 130, 255))
""")
s = repl(s, """            c.text(5648, 240 + i * 9.6, t, 'segoeui.ttf', 7.6, (20, 20, 20, 255))
""", """            c.text(5648, 240 + i * 9.6, t, 'seguisb.ttf', 7.5, (8, 8, 8, 255))
""")
s = repl(s, """        c.text((x0 + x1) / 2, 334.5, t, 'segoeui.ttf', 7.4, (20, 20, 20, 255), anchor='mm')
    return c
""", """        c.text((x0 + x1) / 2, 334.5, t, 'seguisb.ttf', 7.4, (8, 8, 8, 255), anchor='mm')
    # hand-drawn squiggle across the dialog
    c.line([(5651, 222), (5700, 226), (5747, 241), (5690, 250), (5622, 260), (5660, 268), (5701, 276), (5650, 289), (5619, 296)], (12, 12, 12, 255), 0.7)
    return c
""")

s = repl_func(s, 'escalator', '''
def escalator():
    """high-contrast b/w escalator photo (GPT redraw 'escalator-bw.png' of frame 170), world 5758..5987 x 361..769, with the row
    of four round safety signs and their header"""
    W_, H_ = 229.0, 408.0
    im = gen('escalator-bw.png').convert('RGB')
    cw = int(im.height * W_ / H_)
    im = im.crop(((im.width - cw) // 2, 0, (im.width - cw) // 2 + cw, im.height)).resize((int(W_ * K), int(H_ * K)), Image.LANCZOS).convert('RGBA')
    d = ImageDraw.Draw(im)
    y = int(223 * K)
    r = int(19.5 * K)
    wh = (250, 250, 250, 255)
    for i in range(4):
        cx_ = int((25 + i * 50.5) * K)
        if i < 2:
            d.ellipse([cx_ - r, y - r, cx_ + r, y + r], fill=wh)
            d.ellipse([cx_ - r + 3, y - r + 3, cx_ + r - 3, y + r - 3], fill=(36, 84, 190, 255))
            if i == 0:                       # goggles
                for dx in (-0.36, 0.36):
                    d.ellipse([cx_ + (dx - 0.27) * r, y - 0.28 * r, cx_ + (dx + 0.27) * r, y + 0.18 * r], outline=wh, width=max(2, K))
                d.line([cx_ - 0.75 * r, y - 0.05 * r, cx_ + 0.75 * r, y - 0.05 * r], fill=wh, width=max(1, K))
            else:                            # helmet
                d.pieslice([cx_ - 0.52 * r, y - 0.55 * r, cx_ + 0.52 * r, y + 0.45 * r], 180, 360, fill=wh)
                d.rectangle([cx_ - 0.66 * r, y - 0.06 * r, cx_ + 0.66 * r, y + 0.10 * r], fill=wh)
        else:
            d.ellipse([cx_ - r, y - r, cx_ + r, y + r], fill=wh, outline=(200, 30, 44, 255), width=int(3.2 * K))
            d.ellipse([cx_ - 0.34 * r, y - 0.40 * r, cx_ + 0.30 * r, y + 0.38 * r], fill=(24, 24, 24, 255))
            d.line([cx_ - r * 0.68, y - r * 0.68, cx_ + r * 0.68, y + r * 0.68], fill=(200, 30, 44, 255), width=int(3.2 * K))
        d.rectangle([cx_ - 0.8 * r, y + r + 3 * K, cx_ + 0.8 * r, y + r + 4.4 * K], fill=(60, 60, 60, 255))
    d.text((int(85 * K), int(183 * K)), '\\u5b89\\u5168\\u64cd\\u4f5c\\u7a0b\\u5e8f', font=font('simhei.ttf', 9.5 * K), fill=(16, 16, 16, 255), anchor='mm')
    return im
''')

s = repl_func(s, 'half_disc', '''
def half_disc():
    """royal blue half sphere with a lat / long grid on a vignetted grey tile; the flat side is the tile's left edge (x 5781)"""
    x0, y0, x1, y1 = 5781, 596, 5945, 800
    w, h = (x1 - x0) * K, (y1 - y0) * K
    x, y = grid(w, h)
    wx, wy = x / K + x0, y / K + y0
    d = np.hypot(wx - 5846, (wy - 700) / 1.15)
    v = np.clip(250 - (d / 105.0) ** 1.6 * 150.0, 96, 250)
    rgb = np.dstack([v, v, v])
    R_, cx_, cy_ = 86.0, 5781.0, 698.0
    disc = cov((np.hypot(wx - cx_, wy - cy_) - R_) * K) * cov((cx_ - wx) * K)
    u = np.clip((wy - cy_) / R_, -0.999, 0.999)
    half = np.sqrt(1 - u * u) * R_
    lon = np.clip((wx - cx_) / half, 0, 1)
    a_m = np.arcsin(lon) / (math.pi / 2) * 6.0
    a_p = np.arcsin(u) / (math.pi / 2) * 6.0
    fm = np.abs(a_m - np.round(a_m))
    fp = np.abs(a_p - np.round(a_p))
    lines = (np.minimum(fm, fp) < 0.05).astype(np.float32) * 0.75
    blue = np.array((22, 52, 216), np.float32) * (1 - lines[..., None]) + np.array((96, 136, 248), np.float32) * lines[..., None]
    rgb = rgb * (1 - disc[..., None]) + blue * disc[..., None]
    return from_arr(rgb, np.ones((h, w), np.float32))
''')

s = repl_func(s, 'helix_table', '''
def helix_table():
    c = Canvas(5670, 776, 5950, 838, k=3, ss=3)
    bk = (10, 10, 10, 255)
    c.rect(5674, 780, 5945, 833.3, fill=(252, 252, 252, 255), outline=bk, width=0.6)
    for y in (793.3, 806.6, 820.0):
        c.line([(5674, y), (5945, y)], bk, 0.6)
    for x in (5727, 5754, 5834):
        c.line([(x, 780), (x, 833.3)], bk, 0.6)
    f = 'msgothic.ttc'
    cells = [(5794, 786.6, '\\u87ba\\u65cb\\uff08\\u5f26\\u5dfb\\u7dda\\uff09'), (5889.5, 786.6, '\\u6e26\\u5dfb\\uff08\\u6e26\\u5dfb\\u7dda\\uff09'), (5700.5, 800, '\\u82f1\\u8a9e'), (5794, 800, 'helix'),
             (5889.5, 800, 'spiral'), (5700.5, 813.3, '\\u6b21\\u5143'), (5794, 813.3, '3\\u6b21\\u5143\\u66f2\\u7dda'), (5889.5, 813.3, '2\\u6b21\\u5143\\u66f2\\u7dda'), (5700.5, 826.6, '\\u4f8b'),
             (5794, 826.6, '\\u87ba\\u65cb\\u968e\\u6bb5\\u3001DNA\\u5206\\u5b50'), (5889.5, 826.6, '\\u868a\\u53d6\\u308a\\u7dda\\u9999\\u3001\\u5dfb\\u8c9d\\u306e\\u6bbb')]
    for (x, y, t) in cells:
        c.text(x, y, t, f, 6.2, bk, anchor='mm')
    return c
''')

# line art: everything from the CITY_K constant to the scribble is replaced
i = s.index('CITY_K = 1536.0 / 1190.0')
j = s.index('# ----------------------------------------------------------------------------- church disc, sign, toggle ...')
s = s[:i] + '''_BD = {}


def _bd(name):
    if name not in _BD:
        _BD[name] = np.asarray(gen(name).convert('RGBA')).copy()
    return _BD[name]


BD_BOX = {'left': (0, 0, 760, 1004), 'lamps': (760, 700, 925, 1004), 'drum': (925, 430, 1536, 831), 'blocks': (925, 831, 1536, 1004)}


def bd_piece(kind, mode):
    """a piece of the GPT line-art backdrop 'backdrop-lines.png' (redrawn from frames 164 / 172): stepped block + trees + twin-line
    tower / lamp posts / lattice drum / its blocks.  mode 'fill' = white silhouette, 'lines' = the dark contour lines only"""
    a = _bd('backdrop-lines.png')
    x0, y0, x1, y1 = BD_BOX[kind]
    p = a[y0:y1, x0:x1]
    al = p[..., 3].astype(np.float32)
    yy, xx = np.mgrid[0:p.shape[0], 0:p.shape[1]]
    if kind == 'left':
        al = np.where((xx > 588) & (yy < 500), 0.0, al)          # the stay cables are drawn separately
    if kind == 'drum':
        al = np.where(xx < 248, 0.0, al)
    lum = p[..., :3].astype(np.float32).mean(axis=2)
    out = np.zeros(p.shape, np.uint8)
    if mode == 'fill':
        out[..., :3] = 252
        out[..., 3] = np.where(al >= 128, 255, 0)
    else:
        out[..., 0], out[..., 1], out[..., 2] = 14, 14, 16
        out[..., 3] = (np.clip((205.0 - lum) / 110.0, 0, 1) * (al >= 128) * 255).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def cables():
    """thin stay cables fanning from the tower top, plus the two long diagonals that run on to the right (frame 164)"""
    c = Canvas(5900, -520, 6760, 560, k=1.5, ss=3)
    g = (40, 40, 44, 255)
    top = (5976.0, -500.0)
    for q in ((6645, 217), (6262, 92), (6228, 92), (6130, 540), (6205, 540), (6330, 540)):
        c.line([top, q], g, 0.55)
    c.line([(5925, -66), (6700, 190)], g, 0.55)
    c.line([(5925, -60), (6700, 196)], g, 0.55)
    return c


MACH_S = 0.47                        # world px per px of 'lower-lines.png' (GPT redraw of the lower structure, frame 176)
MACH_XY = (5966.0, 539.3)


def la_machine(mode='lines'):
    """curved ramp + mesh fence + round mesh dome below the ruler: 'lines' (black), 'white' (fill) or 'blue' (flat silhouette)"""
    a = _bd('lower-lines.png')
    al = a[..., 3].astype(np.float32)
    lum = a[..., :3].astype(np.float32).mean(axis=2)
    out = np.zeros(a.shape, np.uint8)
    if mode == 'lines':
        out[..., 0], out[..., 1], out[..., 2] = 14, 14, 16
        out[..., 3] = (np.clip((205.0 - lum) / 110.0, 0, 1) * al).astype(np.uint8)
    elif mode == 'white':
        out[..., :3] = 252
        out[..., 3] = np.where(al >= 128, 255, 0)
    else:
        m = Image.fromarray(np.where(al >= 128, 255, 0).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))
        out[..., 0], out[..., 1], out[..., 2] = 86, 110, 240
        out[..., 3] = np.asarray(m)
    return Image.fromarray(out, 'RGBA')


def la_girl():
    return line_art('girl-lines.png', color=(20, 20, 22), lo=70, hi=220)


def scribble(seed=11):
    """two crumpled low-poly wire blobs (outline polygon + inner triangulation), navy lines"""
    rng = np.random.default_rng(seed)
    c = Canvas(5950, 395, 6440, 670, k=K, ss=3)
    col = (26, 32, 150, 255)
    for (cx_, cy_, rx, ry, n, m) in ((6074.0, 524.0, 106.0, 100.0, 13, 5), (6296.0, 532.0, 122.0, 118.0, 15, 7)):
        ang_ = np.sort(rng.random(n) * 2 * math.pi)
        rad = 0.72 + 0.28 * rng.random(n)
        out = [(cx_ + rx * rad[i] * math.cos(ang_[i]), cy_ + ry * rad[i] * math.sin(ang_[i])) for i in range(n)]
        c.line(out + [out[0]], col, 1.25, joint=None)
        inner = [(cx_ + rx * 0.8 * (rng.random() - 0.5), cy_ + ry * 0.8 * (rng.random() - 0.5)) for _ in range(m)]
        for j_, p in enumerate(inner):
            for i_ in rng.choice(n, size=4, replace=False):
                c.line([p, out[int(i_)]], col, 0.85)
            c.line([p, inner[(j_ + 1) % m]], col, 0.85)
    return c


''' + s[j:]

s = repl_func(s, 'church_disc', '''
CH_C, CH_R = (6314.0, 489.0), 192.0


def church_disc():
    """quarter disc (corner bottom-left at CH_C) holding the threshold-look church photo (GPT redraw 'church-bw.png' of frame 172)"""
    x0, y0, x1, y1 = 6306, 290, 6512, 496
    c = Canvas(x0, y0, x1, y1, k=K, ss=2)
    c.image(gen('church-bw.png').convert('RGBA'), 6310.0, 297.3, w=198.0)
    img = c.done()
    w, h = img.size
    x, y = grid(w, h)
    wx, wy = x / K + x0, y / K + y0
    a = cov((np.hypot(wx - CH_C[0], wy - CH_C[1]) - CH_R) * K) * cov((CH_C[0] - wx) * K) * cov((wy - CH_C[1]) * K)
    arr = np.asarray(img).copy()
    arr[..., 3] = (arr[..., 3].astype(np.float32) * a).astype(np.uint8)
    return Image.fromarray(arr, 'RGBA')


def leaves():
    """six autumn leaves on a thin twig, right of the church disc"""
    c = Canvas(6455, 375, 6580, 515, k=3, ss=3)
    c.line([(6484, 402), (6503, 418), (6530, 436), (6548, 452)], (120, 60, 40, 255), 0.5)
    c.line([(6530, 436), (6510, 470), (6494, 492)], (120, 60, 40, 255), 0.5)
    for (lx, ly, rot, L_, col) in ((6478, 396, 205, 24, (198, 66, 46)), (6511, 394, -55, 22, (176, 70, 50)), (6533, 427, 150, 25, (204, 60, 44)),
                                   (6471, 444, 185, 24, (196, 58, 40)), (6554, 454, 80, 22, (150, 96, 60)), (6486, 496, 200, 25, (168, 92, 58))):
        r_ = math.radians(rot)
        ux, uy = math.cos(r_), math.sin(r_)
        vx, vy = -uy, ux
        n = 14
        side = []
        for i in range(n + 1):
            t = i / float(n)
            side.append((t, 0.30 * L_ * math.sin(math.pi * t) ** 0.8 * (1.0 - 0.25 * t)))
        pts = [(lx + ux * (t - 0.5) * L_ + vx * wd, ly + uy * (t - 0.5) * L_ + vy * wd) for t, wd in side]
        pts += [(lx + ux * (t - 0.5) * L_ - vx * wd, ly + uy * (t - 0.5) * L_ - vy * wd) for t, wd in side[::-1]]
        c.poly(pts, rgba(col), outline=(96, 30, 22, 255), width=0.5)
        vein = (246, 226, 214, 255)
        c.line([(lx - ux * 0.5 * L_, ly - uy * 0.5 * L_), (lx + ux * 0.5 * L_, ly + uy * 0.5 * L_)], vein, 0.55)
        for t in (0.22, 0.38, 0.54, 0.70):
            bx, by = lx + ux * (t - 0.5) * L_, ly + uy * (t - 0.5) * L_
            wd = 0.26 * L_ * math.sin(math.pi * t) ** 0.8
            for sg in (1, -1):
                c.line([(bx, by), (bx + ux * 0.16 * L_ + sg * vx * wd, by + uy * 0.16 * L_ + sg * vy * wd)], vein, 0.4)
    return c
''')

s = repl_func(s, 'no_parking', '''
def no_parking():
    """round red / blue sign, centre (0, 0)"""
    c = Canvas(-54, -54, 54, 54, k=K, ss=3)
    c.circle(1.2, 1.6, 51.5, fill=(60, 60, 64, 70))
    c.circle(0, 0, 51.0, fill=(250, 250, 250, 255))
    c.circle(0, 0, 49.0, fill=(214, 28, 40, 255))
    c.circle(0, 0, 37.5, fill=(26, 70, 206, 255))
    for sg in (1, -1):
        c.line([(-27.5, -27.5 * sg), (27.5, 27.5 * sg)], (214, 28, 40, 255), 9.0)
    return c
''')

s = repl_func(s, 'toggle', '''
def toggle():
    """pill switch, knob centre at (0, 0): white-rimmed dark pill to the left, maroon knob with pink and white rings and a '1'"""
    c = Canvas(-140, -38, 38, 38, k=K, ss=3)
    c.rrect(-132, -25, -4, 25, 25, fill=(250, 250, 250, 255), outline=(40, 40, 44, 255), width=0.6)
    c.rrect(-127, -20, -8, 20, 20, fill=(58, 58, 62, 255))
    c.rrect(-120, -16, -34, -7, 4.5, fill=(98, 98, 102, 255))
    c.circle(0, 0, 32.5, fill=(250, 250, 250, 255), outline=(150, 20, 52, 255), width=0.8)
    c.circle(0, 0, 23.5, fill=(226, 44, 112, 255))
    c.circle(0, 0, 20.0, fill=(250, 250, 250, 255))
    c.circle(0, 0, 17.0, fill=(112, 28, 74, 255))
    c.text(0, 0, '1', 'Montserrat-Bold.ttf', 15, (250, 250, 250, 255), anchor='mm')
    return c
''')

s = repl_func(s, 'barcode', '''
def barcode(seed=2):
    rng = np.random.default_rng(seed)
    c = Canvas(6238, 608, 6324, 686, k=K, ss=3)
    x = 6240.0
    while x < 6319:
        w_ = 1.0 + rng.integers(0, 3) * 0.9
        c.rect(x, 610, min(x + w_, 6320), 672, fill=(8, 8, 8, 255))
        x += w_ + 0.9 + rng.integers(0, 2) * 1.0
    c.text(6280, 679, '9 487654 321098', 'arial.ttf', 5.6, (8, 8, 8, 255), anchor='mm')
    return c
''')

s = repl_func(s, 'baton', '''
def lantern():
    """old street lamp lying across the picture: lantern head at (0, 0), the rod runs down-right to a black ferrule"""
    c = Canvas(-40, -40, 170, 190, k=K, ss=3)
    dk, lt = (26, 26, 28, 255), (238, 238, 240, 255)
    ax, ay = 145.0, 168.0
    L_ = math.hypot(ax, ay)
    ux, uy = ax / L_, ay / L_
    c.line([(10 * ux, 10 * uy), (ax, ay)], (52, 52, 56, 255), 5.2)
    c.line([(10 * ux - 1.2 * uy, 10 * uy + 1.2 * ux), (ax - 1.2 * uy, ay + 1.2 * ux)], (150, 150, 156, 255), 1.0)
    c.line([(ax - 30 * ux, ay - 30 * uy), (ax + 6 * ux, ay + 6 * uy)], (8, 8, 8, 255), 9.0)
    c.line([(ax - 36 * ux, ay - 36 * uy), (ax - 31 * ux, ay - 31 * uy)], (120, 120, 126, 255), 7.0)

    def R(px_, py_):                                         # (along the rod, across) -> canvas
        return (px_ * ux - py_ * uy, px_ * uy + py_ * ux)
    c.poly([R(-22, -9), R(-12, -15), R(6, -15), R(12, -8), R(12, 8), R(6, 15), R(-12, 15), R(-22, 9)], lt, outline=dk, width=0.9)
    for q in (-12, -3, 6):
        c.line([R(q, -15), R(q, 15)], dk, 0.7)
    c.poly([R(-22, -9), R(-28, -4), R(-28, 4), R(-22, 9)], (70, 70, 74, 255), outline=dk, width=0.8)
    c.circle(R(-33, 0)[0], R(-33, 0)[1], 5.0, outline=dk, width=1.0)
    return c


def jpg_card():
    """small white file card with a doodle and a 'jpg' caption"""
    c = Canvas(6122, 367, 6178, 412, k=3, ss=3)
    c.rect(6124, 369.5, 6176, 409.5, fill=(252, 252, 252, 255))
    g = (60, 60, 64, 255)
    c.circle(6146, 383, 4.2, outline=g, width=0.5)
    c.line([(6146, 387), (6149, 395), (6144, 398)], g, 0.5)
    c.line([(6141, 381), (6137, 378)], g, 0.5)
    c.line([(6150, 380), (6154, 377), (6157, 380)], g, 0.5)
    c.line([(6133, 400), (6133, 406)], g, 0.5)
    c.text(6152, 403.5, 'jpg', 'arialbd.ttf', 4.6, (30, 30, 30, 255), anchor='mm')
    return c


def sine_box():
    c = Canvas(6603, 652, 6724, 724, k=K, ss=3)
    c.rect(6605, 654, 6721, 722, outline=(20, 20, 20, 255), width=0.6)
    for ph, amp, col in ((0.0, 9.0, (40, 190, 70, 255)), (1.4, 7.0, (70, 210, 90, 255))):
        c.line([(6608 + i * 1.6, 680 + amp * math.sin(i * 0.26 + ph)) for i in range(70)], col, 0.7)
    return c
''')

s = repl_func(s, 'rgb_bar', '''
def rgb_bar():
    c = Canvas(6641, 366, 6902, 388, k=K, ss=2)
    cols = [(40, 60, 232), (30, 210, 60), (232, 30, 40)]
    x = 6642.5
    i = 0
    while x < 6898:
        w_ = 8.4 + (i * 7 % 5) * 0.55
        c.rect(x, 367.5, min(x + w_, 6898.7), 386, fill=rgba(cols[i % 3]))
        x += w_
        i += 1
    return c
''')

s = repl_func(s, 'splatter', '''
def splatter(seed=4):
    """ink blots: a few fat ones near (6830..6900, 450..490) and a fine spray running down to the right below the ruler"""
    rng = np.random.default_rng(seed)
    c = Canvas(6700, 430, 6960, 680, k=K, ss=3)
    bk = (8, 8, 8, 255)
    for (x_, y_, r_) in ((6828, 460, 7.0), (6836, 468, 5.0), (6859, 471, 8.0), (6866, 464, 4.2), (6888, 449, 6.4), (6899, 458, 7.0), (6893.5, 453.5, 4.0),
                         (6826, 485, 9.0), (6838, 480, 5.0), (6812, 478, 2.0), (6850, 452, 1.6), (6873, 486, 2.2)):
        c.circle(x_, y_, r_, fill=bk)
    for _ in range(130):
        t = rng.random()
        x_ = 6736 + t * 205 + rng.normal(0, 6)
        y_ = 566 + t * 36 + rng.normal(0, 13) * (0.5 + t)
        c.circle(x_, y_, 0.45 + rng.random() ** 3 * 2.4, fill=bk)
    for (x_, y_, r_) in ((6732, 646, 3.2), (6757, 644, 2.6), (6780, 662, 3.4), (6803, 613, 2.4), (6920, 598, 2.6)):
        c.circle(x_, y_, r_, fill=bk)
    return c
''')

s = repl_func(s, 'ice', '''
def ice():
    """pale sky / cloud photo behind the ink blots (world 6736..6964 x 394..494), a thin dark line down its left edge"""
    x0, y0, x1, y1 = 6736, 394, 6964, 494
    w, h = (x1 - x0) * K, (y1 - y0) * K
    rng = np.random.default_rng(8)
    acc = np.zeros((h, w), np.float32)
    for cell, amp in ((48, 0.55), (22, 0.30), (10, 0.15)):
        n = rng.random((h // cell + 2, w // cell + 2)).astype(np.float32)
        acc += amp * np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)).astype(np.float32) / 255.0
    t = np.clip((acc - 0.38) * 3.2, 0, 1)
    img = from_arr(lerp_color((178, 206, 242), (252, 253, 255), t), np.ones((h, w), np.float32) * 0.92)
    ImageDraw.Draw(img).line([0, 0, 0, h], fill=(20, 20, 20, 255), width=max(1, K))
    return img
''')

s = repl_func(s, 'axis_line', '''
def axis_line(L=3200, col=(220, 40, 50), arrow=None, w=0.9):
    """long thin line through (0, 0); `arrow` = distance of an arrow head from the centre"""
    c = Canvas(-L / 2, -8, L / 2, 8, k=1, ss=3)
    c.line([(-L / 2, 0), (L / 2, 0)], rgba(col), w)
    if arrow:
        c.poly([(arrow - 22, -5.5), (arrow, 0), (arrow - 22, 5.5)], rgba(col))
    return c
''')

# ---------------------------------------------------------------- build: backdrop .. RGB split
i = s.index('    # ---------------- line art backdrop ----------------')
j = s.index('    # ---------------- camera, labels in front of the film ----------------')
s = s[:i] + '''    def centre(L, cx_, cy_):
        L.x, L.y = cx_ - L.ww / 2.0, cy_ - L.wh / 2.0
        L.pivot = (cx_, cy_)
        return L

    # ---------------- line art backdrop ----------------
    # GPT line art 'backdrop-lines.png', cut into pieces and fitted to the positions measured on frames 158-172.  Each piece =
    # white fill + black contour lines: hot pink silhouettes on 150-152, bleaching to pale pink by 158, white with black lines from 159.
    pieces = (('left', 5527.4, -512.0, 0.794, 1.048), ('lamps', 6120.0, 80.0, 1.0, 1.513), ('drum', 6387.6, 213.5, 0.467, 0.39),
              ('blocks', 6387.6, 370.0, 0.467, 0.9827))
    for kind, wx_, wy_, sx_, sy_ in pieces:
        L = sc.add('C_bdfill_' + kind, bd_piece, wx_, wy_, kind, 'fill', k=1.0 / sx_, crop=False)
        L.pivot = (wx_, wy_)
        L.set(scale=[100.0, 100.0 * sy_ / sx_])
        L.span(150).flashes([(150, (232, 8, 109)), (153, (238, 96, 152)), (155, (244, 160, 192)), (157, (246, 204, 220)), (159, None)]).key(
            'opacity', [(150, 92.0, HOLD), (153, 86.0, HOLD), (156, 74.0, HOLD), (159, 88.0, HOLD)])
    for kind, wx_, wy_, sx_, sy_ in pieces:
        L = sc.add('C_bdline_' + kind, bd_piece, wx_, wy_, kind, 'lines', k=1.0 / sx_, crop=False)
        L.pivot = (wx_, wy_)
        L.set(scale=[100.0, 100.0 * sy_ / sx_])
        L.span(150).flashes([(150, (198, 6, 90)), (153, (224, 84, 136)), (156, (150, 90, 110)), (159, None)])
    sc.addc('C_cables', cables).span(153).set(opacity=70.0)
    # lower structure (GPT 'lower-lines.png'): flat light-blue silhouette on 166-167, then white with black lines
    mk = 1.0 / MACH_S
    sc.add('C_machine_w', la_machine, MACH_XY[0], MACH_XY[1], 'white', k=mk, crop=False).span(166).set(opacity=92.0)
    L = sc.add('C_machine_fill', la_machine, MACH_XY[0], MACH_XY[1], 'blue', k=mk, crop=False)
    L.span(166, 168).set(pano=False).fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': [(166, 0.0, HOLD), (167, 45.0, HOLD)],
                                                              'ADBE Linear Wipe-0002': -135.0, 'ADBE Linear Wipe-0003': 0.0})
    sc.add('C_machine', la_machine, MACH_XY[0], MACH_XY[1], 'lines', k=mk, crop=False).span(166).flashes([(166, (246, 246, 255)), (168, None)])

    # ---------------- axis lines (3-D gizmo look): dark red / green with arrow heads, blue vertical; all through (6640, 493) ----------------
    for nm, col, rot, piv, f0, ah, lw in (('C_axis_r', (156, 18, 46), 26.5, (6640, 493), 167, 342.0, 1.3), ('C_axis_g', (60, 226, 64), -23.5, (6640, 493), 167, 318.0, 0.9)):
        L = sc.addc(nm, axis_line, 3200, col, ah, lw, pivot=(0, 0))
        L.x += piv[0]
        L.y += piv[1]
        L.pivot = piv
        L.span(f0).set(rotation=rot).key('scale', [(f0, [0, 100], LIN), (f0 + 2, [100, 100], LIN)])
    L = sc.addc('C_axis_b', axis_line, 2400, (30, 40, 200), 800.0, pivot=(0, 0))
    L.x += 6642.5
    L.y += 540
    L.pivot = (6642.5, 540)
    L.span(167).set(rotation=-90.0)

    # ---------------- card / dialog / escalator block ----------------
    sc.add('C_card', tongue_card, 5516.5, 174.0, k=K * 1.5, crop=False).span(144).pop(144, 2, 0.7)
    centre(sc.add('C_two', outlined, 0, 0, '(2)', 'georgiab.ttf', 30, double=True), 5579.0, 149.5).span(144).set(scale=[165.0, 85.0])
    sc.addc('C_dialog', crash_dialog).span(144).pop(144, 3, 0.4, over=1.08)
    centre(sc.add('C_crash', outlined, 0, 0, '(crash)', 'times.ttf', 13.5, stroke=0.8), 5858.0, 229.0).span(146)
    sc.add('C_escalator', escalator, 5758, 361, crop=False).span(145).flash(145, (255, 255, 255), 1)
    centre(sc.add('C_elevator', outlined, 0, 0, '(elevator)', 'timesi.ttf', 24.5, tracking=-0.3), 5993.0, 380.0).span(146)
    sc.add('C_halfdisc', half_disc, 5781, 596, crop=False).span(146).pop(146, 2, 0.5)
    sc.addc('C_dna', dna).span(147).wipe(147, 3, angle=0)
    sc.addc('C_table', helix_table).span(149)
    sc.addc('C_chibicard', chibi_card).span(151).pop(151, 2, 0.6)
    sc.add('C_three', outlined, 5918, 846, '(3)', 'georgiab.ttf', 52, double=True).span(151)
    sc.addc('C_wavy', wavy).span(148)

    # pale bar under the ruler (154-164): the head runs right, then the tail follows and leaves a dark pill
    L = sc.add('C_tube', ruler_bar_c, 5360, 551, k=1)
    L.span(154, 165).set(pano=False)
    W_ = 1244.0
    L.fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': [(f, 100.0 * (1 - (h_ - 5360) / W_), HOLD) for f, h_ in
                                                          ((154, 5420), (155, 5588), (156, 5869), (157, 6114), (158, 6360), (159, 6604))],
                                'ADBE Linear Wipe-0002': -90.0, 'ADBE Linear Wipe-0003': 0.0})
    L.fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': [(f, 100.0 * (t_ - 5360) / W_, HOLD) for f, t_ in
                                                          ((154, 5360), (161, 5733), (162, 6106), (163, 6479))],
                                'ADBE Linear Wipe-0002': 90.0, 'ADBE Linear Wipe-0003': 0.0})

    # ---------------- wire blobs / RGB bars / church / labels ----------------
    sc.addc('C_scribble', scribble).span(156).wipe(156, 6, angle=-90).flashes([(156, (120, 120, 124)), (166, None)])
    # thick red / blue / green bars just above the ruler (167-174): the heads run out to the right on 167-171, the tails follow on
    # 172-174 (rows and ends measured per frame on the source)
    from sec_a import _two_wipes
    for nm, col, y0_, y1_, x0_ in (('C_rgbline0', (236, 28, 44), 496.5, 509.0, 5258.0), ('C_rgbline1', (16, 24, 244), 509.8, 522.6, 5060.0),
                                   ('C_rgbline2', (40, 236, 52), 524.0, 536.2, 5060.0)):
        W2 = 7420.0 - x0_
        L = sc.add(nm, solid_rect, x0_, y0_, W2, y1_ - y0_, col)
        L.span(167, 175).set(pano=False)
        _two_wipes(L, x0_, W2, [(167, 6806.0), (168, 7076.0), (169, 7212.0), (170, 7293.0), (171, 7420.0)],
                   [(167, x0_), (172, 5990.0), (173, 6306.0), (174, 6860.0)])
    centre(sc.add('C_four', outlined, 0, 0, '(4)', 'Montserrat-Bold.ttf', 37, stroke=1.5), 6282.0, 512.5).span(166)
    sc.add('C_church', church_disc, 6306, 290, crop=False).span(168).pop(168, 2, 0.6)
    sc.addc('C_leaves', leaves).span(168)
    sc.addc('C_barcode', barcode).span(170)
    centre(sc.add('C_metal', outlined, 0, 0, '(METAL)', 'timesi.ttf', 25.5, tracking=-0.5), 6366.0, 678.0).span(170)
    sc.addc('C_aedata', ae_data).span(171).wipe(171, 4, angle=0)
    sc.addc('C_jpg', jpg_card).span(159)
    sc.addc('C_sine', sine_box).span(169)
    for nm, txt, cx_, cy_ in (('C_2982', '2982', 6032.5, 561.0), ('C_3120', '3120', 6614.3, 561.0)):
        centre(sc.add(nm, text_asset, 0, 0, txt, 'Montserrat-Regular.ttf', 9.5, (16, 16, 16), tracking=-0.3), cx_, cy_).span(154)
    centre(sc.add('C_3279', text_asset, 0, 0, '3279', 'Montserrat-Bold.ttf', 15.0, (226, 30, 84), tracking=-0.4), 6356.0, 564.5).span(169).set(rotation=38.0)
    L = sc.addc('C_baton', lantern, pivot=(0, 0))
    L.span(166).key('position', [(166, [6627.0, 527.0], HOLD), (167, [6463.0, 530.0], HOLD), (168, [6444.0, 535.0], HOLD), (169, [6425.0, 538.0], HOLD),
                                 (170, [6410.0, 540.0], HOLD), (172, [6398.0, 541.0], HOLD)])

    # ---------------- pink beams: thin 166, then big/small flicker 167-171 ----------------
    sc.add('C_ice', ice, 6736, 394).span(168)
    big = sc.addc('C_beam', beam, [(6385, 507), (6875, 322), (7200, 212), (7200, 240), (6875, 420)], pivot=(6385, 507))
    big.span(166).key('scale', [(166, [70, 6], HOLD), (167, [100, 100], HOLD), (168, [86, 22], HOLD), (169, [100, 100], HOLD),
                                 (170, [100, 26], HOLD), (171, [100, 100], HOLD)])
    sc.addc('C_beam2', beam, [(6617, 541.5), (6660, 533), (6732, 529.5), (6865, 542.5), (6732, 555.5), (6690, 552)], pivot=(6617, 541.5)).span(168).key(
        'scale', [(168, [40, 100], LIN), (170, [100, 100], LIN)])
    sc.addc('C_beam3', beam, [(6301, 558), (6420, 590), (6470, 612), (6504, 678), (6455, 645), (6390, 610)]).span(169)
    sc.addc('C_rgb', rgb_bar).span(167).wipe(167, 2, angle=-90)
    sc.addc('C_splatter', splatter).span(166).pop(166, 2, 0.3)
    L = sc.addc('C_sign', no_parking, pivot=(0, 0))
    L.span(166).key('position', [(166, [6566.8, 559.5], HOLD), (167, [6533.7, 559.5], HOLD), (168, [6523.7, 559.5], HOLD), (169, [6520.5, 559.5], HOLD),
                                 (170, [6519.5, 559.5], HOLD), (172, [6518.0, 559.5], LIN), (196, [6514.0, 559.5], LIN)])
    L = sc.addc('C_toggle', toggle, pivot=(0, 0))
    L.span(166).key('position', [(166, [6689.0, 599.5], HOLD), (167, [6700.5, 599.5], HOLD), (168, [6702.6, 599.5], HOLD), (169, [6709.0, 599.5], HOLD),
                                 (170, [6711.6, 599.5], LIN), (180, [6724.0, 599.5], LIN), (196, [6743.0, 599.5], LIN)])
    centre(sc.add('C_4320', text_asset, 0, 0, '4320', 'Montserrat-Bold.ttf', 15.5, (204, 22, 62), tracking=-0.5), 6831.0, 327.0).span(169).set(rotation=-14.0)
    L = sc.add('C_redtext', path_text, 6650, 296, 'She begins a journey across an immense river of time, where countless fragments of information', 'consola.ttf', 8.0, (226, 30, 70))
    L.pivot = (6650, 300)
    L.span(170).set(rotation=-24.0).wipe(170, 5, angle=-90)
    L = sc.add('C_redtext2', path_text, 6730, 582, 'time cannot be reversed.', 'consola.ttf', 9.0, (226, 30, 70))
    L.span(171).set(rotation=12.0)

''' + s[j:]

io.open(P, 'w', encoding='utf-8').write(s)
print('sec_c patched')
