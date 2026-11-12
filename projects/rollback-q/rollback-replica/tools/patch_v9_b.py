"""v9, sec_b.py: seam to section A2 (+59 px for everything that is only seen from the 86-103 shots), chrome path, big
'Waitingfor(connect)', window slide-in, bracelet + desktop-icon cluster redrawn by GPT from the source."""
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

# ---------------------------------------------------------------- mirrored circles: +59.5
pairs.append(("""def circles_b(mirror=False):
    col = (28, 120, 230, 255) if mirror else (20, 20, 20, 255)
    y0, y1 = (545, 1085) if mirror else (-5, 535)
    c = Canvas(2745, y0, 3560, y1, k=K, ss=3)

    def Y(v):
        return 1080 - v if mirror else v
    c.circle(3013, Y(240), 140, outline=col, width=1.0)
    c.circle(3013, Y(240), 13, outline=col, width=1.0)
    c.circle(3082, Y(310), 62, outline=col, width=1.0)
    c.circle(2872, Y(350), 9, outline=col, width=1.0)
    c.circle(3300, Y(492) if not mirror else 612, 42, outline=col, width=1.0)
    pts = []
    for i in range(121):
        t = i / 120.0
        x = 2750 + 900 * t
""", """DXB = 59.5        # the 2750-3560 stretch is only ever seen from the 86-103 shots, whose registration sits 59 px further right


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
"""))
pairs.append(("    c.text(3013, Y(180), '[*]', OCR, 15, col, anchor='mm')\n    return c\n",
              "    c.text(3013 + DXB, Y(180), '[*]', OCR, 15, col, anchor='mm')\n    return c\n"))

# ---------------------------------------------------------------- chrome frame / texts
pairs.append(("""def chrome_frame():
    c = Canvas(2872, 355, 3240, 723, k=K, ss=3)
    c.rect(2877, 360, 3235, 718, outline=(170, 170, 170, 255), width=0.8)
    for (x_, ch) in ((2903, '“'), (3210, '”')):
        c.text(x_, 380, ch, 'georgiab.ttf', 44, (130, 130, 130, 255), anchor='ma')
        c.text(x_, 380.5, ch, 'georgiab.ttf', 42, (250, 250, 250, 255), anchor='ma')
    return c


def waiting_text():
    c = Canvas(2255, 610, 3020, 700, k=K, ss=2)
    f1 = font('times.ttf', 52 * c.f)
    w1 = f1.getlength('Waiting for') / c.f
    c.text(2262, 622, 'Waiting for', 'times.ttf', 52, (176, 178, 178, 255), tracking=-2.0)
    c.text(2262 + w1 - 14, 622, '(connect)', 'timesi.ttf', 52, (150, 170, 166, 255), tracking=-2.0)
    return c


def connect_text():
    return text_asset('(connect)', 'timesi.ttf', 58, (140, 168, 162), tracking=-2.0)
""", """def chrome_frame():
    c = Canvas(2931, 357, 3300, 725, k=K, ss=3)
    c.rect(2936, 362, 3295, 720, outline=(170, 170, 170, 255), width=0.8)
    for (x_, ch) in ((2963, '“'), (3272, '”')):
        c.text(x_, 382, ch, 'georgiab.ttf', 44, (130, 130, 130, 255), anchor='ma')
        c.text(x_, 382.5, ch, 'georgiab.ttf', 42, (250, 250, 250, 255), anchor='ma')
    return c


def _serif_line(parts, width, track=-9.0):
    \"\"\"tight high-contrast serif line (Playfair Display, upright / italic parts) scaled to `width` world px\"\"\"
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
    \"\"\"'Waitingfor(connect)' - 754 world px wide in the source (86-97)\"\"\"
    return _serif_line([('Waitingfor', False, (186, 188, 188)), ('(connect)', True, (172, 184, 180))], 754.0)


def connect_text():
    \"\"\"'(connect)' alone, 280 world px wide (98-103)\"\"\"
    return _serif_line([('(connect)', True, (150, 172, 166))], 280.0)
"""))

# ---------------------------------------------------------------- bracelet + icon cluster (GPT sheet cut into pieces)
pairs.append(("""def bead_chain():
    \"\"\"glossy bead bracelet (GPT image redrawn from the source), mirrored so that it sinks to the right; 372 x 205 world px\"\"\"
    im = gen('bead-chain.png')
    a = np.asarray(im).copy()
    a[..., 3] = np.where(a[..., 3] > 60, a[..., 3], 0).astype(np.uint8)
    im = Image.fromarray(a, 'RGBA')
    im = im.crop(im.getbbox()).transpose(Image.FLIP_LEFT_RIGHT)
    b = np.asarray(im).astype(np.float32)
    b[..., :3] = b[..., :3] * 0.88 + np.array((10, 14, 40), np.float32) * 0.12
    return Image.fromarray(b.astype(np.uint8), 'RGBA').resize((372 * K, 205 * K), Image.LANCZOS)
""", """CHAIN_W, CHAIN_H = 199.9, 113.7        # = 306 x 174 screen px at the zoom of frames 105-122


def bead_chain2():
    \"\"\"the bracelet alone: 13 pearl beads with white centres (GPT image redrawn from frame 107 of the source)\"\"\"
    im = gen('bead-chain2.png').convert('RGBA')
    a = np.asarray(im).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0).astype(np.uint8)
    im = Image.fromarray(a, 'RGBA')
    im = im.crop(im.getbbox())
    return im.resize((int(CHAIN_W * K), int(CHAIN_H * K)), Image.LANCZOS)


_CL = {}


def _cl_src():
    \"\"\"the GPT sheet 'chain-cluster.png' (redrawn from frame 118): hard alpha, the glyph on the small blue badge painted over\"\"\"
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
    m = {'bar': bar, 'win': win, 'monitor': rect(1056, 238, 1332, 432) & ~win, 'gbadge': circ(1340, 390, 42),
         'folder': rect(953, 598, 1114, 752) & ~rect(824, 541, 942, 759), 'star': star, 'shard': shard,
         'network': rect(1303, 618, 1457, 762) & ~star, 'pen': rect(1393, 483, 1492, 607)}[kind]
    return m & (a[..., 3] > 0)


def cl_bbox(kind):
    m = _cl_mask(kind)
    ys, xs = np.nonzero(m)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def cluster_piece(kind, tw, th):
    \"\"\"one object (group) of the cluster sheet, resized to tw x th world px\"\"\"
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
"""))

# ================================================================ build()
pairs.append(("""    sc.add('B_grayline', thick_line, 2430, 362, 1045, 8, (120, 120, 120), pivot=(2430, 366)).span(88).key(
        'scale', [(88, [0, 100], LIN), (91, [100, 100], LIN)])
    sc.add('B_blueline', thick_line, 2545, 739, 930, 9, BL, pivot=(2545, 743)).span(91).key(
        'scale', [(91, [0, 100], LIN), (94, [100, 100], LIN)])
    sc.add('B_lab5921', ocr_text, 3340, 348, '[5921]', 13.0, BL).span(91)

    # ---------------- chrome shape: born on the ruler near x=2150, flies to its frame ----------------
    sc.addc('B_chrome_frame', chrome_frame).span(93)
    ch = sc.add('B_chrome', chrome, 2905, 0, k=3)
    ch.y = 540 - ch.wh / 2
    ch.pivot = (3055.0, 540.0)
    ch.span(82).key('position', [(82, [2152, 540], HOLD), (86, [2560, 548], HOLD), (87, [2600, 590], HOLD), (88, [2640, 596], HOLD),
                                 (90, [2880, 556], HOLD), (91, [2960, 552], HOLD), (93, [3020, 546], HOLD), (97, [3055, 540], HOLD)])
    ch.key('scale', [(82, [22, 22], HOLD), (83, [28, 28], HOLD), (84, [100, 100], HOLD), (86, [62, 62], HOLD), (90, [80, 80], HOLD), (93, [100, 100], HOLD)])
    ch.flashes([(82, BL), (83, (10, 10, 10)), (84, None), (87, BL), (88, None)])
    L = sc.addc('B_waiting', waiting_text)
    L.span(86, 98).set(pano=False)
    L = sc.add('B_connect', connect_text, 2665, 590)
    L.span(98, 104).set(pano=False)

    # ---------------- labels / tree ----------------
    sc.addc('B_2100', label_2100).span(124)
    L = sc.add('B_tree_w', ascii_tree, 3466, 624, (240, 240, 240))
    L.span(104, 137).set(pano=False)
    sc.add('B_tree', ascii_tree, 3466, 624, (24, 24, 24)).span(137)

    # ---------------- the black window ----------------
    sc.addc('B_window', window_black).span(100)
""", """    sc.add('B_grayline', thick_line, 2432, 362, 1101, 8, (120, 120, 120), pivot=(2432, 366)).span(88).key(
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
                                 (88, [2165, 543], HOLD), (89, [3105, 505], HOLD), (91, [3124, 512], HOLD), (92, [3105, 520], HOLD), (95, [3109, 534], HOLD)])
    ch.key('scale', [(82, [89, 89], HOLD), (83, [96, 96], HOLD), (84, [100, 100], HOLD), (86, [102, 102], HOLD), (87, [97, 97], HOLD), (89, [158, 158], HOLD),
                     (91, [92, 92], HOLD), (95, [98, 98], HOLD)])
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
"""))

pairs.append(("""    # cluster, chain, icons
    sc.add('B_cluster', cluster, 3595, 210).span(105).pop(105, 2, 0.5)
    C0 = (4094.0, 383.0)
    grp = []
    for f in range(105, 126):
        cw = s2w(f, 832.0 + (f - 105) * 20.0 / 21.0, 420.0)
        grp.append((f, cw[0], cw[1], 0.7801 / zoom(f)))
    grp.append((126, C0[0], C0[1], 1.0))

    def chain_keys(L):
        px_, py_ = L.pivot
        L.key('position', [(f, [cx_ + (px_ - C0[0]) * k_, cy_ + (py_ - C0[1]) * k_], HOLD) for f, cx_, cy_, k_ in grp])
        L.key('scale', [(f, [100.0 * k_, 100.0 * k_], HOLD) for f, cx_, cy_, k_ in grp])
        return L

    chain = sc.add('B_chain', bead_chain, C0[0] - 186.0, C0[1] - 102.5)
    chain.pivot = C0
    chain_keys(chain)
    chain.span(105).wipe(105, 4, angle=-90)
    for (i, x_, y_, w_, f0, glued) in ((1, 4212, 392, 62, 108, True), (2, 4244, 432, 46, 110, True), (6, 4192, 362, 28, 109, True),
                                       (3, 4298, 476, 78, 115, False), (4, 4384, 442, 62, 118, False)):
        L = sc.add('B_icon%d' % i, sprite, x_, y_, i, float(w_))
        if glued:
            chain_keys(L).span(f0)
        else:
            L.span(f0).pop(f0, 2, 0.4, over=1.2)
    L = chain_keys(sc.add('B_icon5', sprite, 4232, 474, 5, 26.0))
    L.span(112)
    sc.addc('B_folders', folders).span(119).wipe(119, 3, angle=0)
""", """    # cluster, chain, icons
    sc.add('B_cluster', cluster, 3595, 210).span(105).pop(105, 2, 0.5)
    # The bracelet is glued to the SCREEN from 105 to 136 (same place and size while the camera pans and pulls back; it is
    # uncovered from the right on 105-107 and changes its outline a little on 125 / 132); from 137 it stays in the world, twice
    # as large, drifting 2 px per frame.  Boxes = (centre x, centre y, width, height) in screen px, read off the source.
    box = {105: (842.0, 422.0, 306.0, 174.0), 125: (820.5, 424.5, 266.0, 173.0), 126: (824.5, 427.0, 271.0, 176.0), 127: (823.0, 424.0, 266.0, 173.0),
           128: (826.5, 419.5, 277.0, 165.0), 132: (843.5, 431.0, 283.0, 164.5), 134: (841.0, 439.5, 282.0, 165.0), 135: (830.5, 440.5, 283.0, 163.0),
           136: (810.0, 440.5, 278.0, 163.0)}
    chain = sc.add('B_chain', bead_chain2, 4115.5 - CHAIN_W / 2, 392.0 - CHAIN_H / 2)
    chain.span(105)
    cur, kp, ksc = box[105], [], []
    for f in range(105, 137):
        cur = box.get(f, cur)
        kp.append((f, list(s2w(f, cur[0], cur[1])), HOLD))
        ksc.append((f, [cur[2] / zoom(f) / CHAIN_W * 100.0, cur[3] / zoom(f) / CHAIN_H * 100.0], HOLD))
    kp += [(137, [4115.5, 392.0], LIN), (150, [4140.0, 392.0], LIN)]
    ksc += [(137, [393.0 / CHAIN_W * 100.0, 238.0 / CHAIN_H * 100.0], HOLD)]
    chain.key('position', kp).key('scale', ksc)
    chain.static['scale'] = [393.0 / CHAIN_W * 100.0, 238.0 / CHAIN_H * 100.0]
    chain.fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': [(105, 40.8, HOLD), (106, 17.6, HOLD), (107, 1.3, HOLD), (108, 0.0, HOLD)],
                                    'ADBE Linear Wipe-0002': 90.0, 'ADBE Linear Wipe-0003': 0.0})
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
        if kind in ('monitor', 'folder', 'star'):
            L.pop(f0, 2, 0.5, over=1.15)
    sc.add('B_icon4', sprite, 4382, 437, 4, 78.0).span(125).pop(125, 2, 0.4, over=1.2)
    sc.addc('B_info', info_dot).span(116)
    sc.addc('B_folders', folders).span(119).wipe(119, 3, angle=0)
"""))
patch('sec_b.py', pairs)
print('v9 sec_b patches applied')
