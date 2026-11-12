"""sec_a.py v3: quarter-annulus paper sheet, lavender -> pastel holo, sliding Farewell, measured gradient bars,
opening extras (labels, mint shapes, wedge, stamp ...)."""
import io, sys
P = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts\sec_a.py'
src = io.open(P, encoding='utf-8').read()

# ------------------------------------------------------------------ 1. asset functions
a0 = src.index('def paper():')
a1 = src.index('# ----------------------------------------------------------------------------- ring group')
NEW_ASSETS = r'''SHEET_C = (228.0, -70.0)            # final centre of the quarter-annulus paper sheet (world)
SHEET_R0, SHEET_R1 = 359.0, 934.0
PINW = (522.0, 155.0)               # pastel pinwheel centre, relative to the sheet centre


def _sheet_alpha(wx, wy, k):
    """quarter annulus around the origin: radial sides point right (0 deg) and down (90 deg)"""
    d = np.hypot(wx, wy)
    return cov((d - SHEET_R1) * k) * cov((SHEET_R0 - d) * k) * cov(-wx * k) * cov(-wy * k)


def sheet(k=1.5):
    """the white 'paper': a quarter ring with a slightly brighter embossed rim"""
    n = int((SHEET_R1 + 4) * k)
    x, y = grid(n, n)
    wx, wy = x / k - 2, y / k - 2
    d = np.hypot(wx, wy)
    e = np.minimum(np.minimum(d - SHEET_R0, SHEET_R1 - d), np.minimum(wx, wy))
    rim = np.clip(1 - e / 34.0, 0, 1)
    v = 241.0 + 11.0 * rim + 3.0 * np.clip((d - SHEET_R0) / (SHEET_R1 - SHEET_R0), 0, 1)
    rgb = np.dstack([v, v, v + 1.0]) + noise(n, n, 5, 1.0)[..., None]
    return from_arr(rgb, _sheet_alpha(wx, wy, k))


def holo2(k=1.0):
    """pastel conic 'pinwheel' printed on the sheet + the lavender crescent hugging its inner arc"""
    n = int((SHEET_R1 + 4) * k)
    x, y = grid(n, n)
    wx, wy = x / k - 2, y / k - 2
    d = np.hypot(wx, wy)
    px_, py_ = PINW
    dp = np.hypot(wx - px_, wy - py_)
    t = (ang(wx, wy, px_, py_) / 360.0 + 0.035 * np.sin(dp / 55.0)) % 1.0
    stops = [(0.00, (250, 206, 226)), (0.07, (252, 226, 214)), (0.16, (226, 236, 252)), (0.30, (214, 216, 250)), (0.44, (236, 246, 246)),
             (0.56, (156, 236, 226)), (0.68, (206, 246, 238)), (0.80, (240, 244, 250)), (0.90, (172, 238, 232)), (1.00, (250, 206, 226))]
    rgb = grad_stops(t, stops)
    al = np.clip((600.0 - dp) / 330.0, 0, 1) ** 1.25 * 0.92
    cres = np.clip(1 - (d - SHEET_R0) / 96.0, 0, 1) * np.clip((d - SHEET_R0) / 6.0, 0, 1)
    th = np.degrees(np.arctan2(wy, wx))                       # 0 = +x, 90 = down
    cres = cres * np.clip((th - 16) / 14.0, 0, 1) * np.clip((87 - th) / 10.0, 0, 1)
    cm = cres[..., None]
    rgb = rgb * (1 - cm) + np.array((150, 150, 240), np.float32) * cm
    al = np.maximum(al, cres * 0.9)
    rgb = rgb + noise(n, n, 9, 3.2)[..., None]
    return from_arr(rgb, al * _sheet_alpha(wx, wy, k))


def lav_disc(R=310.0, k=1.0):
    """soft lavender disc that the holographic print starts from (frames 25-30)"""
    n = int((2 * R + 8) * k)
    c = n / 2.0
    x, y = grid(n, n)
    d = np.hypot(x - c, y - c) / k
    rgb = lerp_color((178, 170, 250), (130, 126, 240), np.clip(d / R, 0, 1) ** 1.5)
    return from_arr(rgb + noise(n, n, 4, 2.5)[..., None], np.clip((R - d) / 26.0, 0, 1) * 0.95)


def vgrad_rect(w, h, c0, c1, k=K):
    W_, H_ = int(w * k), int(h * k)
    x, y = grid(W_, H_)
    return from_arr(lerp_color(c0, c1, y / H_), np.ones((H_, W_), np.float32))


def zigzag():
    """the pink bar crumples into a zigzag for one frame (27)"""
    c = Canvas(428, 578, 682, 728, k=K, ss=3)
    pts = [(437, 715), (470, 594), (503, 702), (536, 602), (569, 702), (602, 602), (635, 702), (668, 612)]
    c.line(pts, rgba(PK), 13.0)
    return c


# ----------------------------------------------------------------------------- opening extras
def mint_shapes(k=K):
    """mint silhouette blocks inside the holographic disc on frames 3-6 (two-tone photo look)"""
    c = Canvas(0, 0, 430, 250, k=k, ss=2)
    m = (104, 250, 190, 255)
    c.poly([(0, 62), (62, 24), (118, 24), (118, 152), (0, 198)], m)
    c.poly([(132, 32), (196, 32), (196, 152), (132, 152)], m)
    c.poly([(214, 10), (262, 10), (262, 28), (300, 28), (300, 152), (214, 152)], m)
    c.poly([(318, 2), (352, 2), (352, 46), (318, 32)], m)
    for i in range(4):
        y = 168 + i * 19
        c.rect(0, y, 196, y + 11, fill=m)
        c.rect(214, y, 322 - i * 6, y + 11, fill=m)
    for xg in (40, 86, 150, 250):
        c.rect(xg, 160, xg + 5, 246, fill=(0, 0, 0, 0))
    return c


def pale_photo(k=K):
    """washed-out greenish landscape that replaces the mint blocks (frames 5-11)"""
    q = fit(quadrant('photos-sheet.png', 1, 0), 320 * k, 160 * k).convert('RGB')
    a = np.asarray(q).astype(np.float32).mean(axis=2)
    t = np.clip((a - 30) / 190.0, 0, 1)
    rgb = lerp_color((150, 196, 170), (238, 248, 240), t)
    h, w = a.shape
    x, y = grid(w, h)
    top = 0.20 + 0.14 * np.sin(x / w * 9.0) * np.sin(x / w * 23.0)
    return from_arr(rgb, (y / h > top).astype(np.float32) * 0.92)


def stamp(R=37.0):
    """round gauge / stamp outline that hangs near the sphere (frames 5-25)"""
    c = Canvas(-R - 3, -R - 3, R + 3, R + 3, k=4, ss=3)
    g = (128, 128, 132, 255)
    c.circle(0, 0, R, outline=g, width=0.7)
    c.circle(0, 0, R * 0.80, outline=g, width=0.6)
    c.circle(0, 0, R * 0.46, outline=g, width=0.6)
    for a_ in range(0, 360, 30):
        r_ = math.radians(a_)
        c.line([(R * 0.80 * math.cos(r_), R * 0.80 * math.sin(r_)), (R * 0.90 * math.cos(r_), R * 0.90 * math.sin(r_))], g, 0.6)
    c.line([(-R * 0.3, R * 0.25), (R * 0.36, -R * 0.2)], g, 0.7)
    c.line([(R * 0.1, -R * 0.36), (R * 0.3, R * 0.3)], g, 0.6)
    c.text(-R * 0.36, -R * 0.38, 'Mo', 'arial.ttf', R * 0.2, g)
    c.text(R * 0.10, R * 0.06, 'H2', 'arial.ttf', R * 0.2, g)
    return c


def wedge_light(L=520.0, half=16.0):
    """soft light sector pointing up from the holo centre (frames 2-14)"""
    c = Canvas(-L, -L, L, 8, k=1, ss=2)
    c.pie(0, 0, L, 90 - half, 90 + half, (250, 250, 250, 236))
    return blur(c.done(), 1.2)


'''
src = src[:a0] + NEW_ASSETS + src[a1:]

# ------------------------------------------------------------------ 2. build()
b0 = src.index('# ----------------------------------------------------------------------------- build')
NEW_BUILD = r'''# ----------------------------------------------------------------------------- build
def _two_wipes(L, x0, W_, heads, tails):
    """show only [tail, head] of a horizontal bar: heads/tails = [(frame, world x)] (hold keys)"""
    L.fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': [(f, 100.0 * (1 - (h - x0) / W_), HOLD) for f, h in heads],
                                'ADBE Linear Wipe-0002': -90.0, 'ADBE Linear Wipe-0003': 0.0})
    L.fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': [(f, 100.0 * (t - x0) / W_, HOLD) for f, t in tails],
                                'ADBE Linear Wipe-0002': 90.0, 'ADBE Linear Wipe-0003': 0.0})
    return L


def build(sc):
    sc.sec = 'A'
    sc.kdef = K
    hc = HOLO_C
    WHITE = [1.0, 1.0, 1.0, 1.0]

    # ---------------- holographic disc (opening) ----------------
    hp = [(2, s2w(2, 1270, 310), 0.405), (3, s2w(3, 1260, 440), 0.978), (5, s2w(5, 1225, 310), 1.11),
          (7, s2w(7, 1195, 310), 1.69), (9, s2w(9, 1155, 300), 1.77), (12, s2w(12, 1114, 310), 1.77),
          (14, s2w(14, 1085, 310), 1.76), (15, s2w(15, 650, 310), 0.94), (16, hc, 1.0)]
    pos_k = [(f, [p[0], p[1]], LIN) for f, p, s_ in hp]
    sca_k = [(f, [s_ * 100, s_ * 100], LIN) for f, p, s_ in hp]

    def hs(f):                                   # disc scale at frame f
        for (f0, _, a), (f1, _, b) in zip(hp[:-1], hp[1:]):
            if f0 <= f <= f1:
                return a + (b - a) * (f - f0) / float(f1 - f0)
        return hp[-1][2]

    L = sc.add('A_halo', S0.halo_ring, hc[0] - 320 * 1.42 - 2, hc[1] - 320 * 1.42 - 2, 320.0, k=K, pivot=hc, crop=False)
    L.span(3, 5).key('position', pos_k[1:3]).key('scale', sca_k[1:3]).set(pano=False)
    L = sc.add('A_holo', S0.holo_disc, hc[0] - 320 - 2, hc[1] - 320 - 2, 320.0, k=K, pivot=hc, crop=False)
    L.span(2, 24).key('position', pos_k).key('scale', sca_k).set(pano=False)
    # frame 2: almost white; 22-23: washes out to white before the soft white disc of frame 24
    L.fx('ADBE Tint', **{'ADBE Tint-0001': WHITE, 'ADBE Tint-0002': WHITE,
                         'ADBE Tint-0003': [(2, 80.0, HOLD), (3, 0.0, HOLD), (22, 30.0, HOLD), (23, 86.0, HOLD)]})

    # mint two-tone blocks (3-6) that turn into a washed-out photo (5-11), both glued to the screen
    L = sc.addc('A_mint', mint_shapes, pivot=(215, 125))
    L.span(3, 7).set(pano=False).key('opacity', [(3, 100.0, HOLD), (5, 84.0, HOLD)])
    pin(L, [(3, 1218, 526), (4, 1218, 526), (5, 1105, 528), (6, 1105, 528)], [(3, 0.95), (6, 0.95)])
    L = sc.add('A_palephoto', pale_photo, 0, 0)
    L.span(5, 12).set(pano=False).key('opacity', [(5, 70.0, HOLD), (7, 100.0, HOLD), (10, 80.0, HOLD), (11, 55.0, HOLD)])
    pin(L, [(5, 822, 648), (6, 822, 648), (7, 960, 547), (11, 966, 550)], [(5, 0.79), (6, 0.79), (7, 1.3), (11, 1.3)])

    # light wedge between two rays of the disc: white (2-8), then mint (9-14); stepped rotation
    w0 = sc.add('A_wedge0', wedge_light, hc[0] - 520, hc[1] - 520, k=1, pivot=hc, crop=False)
    wk = {2: (1.0, 7), 3: (2.44, 36), 4: (1.5, 20), 5: (0.68, -4), 6: (0.7, 0), 7: (0.7, 6), 8: (0.8, 15)}
    w0.span(2, 9).set(pano=False).key('position', pos_k)
    w0.key('scale', [(f, [kx * 100 * max(hs(f), 0.9), 125 * max(hs(f), 0.9)], HOLD) for f, (kx, r) in wk.items()])
    w0.key('rotation', [(f, float(r), HOLD) for f, (kx, r) in wk.items()])
    w0.flashes([(2, (236, 208, 250)), (3, None)])
    w1 = sc.clone('A_wedge1', w0)
    w1.pivot = hc
    wk = {9: (1.55, 26), 10: (1.2, 40), 11: (0.9, -60), 12: (0.6, -115), 13: (0.55, -108), 14: (0.5, -100)}
    w1.span(9, 15).set(pano=False).key('position', pos_k)
    w1.key('scale', [(f, [kx * 100 * hs(f), 125 * hs(f)], HOLD) for f, (kx, r) in wk.items()])
    w1.key('rotation', [(f, float(r), HOLD) for f, (kx, r) in wk.items()])
    MINT_ = [150 / 255.0, 240 / 255.0, 225 / 255.0, 1.0]
    w1.fx('ADBE Tint', **{'ADBE Tint-0001': MINT_, 'ADBE Tint-0002': MINT_, 'ADBE Tint-0003': 100.0})

    L = sc.add('A_rays', S0.rays, -1150 + hc[0], -1150 + hc[1], pivot=hc, k=1, crop=False)
    L.span(5).key('position', pos_k[2:] + [(24, [hc[0], hc[1]], LIN), (30, [-171.0, 270.0], LIN)]).key(
        'rotation', [(5, -40.0, LIN), (24, -8.0, LIN), (30, 0.0, LIN)])
    L.x, L.y = -171.0 - 1150, 270.0 - 1150
    L.pivot = (-171.0, 270.0)
    L.static['rotation'] = 0.0

    # ---------------- the paper sheet: quarter annulus that fans open (25-31) and slides up (26-36) ----------------
    L = sc.add('A_holo_big', holo_big, 320 - 834, 200 - 834, k=1, pivot=(320, 200), crop=False)
    L.span(36).key('scale', [(36, [55, 55], LIN), (39, [100, 100], LIN)])
    sk = [(25, 229, 160), (26, 230, 168), (27, 229, 160), (28, 226, 150), (29, 229, 113), (30, 229, 23), (31, 229, -14), (32, 229, -35),
          (33, 229, -50), (34, 229, -60), (35, 229, -66), (36, SHEET_C[0], SHEET_C[1])]
    sheet_pos = [(f, [x_, y_], HOLD) for f, x_, y_ in sk]
    L = sc.add('A_sheet', sheet, SHEET_C[0] - 2, SHEET_C[1] - 2, k=1.5, pivot=SHEET_C, crop=False)
    L.span(25).key('position', sheet_pos)
    L.fx('ADBE Radial Wipe', **{'ADBE Radial Wipe-0001': [(25, 6.67, HOLD), (26, 3.39, HOLD), (27, 2.14, HOLD), (28, 1.25, HOLD),
                                                          (29, 0.75, HOLD), (30, 0.44, HOLD), (31, 0.25, HOLD), (32, 0.0, HOLD)],
                                'ADBE Radial Wipe-0002': 90.0, 'ADBE Radial Wipe-0003': [3.0, 3.0], 'ADBE Radial Wipe-0004': 1})
    L = sc.add('A_lav', lav_disc, 0, 0, k=1, crop=False)
    L.x, L.y = 688 - L.ww / 2, 635 - L.wh / 2
    L.pivot = (688.0, 635.0)
    L.span(25, 31).set(pano=False).key('position', [(25, [688, 635], HOLD), (26, [663, 603], HOLD), (27, [703, 487], HOLD),
                                                    (28, [728, 540], HOLD), (29, [781, 504], HOLD), (30, [790, 500], HOLD)])
    L.fx('ADBE Radial Wipe', **{'ADBE Radial Wipe-0001': [(25, 0.0, HOLD), (27, 13.0, HOLD), (28, 20.0, HOLD), (29, 62.0, HOLD), (30, 86.0, HOLD)],
                                'ADBE Radial Wipe-0002': 28.0, 'ADBE Radial Wipe-0004': 1})
    L = sc.add('A_holo2', holo2, SHEET_C[0] - 2, SHEET_C[1] - 2, k=1, pivot=SHEET_C, crop=False)
    L.span(27).key('position', [k_ for k_ in sheet_pos if k_[0] >= 27]).key('opacity', [(27, 0.0, LIN), (31, 100.0, LIN)])

    # ---------------- gradient streaks along the ruler (21-29): head / tail positions measured per frame ----------------
    L = sc.add('A_gbar_mag', hgrad_rect, 96, 405, 934, 67, (124, 54, 236), (240, 62, 150))
    L.span(21, 29).set(pano=False)
    _two_wipes(L, 96.0, 934.0, [(21, 783), (22, 890), (23, 943), (24, 974), (25, 994), (26, 1008), (27, 1017), (28, 1024)],
               [(21, 705), (22, 697), (23, 677), (24, 621), (25, 96), (26, 332), (27, 568), (28, 802)])
    L = sc.add('A_gbar_cyan', vgrad_rect, -200, 472, 1230, 64, (96, 228, 228), (238, 150, 206))
    L.span(22, 30).set(pano=False)
    _two_wipes(L, -200.0, 1230.0, [(22, 120), (23, 151), (24, 152), (25, 957), (26, 979), (27, 992), (28, 1011), (29, 1018)],
               [(22, -200), (27, 121), (28, 428), (29, 733)])
    L = sc.add('A_gbar_violet', solid_rect, 96, 405, 40, 67, (118, 52, 236), pivot=(96, 438.5))
    L.span(22, 25).set(pano=False).key('scale', [(22, [23, 100], HOLD), (23, [100, 100], HOLD), (24, [90, 100], HOLD)])
    L = sc.add('A_whitedisc', S0.white_disc, 384 - 309, 299 - 309, 247.0, k=K, crop=False)
    L.span(24, 25).set(pano=False)

    # ---------------- pole (cut-out photo) ----------------
    L = sc.add('A_pole', pole_photo, 226, 396)
    L.span(16).flashes([(16, (255, 255, 255)), (18, (90, 108, 240)), (20, None)])

    # ---------------- text / bracket ----------------
    L = sc.add('A_farewell', text_asset, 0, 0, 'Farewell', 'Josefin Sans|Thin Italic', 82, (12, 12, 12), rot=78.0)
    L.x, L.y = 492 - L.ww / 2, -27 - L.wh / 2
    L.pivot = (492, -27)
    fk = [(27, 500), (28, 392), (29, 372), (30, 355), (31, 340), (32, 325), (33, 316), (34, 308), (35, 300), (36, 294), (37, 240), (38, 191),
          (39, 189), (40, 187), (41, 164), (48, 110), (54, 60), (56, 34), (58, -24), (60, -27)]
    L.span(27).key('position', [(f, [492, y_], LIN) for f, y_ in fk])
    L = sc.addc('A_bracket', bracket_a)
    L.span(28).fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': [(28, 30.0, LIN), (29, 19.4, LIN), (31, 11.7, LIN), (33, 10.6, LIN), (36, 5.6, LIN), (40, 0.0, LIN)],
                                         'ADBE Linear Wipe-0002': 180.0, 'ADBE Linear Wipe-0003': 0.0})

    # ---------------- sunset photo: a squashed strip that unfolds in steps (22-28), blue bar riding its lower edge ----------------
    L = sc.add('A_sunset', sunset_photo, 654, 498, pivot=(654, 498))
    L.span(22, 65).set(pano=False)
    L.key('position', [(22, [743, 471], HOLD), (24, [673, 472], HOLD), (25, [673, 475], HOLD), (26, [663, 477], HOLD), (27, [661, 470], HOLD),
                       (28, [654, 487], HOLD), (30, [654, 498], HOLD)])
    L.key('scale', [(22, [106, 5], HOLD), (23, [106, 11], HOLD), (24, [147, 22], HOLD), (25, [148, 50], HOLD), (26, [155, 75], HOLD),
                    (27, [110, 88], HOLD), (28, [100, 100], HOLD), (60, [100, 100], LIN), (64, [100, 4], LIN)])
    L.fx('ADBE Wave Warp', **{'ADBE Wave Warp-0001': 2, 'ADBE Wave Warp-0002': [(22, 0.0, HOLD), (25, 14.0, HOLD), (26, 18.0, HOLD), (27, 10.0, HOLD), (28, 0.0, HOLD)],
                              'ADBE Wave Warp-0003': 46.0, 'ADBE Wave Warp-0004': 0.0, 'ADBE Wave Warp-0005': 0.0})
    L = sc.add('A_bluebar', solid_rect, 742, 471, 173, 20, (80, 120, 245), pivot=(742, 471))
    L.span(22, 30).set(pano=False).key('position', [(22, [742, 471], HOLD), (23, [743, 490], HOLD), (24, [741, 513], HOLD), (25, [747, 538], HOLD),
                                                    (26, [745, 548], HOLD), (27, [745, 557], HOLD), (28, [745, 582], HOLD), (29, [745, 617], HOLD)])

    # ---------------- ring group (stepped on the 6-frame grid, measured from the source) ----------------
    L = sc.add('A_crescent', crescent, 405, 538)
    cres = [(35, 75), (36, 65), (41, 105), (42, 115), (43, 125), (47, 145), (51, 180)]       # (frame, swept degrees)
    L.span(35).fx('ADBE Radial Wipe', **{'ADBE Radial Wipe-0001': [(f, 100.0 * (1 - d / 360.0), HOLD) for f, d in cres],
                                         'ADBE Radial Wipe-0002': 270.0,
                                         'ADBE Radial Wipe-0003': [(722 - L.x) * K, (510 - L.y) * K],
                                         'ADBE Radial Wipe-0004': 1})
    sc.addc('A_curl', curl).span(47)
    sc.addc('A_road', road).span(27).flash(27, (0, 0, 0), 1)

    # blue sector: inner strip first (57-59), full radial width from 60, snaps at 65 then drifts home
    L = sc.add('A_ring_blue_in', ring_sector, RC[0] - 278, RC[1] - 278, 197.0, 276.0, 42.0, 90.0, BL, pivot=RC)
    L.span(57, 60).set(pano=False).key('rotation', [(57, 46.0, HOLD), (58, 37.0, HOLD), (59, 31.0, HOLD)])
    L = sc.add('A_ring_blue', ring_sector, RC[0] - 427, RC[1] - 427, 197.0, 425.0, 42.0, 90.0, BL, pivot=RC)
    L.span(60).key('rotation', [(60, 27.0, LIN), (64, 16.0, HOLD), (65, 13.0, LIN), (69, 10.0, LIN), (75, 0.0, LIN)])

    # vinyl: a flat pink disc holds its place (55-59), the record itself lands on 60
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
    L = sc.addc('A_horn', wire_horn)
    L.span(39, 61).set(pano=False).key('opacity', [(39, 0, LIN), (41, 100, LIN), (57, 100, LIN), (60, 0, LIN)])

    L = sc.addc('A_wires', wires)
    L.span(16).flashes([(16, (255, 255, 255)), (18, (90, 108, 240)), (20, None)])

    # ---------------- pins / thin lines ----------------
    for (nm, x_, y_, lab, f0) in (('A_pin1', 655, 447, '2026', 22), ('A_pin2', 1112, 528, None, 31), ('A_pin3', 850, 672, None, 37)):
        L = sc.addc(nm, pin_icon, lab)
        L.x += x_
        L.y += y_
        L.pivot = (x_, y_)
        L.span(f0).pop(f0, 3, 0.2, over=1.25)
    sc.addc('A_lines', lines_a).span(30).wipe(30, 5, angle=-90)
    sc.addc('A_2030', label_2030).span(37)

    # ---------------- transient markers of frames 15-39 ----------------
    L = sc.add('A_pinko0', circle_outline, 621.5 - 33, 544 - 33, 24.5, 13.0, PK, pivot=(621.5, 544), crop=False)
    L.span(15, 16).set(pano=False)                                   # frame 15: small but already thick
    L = sc.add('A_pinko', circle_outline, 621 - 80.5, 543 - 80.5, 72.0, 13.0, PK, pivot=(621, 543), crop=False)
    L.span(16, 40).set(pano=False).key('position', [(16, [621, 543], HOLD), (28, [620, 751], HOLD)]).fx(
        'ADBE Radial Wipe', **{'ADBE Radial Wipe-0001': [(34, 0.0, LIN), (40, 100.0, LIN)], 'ADBE Radial Wipe-0002': 0.0,
                               'ADBE Radial Wipe-0004': 1})
    L = sc.add('A_navy', ball, 692 - 33, 608 - 33, 31.0, crop=False)
    L.span(16, 34).set(pano=False).pop(16, 2, 0.3)
    L = sc.add('A_pinkbar', solid_rect, 435, 638, 209, 39, PK, pivot=(435, 657))
    L.span(16, 27).set(pano=False).key('scale', [(16, [10.5, 100], HOLD), (17, [50, 100], HOLD), (18, [92, 100], HOLD), (19, [100, 100], HOLD),
                                                  (25, [114, 104], HOLD)])
    sc.addc('A_zig', zigzag).span(27, 28).set(pano=False)
    L = sc.add('A_blackbar', solid_rect, 574, 459, 150, 8, (10, 10, 10))
    L.span(16, 26).set(pano=False).key('position', [(16, [649, 463], HOLD), (25, [401, 463], HOLD)]).key(
        'scale', [(16, [100, 100], HOLD), (25, [133, 100], HOLD)])
    L = sc.add('A_graybar', hgrad_rect, 724, 459, 150, 8, (150, 150, 150), (250, 250, 250), hl=False, pivot=(724, 463))
    L.span(16, 26).set(pano=False).key('position', [(16, [724, 463], HOLD), (25, [501, 463], HOLD)]).key(
        'scale', [(16, [20, 100], HOLD), (17, [55, 100], HOLD), (18, [85, 100], HOLD), (20, [97, 100], HOLD), (23, [110, 100], HOLD), (25, [136, 100], HOLD)])

    # ---------------- blue bar on the ruler + icon row ----------------
    sc.add('A_bar_b1', solid_rect, 190, 506, 120, 6, (0, 0, 224)).span(2)
    sc.add('A_bar_b2', solid_rect, 310, 506, 65, 6, (125, 224, 232)).span(5)
    sc.add('A_bar_b3', solid_rect, 375, 506, 50, 6, (12, 12, 60)).span(7)
    sc.add('A_redbar', solid_rect, 100, 507, 28, 4, (222, 20, 60)).span(9)
    sc.addc('A_icons', icons_a).span(9)

    # ---------------- quote card + stopwatch ----------------
    cpath = [(5, s2w(5, 1362, 510)), (7, s2w(7, 1332, 525)), (9, s2w(9, 1285, 565)), (12, s2w(12, 1105, 600)),
             (14, s2w(14, 981, 669)), (15, s2w(15, 885, 776))]
    ck = [(f, [p[0], p[1]], LIN) for f, p in cpath]
    ck[-1] = (15, ck[-1][1], HOLD)
    ck.append((16, [CARD_C[0], CARD_C[1]], HOLD))
    sk = [(5, [220, 220], HOLD), (16, [100, 100], HOLD)]
    for nm, fn, f0 in (('A_quotes', quotes, 5), ('A_card', card, 6), ('A_watch', watch, 7)):
        L = sc.addc(nm, fn, pivot=CARD_C)
        L.span(f0).key('position', ck).key('scale', sk)
    sc.get('A_watch').flashes([(7, (44, 0, 92)), (9, None)])           # flat dark-violet silhouette first

    # ---------------- opening shapes ----------------
    R = S0.px(197)
    p0 = s2w(0, 463, 328)
    L = sc.add('A_sphere', S0.sphere, p0[0] - R - 2, p0[1] - R - 2, R, pivot=p0, crop=False)
    L.span(0, 3).set(pano=False).key('rotation', [(0, 0.0, HOLD), (2, -75.0, HOLD)])
    pin(L, [(0, 463, 328), (2, 463, 328)])
    R2 = S0.px(200)
    L = sc.add('A_donut', S0.donut, 0, 0, R2, crop=False)
    L.x, L.y = p0[0] - 2.9 * R2 * 0.40, p0[1] - 2.9 * R2 / 2
    L.pivot = p0
    L.span(3, 8).set(pano=False)
    pin(L, [(3, 460, 330), (5, 445, 300), (7, 450, 295)])
    L = sc.add('A_ball', S0.sphere, p0[0] - R - 2, p0[1] - R - 2, R, pivot=p0, crop=False)
    L.span(8, 16).set(pano=False)
    pin(L, [(8, 430, 325), (12, 428, 327), (14, 596, 390), (15, 816, 416)], [(8, 0.21), (12, 0.21), (14, 0.15), (15, 0.1)])
    kb = sc.add('A_kaishi', kaishi_big, 0, 0)
    pk_ = s2w(0, 1150, 160)
    kb.x, kb.y = pk_[0] - kb.ww / 2, pk_[1] - kb.wh / 2
    kb.pivot = pk_
    kb.span(0, 1).set(pano=False, scale=[140, 46])                    # frame 0: squashed flat and wide

    # small labels around the sphere (1-6): white while the field is black
    for nm, txt, fnt_, size, path in (('A_lab_start', 'START', 'times.ttf', 6.5, [(1, 306, 133), (2, 303, 135), (3, 299, 156), (4, 299, 156)]),
                                      ('A_lab_kaishi', '开始', 'simsun.ttc', 7.5, [(1, 716, 160), (3, 710, 158), (4, 705, 235), (5, 700, 312), (6, 700, 312)])):
        L = sc.add(nm, text_asset, 0, 0, txt, fnt_, size, (20, 20, 20))
        pw = s2w(path[0][0], path[0][1], path[0][2])
        L.x, L.y = pw[0] - L.ww / 2, pw[1] - L.wh / 2
        L.pivot = pw
        L.span(1, path[-1][0] + 1).set(pano=False).flashes([(1, (255, 255, 255)), (2 if nm == 'A_lab_start' else 3, None)])
        pin(L, path)
    # long hairline above the ruler (1-6): its right end retracts
    L = sc.add('A_blackline', solid_rect, 222, 500.8, 707, 2.4, (24, 24, 24), pivot=(222, 502))
    L.span(1, 7).set(pano=False).key('position', [(1, [222, 502], HOLD), (2, [157, 502], HOLD), (3, [135, 502], HOLD), (4, [130, 502], HOLD),
                                                  (5, [125, 502], HOLD), (6, [120, 502], HOLD)]).key(
        'scale', [(1, [94.5, 100], HOLD), (2, [100, 100], HOLD), (3, [95.5, 100], HOLD), (4, [75, 100], HOLD), (5, [54, 100], HOLD), (6, [25.5, 100], HOLD)])
    L.flashes([(1, (70, 70, 70)), (2, None)])
    # small grey gradient tab (5-15)
    L = sc.add('A_gradtab', hgrad_rect, 0, 0, 52, 7, (40, 40, 40), (232, 232, 232), hl=False)
    pw = s2w(5, 516, 585)
    L.x, L.y = pw[0] - L.ww / 2, pw[1] - L.wh / 2
    L.pivot = pw
    L.span(5, 16).set(pano=False)
    pin(L, [(5, 516, 585), (7, 528, 588), (9, 839, 588), (12, 828, 588), (14, 860, 580), (15, 880, 556)])
    # '2025'
    L = sc.add('A_2025', text_asset, 0, 0, '2025', 'Montserrat-Medium.ttf', 7.5, (20, 20, 20))
    pw = s2w(5, 613, 746)
    L.x, L.y = pw[0] - L.ww / 2, pw[1] - L.wh / 2
    L.pivot = pw
    L.span(5, 27).set(pano=False)
    pin(L, [(5, 613, 746), (9, 600, 746), (12, 587, 746), (13, 600, 740)])
    L.key('position', [(16, [474, 613], LIN), (20, [483, 615], LIN)])
    # round gauge / stamp (5-25)
    L = sc.addc('A_stamp', stamp, pivot=(0, 0))
    L.span(5, 26).set(pano=False)
    pin(L, [(5, 256, 222), (7, 264, 229), (8, 420, 226), (9, 586, 222), (12, 576, 226), (14, 684, 312), (15, 738, 365)],
        [(5, 1.0), (12, 1.0), (14, 0.775), (15, 0.614)])
    L.key('position', [(18, [475.5, 425.0], LIN), (22, [486.0, 426.0], LIN), (23, [483.4, 424.0], LIN), (24, [439.0, 409.0], LIN), (25, [164.0, 386.0], LIN)])

    L = sc.addc('A_tripod', S0.tripod, pivot=(0, 0))
    L.span(1, 14).set(pano=False)
    pin(L, [(1, 965, 872), (3, 965, 868), (5, 965, 850), (7, 965, 755), (12, 965, 735), (13, 965, 735)])
    tri = sc.addc('A_tri', S0.tri_down, S0.px(290), S0.px(345), pivot=(0, S0.px(345) / 2))
    tri.span(5, 26).set(pano=False)
    pin(tri, [(5, 605, 527), (12, 605, 527), (14, 691, 498), (15, 741, 510), (16, 735, 499)],
        [(5, 1.0), (12, 1.0), (14, 0.655), (15, 0.52), (16, 0.52)])
    tri.key('position', [(23, list(s2w(16, 735, 499)), HOLD), (24, [430.0, 512.0], HOLD), (25, [153.0, 517.0], HOLD)])
    t2 = sc.clone('A_tri2', tri)                                     # second triangle below the ruler (13-25)
    t2.pivot = (tri.x + tri.ww / 2, tri.y + tri.wh / 2)
    s_tri = 0.52 * zoom(5) / zoom(16) * 100.0
    t2.span(13, 26).set(pano=False, scale=[s_tri, s_tri]).key('position', [(13, [437.7, 682.0], LIN), (16, [472.0, 660.0], LIN), (20, [483.0, 661.0], LIN),
                                                                          (23, [476.0, 667.0], HOLD), (24, [415.0, 686.0], HOLD), (25, [153.0, 713.0], HOLD)])
    for i, path in enumerate(([(1, 385, 465), (3, 405, 445), (5, 440, 450), (7, 460, 480)],
                              [(1, 432, 565), (3, 478, 558), (5, 450, 595), (7, 400, 612), (8, 400, 612)],
                              [(3, 360, 548), (5, 330, 530), (7, 325, 495), (10, 315, 495)])):
        L = sc.addc('A_marker%d' % i, S0.marker, pivot=(0, 0))
        L.span(path[0][0], path[-1][0] + 1).set(pano=False)
        pin(L, path)
        if path[0][0] == 1:
            L.flashes([(1, (255, 255, 255)), (3, None)])

    # ---------------- tube / houses / hill ----------------
    L = sc.add('A_tube', tube, 996, 545)
    L.pivot = (L.x + 60, L.y + L.wh / 2)
    L.span(29, 104).set(pano=False, scale=[88, 88]).wipe(29, 20, angle=-90, feather=20)
    L = sc.add('A_buildings', buildings, 1115, 0)
    L.y = 538 - L.wh
    L.pivot = (L.x + L.ww / 2, L.y + L.wh / 2)
    L.span(37).flash(37, PK, 2)
    L = sc.add('A_crimson', vgrad_rect, 818, 502, 392, 18, (226, 22, 92), (120, 8, 48))
    L.span(39, 53).set(pano=False)
    _two_wipes(L, 818.0, 392.0, [(39, 1100), (40, 1171), (41, 1195), (42, 1210), (45, 1200), (46, 1180), (47, 1160), (48, 1140), (49, 1125),
                                 (50, 1110), (51, 1095), (52, 1080)],
               [(39, 818), (45, 850), (46, 880), (47, 905), (48, 930), (49, 950), (50, 970), (51, 1005), (52, 1040)])
    return sc
'''
src = src[:b0] + NEW_BUILD
io.open(P, 'w', encoding='utf-8', newline='\n').write(src)
print('sec_a.py patched:', len(src.splitlines()), 'lines')
