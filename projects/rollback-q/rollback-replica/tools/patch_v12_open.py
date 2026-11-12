"""v12: opening (frames 0-15): donut with glow + grey half, retracting black arc, physics stamp, ball spin, bars above the triangle"""
import io
B = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts' + '\\'


def patch(fn, pairs):
    s = io.open(B + fn, encoding='utf-8').read()
    for old, new in pairs:
        assert s.count(old) == 1, (fn, old[:70], s.count(old))
        s = s.replace(old, new)
    io.open(B + fn, 'w', encoding='utf-8').write(s)
    print('patched', fn)


# ------------------------------------------------------------------ shapes0.py
patch('shapes0.py', [
    ("""def holo_disc(R, k=K, seed=3, rim=True, sat=1.0):
""", """def donut2(R, rc, alpha, dark=1.0, k=K):
    \"\"\"frames 3-7: black core (radius rc) with a white glow that falls off to a dark rim, and a flat grey half disc covering
    everything below the diagonal through the centre (the diagonal rises to the right at `alpha` degrees).
    dark < 1 keeps the rim light (frame 3).\"\"\"
    size = int(2 * R * k) + 8
    c = size / 2.0
    x, y = grid(size, size)
    d = np.hypot(x - c, y - c) / k
    phi = np.degrees(np.arctan2(y - c, x - c))                       # 0 = right, 90 = down
    t = np.clip((d - rc) / float(R - rc), 0, 1)
    edge = np.clip(12.0 + 290.0 * (0.5 - 0.5 * np.cos(np.radians(phi + 105.0))), 0, 236)      # darkest up / upper left
    edge = 216.0 + (edge - 216.0) * dark
    v = 252.0 - (252.0 - edge) * t ** 0.75
    core = cov((d - rc) * k)
    v = v * (1 - core) + 6.0 * core
    rgb = np.dstack([v, v, v])
    al = math.radians(alpha)
    s = ((x - c) * math.sin(al) + (y - c) * math.cos(al)) / k         # > 0 on the lower-right side of the diagonal
    half = cov(-s * k)
    g = 206.0 - 72.0 * np.clip((x - c) / (R * k) * 0.5 + 0.5, 0, 1)
    rgb = rgb * (1 - half[..., None]) + np.dstack([g, g, g]) * half[..., None]
    line = cov((np.abs(s) - 0.45) * k)[..., None] * 0.8
    rgb = rgb * (1 - line) + 34.0 * line
    a = cov((d - R) * k)
    rim = cov((np.abs(d - R + 0.6) - 0.6) * k)[..., None]
    rgb = rgb * (1 - rim) + 34.0 * rim
    return from_arr(rgb, a)


def black_arc(a0, a1, r, w, k=K):
    \"\"\"thick black arc piece: angles in degrees clockwise from 'right' (90 = down, 180 = left), centre (0, 0)\"\"\"
    c = Canvas(-r - w, -r - w, r + w, r + w, k=k, ss=3)
    n = max(8, int(abs(a1 - a0) / 1.5))
    outer = [((r + w / 2.0) * math.cos(math.radians(a0 + (a1 - a0) * i / n)), (r + w / 2.0) * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    inner = [((r - w / 2.0) * math.cos(math.radians(a0 + (a1 - a0) * i / n)), (r - w / 2.0) * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    c.poly(outer + inner[::-1], (12, 12, 12, 255))
    return c


def holo_disc(R, k=K, seed=3, rim=True, sat=1.0):
"""),
    ("""def marker(r=8.6, col=(0, 0, 0), w=3.4):
    c = Canvas(-r - 3, -r - 3, r + 3, r + 3, k=4, ss=3)
""", """def marker(r=8.1, col=(0, 0, 0), w=6.3):
    c = Canvas(-r - 5, -r - 5, r + 5, r + 5, k=4, ss=3)
"""),
])

# ------------------------------------------------------------------ sec_a.py
patch('sec_a.py', [
    # physics-diagram stamp
    ("""def stamp(R=37.0):
    \"\"\"round gauge / stamp outline that hangs near the sphere (frames 5-25)\"\"\"
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
""", """def stamp(R=39.4):
    \"\"\"round physics diagram next to the sphere (frames 3-25): a circle, two dotted shells, radius arrows, M(r) / rho(r) / dr labels\"\"\"
    c = Canvas(-R - 3, -R - 3, R + 3, R + 3, k=4, ss=3)
    g = (16, 16, 18, 255)
    c.circle(0, 0, R, outline=g, width=0.62)
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
    v0 = (-R * 0.07, -R * 0.02)
    arrow(v0, (R * 0.44, -R * 0.56))
    arrow(v0, (R * 0.55, R * 0.66))
    arrow((R * 0.30, R * 0.01), (R * 0.69, R * 0.01), 2.4)
    arrow((R * 0.99, R * 0.01), (R * 0.81, R * 0.01), 2.4)
    f = 'timesbi.ttf'
    c.text(-R * 0.30, -R * 0.27, 'M(r)', f, R * 0.185, g, anchor='mm')
    c.text(-R * 0.20, R * 0.27, '\\u03c1(r)', f, R * 0.185, g, anchor='mm')
    c.text(R * 0.47, -R * 0.09, 'r', f, R * 0.17, g, anchor='mm')
    c.text(R * 0.90, -R * 0.11, 'dr', f, R * 0.17, g, anchor='mm')
    c.text(R * 0.50, R * 0.80, 'M,R', f, R * 0.17, g, anchor='mm')
    return c
"""),
    # halo band: frame 3 only
    ("""    L.span(3, 5).key('position', pos_k[1:3]).key('scale', sca_k[1:3]).set(pano=False)
""", """    L.span(3, 4).key('position', pos_k[1:3]).key('scale', sca_k[1:3]).set(pano=False)
"""),
    # the bars move behind the opening shapes block (they sit ABOVE the triangle / sphere on the source)
    ("""    sc.add('A_bar_b1', solid_rect, 190, 506, 120, 6, (0, 0, 224)).span(2)
    sc.add('A_bar_b2', solid_rect, 310, 506, 65, 6, (125, 224, 232)).span(5)
    sc.add('A_bar_b3', solid_rect, 375, 506, 50, 6, (12, 12, 60)).span(7)
    sc.add('A_redbar', solid_rect, 100, 507, 28, 4, (222, 20, 60)).span(9)
    sc.addc('A_icons', icons_a).span(9)
""", """    sc.addc('A_icons', icons_a).span(9)
"""),
    # donut -> per-frame donut2 + retracting arc; ball spin
    ("""    R2 = S0.px(200)
    L = sc.add('A_donut', S0.donut, 0, 0, R2, crop=False)
    L.x, L.y = p0[0] - 2.9 * R2 * 0.40, p0[1] - 2.9 * R2 / 2
    L.pivot = p0
    L.span(3, 8).set(pano=False)
    pin(L, [(3, 460, 330), (5, 445, 300), (7, 450, 295)])
    L = sc.add('A_ball', S0.sphere, p0[0] - R - 2, p0[1] - R - 2, R, pivot=p0, crop=False)
    L.span(8, 16).set(pano=False)
    pin(L, [(8, 430, 325), (12, 428, 327), (14, 596, 390), (15, 816, 416)], [(8, 0.21), (12, 0.21), (14, 0.15), (15, 0.1)])
""", """    # 3-7: black core with a white glow, the lower-right half under a grey half disc whose diagonal tilts a little each frame;
    # (core radius px, diagonal angle, rim darkness, screen centre) fitted to the outline of the source
    R2 = S0.px(198)
    for f_, (rc_, al_, dk_, sx_, sy_) in {3: (146, 47, 0.25, 452.0, 327.5), 4: (134, 32, 1.0, 448.5, 327.5), 5: (131, 38, 1.0, 444.5, 327.5),
                                          6: (128, 46, 1.0, 442.5, 328.0), 7: (129, 42, 1.0, 445.5, 328.0)}.items():
        pw = s2w(f_, sx_, sy_)
        L = sc.add('A_donut%d' % f_, S0.donut2, pw[0] - R2 - 2, pw[1] - R2 - 2, R2, S0.px(rc_), al_, dk_, crop=False)
        L.span(f_, f_ + 1).set(pano=False)
    # thick black arc right of it (circle centre (896,135) px, radius 338 px): its lower end retracts frame by frame
    for f_, (a0_, a1_) in {4: (87.7, 169.6), 5: (117.1, 175.2), 6: (139.7, 180.0), 7: (154.1, 180.0), 8: (167.0, 180.0)}.items():
        L = sc.addc('A_arc%d' % f_, S0.black_arc, a0_, a1_, S0.px(338), S0.px(27), pivot=(0, 0))
        pw = s2w(f_, 896, 135)
        L.x += pw[0]
        L.y += pw[1]
        L.span(f_, f_ + 1).set(pano=False)
    # 8-15: the two-tone ball again, small, spinning clockwise by one turn (light-side direction measured per frame)
    L = sc.add('A_ball', S0.sphere, p0[0] - R - 2, p0[1] - R - 2, R, pivot=p0, crop=False)
    L.span(8, 16).set(pano=False)
    pin(L, [(8, 433.5, 328), (9, 430, 328), (10, 426, 328), (11, 424, 328), (12, 424.5, 327), (13, 507, 358), (14, 596.5, 384), (15, 812, 415.5)],
        [(8, 0.419), (9, 0.218), (10, 0.198), (11, 0.188), (12, 0.188), (13, 0.16), (14, 0.132), (15, 0.117)])
    L.key('rotation', [(f_, r_, HOLD) for f_, r_ in ((8, 120.2), (9, 132.5), (10, 174.6), (11, 259.4), (12, 367.3), (13, 450.1), (14, 503.6), (15, 522.4))])
"""),
    # labels: white on frame 1 only; measured positions
    ("""    for nm, txt, fnt_, size, sx_, path in (('A_lab_start', 'START', 'timesbd.ttf', 10.5, 1.0, [(1, 306, 133), (2, 303, 135), (3, 299, 156), (4, 299, 156)]),
                                           ('A_lab_kaishi', '开始', 'simsun.ttc', 9.5, 2.2, [(1, 716, 160), (3, 710, 158), (4, 705, 235), (5, 700, 312), (6, 700, 312)])):
""", """    for nm, txt, fnt_, size, sx_, path in (('A_lab_start', 'START', 'timesbd.ttf', 10.5, 1.0, [(1, 306, 133), (2, 303, 135), (3, 299, 164), (4, 296, 164)]),
                                           ('A_lab_kaishi', '开始', 'simsun.ttc', 9.5, 2.2, [(1, 716, 160), (3, 710, 162), (4, 708, 290), (5, 702, 316), (6, 700, 334)])):
"""),
    ("""        L.span(1, path[-1][0] + 1).set(pano=False).flashes([(1, (255, 255, 255)), (2 if nm == 'A_lab_start' else 3, None)])
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
""", """        L.span(1, path[-1][0] + 1).set(pano=False).flashes([(1, (255, 255, 255)), (2, None)])
        pin(L, path)
    # tiny pixel-font captions that flash for one frame each
    for nm, txt, f_, sx_, sy_, size, col in (('A_set0', 'set 0', 3, 276, 511, 7.6, (84, 150, 150)), ('A_set1', 'set 1', 7, 964, 612, 8.2, (52, 52, 54))):
        L = sc.add(nm, text_asset, 0, 0, txt, 'Press Start 2P|Regular', size, col, tracking=-0.4)
        pw = s2w(f_, sx_, sy_)
        L.x, L.y = pw[0] - L.ww / 2, pw[1] - L.wh / 2
        L.pivot = pw
        L.span(f_, f_ + 1).set(pano=False)
    # small grey gradient tab (4-15): a stub on 4, full length from 6; it jumps to the right on 8
    L = sc.add('A_gradtab', hgrad_rect, 0, 0, 60.5, 17.3, (40, 40, 40), (232, 232, 232), hl=False)
    pw = s2w(5, 518.5, 592)
    L.x, L.y = pw[0] - L.ww / 2, pw[1] - L.wh / 2
    L.pivot = pw
    L.span(4, 16).set(pano=False)
    pin(L, [(4, 571, 592), (5, 518.5, 592), (6, 534, 592), (7, 528, 592), (8, 848, 593), (10, 838, 593), (12, 828, 590), (14, 860, 582), (15, 880, 558)])
    L.key('scale', [(4, [34, 100], HOLD), (5, [76, 100], HOLD), (6, [100, 100], HOLD), (14, [96, 96], HOLD), (15, [91, 91], HOLD)])
"""),
    # stamp: grows 4-7, squashed smear on 3, tail on 4, jump on 9
    ("""    L = sc.addc('A_stamp', stamp, pivot=(0, 0))
    L.span(5, 26).set(pano=False)
    pin(L, [(5, 256, 222), (7, 264, 229), (8, 420, 226), (9, 586, 222), (12, 576, 226), (14, 684, 312), (15, 738, 365)],
        [(5, 1.0), (12, 1.0), (14, 0.775), (15, 0.614)])
    L.key('position', [(18, [475.5, 425.0], LIN), (22, [486.0, 426.0], LIN), (23, [483.4, 424.0], LIN), (24, [439.0, 409.0], LIN), (25, [164.0, 386.0], LIN)])
""", """    L = sc.addc('A_stamp', stamp, pivot=(0, 0))
    L.span(4, 26).set(pano=False)
    pin(L, [(4, 236, 230), (5, 253.6, 229.6), (6, 257.6, 229.6), (7, 268.4, 232), (8, 281, 232), (9, 588, 228), (10, 582, 231.6), (12, 576, 228),
            (14, 684, 312), (15, 738, 365)],
        [(4, 0.78), (5, 0.86), (6, 1.0), (12, 1.0), (14, 0.727), (15, 0.576)])
    L.key('position', [(18, [475.5, 425.0], LIN), (22, [486.0, 426.0], LIN), (23, [483.4, 424.0], LIN), (24, [439.0, 409.0], LIN), (25, [164.0, 386.0], LIN)])
    # it arrives as a horizontal smear: a flat wide copy on 3, a stretched tail behind it on 4
    for nm, f_, sx_, (kx, ky) in (('A_stamp_in', 3, 104, (260.0, 62.0)), ('A_stamp_tail', 4, 74, (300.0, 76.0))):
        t_ = sc.clone(nm, L)
        t_.pivot = (0, 0)
        pw = s2w(f_, sx_, 230)
        t_.x += pw[0]
        t_.y += pw[1]
        t_.pivot = pw
        t_.span(f_, f_ + 1).set(pano=False, scale=[kx, ky])
"""),
    # triangle: measured size / path, from frame 4
    ("""    tri = sc.addc('A_tri', S0.tri_down, S0.px(290), S0.px(345), pivot=(0, S0.px(345) / 2))
    tri.span(5, 26).set(pano=False)
    pin(tri, [(5, 605, 527), (12, 605, 527), (14, 691, 498), (15, 741, 510), (16, 735, 499)],
        [(5, 1.0), (12, 1.0), (14, 0.655), (15, 0.52), (16, 0.52)])
""", """    tri = sc.addc('A_tri', S0.tri_down, S0.px(274), S0.px(342), pivot=(0, S0.px(342) / 2))
    tri.span(4, 26).set(pano=False)
    pin(tri, [(4, 620, 445), (5, 616, 504), (6, 613, 528), (8, 607, 528), (10, 598, 533), (12, 605, 527), (14, 691, 498), (15, 741, 510), (16, 735, 499)],
        [(4, 1.0), (12, 1.0), (14, 0.655), (15, 0.52), (16, 0.52)])
"""),
    ("""    s_tri = 0.52 * zoom(5) / zoom(16) * 100.0
""", """    s_tri = 0.52 * zoom(4) / zoom(16) * 100.0
"""),
    # markers: black from frame 2, bars + thick line above everything of the opening
    ("""        if path[0][0] == 1:
            L.flashes([(1, (255, 255, 255)), (3, None)])
""", """        if path[0][0] == 1:
            L.flashes([(1, (255, 255, 255)), (2, None)])
    # thick black line above the ruler (1-5): its right end retracts; drawn over the sphere and the triangle
    L = sc.add('A_blackline', solid_rect, 222, 500.8, 707, 4.9, (16, 16, 16), pivot=(222, 503.25))
    L.span(1, 6).set(pano=False).key('position', [(1, [222, 503.25], HOLD), (2, [157, 503.25], HOLD), (3, [135, 503.25], HOLD), (4, [127.8, 503.25], HOLD),
                                                  (5, [125, 503.25], HOLD)]).key(
        'scale', [(1, [94.5, 100], HOLD), (2, [100, 100], HOLD), (3, [95.5, 100], HOLD), (4, [83.1, 100], HOLD), (5, [54.2, 100], HOLD)])
    L.flashes([(1, (70, 70, 70)), (2, None)])
    # blue / cyan / navy bar on the ruler (world x 194.2 .. 425.5, y 508 .. 512.9; the blue part grows on 2-4) and the red stub
    L = sc.add('A_bar_b1', solid_rect, 194.2, 508.0, 118.3, 4.9, (0, 0, 224), pivot=(194.2, 510.45))
    L.span(2).key('scale', [(2, [83.6, 100], HOLD), (3, [95.4, 100], HOLD), (4, [100, 100], HOLD)])
    sc.add('A_bar_b2', solid_rect, 312.5, 508.0, 65.5, 4.9, (125, 224, 232)).span(4)
    sc.add('A_bar_b3', solid_rect, 378.0, 508.0, 47.5, 4.9, (12, 12, 60)).span(6)
    sc.add('A_redbar', solid_rect, 100, 508.0, 28, 4.9, (222, 20, 60)).span(9)
"""),
])
