"""v6: GPT-regenerated assets (tube, chrome, bead chain, city silhouette, chibi), horn swing, cylinder bar,
flip re-timed on measured centres, squeezed ghosts during the flip, thinner RGB split."""
import io, os
D = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts'


def patch(name, pairs=(), cuts=()):
    p = os.path.join(D, name)
    s = io.open(p, encoding='utf-8').read()
    for old, new in pairs:
        assert s.count(old) == 1, (name, s.count(old), old[:70])
        s = s.replace(old, new)
    for start, end, new in cuts:
        a = s.index(start)
        b = s.index(end, a)
        s = s[:a] + new + s[b:]
    io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
    print(name, 'ok')


# ------------------------------------------------------------------ sec_a: tube + horn
patch('sec_a.py', pairs=[
    ("    col = (70, 70, 74, 150)\n", "    col = (62, 62, 66, 215)\n"),
    ("""def tube():
    im = gen('pink-tube.png')
    im = im.crop(im.getbbox())
    w = 446 * K
    return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)""",
     """def tube():
    \"\"\"glossy pink rope with a blue cap (GPT image redrawn from frames 46/50 of the source); 515 x 205 world px\"\"\"
    im = gen('pink-tube2.png')
    a = np.asarray(im).copy()
    a[..., 3] = np.where(a[..., 3] > 40, a[..., 3], 0).astype(np.uint8)
    im = Image.fromarray(a, 'RGBA')
    im = im.crop(im.getbbox())
    return im.resize((515 * K, 205 * K), Image.LANCZOS)"""),
    ("""    L = sc.addc('A_horn', wire_horn)
    L.span(39, 61).set(pano=False).key('opacity', [(39, 0, LIN), (41, 100, LIN), (57, 100, LIN), (60, 0, LIN)])""",
     """    L = sc.addc('A_horn', wire_horn, pivot=(690.0, 400.0))
    L.span(39, 61).set(pano=False).key('opacity', [(39, 0, LIN), (41, 100, LIN), (57, 100, LIN), (60, 0, LIN)])
    # 51-56: while the camera pulls back the horn swings up (mouth from lower right to upper right) and grows
    L.key('rotation', [(50, 0.0, LIN), (53, -34.0, LIN), (56, -62.0, LIN), (60, -68.0, LIN)])
    L.key('position', [(50, [690.0, 400.0], LIN), (53, [625.0, 458.0], LIN), (56, [555.0, 512.0], LIN)])
    L.key('scale', [(50, [100.0, 100.0], LIN), (53, [124.0, 124.0], LIN), (56, [147.0, 147.0], LIN)])"""),
    ("""    L = sc.add('A_tube', tube, 996, 520)
    L.pivot = (L.x + 60, L.y + L.wh / 2)
    L.span(29, 104).set(pano=False, scale=[88, 88]).wipe(29, 20, angle=-90, feather=20)""",
     """    L = sc.add('A_tube', tube, 971, 541)
    L.span(29, 104).set(pano=False).wipe(29, 20, angle=-90, feather=20)"""),
])

# ------------------------------------------------------------------ sec_a2: wide text bar from 84, metallic bar 75-83
patch('sec_a2.py', pairs=[
    ("""    c = Canvas(1946, 474, 2296, 548, k=K, ss=3)
    c.rrect(1950, 478, 2292, 545, 10, fill=(160, 160, 160, 255))""",
     """    c = Canvas(1880, 474, 2432, 548, k=K, ss=3)
    c.rrect(1886, 478, 2427, 545, 10, fill=(160, 160, 160, 255))"""),
    ("        gap = (326.0 - sum(widths)) / max(len(words) - 1, 1)\n        x = 1958.0\n",
     "        gap = (522.0 - sum(widths)) / max(len(words) - 1, 1)\n        x = 1896.0\n"),
    ("""    L = sc.addc('A_textbar', text_bar)
    L.span(75).key('position', [(75, [L.pivot[0] - 330, L.pivot[1] + 34], HOLD), (76, [L.pivot[0] - 200, L.pivot[1] + 34], HOLD),
                                (77, [L.pivot[0] - 90, L.pivot[1] + 34], HOLD), (79, [L.pivot[0], L.pivot[1] + 34], HOLD),
                                (84, [L.pivot[0], L.pivot[1]], HOLD)])""",
     """    sc.addc('A_textbar', text_bar).span(84)
    # 75-83: a black-white-black metallic bar runs along the ruler first (head grows right, then the tail follows)
    from sec_a import _two_wipes
    L = sc.add('A_cylbar', cyl_bar, 1390, 541, k=1)
    L.span(75, 84).set(pano=False)
    _two_wipes(L, 1390.0, 1162.0, [(75, 2100), (76, 2393), (77, 2460), (78, 2528), (79, 2552)],
               [(75, 1390), (79, 1500), (80, 1630), (81, 1760), (82, 1886)])"""),
    ("def text_bar():", """def cyl_bar():
    \"\"\"black-white-black metallic bar under the ruler (world x 1390..2552), frames 75-83\"\"\"
    w, h = 1162, 64
    x, y = grid(w, h)
    v = grad_stops(x / w, [(0.0, (4, 4, 4)), (0.18, (250, 250, 250)), (0.45, (170, 170, 170)), (0.62, (110, 110, 110)), (0.70, (12, 12, 12)),
                           (0.80, (12, 12, 12)), (0.86, (150, 150, 150)), (1.0, (236, 236, 236))])
    return from_arr(v, np.ones((h, w), np.float32))


def text_bar():"""),
])

# ------------------------------------------------------------------ sec_b: chrome, bead chain, top band timing
patch('sec_b.py', pairs=[
    ("""def chrome():
    im = gen('chrome-shape.png')
    im = im.crop(im.getbbox())""",
     """def chrome():
    \"\"\"liquid-chrome calligraphic shape (GPT image redrawn from frame 84 of the source)\"\"\"
    im = gen('chrome-shape2.png')
    a = np.asarray(im).copy()
    a[..., 3] = np.where(a[..., 3] > 40, a[..., 3], 0).astype(np.uint8)
    im = Image.fromarray(a, 'RGBA')
    im = im.crop(im.getbbox())"""),
    ("""        L = sc.addc('B_arcT%d' % i, ribbon, p0, p1, w0, w1, seed, 0.0)
        L.span(120).flashes(""",
     """        L = sc.addc('B_arcT%d' % i, ribbon, p0, p1, w0, w1, seed, 0.0)
        L.set(pano=False)
        L.span(120, 124 if i == 0 else 122).flashes("""),
    ("    chain = chain_keys(sc.addc('B_chain', bead_chain))\n",
     "    chain = sc.add('B_chain', bead_chain, C0[0] - 186.0, C0[1] - 102.5)\n    chain.pivot = C0\n    chain_keys(chain)\n"),
], cuts=[
    ("def bead_chain():", "def ruler_bar():", """def bead_chain():
    \"\"\"glossy bead bracelet (GPT image redrawn from the source), mirrored so that it sinks to the right; 372 x 205 world px\"\"\"
    im = gen('bead-chain.png')
    a = np.asarray(im).copy()
    a[..., 3] = np.where(a[..., 3] > 60, a[..., 3], 0).astype(np.uint8)
    im = Image.fromarray(a, 'RGBA')
    im = im.crop(im.getbbox()).transpose(Image.FLIP_LEFT_RIGHT)
    b = np.asarray(im).astype(np.float32)
    b[..., :3] = b[..., :3] * 0.88 + np.array((10, 14, 40), np.float32) * 0.12
    return Image.fromarray(b.astype(np.uint8), 'RGBA').resize((372 * K, 205 * K), Image.LANCZOS)


"""),
])

# ------------------------------------------------------------------ sec_c: city from the generated silhouette, chibi card, RGB split
patch('sec_c.py', pairs=[
    ("""    im = gen('chibi.png')
    im = im.crop(im.getbbox())
    head = im.crop((0, 0, im.width, int(im.height * 0.47)))""",
     """    from filmrun import _chibi_src
    im = _chibi_src()
    head = im.crop((0, 0, im.width, int(im.height * 0.40)))"""),
    ("        L = sc.add('C_rgbline%d' % i, solid_rect, 5300, 537 + dy, 2400, 6, col, pivot=(5300, 540 + dy))",
     "        L = sc.add('C_rgbline%d' % i, solid_rect, 5300, 538.3 + dy * 0.7, 2400, 3.4, col, pivot=(5300, 540 + dy * 0.7))"),
    ("    L = sc.add('C_cityfill', la_city_fill, 5750, -20, k=1.72)", "    L = sc.add('C_cityfill', la_city_fill, 5510, -178, k=CITY_K)"),
    ("    L = sc.add('C_city', la_city, 5750, -20, k=1.72)", "    L = sc.add('C_city', la_city, 5510, -178, k=CITY_K)"),
    ("    L = sc.add('C_pinkblock', solid_rect, 5526, -136, 240, 240, PK)", "    L = sc.add('C_pinkblock', solid_rect, 5526, -136, 240, 698, PK)"),
], cuts=[
    ("def la_city():", "def la_machine():", """CITY_K = 1536.0 / 1190.0            # generated silhouette is 1536 px wide = 1190 world px (ground line at world y 562)


def _city_mask():
    \"\"\"pink pixels of the GPT silhouette (crane tower, bare trees, pole with cables, ferris-wheel building)\"\"\"
    a = np.asarray(gen('city-sil.png').convert('RGB')).astype(np.float32)
    return ((a[..., 1] < 150) & (a[..., 0] > 150)).astype(np.uint8) * 255


def la_city():
    \"\"\"outline of the silhouettes: what stays as thin grey line art once the pink has bleached out\"\"\"
    m = Image.fromarray(_city_mask())
    edge = ImageChops.subtract(m.filter(ImageFilter.MaxFilter(3)), m.filter(ImageFilter.MinFilter(3)))
    out = Image.new('RGBA', m.size, (128, 128, 132, 0))
    out.putalpha(edge)
    return out


def la_city_fill():
    \"\"\"solid silhouettes: hot pink on 150-152, bleaching to a pale paper fill by 159\"\"\"
    m = Image.fromarray(_city_mask())
    out = Image.new('RGBA', m.size, (255, 255, 255, 0))
    out.putalpha(m)
    return out


"""),
])

# ------------------------------------------------------------------ sec_d: flip on measured centres, clipped 1.6x frame, squeezed ghosts
patch('sec_d.py', pairs=[
    ("""        L.key('scale', [(236, [100 * sg, sy], HOLD), (237, [30 * sg, sy], HOLD), (238, [-40 * sg, sy], HOLD), (239, [-100 * sg, sy], HOLD),
                        (240, [-128 * sg, sy], HOLD), (241, [160 * sg, sy], HOLD), (242, [108 * sg, sy], HOLD), (243, [100 * sg, sy], HOLD)]
              + [(f, [100 * sg * st, sy], HOLD) for f, x_, st in END])
        L.key('position', [(236, [FLIP_X, L.pivot[1]], HOLD)] + [(f, [x_, L.pivot[1]], HOLD) for f, x_, st in END])""",
     """        L.key('scale', [(236, [100 * sg, sy], HOLD)] + [(f, [100 * sg * st, sy], HOLD) for f, x_, st in FLIP + END])
        L.key('position', [(236, [FLIP_X, L.pivot[1]], HOLD)] + [(f, [x_, L.pivot[1]], HOLD) for f, x_, st in FLIP + END])
        # frame 241: the 1.6x panel overflows to the left and is cut off at CLIP_X
        left = 10200.0 + (L.x - FLIP_X) * 1.6
        frac = min(max((CLIP_X - left) / (L.ww * 1.6), 0.0), 1.0)
        if frac > 0.01 and sg > 0:
            L.fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': [(236, 0.0, HOLD), (241, 100.0 * frac, HOLD), (242, 0.0, HOLD)],
                                        'ADBE Linear Wipe-0002': 90.0, 'ADBE Linear Wipe-0003': 0.0})"""),
    ("    END = [(265, 10524.6, 1.234),",
     """    # flip, measured per frame: (frame, world x of the panel's pivot, x-scale). Squeezed -> mirrored -> overshoot -> 1.6x -> settled
    FLIP = [(237, 10157.5, 0.13), (238, 10270.7, -0.23), (239, 10443.7, -0.43), (240, 10653.0, -1.28), (241, 10200.0, 1.6), (242, 10410.0, 1.0)]
    CLIP_X = 10139.0
    END = [(265, 10524.6, 1.234),"""),
    ("""        L.span(224).fx('ADBE Invert', **{'ADBE Invert-0002': [(224, 0.0, HOLD), (226, 100.0, HOLD)]})
    return sc""",
     """        L.span(224).fx('ADBE Invert', **{'ADBE Invert-0002': [(224, 0.0, HOLD), (226, 100.0, HOLD)]})

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
    return sc"""),
    ("def hourglass():", """def flip_ghost():
    \"\"\"white disc with the hourglass (the panel's centre graphic) - shows up squeezed over the film during the flip\"\"\"
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


def hourglass():"""),
])

# ------------------------------------------------------------------ fx: gentle waviness only on the overshoot frame of the flip
patch('fx.py', pairs=[
    ("""    L.span(238, 242)
    L.fx('ADBE Wave Warp', **{'ADBE Wave Warp-0001': 8, 'ADBE Wave Warp-0002': [(238, 6.0, HOLD), (239, 10.0, HOLD), (240, 22.0, HOLD), (241, 8.0, HOLD)],
                              'ADBE Wave Warp-0003': 14.0, 'ADBE Wave Warp-0004': 0.0, 'ADBE Wave Warp-0005': 6.0})""",
     """    L.span(240, 242)
    L.fx('ADBE Wave Warp', **{'ADBE Wave Warp-0001': 9, 'ADBE Wave Warp-0002': [(240, 9.0, HOLD), (241, 4.0, HOLD)],
                              'ADBE Wave Warp-0003': 26.0, 'ADBE Wave Warp-0004': 0.0, 'ADBE Wave Warp-0005': 3.0})"""),
])
print('v6 patches applied')
