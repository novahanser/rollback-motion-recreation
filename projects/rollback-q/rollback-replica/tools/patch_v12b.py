"""v12b: fixes after the first v12 render (see the comparison sheets v12_*.jpg)"""
import io
B = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts' + '\\'


def patch(fn, pairs):
    s = io.open(B + fn, encoding='utf-8').read()
    for old, new in pairs:
        assert s.count(old) == 1, (fn, old[:80], s.count(old))
        s = s.replace(old, new)
    io.open(B + fn, 'w', encoding='utf-8').write(s)
    print('patched', fn)


# ------------------------------------------------------------------ chain: bluer bodies
patch('chain3d.py', [
    ("""        rho = np.hypot(u - u0, v - v0) / 1.10
        L = (0.84 + 0.16 * near_t) * (1.0 - np.clip(rho, 0, 1.4))
""", """        rho = np.hypot(u - u0, v - v0) / 0.95
        L = (0.86 + 0.14 * near_t) * (1.0 - np.clip(rho, 0, 1.6))
"""),
    ("""BODY = [(-0.40, (0, 0, 8)), (0.02, (0, 0, 8)), (0.08, (4, 10, 96)), (0.17, (12, 28, 186)), (0.30, (40, 68, 226)), (0.42, (104, 130, 240)),
        (0.54, (172, 188, 246)), (0.66, (224, 230, 250)), (1.00, (242, 244, 252))]
""", """BODY = [(-0.60, (0, 0, 8)), (-0.28, (0, 0, 8)), (-0.12, (4, 10, 96)), (0.04, (12, 28, 186)), (0.20, (40, 68, 226)), (0.38, (104, 130, 240)),
        (0.54, (172, 188, 246)), (0.68, (224, 230, 250)), (1.00, (242, 244, 252))]
"""),
    ("return 'chain3d-4'", "return 'chain3d-5'"),
])

# ------------------------------------------------------------------ window: rotating conic gradient, girl edge
patch('sec_b.py', [
    ("""def clouds_sil_silver():
    \"\"\"the cloud region as a silver conic gradient (apex inside the window), sky stays royal blue\"\"\"
    im = fit(gen('clouds.png'), PLATE_W, PLATE_H).convert('RGB')
    a = np.asarray(im).astype(np.float32)
    white = (a.mean(axis=2) > 150) & ((a.max(axis=2) - a.min(axis=2)) < 90)
    h, w = white.shape
    x, y = grid(w, h)
    an = ang(x, y, 230.0, 375.0)                                  # apex measured in plate coordinates
    v = 150.0 - 92.0 * np.cos(np.radians(an - 318.0))
    v = np.where((an > 300) & (an < 322), v * 0.35 + 10, v)        # the dark wedge pointing down-right
    v = v + 26.0 * np.clip(1 - y / (h * 0.6), 0, 1)
""", """def clouds_sil_silver(a0=35.0):
    \"\"\"the cloud region as a conic gradient around an apex inside the window: black at angle a0 (degrees, clockwise from 'right'),
    rising linearly to white one full turn later, with a hard edge (measured on 106-112: the edge turns from 39 to -47 deg);
    the sky stays royal blue\"\"\"
    im = fit(gen('clouds.png'), PLATE_W, PLATE_H).convert('RGB')
    a = np.asarray(im).astype(np.float32)
    white = (a.mean(axis=2) > 150) & ((a.max(axis=2) - a.min(axis=2)) < 90)
    h, w = white.shape
    x, y = grid(w, h)
    an = np.degrees(np.arctan2(y - 375.0, x - 230.0))              # apex measured in plate coordinates
    v = 0.71 * ((an - a0) % 360.0)
"""),
    ("""    L = plate_keys(sc.add('B_clouds_silver', clouds_sil_silver, PLATE[0], PLATE[1], k=1))
    L.span(106, 114).set(pano=False)
""", """    for f_, a0_ in ((106, 39.0), (107, 35.0), (108, 31.0), (109, 13.5), (110, -0.5), (111, -19.0), (112, -47.5), (113, -80.0)):
        L = sc.add('B_clouds_silver%d' % f_, clouds_sil_silver, PLATE[0] + DX.get(f_, 0.0), PLATE[1] - 144.0, a0_, k=1)
        L.span(f_, f_ + 1).set(pano=False)
"""),
    ("""    a[..., 3] = (np.clip((x - 0.02) / 0.22, 0, 1) * 255).astype(np.uint8)       # fade into the clouds on the left
""", """    a[..., 3] = (np.clip((x - 0.36) / 0.08, 0, 1) * 255).astype(np.uint8)       # the sky stays clear up to ~58 % of the plate
"""),
])

# ------------------------------------------------------------------ opening
patch('shapes0.py', [
    ("""    c = Canvas(-r - 5, -r - 5, r + 5, r + 5, k=4, ss=3)
    c.circle(0, 0, r, outline=rgba(col), width=w)
""", """    c = Canvas(-r - w / 2 - 2, -r - w / 2 - 2, r + w / 2 + 2, r + w / 2 + 2, k=4, ss=3)
    c.circle(0, 0, r + w / 2.0, outline=rgba(col), width=w)          # r = centre line of the ring
"""),
])
patch('sec_a.py', [
    ("""    # thick black arc right of it (circle centre (896,135) px, radius 338 px): its lower end retracts frame by frame
    for f_, (a0_, a1_) in {4: (87.7, 169.6), 5: (117.1, 175.2), 6: (139.7, 180.0), 7: (154.1, 180.0), 8: (167.0, 180.0)}.items():
        L = sc.addc('A_arc%d' % f_, S0.black_arc, a0_, a1_, S0.px(338), S0.px(27), pivot=(0, 0))
        pw = s2w(f_, 896, 135)
        L.x += pw[0]
        L.y += pw[1]
        L.span(f_, f_ + 1).set(pano=False)
""", ""),
    ("""    # thick black line above the ruler (1-5): its right end retracts; drawn over the sphere and the triangle
""", """    # thick black arc right of the sphere (circle centre (896,135) px, radius 338 px): its lower end retracts frame by frame;
    # it runs over the triangle
    for f_, (a0_, a1_) in {4: (87.7, 169.6), 5: (117.1, 175.2), 6: (139.7, 180.0), 7: (154.1, 180.0), 8: (167.0, 180.0)}.items():
        L = sc.addc('A_arc%d' % f_, S0.black_arc, a0_, a1_, S0.px(338), S0.px(27), pivot=(0, 0))
        pw = s2w(f_, 896, 135)
        L.x += pw[0]
        L.y += pw[1]
        L.span(f_, f_ + 1).set(pano=False)
    # thick black line above the ruler (1-5): its right end retracts; drawn over the sphere and the triangle
"""),
    ("""    c.circle(0, 0, R, outline=g, width=0.62)
    for rr in (0.80, 0.70):
        n = int(2 * math.pi * R * rr / 1.7)
        for i in range(n):
            a_ = 2 * math.pi * i / n
            c.circle(R * rr * math.cos(a_), R * rr * math.sin(a_), 0.36, fill=g)

    def arrow(p, q, head=3.0):
        c.line([p, q], g, 0.62)
        a_ = math.atan2(q[1] - p[1], q[0] - p[0])
        for da in (2.6, -2.6):
            c.line([q, (q[0] + head * math.cos(a_ + da), q[1] + head * math.sin(a_ + da))], g, 0.62)
""", """    c.circle(0, 0, R, outline=g, width=0.8)
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
"""),
    ("""('A_set0', 'set 0', 3, 276, 511, 7.6, (84, 150, 150))""", """('A_set0', 'set 0', 3, 276, 511, 9.4, (60, 132, 132))"""),
])

# ------------------------------------------------------------------ target / guides
patch('sec_a2.py', [
    ("""        marks = op & ~strip & (a[..., :3].max(axis=2) < 108)
""", """        marks = op & ~strip & (a[..., :3].max(axis=2) < 108)
        mm = Image.fromarray((marks * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(5))
        marks = np.asarray(mm) > 0                           # opening: drops the thin dark rim line of the rings
"""),
    ("""    for (nm, x_, y_, w_, h_) in blue:
        L = sc.add(nm, solid_rect, x_, y_, w_, h_, BL)
""", """    for (nm, x_, y_, w_, h_) in blue:
        # 97-101: a white copy slides out from under every mirrored blue piece (same offsets as under the target's twin)
        Lw = sc.add(nm + '_w', solid_rect, x_, y_, w_, h_, (250, 250, 250))
        wx_, wy_ = Lw.pivot
        Lw.span(97, 102).set(pano=False).key('position', [(f, [wx_ + dx, wy_ + dy], HOLD) for f, dx, dy in (
            (97, 25.0, 6.0), (98, -45.0, -10.0), (99, -50.0, -10.0), (100, -17.0, -6.0), (101, -5.0, -2.0))])
        L = sc.add(nm, solid_rect, x_, y_, w_, h_, BL)
"""),
    ("""    for i, (x_, y_, w_, h_, f0, f1) in enumerate(((1690, -700, 1.6, 2500, 86, 98), (600, 330, 4200, 1.6, 86, 98), (600, 748, 4200, 1.6, 86, 98),
                                                  (2110, -700, 1.6, 2500, 86, 98), (600, 150, 4200, 1.6, 86, 98))):
        sc.add('A_guide%d' % i, guide, x_, y_, w_, h_, k=1, crop=False).span(f0, f1).set(pano=False)
""", """    for i, (x_, y_, w_, h_, f0, f1) in enumerate(((1690, -700, 1.6, 2500, 86, 98), (0, 330, 4800, 1.6, 86, 98), (0, 748, 4800, 1.6, 86, 98),
                                                  (2110, -700, 1.6, 2500, 86, 98), (0, 150, 4800, 1.6, 86, 98))):
        sc.add('A_guide%d' % i, guide, x_, y_, w_, h_, k=1, crop=False).span(f0, f1).set(pano=False)
    # on the source the guides run BEHIND the ring group (pink / blue sectors, record): move them down in the stack
    gl = [L_ for L_ in sc.layers if L_.name.startswith('A_guide')]
    for L_ in gl:
        sc.layers.remove(L_)
    gi = [i for i, L_ in enumerate(sc.layers) if L_.name == 'A_buildings'][0] + 1
    sc.layers[gi:gi] = gl
"""),
])

# ------------------------------------------------------------------ section C
s = io.open(B + 'sec_c.py', encoding='utf-8').read()


def repl(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)


# RGB bars: behind the card block and the wire blobs
i0 = s.index("    # thick red / blue / green bars just above the ruler (167-174)")
i1 = s.index("    centre(sc.add('C_four', outlined, 0, 0, '(4)'")
bars = s[i0:i1]
s = s[:i0] + s[i1:]
repl("    # ---------------- card / dialog / escalator block ----------------\n", bars + "\n    # ---------------- card / dialog / escalator block ----------------\n")

# backdrop pieces rearranged: building / dense tree (now right of the tower) / tower / small tree / lamps / drum / blocks
repl("""BD_BOX = {'left': (0, 0, 760, 1004), 'lamps': (760, 700, 925, 1004), 'drum': (925, 430, 1536, 831), 'blocks': (925, 831, 1536, 1004)}""",
     """BD_BOX = {'bld': (0, 300, 291, 1004), 'tree1': (291, 380, 547, 1004), 'tower': (547, 0, 590, 1004), 'tree2': (590, 480, 760, 1004),
          'lamps': (760, 700, 925, 1004), 'drum': (925, 430, 1536, 831), 'blocks': (925, 831, 1536, 1004)}""")
repl("""    if kind == 'left':
        al = np.where((xx > 588) & (yy < 500), 0.0, al)          # the stay cables are drawn separately
    if kind == 'drum':""", """    if kind == 'drum':                                           # (the stay cables are drawn separately)""")
repl("""    pieces = (('left', 5527.4, -512.0, 0.794, 1.048), ('lamps', 6120.0, 80.0, 1.0, 1.513), ('drum', 6387.6, 213.5, 0.467, 0.39),
              ('blocks', 6387.6, 370.0, 0.467, 0.9827))""",
     """    pieces = (('bld', 5527.4, -197.7, 1.34, 1.048), ('tree2', 5850.0, 300.0, 0.53, 0.458), ('tower', 5962.0, -512.0, 0.66, 1.048),
              ('tree1', 5945.0, 190.0, 0.70, 0.561), ('lamps', 6120.0, 80.0, 1.0, 1.513), ('drum', 6387.6, 213.5, 0.467, 0.39),
              ('blocks', 6387.6, 370.0, 0.467, 0.9827))""")
repl("""        L = sc.add('C_bdline_' + kind, bd_piece, wx_, wy_, kind, 'lines', sx_, sy_, crop=False)
        L.span(150)""", """        L = sc.add('C_bdline_' + kind, bd_piece, wx_, wy_, kind, 'lines', sx_, sy_, crop=False)
        L.set(opacity=45.0 if kind == 'lamps' else 86.0)
        L.span(150)""")
# wire blobs: larger, heavier
repl("""    col = (26, 32, 150, 255)
    for (cx_, cy_, rx, ry, n, m) in ((6074.0, 524.0, 106.0, 100.0, 16, 8), (6296.0, 532.0, 122.0, 118.0, 18, 10)):""",
     """    col = (22, 26, 138, 255)
    for (cx_, cy_, rx, ry, n, m) in ((6074.0, 525.0, 120.0, 110.0, 16, 8), (6297.0, 534.0, 134.0, 126.0, 18, 10)):""")
repl("""        c.line(out + [out[0]], col, 1.4, joint=None)""", """        c.line(out + [out[0]], col, 1.7, joint=None)""")
repl("""                c.line([p, out[int(i_)]], col, 0.95)
            c.line([p, inner[(j_ + 1) % m]], col, 0.95)
            c.line([p, inner[(j_ + 3) % m]], col, 0.8)""", """                c.line([p, out[int(i_)]], col, 1.15)
            c.line([p, inner[(j_ + 1) % m]], col, 1.15)
            c.line([p, inner[(j_ + 3) % m]], col, 1.0)""")
repl("""    c = Canvas(5950, 395, 6440, 670, k=K, ss=3)
    col = (22, 26, 138, 255)""", """    c = Canvas(5940, 385, 6445, 680, k=K, ss=3)
    col = (22, 26, 138, 255)""")
# church: larger disc, more contrast
repl("""CH_C, CH_R = (6314.0, 489.0), 192.0""", """CH_C, CH_R = (6314.0, 489.0), 200.0""")
repl("""    x0, y0, x1, y1 = 6306, 290, 6512, 496
    c = Canvas(x0, y0, x1, y1, k=K, ss=2)
    c.image(gen('church-bw.png').convert('RGBA'), 6310.0, 297.3, w=198.0)
    img = c.done()""", """    x0, y0, x1, y1 = 6306, 282, 6520, 496
    c = Canvas(x0, y0, x1, y1, k=K, ss=2)
    ph = np.asarray(gen('church-bw.png').convert('RGB')).astype(np.float32)
    ph = np.clip((ph - 128.0) * 1.32 + 114.0, 0, 255).astype(np.uint8)                 # the source is harsher
    c.image(Image.fromarray(ph, 'RGB').convert('RGBA'), 6306.0, 288.0, w=212.0)
    img = c.done()""")
repl("""    sc.add('C_church', church_disc, 6306, 290, crop=False).span(168).pop(168, 2, 0.6)""",
     """    sc.add('C_church', church_disc, 6306, 282, crop=False).span(168).pop(168, 2, 0.6)""")
# clouds paler, spray higher and finer, a second batch of blots from 175
repl("""    img = from_arr(lerp_color((204, 222, 246), (253, 254, 255), t ** 0.7), np.ones((h, w), np.float32) * 0.92)""",
     """    img = from_arr(lerp_color((222, 234, 248), (255, 255, 255), t ** 0.7), np.ones((h, w), np.float32) * 0.9)""")
repl("""    for _ in range(130):
        t = rng.random()
        x_ = 6736 + t * 205 + rng.normal(0, 6)
        y_ = 566 + t * 36 + rng.normal(0, 13) * (0.5 + t)
        c.circle(x_, y_, 0.45 + rng.random() ** 3 * 2.4, fill=bk)""", """    for _ in range(95):
        t = rng.random()
        x_ = 6736 + t * 205 + rng.normal(0, 6)
        y_ = 550 + t * 30 + rng.normal(0, 9) * (0.5 + t)
        c.circle(x_, y_, 0.4 + rng.random() ** 3 * 1.7, fill=bk)""")
repl("""def ice():""", """def splatter2(seed=9):
    \"\"\"the larger crowd of blots that has gathered by frame 175 (world 6731..6925 x 447..541)\"\"\"
    rng = np.random.default_rng(seed)
    c = Canvas(6720, 436, 6940, 552, k=K, ss=3)
    for _ in range(30):
        x_ = 6740 + rng.random() * 175
        y_ = 456 + rng.random() * 78 * (0.45 + 0.55 * (1 - (x_ - 6740) / 175.0))
        c.circle(x_, y_, 1.6 + rng.random() ** 2 * 6.0, fill=(8, 8, 8, 255))
    return c


def helix_plot():
    \"\"\"what is left of the 3-D helix plot around the DNA: two thin ellipses and a few axis numbers\"\"\"
    c = Canvas(5890, 600, 6070, 815, k=K, ss=3)
    g = (30, 30, 34, 255)
    c.ellipse(5908, 670, 6052, 710, outline=g, width=0.5)
    c.ellipse(5880 + 12, 734, 6070 - 2, 786, outline=g, width=0.5)
    for (x_, y_, t_) in ((5996, 613, '12'), (5996, 640, '10'), (5996, 672, '8'), (5991, 745, '2'), (6014, 772, '-1'), (5926, 792, '-0.5'),
                         (6002, 800, '0.5'), (6042, 795, '1')):
        c.text(x_, y_, t_, 'arial.ttf', 5.2, g, anchor='mm')
    return c


def bullet_tri():
    c = Canvas(-8, -8, 8, 8, k=4, ss=3)
    c.poly([(-5, -5.5), (5.5, 0), (-5, 5.5)], (196, 22, 70, 255))
    return c


def ice():""")
repl("""    sc.addc('C_splatter', splatter).span(166).pop(166, 2, 0.3)
""", """    sc.addc('C_splatter', splatter).span(166).pop(166, 2, 0.3)
    sc.addc('C_splatter2', splatter2).span(175).pop(175, 2, 0.5)
    centre(sc.add('C_5912', text_asset, 0, 0, '5912', 'Montserrat-Bold.ttf', 8.5, (196, 22, 70), tracking=-0.3), 6992.0, 497.0).span(176)
    L = sc.addc('C_5912tri', bullet_tri, pivot=(0, 0))
    L.x += 7027.0
    L.y += 497.0
    L.pivot = (7027.0, 497.0)
    L.span(176)
""")
repl("""    sc.addc('C_dna', dna).span(147).wipe(147, 3, angle=0)
""", """    sc.addc('C_helixplot', helix_plot).span(147)
    sc.addc('C_dna', dna).span(147).wipe(147, 3, angle=0)
""")
# sign / toggle a little lower, bigger 3279, bolder (elevator), blue axis arrow, wavy
s = s.replace('559.5]', '561.5]').replace("L.y += 559.5\n    L.pivot = (6518.0, 559.5)", "L.y += 561.5\n    L.pivot = (6518.0, 561.5)")
s = s.replace('599.5]', '603.5]').replace("L.y += 599.5\n    L.pivot = (6714.0, 599.5)", "L.y += 603.5\n    L.pivot = (6714.0, 603.5)")
repl("""'3279', 'Montserrat-Bold.ttf', 15.0, (226, 30, 84)""", """'3279', 'Montserrat-Bold.ttf', 19.0, (226, 30, 84)""")
repl("""'(elevator)', 'timesi.ttf', 24.5, tracking=-0.3)""", """'(elevator)', 'timesi.ttf', 24.5, stroke=1.5, tracking=-0.3)""")
repl("""    L = sc.addc('C_axis_b', axis_line, 2400, (30, 40, 200), 800.0, pivot=(0, 0))""", """    L = sc.addc('C_axis_b', axis_line, 2400, (30, 40, 200), 400.0, pivot=(0, 0))""")
repl("""        c.line(pts, (30, 30, 30, 255), 1.4)""", """        c.line(pts, (16, 16, 16, 255), 2.3)""")
# the long crimson sentence: longer, darker, measured slope
repl("""    L = sc.add('C_redtext', path_text, 6650, 296, 'She begins a journey across an immense river of time, where countless fragments of information', 'consola.ttf', 8.0, (226, 30, 70))
    L.pivot = (6650, 300)
    L.span(170).set(rotation=-24.0).wipe(170, 5, angle=-90)""", """    L = sc.add('C_redtext', path_text, 6664, 301, 'She begins a journey across an immense river of time, where countless fragments of information, memories, '
               'civilizations, and possibilities rush past her - some nearly witnessed, others long forgotten.', 'consolab.ttf', 7.2, (176, 20, 62))
    L.pivot = (6664, 305)
    L.span(174).set(rotation=-22.4).wipe(174, 4, angle=-90)""")
# the rolling ball and the bar behind it are much heavier on the source
repl("""    L = sc.add('C_bullet', solid_rect, 6990, 546, 44, 4, (10, 10, 10))""", """    L = sc.add('C_bullet', solid_rect, 6990, 543.5, 118, 9, (14, 14, 14))""")
repl("""    L = sc.add('C_bulletdot', circle_outline, 6975, 541, 3.0, 6.0, (10, 10, 10), crop=False)""",
     """    L = sc.add('C_bulletdot', circle_outline, 6966, 532, 4.0, 8.0, (10, 10, 10), crop=False)""")
io.open(B + 'sec_c.py', 'w', encoding='utf-8').write(s)
print('patched sec_c.py')
