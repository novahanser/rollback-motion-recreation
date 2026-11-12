"""Ring group: replace smooth guesses with the measured stepped animation."""
p = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts\sec_a.py'
s = open(p, encoding='utf-8').read()
a = s.index("    # ---------------- ring group ----------------")
b = s.index("    L = sc.addc('A_horn', wire_horn)")
new = '''    # ---------------- ring group (stepped on the 6-frame grid, measured from the source) ----------------
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
    L = sc.add('A_vinyl_ph', circle_outline, 980 - 130, 437 - 130, 64.0, 128.0, PK, pivot=(980, 437), crop=False)
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
'''
s = s[:a] + new + s[b:]
open(p, 'w', encoding='utf-8').write(s)
print('ok')
