"""sec_a.py v4: label sizes, sphere turn, short mint wedge, lavender bowl + fan, curl / rays timing, crescent flashes,
paler holo print, big holo disc leaves on 56, Farewell keeps rising, tube a little higher."""
import io
P = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts\sec_a.py'
src = io.open(P, encoding='utf-8').read()
n_done = [0]


def rep(old, new):
    global src
    assert src.count(old) == 1, ('not found / ambiguous (%d): ' % src.count(old)) + old[:70]
    src = src.replace(old, new)
    n_done[0] += 1


def cut(start, end, new):
    global src
    a = src.index(start)
    b = src.index(end, a)
    src = src[:a] + new + src[b:]
    n_done[0] += 1


# labels
rep("""    for nm, txt, fnt_, size, path in (('A_lab_start', 'START', 'times.ttf', 6.5, [(1, 306, 133), (2, 303, 135), (3, 299, 156), (4, 299, 156)]),
                                      ('A_lab_kaishi', '开始', 'simsun.ttc', 7.5, [(1, 716, 160), (3, 710, 158), (4, 705, 235), (5, 700, 312), (6, 700, 312)])):
        L = sc.add(nm, text_asset, 0, 0, txt, fnt_, size, (20, 20, 20))""",
    """    for nm, txt, fnt_, size, sx_, path in (('A_lab_start', 'START', 'timesbd.ttf', 10.5, 1.0, [(1, 306, 133), (2, 303, 135), (3, 299, 156), (4, 299, 156)]),
                                           ('A_lab_kaishi', '开始', 'simsun.ttc', 9.5, 2.2, [(1, 716, 160), (3, 710, 158), (4, 705, 235), (5, 700, 312), (6, 700, 312)])):
        L = sc.add(nm, text_asset, 0, 0, txt, fnt_, size, (20, 20, 20), sx=sx_)""")
# sphere: on frame 2 the light half faces right
rep("L.span(0, 3).set(pano=False).key('rotation', [(0, 0.0, HOLD), (2, -75.0, HOLD)])",
    "L.span(0, 3).set(pano=False).key('rotation', [(0, 0.0, HOLD), (2, 80.0, HOLD)])")
# mint wedge: short and narrow once it swings to the left (11-14)
rep("""    wk = {9: (1.55, 26), 10: (1.2, 40), 11: (0.9, -60), 12: (0.6, -115), 13: (0.55, -108), 14: (0.5, -100)}
    w1.span(9, 15).set(pano=False).key('position', pos_k)
    w1.key('scale', [(f, [kx * 100 * hs(f), 125 * hs(f)], HOLD) for f, (kx, r) in wk.items()])
    w1.key('rotation', [(f, float(r), HOLD) for f, (kx, r) in wk.items()])""",
    """    wk = {9: (1.55, 26, 1.0), 10: (1.2, 40, 1.0), 11: (0.5, -80, 0.6), 12: (0.3, -115, 0.5), 13: (0.3, -108, 0.5), 14: (0.28, -100, 0.5)}
    w1.span(9, 15).set(pano=False).key('position', pos_k)
    w1.key('scale', [(f, [kx * 100 * hs(f), 125 * hs(f) * ln], HOLD) for f, (kx, r, ln) in wk.items()])
    w1.key('rotation', [(f, float(r), HOLD) for f, (kx, r, ln) in wk.items()])""")
# rays: gone while the sheet opens (25-52), back for the wide shots
rep("""        'rotation', [(5, -40.0, LIN), (24, -8.0, LIN), (30, 0.0, LIN)])
    L.x, L.y = -171.0 - 1150, 270.0 - 1150""",
    """        'rotation', [(5, -40.0, LIN), (24, -8.0, LIN), (30, 0.0, LIN)]).key('opacity', [(5, 100.0, HOLD), (25, 0.0, HOLD), (53, 100.0, HOLD)])
    L.x, L.y = -171.0 - 1150, 270.0 - 1150""")
# big holo disc: only 36-56
rep("""    L.span(36).key('scale', [(36, [55, 55], LIN), (39, [100, 100], LIN)])
    sk = [""",
    """    L.span(36, 57).set(pano=False).key('scale', [(36, [55, 55], LIN), (39, [100, 100], LIN)]).key('opacity', [(52, 100.0, LIN), (56, 0.0, LIN)])
    sk = [""")
# lavender disc: lower bowl (25-29) + an upper fan that opens (26-30); measured centre (697, 478), R 300 -> 250
cut("    L = sc.add('A_lav', lav_disc, 0, 0, k=1, crop=False)", "    L = sc.add('A_holo2', holo2,", r'''    lav = sc.add('A_lav', lav_disc, 697 - 314, 478 - 314, k=1, crop=False, pivot=(697.0, 478.0))
    shrink = [(25, [100, 100], HOLD), (26, [96, 96], HOLD), (27, [92.7, 92.7], HOLD), (28, [88, 88], HOLD), (29, [83, 83], HOLD)]
    lav.span(25, 30).set(pano=False).key('scale', shrink).key('opacity', [(25, 100.0, HOLD), (29, 22.0, HOLD)])
    lav.fx('ADBE Radial Wipe', **{'ADBE Radial Wipe-0001': 50.0, 'ADBE Radial Wipe-0002': 270.0, 'ADBE Radial Wipe-0004': 1})
    lav2 = sc.clone('A_lav_up', lav)
    lav2.pivot = (697.0, 478.0)
    lav2.span(26, 31).set(pano=False).key('scale', shrink[1:] + [(30, [78, 78], HOLD)])
    fan = [(26, 12), (27, 25), (28, 40), (29, 52), (30, 20)]
    lav2.fx('ADBE Radial Wipe', **{'ADBE Radial Wipe-0001': [(f, 100.0 * (360 - 2 * h) / 360.0, HOLD) for f, h in fan],
                                   'ADBE Radial Wipe-0002': [(f, float(h), HOLD) for f, h in fan], 'ADBE Radial Wipe-0004': 1})
''')
rep(".key('opacity', [(27, 0.0, LIN), (31, 100.0, LIN)])", ".key('opacity', [(27, 0.0, LIN), (31, 78.0, LIN)])")
# Farewell keeps climbing out of the frame
rep("(56, 34), (58, -24), (60, -27)]", "(56, 34), (58, -24), (60, -27), (64, -60), (74, -290)]")
# crescent: white -> grey -> pale placeholders before the real gradient (34-36)
rep("""    cres = [(35, 75), (36, 65), (41, 105), (42, 115), (43, 125), (47, 145), (51, 180)]       # (frame, swept degrees)
    L.span(35).fx(""",
    """    cres = [(34, 60), (35, 75), (36, 65), (41, 105), (42, 115), (43, 125), (47, 145), (51, 180)]       # (frame, swept degrees)
    L.flashes([(34, (255, 255, 255)), (35, (118, 118, 118)), (36, (190, 190, 190)), (37, None)])
    L.span(34).fx(""")
rep("    sc.addc('A_curl', curl).span(47)", "    sc.addc('A_curl', curl).span(25)")
rep("    L = sc.add('A_tube', tube, 996, 545)", "    L = sc.add('A_tube', tube, 996, 520)")

io.open(P, 'w', encoding='utf-8', newline='\n').write(src)
print('sec_a.py patched,', n_done[0], 'edits')
