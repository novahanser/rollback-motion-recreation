"""v10: record wedge / ruler clip, tube growth with a travelling cap, crimson bar, code disc, QR disc, photo timing,
mirror-group order, blue target, cluster pops, ruler bar slide."""
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


# =============================================================== sec_a.py
A = []
A.append(("""    L.fx('ADBE Radial Wipe', **{'ADBE Radial Wipe-0001': [(51, 100.0 * (1 - 25 / 180.0), HOLD), (52, 100.0 * (1 - 30 / 180.0), HOLD),
                                                          (53, 100.0 * (1 - 34 / 180.0), HOLD), (54, 100.0 * (1 - 37 / 180.0), HOLD), (57, 0.0, HOLD)],
                                'ADBE Radial Wipe-0002': 180.0 - 51.1, 'ADBE Radial Wipe-0003': [(apx - L.x) * K, (apy - L.y) * K],
                                'ADBE Radial Wipe-0004': 3})
""", """    # the wedge (half angle 25 -> 37 deg) stays attached to the record while it turns and only opens up on 60-62
    L.fx('ADBE Radial Wipe', **{'ADBE Radial Wipe-0001': [(51, 100.0 * (1 - 25 / 180.0), HOLD), (52, 100.0 * (1 - 30 / 180.0), HOLD),
                                                          (53, 100.0 * (1 - 34 / 180.0), HOLD), (54, 100.0 * (1 - 37 / 180.0), HOLD),
                                                          (60, 100.0 * (1 - 60 / 180.0), HOLD), (61, 100.0 * (1 - 110 / 180.0), HOLD), (62, 0.0, HOLD)],
                                'ADBE Radial Wipe-0002': 180.0 - 51.1, 'ADBE Radial Wipe-0003': [(apx - L.x) * K, (apy - L.y) * K],
                                'ADBE Radial Wipe-0004': 3})
    # 51-56: nothing of it shows above the ruler (a half-plane through the pivot = a 180 deg radial wipe around the ring centre)
    L.fx('ADBE Radial Wipe', **{'ADBE Radial Wipe-0001': [(51, 50.0, HOLD), (57, 0.0, HOLD)], 'ADBE Radial Wipe-0002': 270.0 - 51.1,
                                'ADBE Radial Wipe-0003': [(RC[0] - L.x) * K, (RC[1] - L.y) * K], 'ADBE Radial Wipe-0004': 1})
"""))
A.append(("""    L = sc.add('A_tube', tube, 971, 541)
    L.span(29, 104).set(pano=False).wipe(29, 20, angle=-90, feather=20)
    L = sc.add('A_crimson', vgrad_rect, 818, 502, 392, 18, (226, 22, 92), (120, 8, 48))
    L.span(39, 53).set(pano=False)
    _two_wipes(L, 818.0, 392.0, [(39, 1100), (40, 1171), (41, 1195), (42, 1210), (45, 1200), (46, 1180), (47, 1160), (48, 1140), (49, 1125),
                                 (50, 1110), (51, 1095), (52, 1080)],
               [(39, 818), (45, 850), (46, 880), (47, 905), (48, 930), (49, 950), (50, 970), (51, 1005), (52, 1040)])
""", """    # the rope grows along its own length: the tangle first (uncovered towards the left, 29-36), then the tail runs out to the
    # right (40-46); a blue cap rides on the growing end until the cap of the picture itself is uncovered
    L = sc.add('A_tube', tube, 971, 541)
    L.span(29, 104).set(pano=False)
    _two_wipes(L, 971.0, 515.0, [(29, 1140), (30, 1136), (32, 1212), (38, 1218), (40, 1250), (42, 1320), (44, 1400), (45, 1445), (46, 1486)],
               [(29, 1120), (30, 1055), (32, 1048), (34, 1000), (36, 962), (37, 971)])
    L = sc.add('A_tubecap', hgrad_rect, 1050, 627, 28, 15, (24, 40, 236), (60, 96, 250), hl=False)
    L.span(30, 46).set(pano=False)
    L.key('position', [(f, [float(x_), float(y_)], HOLD) for f, x_, y_ in ((30, 1065, 635), (31, 1110, 650), (32, 1150, 665), (33, 1080, 660),
                                                                           (34, 1020, 650), (35, 1090, 655), (36, 1172, 655), (37, 1210, 690),
                                                                           (38, 1150, 740), (40, 1139, 720), (42, 1305, 716), (44, 1388, 727),
                                                                           (45, 1432, 731))])
    # crimson bar (39-47): 847 -> 1238, head first, the tail follows it out
    L = sc.add('A_crimson', vgrad_rect, 847, 502, 392, 18, (226, 22, 92), (120, 8, 48))
    L.span(39, 48).set(pano=False)
    _two_wipes(L, 847.0, 392.0, [(39, 1124), (40, 1172), (41, 1195), (42, 1209), (43, 1218), (44, 1224), (45, 1229), (46, 1232), (47, 1238)],
               [(39, 847), (44, 925), (45, 1030), (46, 1133), (47, 1234)])
"""))
patch('sec_a.py', A)

# =============================================================== sec_a2.py
B = []
B.append(("""def code_circle():
    c = Canvas(1096, -182, 1486, 206, k=K, ss=2)
    c.circle(1290, 12, 190, fill=(250, 251, 252, 255), outline=(20, 20, 20, 255), width=1.0)
    kw, tx = (26, 58, 150, 255), (30, 34, 40, 255)
    lines = [('let', ' grid, cols, rows;'), ('let', ' ant = {'), ('', '  x: floor(cols / 2),'), ('', '  y: floor(rows / 2),'),
             ('', '  dir: 0   // 0上 1右 2下 3左'), ('', '};'), ('', ''), ('function', ' setup() {'),
             ('', '  createCanvas(600, 600);'), ('', '  background(255);'), ('', '}'), ('', ''),
             ('function', ' draw() {'), ('', ''), ('  if', ' (running) {'),
             ('    for', ' (let i = 0; i < stepsPerFrame; i++) {'), ('', '      moveAnt();'), ('', '    }'), ('', '  }'), ('', '}')]
    y = -92.0
    for a, b in lines:
        x = 1128.0
        if a:
            c.text(x, y, a, 'consola.ttf', 12.5, kw)
            x += font('consola.ttf', 12.5 * c.f).getlength(a) / c.f
        if b:
            c.text(x, y, b, 'consola.ttf', 12.5, tx)
        y += 14.0
    # keep only what is inside the circle
    im = c.im
    w, h = im.size
    xx, yy = grid(w, h)
    m = cov(np.hypot(xx - (1290 - c.x0) * c.f, yy - (12 - c.y0) * c.f) - 190.5 * c.f)
    a = np.asarray(im).copy()
    a[..., 3] = (a[..., 3] * m).astype(np.uint8)
    c.im = Image.fromarray(a, 'RGBA')
    return c


def qr_circle(seed=7, n=15):
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
    v = np.where(cells[iy, ix], 6.0, 244.0)
    d = np.hypot(x - cc, y - cc)
    edge = cov(np.abs(d - r * K) - 1.0)
    v = v * (1 - edge) + 10.0 * edge
    return from_arr(np.dstack([v, v, v]), cov(d - r * K - 1.0))
""", """CODE_C, CODE_R = (1253.0, -118.0), 315.0


def code_circle():
    \"\"\"big white disc (centre (1253, -118), radius 315 when fully grown) holding a code-editor screenshot (small text, upper
    part) and a few larger code lines below it\"\"\"
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
    \"\"\"white disc (r 132) with a black / white cell pattern that has grown to `frac` of the disc (one red cell)\"\"\"
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
    \"\"\"three slanted ticks above the QR disc (74-77)\"\"\"
    c = Canvas(1618, -400, 1670, -236, k=K, ss=3)
    for i in range(3):
        y = -386 + i * 50.0
        c.line([(1660, y), (1632, y + 34)], (24, 24, 28, 255), 7.0)
    return c


def top_glyph():
    \"\"\"the black glyph that replaces the ticks from 78\"\"\"
    return text_asset('再', 'A-OTF-RyuminPr5-Regular.otf', 118, (14, 14, 16))
"""))
B.append(("""    m = ((lum < 170) | (sat > 46)).astype(np.float32)
""", """    m = ((lum < 105) | (sat > 90)).astype(np.float32)                 # rings and dark marks only: the sand stays open
"""))
B.append(("""    sc.addc('A_codecircle', code_circle).span(71).pop(71, 2, 0.6)
    for i, (f0, f1) in enumerate(((71, 73), (73, 75), (75, 77), (77, 79), (79, 272))):
        L = sc.add('A_qr%d' % i, qr_circle, 1508 - 134, 135 - 134, 7 + i, 5 + i * 2 if i < 4 else 15, pivot=(1508, 135), crop=False)
        L.span(f0, f1)
        if i < 4:
            L.set(pano=False, scale=[46 + i * 14, 46 + i * 14])
""", """    # code disc: grows from 43 % (71) to full size (radius 137 -> 242 -> 272 -> 298 -> 315, fitted on the source)
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
"""))
B.append(("""    sc.add('A_ph1', bw_photo, 1622, 214, 1, 0, 70, 78, box=(0.1, 0.2, 0.6, 0.95)).span(54).pop(54, 2, 0.5)
    sc.add('A_ph2', bw_photo, 1542, 276, 0, 0, 66, 46, box=(0.45, 0.25, 0.85, 0.6)).span(59)
    sc.add('A_ph3', bw_photo, 1478, 308, 0, 1, 54, 72, box=(0.3, 0.05, 0.7, 0.75)).span(59)
""", """    sc.add('A_ph1', bw_photo, 1622, 214, 1, 0, 70, 78, box=(0.1, 0.2, 0.6, 0.95)).span(65)
    sc.add('A_ph2', bw_photo, 1542, 276, 0, 0, 66, 46, box=(0.45, 0.25, 0.85, 0.6)).span(59)
    sc.add('A_ph3', bw_photo, 1478, 308, 0, 1, 54, 72, box=(0.3, 0.05, 0.7, 0.75)).span(54).pop(54, 2, 0.5)
"""))
# mirror group: the white tower goes under the text / circles; darker, heavier text
B.append(("""    mirrored('A_p1_text', jura_fit, 1669, 266, T_CMD, 376.0, (58, 58, 62), 520, frames=set(range(71, 83)))
""", """    L = sc.add('A_p1_tower', solid_rect, 1696, 203, 100, 678, (252, 252, 252))
    vis(L.span(70, 84).set(pano=False), {75, 77, 79, 80, 81, 82})
    mirrored('A_p1_text', jura_fit, 1669, 266, T_CMD, 376.0, (40, 40, 44), 640, frames=set(range(71, 83)))
"""))
B.append(("""    L = sc.add('A_p1_tower', solid_rect, 1696, 203, 100, 678, (252, 252, 252))
    vis(L.span(70, 84).set(pano=False), {75, 77, 79, 80, 81, 82})
    mirrored('A_p1_gray', gray_rect, 1823, 76, frames={78, 80, 82})
""", """    mirrored('A_p1_gray', gray_rect, 1823, 76, frames={78, 80, 82})
"""))
B.append(("    sc.add('A_ocr', jura_fit, 1822, 397, T_CMD, 414.0, (78, 78, 82), 520).span(86).set(opacity=86)\n",
          "    sc.add('A_ocr', jura_fit, 1822, 397, T_CMD, 414.0, (56, 56, 60), 620).span(86)\n"))
B.append(("    sc.add('A_ocr_mirror', jura_fit, 1822, 668, T_CMD, 414.0, BL, 520, True).span(90)\n",
          "    sc.add('A_ocr_mirror', jura_fit, 1822, 668, T_CMD, 414.0, BL, 620, True).span(90)\n"))
patch('sec_a2.py', B)

# =============================================================== sec_b.py
C = []
C.append(("    sc.add('B_rulerbar', ruler_bar, 3628, 538).span(105)\n", """    # white ruler strip: starts 531 px long further right (3875..4406 on 105) and slides / shrinks to its place by 112
    L = sc.add('B_rulerbar', ruler_bar, 3628, 538)
    L.pivot = (L.x, L.y + L.wh / 2)
    rb = {105: (3875, 4406), 106: (3840, 4033), 107: (3805, 3978), 108: (3770, 3947), 109: (3735, 3932), 110: (3700, 3917), 111: (3665, 3885),
          112: (L.x, L.x + L.ww)}
    L.span(105).key('position', [(f, [float(a_), L.pivot[1]], HOLD) for f, (a_, b_) in sorted(rb.items())]).key(
        'scale', [(f, [(b_ - a_) / L.ww * 100.0, 100.0], HOLD) for f, (a_, b_) in sorted(rb.items())])
"""))
C.append(("    sc.add('B_cluster', cluster, 3595, 210).span(105).pop(105, 2, 0.5)\n", "    sc.add('B_cluster', cluster, 3595, 210).span(105)\n"))
C.append(("""        L.span(f0)
        if kind in ('monitor', 'folder', 'star'):
            L.pop(f0, 2, 0.5, over=1.15)
""", """        L.span(f0)
"""))
C.append(("'gbadge': circ(1340, 390, 42),", "'gbadge': circ(1340, 390, 37),"))
patch('sec_b.py', C)
print('v10 patches applied')
