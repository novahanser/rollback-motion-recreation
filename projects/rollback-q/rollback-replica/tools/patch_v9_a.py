"""v9, sec_a.py: sunset photo, wires, lasso lines, vinyl orbit, grey ring geometry, houses, horn sprites, pink sector keys."""
import io, os
D = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts'


def patch(name, pairs):
    p = os.path.join(D, name)
    s = io.open(p, encoding='utf-8').read()
    for old, new in pairs:
        assert s.count(old) == 1, (name, s.count(old), old[:80])
        s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
    print(name, 'ok')


pairs = []

# ---------------------------------------------------------------- imports
pairs.append(("import shapes0 as S0\n\nK = 2\nRC = (700.0, 540.0)                 # ring centre\n",
              "import shapes0 as S0\nimport horn\n\nK = 2\nRC = (700.0, 540.0)                 # ring centre\n"
              "VIN_C, VIN_R = (980.0, 436.5), 215.0       # vinyl record: resting centre / radius\n"
              "CRES_C, CRES_R0, CRES_R1 = (750.0, 540.0), 177.0, 276.0    # grey half ring under the ruler\n"))

# ---------------------------------------------------------------- sunset photo
pairs.append(("""def sunset_photo():
    return fit(quadrant('photos-sheet.png', 1, 0), 163 * K, 168 * K)
""", """def sunset_photo():
    \"\"\"dusk city photo (GPT image redrawn from frame 46) between two black posts; the upper third is washed out and two thin
    white lines cross it, as in the source.  175 x 172 world px, top-left at (647, 500).\"\"\"
    W_, H_ = 175 * K, 172 * K
    bar = int(12.5 * K)
    a = np.asarray(fit(gen('sunset-city.png').convert('RGB'), W_ - 2 * bar, H_)).astype(np.float32)
    g = a.mean(axis=2, keepdims=True)
    a = g + (a - g) * 0.80                                        # the source is less saturated ...
    a[..., 1] = np.clip(a[..., 1] * 1.05 + 5, 0, 255)             # ... and its glow is more yellow than orange
    h, w = a.shape[:2]
    t = np.clip(np.linspace(0, 1, h)[:, None] / 0.38, 0, 1)
    wash = (0.52 + 0.48 * t)[..., None]
    a = a * wash + np.array((234, 242, 240), np.float32) * (1 - wash)
    out = Image.new('RGBA', (W_, H_), (8, 8, 8, 255))
    out.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGB'), (bar, 0))
    d = ImageDraw.Draw(out)
    for yy in (589.0, 653.0):
        py = int((yy - 500.0) * K)
        d.line([(0, py), (W_, py)], fill=(246, 246, 246, 235), width=max(1, K // 2))
    return out
"""))

# ---------------------------------------------------------------- wires
pairs.append(("""def wires():
    c = Canvas(290, 320, 1050, 520, k=K, ss=3)
    col = (58, 58, 62, 255)
    for (y0, x1, y1) in ((428, 1010, 338), (452, 1020, 392), (480, 1030, 448), (505, 1040, 500)):
        c.dashed((300, y0), (x1, y1), col, 1.3, 15, 5)
        for t in (0.52, 0.585, 0.65):
            bx, by = 300 + (x1 - 300) * t, y0 + (y1 - y0) * t
            ang_ = math.degrees(math.atan2(y1 - y0, x1 - 300))
            blob = Image.new('RGBA', (int(16 * c.f), int(7 * c.f)), (0, 0, 0, 0))
            ImageDraw.Draw(blob).ellipse([0, 0, blob.width - 1, blob.height - 1], fill=(34, 34, 40, 255))
            blob = blob.rotate(-ang_, resample=Image.BICUBIC, expand=True)
            px_, py_ = c.P(bx, by)
            c.paste(blob, px_ - blob.width / 2, py_ - blob.height / 2)
    return c
""", """def wires():
    \"\"\"four parallel power lines (fine dotted hairlines rising to the right) with pairs of dark insulators\"\"\"
    c = Canvas(420, 260, 1110, 500, k=K, ss=3)
    col = (56, 56, 62, 255)
    lines = [((430, 363), (900, 279), (727, 762)), ((430, 440), (1090, 280), (655, 690)), ((560, 454), (1095, 335), (835, 870)),
             ((610, 481), (1095, 377), (912,))]
    for (p0, p1, blobs) in lines:
        c.dashed(p0, p1, col, 0.9, 2.2, 1.8)
        ang_ = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
        for bx in blobs:
            t = (bx - p0[0]) / float(p1[0] - p0[0])
            by = p0[1] + (p1[1] - p0[1]) * t
            blob = Image.new('RGBA', (int(15 * c.f), int(5.2 * c.f)), (0, 0, 0, 0))
            ImageDraw.Draw(blob).rounded_rectangle([0, 0, blob.width - 1, blob.height - 1], radius=2.2 * c.f, fill=(30, 30, 36, 255))
            blob = blob.rotate(-ang_, resample=Image.BICUBIC, expand=True)
            px_, py_ = c.P(bx, by)
            c.paste(blob, px_ - blob.width / 2, py_ - blob.height / 2)
    return c
"""))

# ---------------------------------------------------------------- holo saturation
pairs.append(("    return S0.holo_disc(830.0, k=1, seed=11, rim=True, sat=0.5)\n",
              "    return S0.holo_disc(830.0, k=1, seed=11, rim=True, sat=0.2)\n"))

# ---------------------------------------------------------------- vinyl: a full disc centred on VIN_C
pairs.append(("""def vinyl():
    x0, y0, x1, y1 = 760, 215, 1200, 545
    w, h = (x1 - x0) * K, (y1 - y0) * K
    x, y = grid(w, h)
    wx, wy = x / K + x0, y / K + y0
    d = np.hypot(wx - 980, wy - 437)
    a = cov((d - 215) * K) * cov((np.hypot(wx - 700, wy - 540) - 425) * K) * cov((wy - 540) * K)
    th = np.radians(ang(wx, wy, 980, 437))
""", """def vinyl():
    \"\"\"the record: a full disc in a square canvas centred on VIN_C (it orbits the ring centre, so nothing is clipped here)\"\"\"
    x0, y0 = VIN_C[0] - VIN_R - 2, VIN_C[1] - VIN_R - 2
    w = h = int((2 * VIN_R + 4) * K)
    x, y = grid(w, h)
    wx, wy = x / K + x0, y / K + y0
    d = np.hypot(wx - VIN_C[0], wy - VIN_C[1])
    a = cov((d - VIN_R) * K)
    th = np.radians(ang(wx, wy, VIN_C[0], VIN_C[1]))
"""))
pairs.append(("""        cx_ = (980 - x0) * K + 56 * K * math.cos(math.radians(ang_))
        cy_ = (437 - y0) * K + 56 * K * math.sin(math.radians(ang_))
""", """        cx_ = (VIN_C[0] - x0) * K + 56 * K * math.cos(math.radians(ang_))
        cy_ = (VIN_C[1] - y0) * K + 56 * K * math.sin(math.radians(ang_))
"""))

# ---------------------------------------------------------------- pale inner disc -> white paper
pairs.append(("""    t = np.clip(((wx - 520) / 360.0) * 0.6 + (1 - (wy - 345) / 195.0) * 0.4, 0, 1)
    rgb = grad_stops(t, [(0, (240, 204, 222)), (0.45, (228, 228, 236)), (1, (196, 212, 238))])
    rgb = rgb + noise(h, w, 21, 11.0)[..., None]
    return from_arr(rgb, a * 0.96)
""", """    t = np.clip(((wx - 520) / 360.0) * 0.6 + (1 - (wy - 345) / 195.0) * 0.4, 0, 1)
    rgb = grad_stops(t, [(0, (247, 244, 247)), (0.45, (248, 248, 250)), (1, (243, 246, 250))])
    rgb = rgb + noise(h, w, 21, 2.0)[..., None]
    return from_arr(rgb, a)


def inner_low():
    \"\"\"white paper inside the grey ring, below the ruler (hides the record where it passes behind)\"\"\"
    r = CRES_R0 + 2.0
    w, h = int((2 * r + 4) * K), int((r + 4) * K)
    x, y = grid(w, h)
    wx, wy = x / K - r - 2, y / K - 2                       # relative to CRES_C
    a = cov((np.hypot(wx, wy) - r) * K) * cov(-wy * K)
    return from_arr(np.dstack([np.full_like(wx, 249.0)] * 3) + noise(h, w, 22, 1.5)[..., None], a)
"""))

# ---------------------------------------------------------------- grey half ring
pairs.append(("""def crescent():
    x0, y0, x1, y1 = 405, 538, 1040, 826
    w, h = (x1 - x0) * K, (y1 - y0) * K
    x, y = grid(w, h)
    wx, wy = x / K + x0, y / K + y0
    a = cov((np.hypot(wx - 722, wy - 510) - 312) * K) * (1 - cov((np.hypot(wx - 740, wy - 525) - 195) * K)) * cov((540 - wy) * K)
    th = ang(wx, wy, 722, 510)                       # 180 (left) .. 270 (bottom) .. 360 (right)
    t = np.clip((th - 180.0) / 180.0, 0, 1)
    v = grad_stops(t, [(0, (26, 26, 26)), (0.45, (62, 62, 62)), (1, (156, 156, 156))])
    v = v + noise(h, w, 8, 2.0)[..., None]
    return from_arr(v, a)
""", """def crescent(mode=0):
    \"\"\"half ring below the ruler, centre CRES_C, radii CRES_R0..CRES_R1, in a square canvas centred on CRES_C.
    mode 0: light head at the right end fading to a black tail (the ring is turned out from under the ruler head first);
    mode 1: plain black (the head goes dark after frame 58).\"\"\"
    x0, y0 = CRES_C[0] - CRES_R1 - 2, CRES_C[1] - CRES_R1 - 2
    w = h = int((2 * CRES_R1 + 4) * K)
    x, y = grid(w, h)
    wx, wy = x / K + x0, y / K + y0
    d = np.hypot(wx - CRES_C[0], wy - CRES_C[1])
    a = cov((d - CRES_R1) * K) * cov((CRES_R0 - d) * K) * cov((CRES_C[1] - wy) * K)
    if mode == 1:
        return from_arr((3, 3, 3), a)
    phi = np.degrees(np.arctan2(wy - CRES_C[1], wx - CRES_C[0]))           # 0 = right end, 90 = bottom, 180 = left end
    g = [(0.0, 152.0), (15 / 180.0, 124.0), (35 / 180.0, 74.0), (55 / 180.0, 24.0), (66 / 180.0, 4.0), (1.0, 3.0)]
    v = grad_stops(np.clip(phi / 180.0, 0, 1), [(p, (q, q, q)) for p, q in g])
    v = v + noise(h, w, 8, 1.6)[..., None]
    return from_arr(v, a)
"""))

# ---------------------------------------------------------------- curl
pairs.append(("""    cw, chh = 95.0, 127.0
    w, h = int(cw * K), int(chh * K)
    x, y = grid(w, h)
    wx, wy = x / K, y / K
    dist = np.hypot(wx - cw, (wy - chh) * cw / chh)
    rgb = lerp_color((32, 32, 34), (124, 124, 126), np.clip(np.hypot(wx, wy) / 135.0, 0, 1) ** 1.5)
""", """    cw, chh = 147.0, 147.0
    w, h = int(cw * K), int(chh * K)
    x, y = grid(w, h)
    wx, wy = x / K, y / K
    dist = np.hypot(wx - cw, (wy - chh) * cw / chh)
    rgb = lerp_color((30, 30, 32), (126, 126, 128), np.clip(np.hypot(wx, wy) / 150.0, 0, 1) ** 1.4)
"""))

# ---------------------------------------------------------------- wire horn -> per-frame sprites live in horn.py
pairs.append(("""def wire_horn():
    c = Canvas(640, 330, 1140, 830, k=1, ss=3)
    ax, ay, bx, by = 690.0, 400.0, 1000.0, 700.0
    L = math.hypot(bx - ax, by - ay)
    ux, uy = (bx - ax) / L, (by - ay) / L
    nx, ny = -uy, ux
    col = (62, 62, 66, 215)
    rings = []
    for i in range(30):
        t = i / 29.0
        cx_, cy_ = ax + (bx - ax) * t, ay + (by - ay) * t
        r = 24 + 100 * t ** 1.7
        pts = []
        for j in range(49):
            th = 2 * math.pi * j / 48.0
            pts.append((cx_ + r * math.cos(th) * nx + 0.33 * r * math.sin(th) * ux,
                        cy_ + r * math.cos(th) * ny + 0.33 * r * math.sin(th) * uy))
        rings.append(pts)
        c.line(pts, col, 0.7)
    for j in range(0, 48, 4):
        c.line([rg[j] for rg in rings], col, 0.7)
    return c
""", """def horn_sprite(f, ver):
    \"\"\"the wire horn at frame f (see horn.py); `ver` only keys the asset cache to the pose tables\"\"\"
    return horn.horn_frame(f)
"""))

# ---------------------------------------------------------------- thin lines: lasso + curve with a ringed end
pairs.append(("""def lines_a():
    c = Canvas(560, 100, 1130, 610, k=K, ss=3)
    bk = (20, 20, 20, 255)
    c.arc(640, 340, 55, -160, 100, bk, 1.0)
    c.circle(705, 500, 28, outline=bk, width=1.0)
    c.circle(870, 125, 12, outline=bk, width=1.0)
    c.circle(858, 495, 5, outline=bk, width=1.0)
    c.circle(962, 568, 13, outline=bk, width=1.0)
    c.line([(642, 337), (870, 125), (768, 497), (858, 495)], (60, 60, 60, 255), 1.0)
    gr = (30, 140, 44, 255)
    c.line([(640, 480), (700, 470), (800, 478), (950, 505), (1110, 538)], gr, 1.3)
    c.line([(575, 590), (660, 560), (740, 542), (830, 558), (935, 592)], gr, 1.3)
    return c
""", """def _smooth(pts, n=14):
    \"\"\"Catmull-Rom through the points\"\"\"
    out = []
    P = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            t = j / float(n)
            out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t * t
                                    + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t ** 3) for k in (0, 1)))
    out.append(pts[-1])
    return out


def lines_a():
    \"\"\"two dark-green hairlines: a long thin 'lasso' loop that ends on the 2030 pin, and a curve that rises over the photo and
    drops to a small ringed end\"\"\"
    c = Canvas(560, 440, 1130, 640, k=K, ss=3)
    gr = (26, 104, 40, 255)
    top = _smooth([(634, 478), (646, 470), (700, 465), (800, 470), (900, 485), (1000, 505), (1110, 527)])
    bot = _smooth([(1110, 527), (1000, 517), (900, 507), (800, 497), (700, 490), (646, 486), (634, 478)])
    c.line(top + bot, gr, 1.0)
    low = _smooth([(575, 590), (660, 560), (740, 543), (830, 556), (900, 580), (948, 603)])
    c.line(low, gr, 1.0)
    c.circle(953, 607, 5.0, outline=(34, 34, 38, 255), width=0.9)
    return c
"""))

# ---------------------------------------------------------------- houses
pairs.append(("""def buildings():
    im = gen('buildings.png')
    im = im.crop(im.getbbox())
    w = 245 * K
    return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
""", """def buildings():
    \"\"\"white paper-model houses (GPT image redrawn from frames 42 / 46); 501 world px wide, top-left at (852, 419)\"\"\"
    im = gen('buildings2.png')
    a = np.asarray(im).copy()
    a[..., 3] = np.where(a[..., 3] > 40, a[..., 3], 0).astype(np.uint8)
    im = Image.fromarray(a, 'RGBA')
    im = im.crop(im.getbbox())
    w = 501 * K
    return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
"""))

# ================================================================ build()
pairs.append(("    L.span(27).key('position', [k_ for k_ in sheet_pos if k_[0] >= 27]).key('opacity', [(27, 0.0, LIN), (31, 78.0, LIN)])\n",
              "    L.span(27).key('position', [k_ for k_ in sheet_pos if k_[0] >= 27]).key('opacity', [(27, 0.0, LIN), (31, 48.0, LIN)])\n"))

pairs.append(("""    L = sc.add('A_sunset', sunset_photo, 654, 498, pivot=(654, 498))
    L.span(22, 65).set(pano=False)
    L.key('position', [(22, [743, 471], HOLD), (24, [673, 472], HOLD), (25, [673, 475], HOLD), (26, [663, 477], HOLD), (27, [661, 470], HOLD),
                       (28, [654, 487], HOLD), (30, [654, 498], HOLD)])
    L.key('scale', [(22, [106, 5], HOLD), (23, [106, 11], HOLD), (24, [147, 22], HOLD), (25, [148, 50], HOLD), (26, [155, 75], HOLD),
                    (27, [110, 88], HOLD), (28, [100, 100], HOLD), (60, [100, 100], LIN), (64, [100, 4], LIN)])
    L.fx('ADBE Wave Warp', **{'ADBE Wave Warp-0001': 2, 'ADBE Wave Warp-0002': [(22, 0.0, HOLD), (25, 14.0, HOLD), (26, 18.0, HOLD), (27, 10.0, HOLD), (28, 0.0, HOLD)],
                              'ADBE Wave Warp-0003': 46.0, 'ADBE Wave Warp-0004': 0.0, 'ADBE Wave Warp-0005': 0.0})
""", """    L = sc.add('A_sunset', sunset_photo, 647, 500, pivot=(647, 500), crop=False)
    L.span(22, 64).set(pano=False)
    L.key('position', [(22, [736, 473], HOLD), (24, [666, 474], HOLD), (25, [666, 477], HOLD), (26, [656, 479], HOLD), (27, [654, 472], HOLD),
                       (28, [647, 489], HOLD), (30, [647, 500], HOLD)])
    L.key('scale', [(22, [106, 5], HOLD), (23, [106, 11], HOLD), (24, [147, 22], HOLD), (25, [148, 50], HOLD), (26, [155, 75], HOLD),
                    (27, [110, 88], HOLD), (28, [100, 100], HOLD)])
    L.fx('ADBE Wave Warp', **{'ADBE Wave Warp-0001': 2, 'ADBE Wave Warp-0002': [(22, 0.0, HOLD), (25, 14.0, HOLD), (26, 18.0, HOLD), (27, 10.0, HOLD), (28, 0.0, HOLD)],
                              'ADBE Wave Warp-0003': 46.0, 'ADBE Wave Warp-0004': 0.0, 'ADBE Wave Warp-0005': 0.0})
    # 57-63: eaten from the top down at 21.7 world px per frame (the city strip at the bottom goes last)
    L.fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': [(22, 0.0, HOLD), (57, 13.0, HOLD), (58, 26.0, HOLD), (59, 38.7, HOLD), (60, 51.6, HOLD),
                                                          (61, 63.8, HOLD), (62, 75.8, HOLD), (63, 89.3, HOLD)],
                                'ADBE Linear Wipe-0002': 180.0, 'ADBE Linear Wipe-0003': 0.0})
"""))

# ring group: houses first, then blue sector / record / paper / grey ring / curl / road / pink sector / horn
pairs.append(("""    # ---------------- ring group (stepped on the 6-frame grid, measured from the source) ----------------
    L = sc.add('A_crescent', crescent, 405, 538)
    cres = [(34, 60), (35, 75), (36, 65), (41, 105), (42, 115), (43, 125), (47, 145), (51, 180)]       # (frame, swept degrees)
    L.flashes([(34, (255, 255, 255)), (35, (118, 118, 118)), (36, (190, 190, 190)), (37, None)])
    L.span(34).fx('ADBE Radial Wipe', **{'ADBE Radial Wipe-0001': [(f, 100.0 * (1 - d / 360.0), HOLD) for f, d in cres],
                                         'ADBE Radial Wipe-0002': 270.0,
                                         'ADBE Radial Wipe-0003': [(722 - L.x) * K, (510 - L.y) * K],
                                         'ADBE Radial Wipe-0004': 1})
    sc.add('A_curl', curl, 821, 677).span(25)
    sc.addc('A_road', road).span(27).flash(27, (0, 0, 0), 1)

""", """    # ---------------- houses: behind the ring group; the tube, the pins and the ruler pass in front ----------------
    L = sc.add('A_buildings', buildings, 852, 419)
    L.span(37).flash(37, PK, 2)

    # ---------------- ring group (stepped on the 6-frame grid, measured from the source) ----------------
"""))

pairs.append(("""    # vinyl: a flat pink disc holds its place (55-59), the record itself lands on 60
    L = sc.add('A_vinyl_ph', circle_outline, 980 - 94, 437 - 94, 46.0, 92.0, PK, pivot=(980, 437), crop=False)
    L.span(55, 60).set(pano=False)
    sc.add('A_vinyl', vinyl, 760, 215, pivot=(980, 437)).span(60)
    sc.add('A_ring_inner', ring_inner, 500, 340).span(60)

    # pink sector: a sliver grows out of 0 deg (50-54), then the quarter ring steps round to 90-180
    L = sc.add('A_pink_sliver', ring_sector, RC[0] - 431, RC[1] - 431, 278.5, 429.0, 0.0, 25.0, PK, pivot=RC)
    L.span(50, 55).set(pano=False).fx('ADBE Radial Wipe', **{
        'ADBE Radial Wipe-0001': [(f, (25.0 - w) / 3.6, HOLD) for f, w in ((50, 4), (51, 6), (52, 8), (53, 14), (54, 24))],
        'ADBE Radial Wipe-0002': 65.0, 'ADBE Radial Wipe-0003': [(RC[0] - L.x) * K, (RC[1] - L.y) * K], 'ADBE Radial Wipe-0004': 1})
    L = sc.add('A_ring_pink', ring_sector, RC[0] - 431, RC[1] - 431, 278.5, 429.0, 90.0, 180.0, PK, pivot=RC)
    L.span(55).key('rotation', [(55, 50.0, HOLD), (56, 60.0, HOLD), (60, 40.0, LIN), (64, 36.0, HOLD), (65, 6.0, LIN), (70, 0.0, LIN)])
    L.fx('ADBE Radial Wipe', **{
        'ADBE Radial Wipe-0001': [(f, 100.0 * (1 - w / 360.0), HOLD) for f, w in ((55, 15), (56, 45), (57, 50), (58, 58), (59, 63))] + [(60, 0.0, HOLD)],
        'ADBE Radial Wipe-0002': 0.0, 'ADBE Radial Wipe-0003': [(RC[0] - L.x) * K, (RC[1] - L.y) * K], 'ADBE Radial Wipe-0004': 1})
    L = sc.addc('A_horn', wire_horn, pivot=(690.0, 400.0))
    L.span(39, 61).set(pano=False).key('opacity', [(39, 0, LIN), (41, 100, LIN), (57, 100, LIN), (60, 0, LIN)])
    # 51-56: while the camera pulls back the horn swings up (mouth from lower right to upper right) and grows
    L.key('rotation', [(50, 0.0, LIN), (53, -34.0, LIN), (56, -62.0, LIN), (60, -68.0, LIN)])
    L.key('position', [(50, [690.0, 400.0], LIN), (53, [625.0, 458.0], LIN), (56, [555.0, 512.0], LIN)])
    L.key('scale', [(50, [100.0, 100.0], LIN), (53, [124.0, 124.0], LIN), (56, [147.0, 147.0], LIN)])
""", """    # record: it rides the ring group - its centre orbits the ring centre at radius 298.5 (tracked on the blue dot of the label),
    # easing from 51 deg below its resting place to rest on 87.  51-56 it is only seen through a wedge that opens upwards from
    # (975, 862); the wedge is a 'both ways' radial wipe expressed in the layer's own (turned) space.
    L = sc.add('A_vinyl', vinyl, VIN_C[0] - VIN_R - 2, VIN_C[1] - VIN_R - 2, pivot=RC, crop=False)
    vrot = {51: 51.1, 57: 32.8, 58: 30.3, 59: 27.0, 60: 22.6, 61: 18.2, 62: 16.7, 63: 14.6, 64: 13.3, 65: 11.9, 66: 10.6, 67: 9.5, 68: 8.5,
            69: 7.55, 70: 6.75, 71: 5.95, 72: 5.3, 73: 4.6, 74: 3.9, 75: 3.35, 76: 2.8, 77: 2.5, 78: 2.15, 79: 1.7, 80: 1.5, 81: 1.05,
            82: 0.9, 83: 0.7, 84: 0.5, 86: 0.2, 87: 0.0}
    L.span(51).key('rotation', [(f, r_, HOLD) for f, r_ in sorted(vrot.items())])
    th_ = math.radians(-51.1)
    vx_, vy_ = 975.0 - RC[0], 862.0 - RC[1]
    apx, apy = RC[0] + vx_ * math.cos(th_) - vy_ * math.sin(th_), RC[1] + vx_ * math.sin(th_) + vy_ * math.cos(th_)
    L.fx('ADBE Radial Wipe', **{'ADBE Radial Wipe-0001': [(51, 100.0 * (1 - 25 / 180.0), HOLD), (52, 100.0 * (1 - 30 / 180.0), HOLD),
                                                          (53, 100.0 * (1 - 34 / 180.0), HOLD), (54, 100.0 * (1 - 37 / 180.0), HOLD), (57, 0.0, HOLD)],
                                'ADBE Radial Wipe-0002': 180.0 - 51.1, 'ADBE Radial Wipe-0003': [(apx - L.x) * K, (apy - L.y) * K],
                                'ADBE Radial Wipe-0004': 3})

    # white paper inside the ring: below the ruler (inside the grey ring) and above it (radius 197 around the ring centre)
    sc.add('A_inner_low', inner_low, CRES_C[0] - CRES_R0 - 4, CRES_C[1] - 2, crop=False).span(51)
    sc.add('A_ring_inner', ring_inner, 500, 340).span(57)

    # grey ring: a half ring with a light head that is turned out from under the ruler in steps (swept angle per frame);
    # the piece that arrives on 40 is white for that frame; from 59 the head darkens (a black copy underneath shows through)
    cres = {34: 60, 35: 75, 36: 65, 40: 100, 41: 105, 42: 115, 43: 125, 47: 145, 51: 180}
    ks = sorted(cres.items())
    for nm, mode in (('A_cres_blk', 1), ('A_crescent', 0)):
        L = sc.add(nm, crescent, CRES_C[0] - CRES_R1 - 2, CRES_C[1] - CRES_R1 - 2, mode, pivot=CRES_C, crop=False)
        L.span(34 if mode == 0 else 37).key('rotation', [(f, 180.0 - s_, HOLD) for f, s_ in ks])
        L.fx('ADBE Radial Wipe', **{'ADBE Radial Wipe-0001': [(f, 100.0 * (1 - s_ / 360.0), HOLD) for f, s_ in ks],
                                    'ADBE Radial Wipe-0002': [(f, 90.0 + s_, HOLD) for f, s_ in ks],
                                    'ADBE Radial Wipe-0003': [(CRES_C[0] - L.x) * K, (CRES_C[1] - L.y) * K], 'ADBE Radial Wipe-0004': 1})
    L.flashes([(34, (255, 255, 255)), (35, (118, 118, 118)), (36, (190, 190, 190)), (37, None)])
    L.key('opacity', [(34, 100.0, HOLD), (59, 100.0, LIN), (60, 56.0, LIN), (64, 50.0, LIN), (66, 38.0, LIN), (70, 32.0, LIN), (76, 28.0, LIN),
                      (88, 10.0, LIN)])
    L = sc.add('A_cres_flash', ring_sector, CRES_C[0] - CRES_R1 - 2, CRES_C[1] - CRES_R1 - 2, CRES_R0, CRES_R1, 245.0, 280.0, (255, 255, 255),
               pivot=CRES_C, crop=False)
    L.span(40, 41).set(pano=False)
    sc.add('A_curl', curl, 819, 672).span(25)
    sc.addc('A_road', road).span(27).flash(27, (0, 0, 0), 1)

    # pink sector: a quarter ring wiped in from 0 deg (51-59: leading edge 4, 7, 12, 20, 54, 73, 79, 85, 91 deg), then it steps round
    L = sc.add('A_pink_sliver', ring_sector, RC[0] - 431, RC[1] - 431, 278.5, 429.0, 0.0, 25.0, PK, pivot=RC)
    L.span(51, 55).set(pano=False).fx('ADBE Radial Wipe', **{
        'ADBE Radial Wipe-0001': [(f, (25.0 - w) / 3.6, HOLD) for f, w in ((51, 4), (52, 7), (53, 12), (54, 20))],
        'ADBE Radial Wipe-0002': 65.0, 'ADBE Radial Wipe-0003': [(RC[0] - L.x) * K, (RC[1] - L.y) * K], 'ADBE Radial Wipe-0004': 1})
    L = sc.add('A_ring_pink', ring_sector, RC[0] - 431, RC[1] - 431, 278.5, 429.0, 90.0, 180.0, PK, pivot=RC)
    L.span(55).key('rotation', [(55, 90.0, HOLD), (60, 40.0, LIN), (64, 36.0, HOLD), (65, 6.0, LIN), (70, 0.0, LIN)])
    L.fx('ADBE Radial Wipe', **{
        'ADBE Radial Wipe-0001': [(f, 100.0 * (1 - w / 360.0), HOLD) for f, w in ((55, 54), (56, 73), (57, 79), (58, 85), (59, 90))] + [(60, 0.0, HOLD)],
        'ADBE Radial Wipe-0002': 0.0, 'ADBE Radial Wipe-0003': [(RC[0] - L.x) * K, (RC[1] - L.y) * K], 'ADBE Radial Wipe-0004': 1})

    # wire horn: one sprite per frame while it tumbles (30-73), then the resting pose
    hv = horn.version()
    for f in range(horn.F0, horn.F1):
        L = sc.add('A_horn_%02d' % f, horn_sprite, horn.HW[0], horn.HW[1], f, hv, k=horn.HK)
        L.span(f, f + 1).set(pano=False)
    sc.add('A_horn_end', horn_sprite, horn.HW[0], horn.HW[1], horn.F1, hv, k=horn.HK).span(horn.F1)
"""))

pairs.append(("""    L = sc.add('A_buildings', buildings, 1115, 0)
    L.y = 538 - L.wh
    L.pivot = (L.x + L.ww / 2, L.y + L.wh / 2)
    L.span(37).flash(37, PK, 2)
    L = sc.add('A_crimson',""", """    L = sc.add('A_crimson',"""))

patch('sec_a.py', pairs)

# horn.py: cache key for the pose tables
p = os.path.join(D, 'horn.py')
s = io.open(p, encoding='utf-8').read()
if 'def version()' not in s:
    s += '''

def version():
    """short hash of the pose tables + drawing code revision (keys the asset cache)"""
    import hashlib
    return hashlib.md5((repr(sorted(POSES.items())) + repr(sorted(FAN.items())) + 'draw-3').encode('utf-8')).hexdigest()[:8]
'''
    io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('v9 sec_a patches applied')
