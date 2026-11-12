"""v12: target = GPT cutout with transparent ground, glitch frames 86-88, flat blue twin with a sliding white copy"""
p = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts\sec_a2.py'
s = open(p, encoding='utf-8').read()

old = """def target_photo():
    im = gen('target.png')
    return ImageOps.fit(im, (450 * K, 340 * K), Image.LANCZOS, centering=(0.5, 0.1))


def target_blue():
    \"\"\"mirrored two-tone (blue / background) version of the target photo\"\"\"
    im = gen('target.png')
    im = ImageOps.fit(im, (450 * K, 350 * K), Image.LANCZOS, centering=(0.5, 0.1)).transpose(Image.FLIP_TOP_BOTTOM)
    a = np.asarray(im.convert('RGB')).astype(np.float32)
    lum = a.mean(axis=2)
    sat = a.max(axis=2) - a.min(axis=2)
    m = ((lum < 105) | (sat > 90)).astype(np.float32)                 # rings and dark marks only: the sand stays open
    out = np.zeros(lum.shape + (4,), np.uint8)
    out[..., 0], out[..., 1], out[..., 2] = BL
    out[..., 3] = (m * 255).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')
"""
new = """# target: GPT cutout 'target-cutout.png' (redrawn from frames 100 / 103 of the source): transparent ground, dirt strip with
# animal-shaped holes, cream / purple / red / orange / yellow rings, dark marks scattered over everything
TGT_S = 0.3272                        # world px per sheet px (white ring radius 463 px = 151.5 world px)
TGT_X0, TGT_Y0 = 2234.3, 194.1        # world position of the sheet's top-left: disc centre (504.8, 559.8) px -> (2399.5, 377.3)
TGT_C = (2399.5, 377.3)
_TG = {}


def _tgt():
    if 'a' not in _TG:
        a = np.asarray(gen('target-cutout.png').convert('RGBA')).copy()
        a[..., 3] = np.where(a[..., 3] >= 128, 255, 0).astype(np.uint8)
        a[:, 1399:, 3] = 0                                  # the picture ends at world x 2692 on the source
        hh, ww = a.shape[:2]
        yy, xx = np.mgrid[0:hh, 0:ww]
        op = a[..., 3] > 0
        strip = op & (yy < 136 + 0.144 * xx)                # everything above the lower edge of the log
        marks = op & ~strip & (a[..., :3].max(axis=2) < 108)
        _TG.update(a=a, strip=strip, marks=marks, d=np.hypot(xx - 504.8, yy - 559.8), op=op)
    return _TG


def _tgt_out(arr):
    im = Image.fromarray(arr, 'RGBA')
    return im.resize((int(round(im.width * TGT_S * K)), int(round(im.height * TGT_S * K))), Image.LANCZOS)


def target_photo(ver=2):
    return _tgt_out(_tgt()['a'])


def target_part(kind, col=None):
    \"\"\"pieces of the cutout for the glitch frames 86-88: 'strip' / 'marks', in their own colours or as a flat silhouette\"\"\"
    t = _tgt()
    m = t['strip'] if kind == 'strip' else t['marks']
    if kind == 'marks':                                     # close pin holes
        mm = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
        m = np.asarray(mm) > 0
    out = t['a'].copy()
    if col is not None:
        out[..., 0], out[..., 1], out[..., 2] = col
    out[..., 3] = np.where(m, 255, 0).astype(np.uint8)
    return _tgt_out(out)


def target_disc(mode=0):
    \"\"\"flat rings without the white one, centred on (0, 0): mode 0 = frame 88 (dark rim), mode 1 = frame 86 (plain red)\"\"\"
    R_ = 113.0
    c = Canvas(-R_ - 2, -R_ - 2, R_ + 2, R_ + 2, k=K, ss=3)
    if mode == 0:
        rings = [(1.0, (90, 40, 92)), (0.975, (197, 46, 60)), (0.78, (233, 63, 71)), (0.435, (236, 140, 72)), (0.22, (234, 214, 70))]
    else:
        rings = [(1.0, (227, 64, 87)), (0.435, (240, 150, 72)), (0.24, (238, 220, 74))]
    for fr, col in rings:
        c.circle(0, 0, R_ * fr, fill=rgba(col))
    return c


def target_sil(col):
    \"\"\"the whole cutout as a flat silhouette (disc filled to the rim of the white ring), flipped top-bottom: the twin below the ruler\"\"\"
    t = _tgt()
    m = t['op'] | (t['d'] < 463.0)
    out = np.zeros(t['a'].shape, np.uint8)
    out[..., 0], out[..., 1], out[..., 2] = col
    out[..., 3] = np.where(m, 255, 0).astype(np.uint8)
    return _tgt_out(out[::-1].copy())
"""
assert s.count(old) == 1
s = s.replace(old, new)

old = """    # target photo + its blue mirrored twin (the twin starts as a plain copy on 86-89)
    sc.add('A_target', target_photo, 2245, 200).span(86).pop(86, 2, 0.7)
    # the mirrored twin sits 510 px further left at first (88-96) and jumps under the target on 97
    L = sc.add('A_target_copy', target_photo, 1737, 556)
    L.span(88, 90).set(pano=False)
    L = sc.add('A_target_blue', target_blue, 2247, 556)
    tx, ty = L.pivot
    L.span(90).key('position', [(90, [tx - 510.0, ty], HOLD), (97, [tx, ty], HOLD)])
"""
new = """    # target: GPT cutout (transparent ground).  86-88 are glitch frames on the source: strip and marks as flat blue silhouettes,
    # the rings without the white one and larger (x1.27 on 86, x1.18 on 88, none on 87), only x < 2536 on 86 and x < 2667 on 87
    # (left part photographic with black marks, right part blue); the finished cutout from 89.
    TW = 1462 * TGT_S

    def clip(L, lo=None, hi=None):
        if lo is not None:
            L.fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': 100.0 * (lo - TGT_X0) / TW, 'ADBE Linear Wipe-0002': 90.0, 'ADBE Linear Wipe-0003': 0.0})
        if hi is not None:
            L.fx('ADBE Linear Wipe', **{'ADBE Linear Wipe-0001': 100.0 * (TGT_X0 + TW - hi) / TW, 'ADBE Linear Wipe-0002': -90.0, 'ADBE Linear Wipe-0003': 0.0})
        return L
    TB = (84, 92, 242)
    for f_, mode, sc_ in ((86, 1, 126.5), (88, 0, 117.7)):
        L = sc.addc('A_tgt_disc%d' % f_, target_disc, mode)
        L.x += TGT_C[0]
        L.y += TGT_C[1]
        L.pivot = TGT_C
        L.span(f_, f_ + 1).set(pano=False, scale=[sc_, sc_])
    clip(sc.add('A_tgt_strip', target_part, TGT_X0, TGT_Y0, 'strip', crop=False).span(87, 88).set(pano=False), hi=2536.0)
    clip(sc.add('A_tgt_marks', target_part, TGT_X0, TGT_Y0, 'marks', crop=False).span(87, 88).set(pano=False), hi=2536.0)
    for nm, kind in (('A_tgt_stripB', 'strip'), ('A_tgt_marksB', 'marks')):
        src_ = sc.add(nm, target_part, TGT_X0, TGT_Y0, kind, TB, crop=False)
        clip(src_.span(86, 87).set(pano=False), hi=2536.0)
        clip(sc.clone(nm + '87', src_).span(87, 88).set(pano=False), lo=2536.0, hi=2667.0)
        sc.clone(nm + '88', src_).span(88, 89).set(pano=False)
    sc.add('A_target', target_photo, TGT_X0, TGT_Y0, 2, crop=False).span(89)
    # The twin below the ruler is the flipped silhouette in flat blue (mirror line y = 558).  It sits 510 px further left at first
    # (88-96, a plain copy on 88-89) and jumps under the target on 97, where a white copy slides out from under it (97-101).
    L = sc.add('A_target_copy', target_photo, TGT_X0 - 508.0, TGT_Y0 + 356.0, 2, crop=False)
    L.span(88, 90).set(pano=False)
    TWY = 1116.0 - (TGT_Y0 + 1076 * TGT_S)
    L = sc.add('A_target_wht', target_sil, TGT_X0, TWY, (250, 250, 250), crop=False)
    wx_, wy_ = L.pivot
    L.span(97, 102).set(pano=False).key('position', [(f, [wx_ + dx, wy_ + dy], HOLD) for f, dx, dy in (
        (97, 25.0, 6.0), (98, -45.0, -10.0), (99, -50.0, -10.0), (100, -17.0, -6.0), (101, -5.0, -2.0))])
    L = sc.add('A_target_blue', target_sil, TGT_X0, TWY, (12, 137, 247), crop=False)
    tx, ty = L.pivot
    L.span(90).key('position', [(90, [tx - 510.0, ty], HOLD), (97, [tx, ty], HOLD)])
"""
assert s.count(old) == 1
s = s.replace(old, new)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
