"""v11: opening photo (ferry deck, GPT redraw) + its flat mint silhouette, ray fans, wedge on 11, guides 74-78,
the tall grey block of 86-95, 'None will revive' label path, chrome size on 89-92."""
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


# =============================================================== shapes0.py
patch('shapes0.py', [("""def rays(L=1150.0, k=1):
    c = Canvas(-L, -L, L, L, k=k, ss=3)
    for a in (90, 37, 180, -68, -42, 120):
""", """def rays(L=1150.0, k=1, cw=None):
    \"\"\"thin lines from one centre; `cw` = angles in degrees clockwise from 'up' (default: the late set of frames 53+)\"\"\"
    c = Canvas(-L, -L, L, L, k=k, ss=3)
    for a in ((90, 37, 180, -68, -42, 120) if cw is None else [90.0 - v for v in cw]):
""")])

# =============================================================== sec_a.py
A = []
A.append(("""def mint_shapes(k=K):
    \"\"\"mint silhouette blocks inside the holographic disc on frames 3-6 (two-tone photo look)\"\"\"
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
    \"\"\"washed-out greenish landscape that replaces the mint blocks (frames 5-11)\"\"\"
    q = fit(quadrant('photos-sheet.png', 1, 0), 320 * k, 160 * k).convert('RGB')
    a = np.asarray(q).astype(np.float32).mean(axis=2)
    t = np.clip((a - 30) / 190.0, 0, 1)
    rgb = lerp_color((150, 196, 170), (238, 248, 240), t)
    h, w = a.shape
    x, y = grid(w, h)
    top = 0.20 + 0.14 * np.sin(x / w * 9.0) * np.sin(x / w * 23.0)
    return from_arr(rgb, (y / h > top).astype(np.float32) * 0.92)
""", """DECK_W, DECK_H = 416.4, 239.0          # = 770 x 442 screen px at the zoom of the opening (1.849)


def _deck():
    \"\"\"the opening photo: view from a ferry deck (GPT image rebuilt from frames 6 / 10 of the source).  As in the source the sky is
    cut away and the white railing tubes are keyed out, so only the pale sea shows between them; tones lifted to the washed mint.\"\"\"
    a = np.asarray(gen('deck-view.png').convert('RGBA')).astype(np.float32)
    h, w = a.shape[:2]
    yy = np.mgrid[0:h, 0:w][0]
    al = (a[..., 3] >= 200).astype(np.float32)
    al = al * (1.0 - ((a[..., :3].min(axis=2) > 222) & (yy > 0.795 * h)).astype(np.float32))
    rgb = a[..., :3]
    rgb = rgb + (255.0 - rgb) * (np.clip((rgb - 110.0) / 60.0, 0, 1) * 0.42)
    rgb = rgb * np.array((0.985, 1.0, 0.985), np.float32)
    im = from_arr(rgb, al)
    im = im.crop(im.getbbox())
    return im.resize((int(DECK_W * K), int(DECK_H * K)), Image.LANCZOS)


def mint_shapes():
    \"\"\"flat mint silhouette of the deck photo (frames 3-6), wiped away from the left as the photo itself appears\"\"\"
    a = np.asarray(_deck()).copy()
    a[..., 0], a[..., 1], a[..., 2] = 104, 250, 190
    a[..., 3] = np.where(a[..., 3] > 110, 255, 0).astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


def pale_photo():
    \"\"\"the washed-out deck photo (frames 5-11)\"\"\"
    return _deck()
"""))
A.append(("""    L = sc.addc('A_mint', mint_shapes, pivot=(215, 125))
    L.span(3, 7).set(pano=False).key('opacity', [(3, 100.0, HOLD), (5, 84.0, HOLD)])
    pin(L, [(3, 1218, 526), (4, 1218, 526), (5, 1105, 528), (6, 1105, 528)], [(3, 0.95), (6, 0.95)])
    L = sc.add('A_palephoto', pale_photo, 0, 0)
    L.span(5, 12).set(pano=False).key('opacity', [(5, 70.0, HOLD), (7, 100.0, HOLD), (10, 80.0, HOLD), (11, 55.0, HOLD)])
    pin(L, [(5, 822, 648), (6, 822, 648), (7, 960, 547), (11, 966, 550)], [(5, 0.79), (6, 0.79), (7, 1.3), (11, 1.3)])
""", """    # (photo: screen box 580..1349 x 311..753 on 5-11; silhouette: 258 px further right on 3-4, then on the photo, wiped off)
    L = sc.add('A_palephoto', pale_photo, 300, 400)
    L.span(5, 12).set(pano=False).key('opacity', [(5, 100.0, HOLD), (10, 86.0, HOLD), (11, 62.0, HOLD)])
    pin(L, [(5, 964.5, 532), (11, 964.5, 532)], [(5, 1.0), (11, 1.0)])
    L = sc.add('A_mint', mint_shapes, 300, 400)
    L.span(3, 7).set(pano=False)
    pin(L, [(3, 1222.5, 533), (4, 1222.5, 533), (5, 964.5, 532), (6, 964.5, 532)], [(3, 1.0), (6, 1.0)])
    L.fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': [(3, 0.0, HOLD), (5, 55.0, HOLD), (6, 63.0, HOLD)], 'ADBE Linear Wipe-0002': 90.0,
                                'ADBE Linear Wipe-0003': 0.0})
"""))
A.append(("    wk = {9: (274, 221, 26), 10: (212, 221, 40), 11: (40, 100, -80), 12: (15, 50, -115), 13: (15, 50, -108), 14: (14, 48, -100)}   # (sx %, sy %, rotation)\n",
          "    wk = {9: (274, 221, 26), 10: (212, 221, 40), 11: (10, 60, -83), 12: (15, 50, -115), 13: (15, 50, -108), 14: (14, 48, -100)}   # (sx %, sy %, rotation)\n"))
A.append(("""    L = sc.add('A_rays', S0.rays, -1150 + hc[0], -1150 + hc[1], pivot=hc, k=1, crop=False)
    L.span(5).key('position', pos_k[2:] + [(24, [hc[0], hc[1]], LIN), (30, [-171.0, 270.0], LIN)]).key(
        'rotation', [(5, -40.0, LIN), (24, -8.0, LIN), (30, 0.0, LIN)]).key('opacity', [(5, 100.0, HOLD), (25, 0.0, HOLD), (53, 100.0, HOLD)])
    L.x, L.y = -171.0 - 1150, 270.0 - 1150
    L.pivot = (-171.0, 270.0)
    L.static['rotation'] = 0.0
""", """    # thin rays from the disc centre.  5-9: a narrow fan in the upper sector; from 10 the lines spread out to
    # -88 / 0 / 60 / 110 / 136 / 155 deg (clockwise from 'up', measured on 11-13).  From 53 a fan from far left of the frame.
    L = sc.add('A_raysA', S0.rays, -1150 + hc[0], -1150 + hc[1], 1150.0, 1, (-36, -17, 5, 40, 60), pivot=hc, k=1, crop=False)
    L.span(5, 10).set(pano=False).key('position', pos_k[2:])
    L = sc.add('A_raysB', S0.rays, -1150 + hc[0], -1150 + hc[1], 1150.0, 1, (-88, 0, 60, 110, 136, 155), pivot=hc, k=1, crop=False)
    L.span(10, 25).set(pano=False).key('position', pos_k[2:] + [(24, [hc[0], hc[1]], LIN)]).key(
        'rotation', [(10, 8.0, HOLD), (11, 3.0, HOLD), (12, 0.0, HOLD)])
    L = sc.add('A_rays', S0.rays, -171.0 - 1150, 270.0 - 1150, pivot=(-171.0, 270.0), k=1, crop=False)
    L.span(53)
"""))
patch('sec_a.py', A)

# =============================================================== sec_a2.py
B = []
B.append(("    vx = {73: 1675, 77: 1745, 79: 1827, 80: 1925, 81: 1906, 84: 1861, 85: 1861}\n",
          "    vx = {73: 1675, 74: 1681, 75: 1681, 76: 1681, 77: 1745, 78: 1681, 79: 1827, 80: 1925, 81: 1906, 84: 1861, 85: 1861}\n"))
B.append(("    for nm, ys in (('A_p1_hline', {79: 397, 80: 361, 81: 361}), ('A_p1_hline_m', {79: 685, 80: 719, 81: 719})):\n",
          "    for nm, ys in (('A_p1_hline', {74: 204, 75: 204, 76: 204, 77: 204, 78: 204, 79: 397, 80: 361, 81: 361}),\n"
          "                   ('A_p1_hline_m', {74: 849, 75: 849, 76: 849, 77: 849, 78: 849, 79: 685, 80: 719, 81: 719})):\n"))
B.append(("""    L.span(91, 93).set(pano=False).key('position', [(91, [nx_, ny_ + 273.0], HOLD), (92, [nx_, ny_], HOLD)])
""", """    # it climbs about 276 px per frame from below the frame (89) to above the ruler and off the top
    L.span(89, 96).set(pano=False).key('position', [(f, [nx_, ny_ + dy], HOLD) for f, dy in ((89, 825.0), (90, 551.0), (91, 273.0), (92, -3.0),
                                                                                          (93, -279.0), (94, -482.0), (95, -379.0))])
"""))
B.append(("""    # transient tall grey 'scrollbars' (88-94)
    L = sc.add('A_scroll1', scrollbar, 2905, 120, 58, 760)
    L.span(88, 95).set(pano=False)
    L = sc.add('A_scroll2', scrollbar, 2990, 760, 30, 150)
    L.span(88, 93).set(pano=False)
""", """    # tall grey rounded block: drops in from the top (86-88), spans the whole frame height while it jumps sideways (89-91) and
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
"""))
patch('sec_a2.py', B)

# =============================================================== sec_b.py
C = []
C.append(("""    ch.span(82).key('position', [(82, [2175, 541], HOLD), (83, [2156, 545], HOLD), (84, [2146, 541], HOLD), (86, [2133, 564], HOLD), (87, [2160, 536], HOLD),
                                 (88, [2165, 543], HOLD), (89, [3105, 505], HOLD), (91, [3124, 512], HOLD), (92, [3105, 520], HOLD), (95, [3109, 534], HOLD)])
    ch.key('scale', [(82, [89, 89], HOLD), (83, [96, 96], HOLD), (84, [100, 100], HOLD), (86, [102, 102], HOLD), (87, [97, 97], HOLD), (89, [158, 158], HOLD),
                     (91, [92, 92], HOLD), (95, [98, 98], HOLD)])
""", """    ch.span(82).key('position', [(82, [2175, 541], HOLD), (83, [2156, 545], HOLD), (84, [2146, 541], HOLD), (86, [2133, 564], HOLD), (87, [2160, 536], HOLD),
                                 (88, [2165, 543], HOLD), (89, [3103, 527], HOLD), (91, [3118, 540], HOLD), (92, [3113, 540], HOLD), (95, [3109, 534], HOLD)])
    ch.key('scale', [(82, [89, 89], HOLD), (83, [96, 96], HOLD), (84, [100, 100], HOLD), (86, [102, 102], HOLD), (87, [97, 97], HOLD), (89, [160, 160], HOLD),
                     (91, [97, 97], HOLD), (95, [98, 98], HOLD)])
"""))
patch('sec_b.py', C)
print('v11 patches applied')
