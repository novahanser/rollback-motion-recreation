"""sec_c.py v3: lighter city line art + silhouette fill, measured ruler bar, machine fill wipe, church disc, splatter, ice order,
film-run hook, dot-matrix brightness."""
import io
P = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts\sec_c.py'
src = io.open(P, encoding='utf-8').read()
n_done = [0]


def rep(old, new, count=1):
    global src
    assert src.count(old) >= 1, 'not found: ' + old[:70]
    assert count != 1 or src.count(old) == 1, 'ambiguous: ' + old[:70]
    src = src.replace(old, new)
    n_done[0] += 1


def cut(start, end, new):
    """replace everything from `start` (inclusive) to `end` (exclusive)"""
    global src
    a = src.index(start)
    b = src.index(end, a)
    src = src[:a] + new + src[b:]
    n_done[0] += 1


# ---- escalator: signs a little higher inside the photo (the photo itself moves down in build)
rep("    y = int(163 * K)\n", "    y = int(150 * K)\n")

# ---- line art
cut('def la_city():', 'def la_girl():', r'''def la_city():
    return line_art('lineart-city.png', color=(128, 128, 132), lo=60, hi=215)


def la_city_fill():
    """closed silhouette of the city drawing: solid pink blocks on 150-153 that bleach to a pale paper fill"""
    im = gen('lineart-city.png').convert('L')
    a = np.asarray(im).astype(np.float32)
    dark = (a < 215).astype(np.uint8) * 255
    m = Image.fromarray(dark).filter(ImageFilter.MaxFilter(17)).filter(ImageFilter.MinFilter(13))
    out = Image.new('RGBA', im.size, (255, 255, 255, 0))
    out.putalpha(m)
    return out


def la_machine():
    return line_art('lineart-machine.png', color=(70, 70, 74), lo=60, hi=215)


def la_machine_fill():
    """solid blue silhouette of the machine (frames 166-170)"""
    im = gen('lineart-machine.png').convert('L')
    a = np.asarray(im).astype(np.float32)
    dark = (a < 215).astype(np.uint8) * 255
    m = Image.fromarray(dark).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(5))
    out = Image.new('RGBA', im.size, (64, 84, 232, 0))
    out.putalpha(m)
    return out


''')

# ---- scribble: straight-edged wire mesh instead of a smooth curl
cut('def scribble(seed=11):', '# ----------------------------------------------------------------------------- church disc', r'''def scribble(seed=11):
    """crumpled wireframe: a polyline of straight segments that keeps crossing itself"""
    rng = np.random.default_rng(seed)
    c = Canvas(5950, 400, 6420, 680, k=K, ss=3)
    pts = [(5972 + rng.random() * 420, 424 + rng.random() * 230) for _ in range(46)]
    c.line(pts, (24, 36, 172, 255), 1.15, joint=None)
    for i in range(0, 40, 3):
        c.line([pts[i], pts[i + 5]], (24, 36, 172, 255), 0.8)
    return c


''')

# ---- church disc: stippled grey gradient, dark church with a clock tower, autumn leaves
cut('def church_disc():', 'def no_parking():', r'''def church_disc():
    x0, y0, x1, y1 = 6308, 262, 6552, 506
    w, h = (x1 - x0) * K, (y1 - y0) * K
    x, y = grid(w, h)
    wx, wy = x / K + x0, y / K + y0
    a = cov((np.hypot(wx - 6312, wy - 500) - 236) * K) * cov((6312 - wx) * K) * cov((wy - 500) * K)
    rng = np.random.default_rng(6)
    g = np.clip(((wx - 6312) / 240.0) * 0.55 + ((wy - 262) / 240.0) * 0.85 - 0.12, 0, 1)
    v = (rng.random((h, w)) < g ** 1.2).astype(np.float32) * 228.0 + 10.0
    img = from_arr(np.dstack([v, v, v]), a)
    c = Canvas(x0, y0, x1, y1, k=K, ss=3)
    dk = (22, 22, 24, 255)
    c.poly([(6382, 480), (6382, 398), (6398, 360), (6414, 398), (6414, 480)], dk)                 # tower
    c.poly([(6392, 366), (6398, 326), (6404, 366)], dk)                                           # spire
    c.circle(6398, 410, 7.5, fill=(232, 232, 232, 255), outline=dk, width=0.8)                    # clock
    c.line([(6398, 410), (6398, 405)], dk, 0.9)
    c.line([(6398, 410), (6402, 412)], dk, 0.9)
    c.poly([(6414, 480), (6414, 436), (6440, 418), (6474, 442), (6474, 480)], (40, 40, 42, 255))    # nave
    c.poly([(6410, 438), (6440, 414), (6478, 442), (6474, 446), (6440, 422), (6414, 442)], dk)
    c.rect(6392, 452, 6402, 480, fill=(210, 210, 210, 255))
    for (lx, ly, r_, col) in ((6462, 372, 40, (196, 70, 44)), (6494, 396, -20, (214, 104, 60)), (6478, 426, 70, (188, 60, 40)),
                              (6508, 352, 10, (206, 90, 52)), (6522, 420, -50, (198, 74, 46))):
        leaf = Image.new('RGBA', (int(27 * c.f), int(13 * c.f)), (0, 0, 0, 0))
        ImageDraw.Draw(leaf).ellipse([0, 0, leaf.width - 1, leaf.height - 1], fill=col + (255,))
        ImageDraw.Draw(leaf).line([2, leaf.height / 2, leaf.width - 3, leaf.height / 2], fill=(120, 40, 26, 255), width=max(1, int(0.8 * c.f)))
        leaf = leaf.rotate(r_, resample=Image.BICUBIC, expand=True)
        px_, py_ = c.P(lx, ly)
        c.paste(leaf, px_ - leaf.width / 2, py_ - leaf.height / 2)
    c.text(6440, 372, 'C', 'Montserrat-Bold.ttf', 20, (226, 30, 60, 255), anchor='mm')
    ov = np.asarray(c.done()).copy()
    ov[..., 3] = (ov[..., 3] * (np.asarray(img)[..., 3] / 255.0)).astype(np.uint8)
    img.alpha_composite(Image.fromarray(ov, 'RGBA'))
    return img


''')

# ---- splatter: many fine specks + a few drops, stretched along the ruler
cut('def splatter(seed=4):', 'def ice():', r'''def splatter(seed=4):
    rng = np.random.default_rng(seed)
    c = Canvas(6650, 420, 6935, 590, k=K, ss=3)
    for _ in range(420):
        t = rng.random() ** 1.5
        x = 6915 - t * 250 + (rng.random() - 0.5) * 16
        y = 502 + rng.normal(0, 1) * (10 + 34 * (1 - t) ** 0.7)
        r = (0.5 + rng.random() ** 6 * 12.0) * (1.05 - 0.55 * t)
        c.circle(x, y, r, fill=(8, 8, 8, 255))
    for _ in range(26):                                   # short streaks flying out to the left
        x = 6660 + rng.random() * 120
        y = 500 + rng.normal(0, 1) * 30
        ln = 4 + rng.random() * 14
        c.line([(x, y), (x - ln, y + (rng.random() - 0.5) * 4)], (8, 8, 8, 255), 0.6 + rng.random())
    return c


''')
rep("    return from_arr(rgb, a * 0.9)\n", "    return from_arr(rgb, a * 0.62)\n")

# ---- the pale bar under the ruler (154-164): fixed colours, measured head / tail
cut('def beam(pts):', 'def rgb_bar():', r'''def beam(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    c = Canvas(min(xs) - 2, min(ys) - 2, max(xs) + 2, max(ys) + 2, k=K, ss=3)
    c.poly(pts, rgba(PK))
    return c


def ruler_bar_c():
    """rounded bar just below the ruler, world x 5360..6604: blue-grey -> dark -> pink -> pale -> dark pill end"""
    x0, y0, x1, y1 = 5360, 551, 6604, 607
    k = 1
    w, h = (x1 - x0) * k, (y1 - y0) * k
    x, y = grid(w, h)
    wx = x / k + x0
    rgb = grad_stops((wx - x0) / float(x1 - x0), [(0.0, (160, 172, 184)), (0.22, (176, 186, 196)), (0.43, (158, 166, 174)), (0.50, (112, 114, 118)),
                                                  (0.522, (236, 30, 110)), (0.60, (238, 60, 130)), (0.66, (224, 180, 196)), (0.78, (214, 214, 216)),
                                                  (0.90, (150, 150, 152)), (1.0, (92, 92, 96))])
    sh = np.clip(1 - np.abs(y / h - 0.32) / 0.5, 0, 1)[..., None] * 16.0          # soft highlight along the upper half
    a = cov(sd_box(x, y, w / 2.0, h / 2.0, w / 2.0, h / 2.0, 7.0 * k))
    edge = cov(np.abs(sd_box(x, y, w / 2.0, h / 2.0, w / 2.0, h / 2.0, 7.0 * k) + 1.0) - 0.8)[..., None]
    rgb = (rgb + sh) * (1 - edge) + np.array((60, 60, 66), np.float32) * edge
    return from_arr(rgb, a)


''')

# ---- film dot-matrix print: bigger dots so the lettering reads as bright as in the source
rep("            im = dot_text(s, dot=pitch * 0.62, pitch=pitch, col=col, k=c.f)", "            im = dot_text(s, dot=pitch * 0.95, pitch=pitch, col=col, k=c.f)")

# ---- build: line-art backdrop
cut("    L = sc.add('C_city', la_city, 5750, -20, k=1.72)", "    # ---------------- axis lines", r'''    L = sc.add('C_cityfill', la_city_fill, 5750, -20, k=1.72)
    L.span(150).flashes([(150, (232, 8, 109)), (153, (238, 96, 152)), (155, (244, 160, 192)), (157, (246, 204, 220)), (159, None)]).key(
        'opacity', [(150, 92.0, HOLD), (153, 86.0, HOLD), (156, 74.0, HOLD), (159, 50.0, HOLD)])
    L = sc.add('C_city', la_city, 5750, -20, k=1.72)
    L.span(150).set(opacity=58.0).flashes([(150, (198, 6, 90)), (153, (224, 84, 136)), (156, (236, 156, 182)), (159, None)])
    fade = [(150, 100.0, HOLD), (153, 85.0, HOLD), (154, 65.0, HOLD), (155, 50.0, HOLD), (156, 38.0, HOLD), (157, 26.0, HOLD), (158, 14.0, HOLD)]
    L = sc.add('C_pinkblock', solid_rect, 5526, -136, 240, 240, PK)
    L.span(150, 159).set(pano=False).key('opacity', fade)
    L = sc.add('C_pinkblock2', solid_rect, 6504, 213, 131, 327, PK)
    L.span(150, 159).set(pano=False).key('opacity', fade)
    L = sc.add('C_machine_fill', la_machine_fill, 5940, 478, k=2.0)
    L.span(166, 171).set(pano=False).fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': [(166, 0.0, HOLD), (169, 55.0, HOLD), (170, 90.0, HOLD)],
                                                              'ADBE Linear Wipe-0002': -135.0, 'ADBE Linear Wipe-0003': 0.0})
    sc.add('C_machine', la_machine, 5940, 478, k=2.0).span(166).flashes([(166, (246, 246, 255)), (169, None)])

''')
rep("    sc.add('C_escalator', escalator, 5758, 395).span(145).flash(145, (255, 255, 255), 1)",
    "    sc.add('C_escalator', escalator, 5758, 439).span(145).flash(145, (255, 255, 255), 1)")

cut("    # transient pale 'tube' sliding along the ruler (153-164)", "    # ---------------- scribble / church / sign / toggle", r'''    # pale bar under the ruler (154-164): the head runs right, then the tail follows and leaves a dark pill
    L = sc.add('C_tube', ruler_bar_c, 5360, 551, k=1)
    L.span(154, 165).set(pano=False)
    W_ = 1244.0
    L.fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': [(f, 100.0 * (1 - (h_ - 5360) / W_), HOLD) for f, h_ in
                                                          ((154, 5420), (155, 5588), (156, 5869), (157, 6114), (158, 6360), (159, 6604))],
                                'ADBE Linear Wipe-0002': -90.0, 'ADBE Linear Wipe-0003': 0.0})
    L.fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': [(f, 100.0 * (t_ - 5360) / W_, HOLD) for f, t_ in
                                                          ((154, 5360), (161, 5733), (162, 6106), (163, 6479))],
                                'ADBE Linear Wipe-0002': 90.0, 'ADBE Linear Wipe-0003': 0.0})

''')
rep("    sc.addc('C_scribble', scribble).span(156).wipe(156, 6, angle=-90).flashes([(156, (150, 150, 150)), (160, None)])",
    "    sc.addc('C_scribble', scribble).span(156).wipe(156, 6, angle=-90).flashes([(156, (120, 120, 124)), (166, None)])")

# ice goes under the pink beams
rep("    sc.add('C_ice', ice, 6640, 384).span(168)\n", "")
rep("    big = sc.addc('C_beam', beam,", "    sc.add('C_ice', ice, 6640, 384).span(168)\n    big = sc.addc('C_beam', beam,")
rep("    sc.add('C_toggle', toggle, 6634, 608).span(166).slide(166, 3, dx=-60)",
    "    sc.add('C_toggle', toggle, 6634, 608).span(166).key('position', [(166, [6653, 601], LIN), (167, [6680, 615], LIN), (168, [6705, 628], LIN), (169, [6722, 636], LIN)])")

# film-run digits / chibi parade sit under every film strip
rep("    # ---------------- film frames (C half) ----------------\n",
    "    # ---------------- film-run digits + chibi parade (screen-glued, under the film) ----------------\n"
    "    import filmrun\n    filmrun.build_under(sc)\n\n    # ---------------- film frames (C half) ----------------\n")

io.open(P, 'w', encoding='utf-8', newline='\n').write(src)
print('sec_c.py patched,', n_done[0], 'edits,', len(src.splitlines()), 'lines')
