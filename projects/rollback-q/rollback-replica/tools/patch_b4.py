"""sec_b.py v4: window plate geometry + its slide (104-122), bead chain glued to the screen until 126, longer ribbons,
steeper white flare."""
import io
P = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts\sec_b.py'
src = io.open(P, encoding='utf-8').read()
n_done = [0]


def rep(old, new):
    global src
    assert src.count(old) == 1, ('not found / ambiguous (%d): ' % src.count(old)) + old[:70]
    src = src.replace(old, new)
    n_done[0] += 1


# ---- plate = 770 x 538 world px at (3803, 412)
rep("    im = fit(gen('clouds.png'), 919 * K // 2 * 2 // 2, 505 * K // 2 * 2 // 2)", "    im = fit(gen('clouds.png'), PLATE_W, PLATE_H)")
rep("""    \"\"\"white-on-blue two tone silhouette of the cloud photo (frames 104-112)\"\"\"
    im = fit(gen('clouds.png'), 919, 505).convert('RGB')""",
    """    \"\"\"white-on-blue two tone silhouette of the cloud photo (frames 104-105)\"\"\"
    im = fit(gen('clouds.png'), PLATE_W, PLATE_H).convert('RGB')""")
rep("""    im = fit(gen('clouds.png'), 919, 505).convert('RGB')
    a = np.asarray(im).astype(np.float32)
    white = (a.mean(axis=2) > 150) & ((a.max(axis=2) - a.min(axis=2)) < 90)
    h, w = white.shape
    x, y = grid(w, h)
    an = ang(x, y, 327.0, 208.0)                                  # apex at world (4130, 648)""",
    """    im = fit(gen('clouds.png'), PLATE_W, PLATE_H).convert('RGB')
    a = np.asarray(im).astype(np.float32)
    white = (a.mean(axis=2) > 150) & ((a.max(axis=2) - a.min(axis=2)) < 90)
    h, w = white.shape
    x, y = grid(w, h)
    an = ang(x, y, 230.0, 375.0)                                  # apex measured in plate coordinates""")
rep("    im = fit(im, 640, 505)\n", "    im = fit(im, 520, PLATE_H)\n")
rep("WIN = (3653, 362, 4722, 992)          # the black 'window'\n",
    "WIN = (3653, 362, 4722, 992)          # the black 'window'\nPLATE = (3803, 412)                   # picture plate inside the window (final position)\nPLATE_W, PLATE_H = 770, 538\n")

# ---- bead chain a little smaller (pano: 372 x 205 incl. beads)
rep("    cx_, cy_, ax, by, rot = 4094.0, 383.0, 183.0, 86.0, math.radians(18.0)", "    cx_, cy_, ax, by, rot = 4094.0, 383.0, 152.0, 68.0, math.radians(18.0)")
rep("        r = 34.0 * (0.84 + 0.16 * (depth + 1) / 2.0) * c.f", "        r = 33.0 * (0.84 + 0.16 * (depth + 1) / 2.0) * c.f")

# ---- window contents with the slide
old_a = src.index("    L = sc.add('B_clouds_sil', clouds_sil, 3803, 440, k=1)")
old_b = src.index("    sc.add('B_rulerbar', ruler_bar, 3628, 538).span(105)")
src = src[:old_a] + r'''    # the picture plate drifts in from the right (104-116) and then sinks to its place (115-122)
    DX = {104: 143, 105: 128, 106: 114, 107: 110, 108: 106, 109: 86, 110: 67, 111: 52, 112: 37, 113: 23, 114: 10, 115: 4}
    DY = {115: -130, 116: -117, 117: -95, 118: -72, 119: -50, 120: -29, 121: -14}
    slide = [(f, DX.get(f, 0.0), DY.get(f, -144.0 if f < 115 else 0.0)) for f in range(104, 123)]

    def plate_keys(L):
        px_, py_ = L.pivot
        L.key('position', [(f, [px_ + dx, py_ + dy], HOLD) for f, dx, dy in slide])
        return L

    L = plate_keys(sc.add('B_clouds_sil', clouds_sil, PLATE[0], PLATE[1], k=1))
    L.span(104, 106).set(pano=False)
    L = plate_keys(sc.add('B_clouds_silver', clouds_sil_silver, PLATE[0], PLATE[1], k=1))
    L.span(106, 114).set(pano=False)
    plate_keys(sc.add('B_clouds', clouds_photo, PLATE[0], PLATE[1], k=1)).span(114)
    L = plate_keys(sc.add('B_girl', girl_plate, PLATE[0] + PLATE_W - 520, PLATE[1], k=1))
    # dark and out of focus at first, sharpening in steps until the clouds photo lands (114)
    L.span(104).fx('ADBE Tint', **{'ADBE Tint-0001': [0.02, 0.02, 0.02, 1.0], 'ADBE Tint-0002': [0.42, 0.42, 0.44, 1.0],
                                   'ADBE Tint-0003': [(104, 100.0, HOLD), (110, 70.0, HOLD), (112, 40.0, HOLD), (114, 0.0, HOLD)]})
    L.fx('ADBE Gaussian Blur 2', **{'ADBE Gaussian Blur 2-0001': [(104, 46.0, HOLD), (106, 38.0, HOLD), (108, 28.0, HOLD), (110, 16.0, HOLD),
                                                                (112, 7.0, HOLD), (114, 0.0, HOLD)]})
''' + src[old_b:]
n_done[0] += 1

# ---- ribbons run on past the star towards the streak focus
rep("""    ribs = [((4380, 575), (3560, 1075), 30, 70, 1, -40, 110, 2), ((4370, 590), (3340, 1090), 26, 58, 2, 30, 113, 0),
            ((4400, 600), (3760, 1085), 24, 50, 3, -25, 113, 0), ((4350, 560), (3420, 930), 22, 44, 4, 46, 116, 0),
            ((4410, 610), (3960, 1090), 22, 40, 5, 12, 117, 0), ((4360, 570), (3300, 1010), 18, 34, 6, -60, 120, 0),
            ((4420, 590), (4120, 1085), 20, 34, 7, -14, 120, 0), ((4330, 548), (3560, 800), 16, 30, 8, 30, 122, 0)]""",
    """    ribs = [((4550, 480), (3560, 1075), 26, 70, 1, -40, 110, 2), ((4540, 495), (3340, 1090), 22, 58, 2, 30, 113, 0),
            ((4570, 505), (3760, 1085), 20, 50, 3, -25, 113, 0), ((4520, 470), (3420, 930), 18, 44, 4, 46, 116, 0),
            ((4575, 515), (3960, 1090), 18, 40, 5, 12, 117, 0), ((4530, 478), (3300, 1010), 14, 34, 6, -60, 120, 0),
            ((4580, 500), (4120, 1085), 16, 34, 7, -14, 120, 0), ((4500, 462), (3560, 800), 12, 30, 8, 30, 122, 0)]""")

# ---- chain + its icons: constant size on screen, parked at screen (832..852, 420) until the zoom-out ends on 126
old_a = src.index("    chain = sc.addc('B_chain', bead_chain)")
old_b = src.index("    sc.addc('B_folders', folders)")
src = src[:old_a] + r'''    C0 = (4094.0, 383.0)
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

    chain = chain_keys(sc.addc('B_chain', bead_chain))
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
''' + src[old_b:]
n_done[0] += 1

# ---- streaks: the white flare is the steep one
rep("(20, (4565, 470), 14, 'white', 121), (52, (4580, 430), 9, 'blue', 122),", "(56, (4565, 470), 14, 'white', 121), (22, (4580, 430), 9, 'blue', 122),")

io.open(P, 'w', encoding='utf-8', newline='\n').write(src)
print('sec_b.py patched,', n_done[0], 'edits')
