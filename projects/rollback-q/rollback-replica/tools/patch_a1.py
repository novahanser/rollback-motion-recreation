p = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts\sec_a.py'
s = open(p, encoding='utf-8').read()


def rep(a, b, count=1):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, count)


# (1) pole photo: key out the white sky
rep("""    a[..., 0] = a[..., 1] = a[..., 2] = v
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def sunset_photo():""",
    """    a[..., 0] = a[..., 1] = a[..., 2] = v
    a[..., 3] = np.clip((236 - v) / 40.0, 0, 1) * 255
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def sunset_photo():""")

# (2) softer crescent gradient
rep("[(0, (6, 6, 6)), (0.45, (58, 58, 58)), (1, (176, 176, 176))]", "[(0, (26, 26, 26)), (0.45, (62, 62, 62)), (1, (156, 156, 156))]")

# (3) stronger big holo
rep("return S0.holo_disc(830.0, k=1, seed=11, rim=True, sat=0.45)", "return S0.holo_disc(830.0, k=1, seed=11, rim=True, sat=0.8)")

# (4) curl stays inside the ring
rep("c.rect(838, 655, 905, 790, (50, 50, 50, 255))", "c.rect(838, 655, 905, 781, (50, 50, 50, 255))")

# (5) move pole + wires blocks
pole_block = """    # ---------------- pole + wires ----------------
    L = sc.add('A_pole', pole_photo, 226, 396)
    L.span(16).flashes([(16, (255, 255, 255)), (18, (90, 108, 240)), (20, None)])
    L = sc.addc('A_wires', wires)
    L.span(16).flashes([(16, (255, 255, 255)), (18, (90, 108, 240)), (20, None)])

"""
rep(pole_block, "")
rep("""    # ---------------- sliding gradient bars (frames 21-29) ----------------""",
    """    # ---------------- pole (cut-out photo) ----------------
    L = sc.add('A_pole', pole_photo, 226, 396)
    L.span(16).flashes([(16, (255, 255, 255)), (18, (90, 108, 240)), (20, None)])

    # ---------------- sliding gradient bars (frames 21-29) ----------------""")
rep("""    # ---------------- pins / thin lines ----------------""",
    """    L = sc.addc('A_wires', wires)
    L.span(16).flashes([(16, (255, 255, 255)), (18, (90, 108, 240)), (20, None)])

    # ---------------- pins / thin lines ----------------""")

# (6) ring order: blue, vinyl, inner disc, pink
inner_line = "    sc.add('A_ring_inner', ring_inner, 500, 340).span(56).fade(56, 3)\n"
rep(inner_line, "")
rep("    L = sc.add('A_ring_pink', ring_sector,", inner_line + "    L = sc.add('A_ring_pink', ring_sector,")

# (7) farewell size / position
rep("'Farewell', 'Roboto-ThinItalic.ttf', 92, (12, 12, 12), rot=78.0)", "'Farewell', 'Roboto-ThinItalic.ttf', 68, (12, 12, 12), rot=78.0)")
rep("    L.x, L.y = 492 - L.ww / 2, 40 - L.wh / 2\n    L.pivot = (492, 40)", "    L.x, L.y = 497 - L.ww / 2, 6 - L.wh / 2\n    L.pivot = (497, 6)")

# (8) rays persist, drifting to their final centre
rep("L.span(5, 25).key('position', pos_k[2:]).key('rotation', [(5, 0.0, LIN), (24, 30.0, LIN)]).set(pano=False)",
    "L.span(5).key('position', pos_k[2:] + [(24, [hc[0], hc[1]], LIN), (30, [-171.0, 270.0], LIN)]).key(\n"
    "        'rotation', [(5, -40.0, LIN), (24, -8.0, LIN), (30, 0.0, LIN)])\n"
    "    L.x, L.y = -171.0 - 1150, 270.0 - 1150\n"
    "    L.pivot = (-171.0, 270.0)\n"
    "    L.static['rotation'] = 0.0")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
