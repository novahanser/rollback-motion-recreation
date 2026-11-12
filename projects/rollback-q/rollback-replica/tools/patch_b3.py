"""sec_b.py v3: silver disc pop, silver cloud silhouette, blurred dark girl, pink top band, glassy bead chain,
thinner flickering streaks, counter timing."""
import io
P = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts\sec_b.py'
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


# ---- silver version of the cloud silhouette (frames 106-113): conic grey under the cloud edge
rep("def girl_plate():", r'''def clouds_sil_silver():
    """the cloud region as a silver conic gradient (apex inside the window), sky stays royal blue"""
    im = fit(gen('clouds.png'), 919, 505).convert('RGB')
    a = np.asarray(im).astype(np.float32)
    white = (a.mean(axis=2) > 150) & ((a.max(axis=2) - a.min(axis=2)) < 90)
    h, w = white.shape
    x, y = grid(w, h)
    an = ang(x, y, 327.0, 208.0)                                  # apex at world (4130, 648)
    v = 150.0 - 92.0 * np.cos(np.radians(an - 318.0))
    v = np.where((an > 300) & (an < 322), v * 0.35 + 10, v)        # the dark wedge pointing down-right
    v = v + 26.0 * np.clip(1 - y / (h * 0.6), 0, 1)
    out = np.zeros(a.shape[:2] + (4,), np.uint8)
    for i in range(3):
        out[..., i] = np.where(white, np.clip(v, 0, 255), ROYAL[i]).astype(np.uint8)
    out[..., 3] = 255
    return Image.fromarray(out, 'RGBA')


def girl_plate():''')

# ---- procedural bead chain (bracelet of glassy blue spheres)
cut('def chain_arc():', 'def ruler_bar():', r'''def _bead(r):
    """one glassy bead sprite of radius r px"""
    n = int(2 * r + 6)
    c = n / 2.0
    x, y = grid(n, n)
    d = np.hypot(x - c, y - c)
    dl = np.hypot(x - (c - 0.28 * r), y - (c - 0.32 * r)) / (1.25 * r)
    rgb = lerp_color((196, 214, 255), (26, 56, 206), np.clip(dl, 0, 1) ** 1.3)
    ring = cov(np.abs(d - 0.56 * r) - 0.085 * r)[..., None] * 0.92
    rgb = rgb * (1 - ring) + 255.0 * ring
    spec = cov(np.hypot((x - (c - 0.36 * r)) / 1.4, y - (c - 0.40 * r)) - 0.13 * r)[..., None]
    rgb = rgb * (1 - spec) + 255.0 * spec
    edge = cov(np.abs(d - r + 1.6) - 1.6)[..., None]
    rgb = rgb * (1 - edge) + np.array((10, 22, 128), np.float32) * edge
    return from_arr(rgb, cov(d - r))


def bead_chain():
    """bracelet of beads on a tilted ellipse, drawn back to front"""
    c = Canvas(3870, 250, 4330, 525, k=K, ss=2)
    cx_, cy_, ax, by, rot = 4094.0, 383.0, 183.0, 86.0, math.radians(18.0)
    n = 17
    beads = []
    for i in range(n):
        t = 2 * math.pi * i / n
        ex, ey = ax * math.cos(t), by * math.sin(t)
        beads.append((math.sin(t), cx_ + ex * math.cos(rot) - ey * math.sin(rot), cy_ + ex * math.sin(rot) + ey * math.cos(rot)))
    beads.sort()
    for depth, bx, by_ in beads:
        r = 34.0 * (0.84 + 0.16 * (depth + 1) / 2.0) * c.f
        im = _bead(r)
        px_, py_ = c.P(bx, by_)
        c.paste(im, px_ - im.width / 2, py_ - im.height / 2)
    return c


''')

# ---- streaks: true width (was doubled)
rep("    W_, H_ = int(length), max(2, int(round(width * 2)))", "    W_, H_ = int(length), max(2, int(round(width)))")

# ---- build: discs
rep("""    L.span(122, 131).set(pano=False).key('rotation', [(122, 0.0, LIN), (130, 28.0, LIN)]).key(
        'scale', [(122, [70, 70], LIN), (124, [100, 100], LIN)])""",
    """    L.span(122, 133).set(pano=False).key('rotation', [(122, 0.0, LIN), (130, 28.0, LIN)]).key(
        'scale', [(122, [300, 300], HOLD), (124, [70, 70], HOLD), (125, [100, 100], HOLD)])       # fills the frame, snaps small, settles""")
rep("    L.span(131, 137).set(pano=False)\n",
    "    L.span(131, 137).set(pano=False).key('position', [(131, [cx_ + 75, cy_ + 20], HOLD), (132, [cx_ + 38, cy_ - 8], HOLD), (133, [cx_, cy_], HOLD)])\n")

# ---- window contents
rep("""    L = sc.add('B_clouds_sil', clouds_sil, 3803, 440, k=1)
    L.span(104, 113).set(pano=False)
    sc.add('B_clouds', clouds_photo, 3803, 440, k=1).span(113)
    L = sc.add('B_girl', girl_plate, 4082, 440, k=1)
    L.span(104).flashes([(104, (60, 60, 60)), (106, None)])""",
    """    L = sc.add('B_clouds_sil', clouds_sil, 3803, 440, k=1)
    L.span(104, 106).set(pano=False)
    L = sc.add('B_clouds_silver', clouds_sil_silver, 3803, 440, k=1)
    L.span(106, 114).set(pano=False)
    sc.add('B_clouds', clouds_photo, 3803, 440, k=1).span(114)
    L = sc.add('B_girl', girl_plate, 4082, 440, k=1)
    # dark and out of focus at first, sharpening in steps until the clouds photo lands (114)
    L.span(104).fx('ADBE Tint', **{'ADBE Tint-0001': [0.02, 0.02, 0.02, 1.0], 'ADBE Tint-0002': [0.42, 0.42, 0.44, 1.0],
                                   'ADBE Tint-0003': [(104, 100.0, HOLD), (110, 70.0, HOLD), (112, 40.0, HOLD), (114, 0.0, HOLD)]})
    L.fx('ADBE Gaussian Blur 2', **{'ADBE Gaussian Blur 2-0001': [(104, 46.0, HOLD), (106, 38.0, HOLD), (108, 28.0, HOLD), (110, 16.0, HOLD),
                                                                (112, 7.0, HOLD), (114, 0.0, HOLD)]})""")

# ---- crumpled arcs: white on 120, a faint ghost on 121, pink from 122; plus the wide band along the window top
rep("""        L = sc.addc('B_arc%d' % i, ribbon, p0, p1, w0, w1, seed, 0.0)
        L.span(120).flashes([(120, (255, 255, 255)), (122, None)])""",
    """        L = sc.addc('B_arc%d' % i, ribbon, p0, p1, w0, w1, seed, 0.0)
        L.span(120).flashes([(120, (255, 255, 255)), (122, None)]).key('opacity', [(120, 100.0, HOLD), (121, 12.0, HOLD), (122, 100.0, HOLD)])
    top = [((3850, 428), (4050, 416), 104, 112, 31), ((4050, 416), (4300, 432), 112, 100, 32), ((4300, 432), (4575, 486), 100, 78, 33)]
    for i, (p0, p1, w0, w1, seed) in enumerate(top):
        L = sc.addc('B_arcT%d' % i, ribbon, p0, p1, w0, w1, seed, 0.0)
        L.span(120).flashes([(120, (255, 255, 255)), (122, None)]).key('opacity', [(120, 100.0, HOLD), (121, 12.0, HOLD), (122, 100.0, HOLD)])""")

# ---- chain
rep("""    chain = sc.add('B_chain', chain_arc, 3895, 255)
    chain.span(106).wipe(106, 3, angle=-90)""",
    """    chain = sc.addc('B_chain', bead_chain)
    chain.span(105).wipe(105, 4, angle=-90)""")

# ---- streaks: thick flash on arrival, then hairlines; the white one flares on 124 and 127
rep("""        L.span(f0).set(rotation=-th).key('scale', [(f0, [8, 100], LIN), (f0 + 2, [100, 100], LIN)])""",
    """        L.span(f0).set(rotation=-th)
        if i == 1:
            L.key('scale', [(f0, [8, 260], HOLD), (f0 + 1, [60, 200], HOLD), (f0 + 2, [100, 130], HOLD), (124, [100, 620], HOLD), (125, [100, 100], HOLD),
                            (127, [100, 520], HOLD), (128, [100, 100], HOLD)])
        else:
            L.key('scale', [(f0, [8, 300], LIN), (f0 + 2, [100, 170], LIN), (f0 + 4, [100, 100], LIN)])""")

# ---- counter strip already flashes in on 137
rep("    sc.addc('B_counter', counter_strip).span(140).wipe(140, 3, angle=-90)",
    "    sc.addc('B_counter', counter_strip).span(137).wipe(137, 3, angle=-90).flashes([(137, PK), (139, None)])")

io.open(P, 'w', encoding='utf-8', newline='\n').write(src)
print('sec_b.py patched,', n_done[0], 'edits,', len(src.splitlines()), 'lines')
