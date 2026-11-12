"""v12: ring group on the far shots - denser horn, record clipped at world x 1119, pinwheel label, blue sector gap, leaning pole"""
import io
B = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts' + '\\'


def patch(fn, pairs):
    s = io.open(B + fn, encoding='utf-8').read()
    for old, new in pairs:
        assert s.count(old) == 1, (fn, old[:70], s.count(old))
        s = s.replace(old, new)
    io.open(B + fn, 'w', encoding='utf-8').write(s)
    print('patched', fn)


patch('horn.py', [
    ("""def _segments(f, tw=158.0, nl=66):
""", """def _segments(f, tw=158.0, nl=66, fan_mul=1):
"""),
    ("""        H, C, r, a0, a1, cnt, rr = fn_
        for i in range(cnt):
""", """        H, C, r, a0, a1, cnt, rr = fn_
        if fan_mul > 1 and f >= 57:                       # the settled fan has about twice as many spokes
            cnt = cnt * fan_mul - (fan_mul - 1)
        for i in range(cnt):
"""),
    ("""def horn_frame(f, ver=1):
    \"\"\"RGBA sprite of the horn at frame f covering the world window HW (HK px per world px)\"\"\"
    ss = 2
    kk = HK * ss
    W_, H_ = int((HW[2] - HW[0]) * kk), int((HW[3] - HW[1]) * kk)
    strings, rings, spokes = _segments(f)
""", """def horn_frame(f, ver=1, lw_w=0.5, nl=66, val=92.0, al=0.62, fan_mul=1):
    \"\"\"RGBA sprite of the horn at frame f covering the world window HW (HK px per world px).
    lw_w = string width in world px, nl = number of strings, val / al = grey value and opacity of one string\"\"\"
    ss = 2
    kk = HK * ss
    W_, H_ = int((HW[2] - HW[0]) * kk), int((HW[3] - HW[1]) * kk)
    strings, rings, spokes = _segments(f, nl=nl, fan_mul=fan_mul)
"""),
    ("""    lw = max(1, int(round(0.5 * kk)))
""", """    lw = max(1, int(round(lw_w * kk)))
"""),
    ("""    alpha = 1.0 - np.power(1.0 - 0.62, acc)
    v = 92.0 - 34.0 * np.clip(acc - 1.0, 0, 3) / 3.0              # denser -> darker
""", """    alpha = 1.0 - np.power(1.0 - al, acc)
    v = val - 34.0 * np.clip(acc - 1.0, 0, 3) / 3.0               # denser -> darker
"""),
    ("""+ 'draw-4').encode('utf-8')""", """+ 'draw-5').encode('utf-8')"""),
])

patch('sec_a.py', [
    ("""def horn_sprite(f, ver):
    \"\"\"the wire horn at frame f (see horn.py); `ver` only keys the asset cache to the pose tables\"\"\"
    return horn.horn_frame(f)
""", """def horn_sprite(f, ver, lw_w=0.5, nl=66, val=92.0, al=0.62, fan_mul=2):
    \"\"\"the wire horn at frame f (see horn.py); `ver` only keys the asset cache to the pose tables\"\"\"
    return horn.horn_frame(f, 1, lw_w, nl, val, al, fan_mul)
"""),
    # pole: GPT redraw of the leaning pole + tree; a small cross-arm silhouette is all that is left of it from 74
    ("""def pole_photo():
    q = quadrant('photos-sheet.png', 0, 0)
    w, h = q.size
    cw = int(h * 222.0 / 379.0)
    x0 = int(w * 0.50 - cw * 0.45)
    im = gray(q.crop((x0, 0, x0 + cw, h))).resize((222 * K, 379 * K), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    v = np.clip((a[..., 0] - 110) * 1.9 + 128, 0, 255)
    a[..., 0] = a[..., 1] = a[..., 2] = v
    a[..., 3] = np.clip((236 - v) / 40.0, 0, 1) * 255
    return Image.fromarray(a.astype(np.uint8), 'RGBA')
""", """def pole_photo(part='all'):
    \"\"\"leaning utility pole with cross-arm, disc insulators and a mass of foliage (GPT redraw 'pole-lean.png' of frames 24 / 32):
    world (228, 410) .. (410, 776).  part 'top' = the cross-arm region only, as a flat black silhouette (what is left from 74)\"\"\"
    a = np.asarray(gen('pole-lean.png').convert('RGBA')).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0).astype(np.uint8)
    a = a[1:1533, 73:990]
    if part == 'top':
        a = a[60:700, 330:917].copy()
        a[..., :3] = 10
        im = Image.fromarray(a, 'RGBA')
        return im.resize((int(104 * K), int(196 * K)), Image.LANCZOS)
    im = Image.fromarray(a, 'RGBA')
    return im.resize((int(182 * K), int(366 * K)), Image.LANCZOS)
"""),
    ("""    L = sc.add('A_pole', pole_photo, 226, 396)
    L.span(16).flashes([(16, (255, 255, 255)), (18, (90, 108, 240)), (20, None)])
""", """    L = sc.add('A_pole', pole_photo, 228, 410, crop=False)
    L.span(16, 73).flashes([(16, (255, 255, 255)), (18, (90, 108, 240)), (20, None)])
    sc.add('A_pole_top', pole_photo, 218, 432, 'top', crop=False).span(74).set(pano=False)
"""),
    # blue sector: stops 3 degrees short, leaving a white gap after the pink one
    ("""    L.span(60).key('rotation', [(60, 27.0, LIN), (64, 16.0, HOLD), (65, 13.0, LIN), (69, 10.0, LIN), (75, 0.0, LIN)])
""", """    L.span(60).key('rotation', [(60, 27.0, LIN), (64, 16.0, HOLD), (65, 13.0, LIN), (69, 10.0, LIN), (75, 3.0, LIN)])
    L.static['rotation'] = 3.0
"""),
    # record label: four-blade pinwheel instead of six sectors
    ("""    seg = (np.floor(np.degrees(th) / 60.0) % 2)[..., None]
    labc = np.where(seg > 0, np.array((238, 52, 126), np.float32), np.array((221, 30, 112), np.float32))
""", """    seg = (((np.degrees(th) + 18.0) % 90.0) < 40.0)[..., None]             # four lighter blades (pinwheel)
    labc = np.where(seg, np.array((246, 94, 152), np.float32), np.array((226, 28, 112), np.float32))
"""),
    # record: clipped at the fixed world edge x = 1119
    ("""    L.fx('ADBE Radial Wipe', **{'ADBE Radial Wipe-0001': [(51, 50.0, HOLD), (57, 0.0, HOLD)], 'ADBE Radial Wipe-0002': 270.0 - 51.1,
                                'ADBE Radial Wipe-0003': [(RC[0] - L.x) * K, (RC[1] - L.y) * K], 'ADBE Radial Wipe-0004': 1})
""", """    L.fx('ADBE Radial Wipe', **{'ADBE Radial Wipe-0001': [(51, 50.0, HOLD), (57, 0.0, HOLD)], 'ADBE Radial Wipe-0002': 270.0 - 51.1,
                                'ADBE Radial Wipe-0003': [(RC[0] - L.x) * K, (RC[1] - L.y) * K], 'ADBE Radial Wipe-0004': 1})
    # On the source nothing of the record shows right of world x = 1119 (a fixed vertical edge while the record turns): a linear
    # wipe whose direction is counter-rotated with the layer; completion = share of the layer's extent along that direction.
    XE = 1119.0
    wa, wc = [], []
    for f_, r_ in sorted(vrot.items()):
        rr_ = math.radians(r_)
        d_ = (-math.cos(rr_), math.sin(rr_))
        cs_ = [d_[0] * cx_ + d_[1] * cy_ for cx_, cy_ in ((0.0, 0.0), (L.ww, 0.0), (0.0, L.wh), (L.ww, L.wh))]
        se_ = -(XE - RC[0]) + d_[0] * (RC[0] - L.x) + d_[1] * (RC[1] - L.y)
        wc.append((f_, max(0.0, min(100.0, 100.0 * (se_ - min(cs_)) / (max(cs_) - min(cs_)))), HOLD))
        wa.append((f_, -90.0 - r_, HOLD))
    L.fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': wc, 'ADBE Linear Wipe-0002': wa, 'ADBE Linear Wipe-0003': 0.0})
"""),
    # resting horn: heavier strings on the far shots
    ("""    sc.add('A_horn_end', horn_sprite, horn.HW[0], horn.HW[1], horn.F1, hv, k=horn.HK).span(horn.F1)
""", """    # Resting pose.  On the far shots (zoom 0.47) the source keeps its strings about a pixel wide, so the bundle reads much
    # denser there: a heavier sprite on 74-83 and 86-97, the fine one on the close shots (84-85, 98+).
    thin = sc.add('A_horn_end', horn_sprite, horn.HW[0], horn.HW[1], horn.F1, hv, k=horn.HK)
    thin.span(98)
    sc.clone('A_horn_end84', thin).span(84, 86).set(pano=False)
    far = sc.add('A_horn_far', horn_sprite, horn.HW[0], horn.HW[1], horn.F1, hv, 1.3, 100, 58.0, 0.74, k=horn.HK)
    far.span(horn.F1, 84).set(pano=False)
    sc.clone('A_horn_far2', far).span(86, 98).set(pano=False)
"""),
])
