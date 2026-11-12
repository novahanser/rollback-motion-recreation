"""v9, sec_a2.py: caption line, hill / lamp, thumbs row, the mirrored sketch of frames 70-83, metallic bar, text panel, tower timing."""
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
pairs.append(("from sec_a import solid_rect, hgrad_rect, text_asset, PK, BL\n",
              "from sec_a import solid_rect, hgrad_rect, text_asset, circle_outline, PK, BL\n"))

# ---------------------------------------------------------------- thumbs row: three more items to the right
pairs.append(("""def thumbs_row():
    c = Canvas(1340, 444, 1730, 540, k=K, ss=3)
""", """def thumbs_row():
    c = Canvas(1340, 444, 1872, 540, k=K, ss=3)
    c.rect(1749, 470, 1798, 498, fill=(122, 150, 112, 255), outline=(60, 60, 60, 255), width=0.5)        # green landscape thumb
    c.rect(1756, 484, 1791, 498, fill=(96, 124, 84, 255))
    c.rect(1812, 479, 1862, 500, fill=(246, 246, 246, 255), outline=(130, 130, 130, 255), width=0.6)     # empty frame
    c.text(1773, 501, 'QQ截图', 'msyh.ttc', 6.5, (20, 20, 20, 255), anchor='ma')
    c.text(1773, 510, '2026080521 57', 'msyh.ttc', 6.5, (20, 20, 20, 255), anchor='ma')
    c.text(1773, 519, '05', 'msyh.ttc', 6.5, (20, 20, 20, 255), anchor='ma')
    c.text(1837, 503, '时间线_00543', 'msyh.ttc', 6.5, (20, 20, 20, 255), anchor='ma')
"""))

# ---------------------------------------------------------------- caption line: tighter tracking (328 world px wide)
pairs.append(("    return text_asset('人間の時間に対する感知は、周囲の物事の変化に由来する。', 'A-OTF-RyuminPr5-Regular.otf', 10.5, (16, 16, 16), tracking=5.2)\n",
              "    return text_asset('人間の時間に対する感知は、周囲の物事の変化に由来する。', 'A-OTF-RyuminPr5-Regular.otf', 10.5, (16, 16, 16), tracking=2.1)\n"))

# ---------------------------------------------------------------- hill / lamp
pairs.append(("""def hill2():
    x0, y0, x1, y1 = 1224, 480, 1556, 541
    w, h = (x1 - x0) * K, (y1 - y0) * K
    x, y = grid(w, h)
    wx, wy = x / K + x0, y / K + y0
    top = 508 - 15 * np.maximum(np.sin(np.clip((wx - 1228) / 322.0, 0, 1) * math.pi), 0.0) ** 0.8 - 2.5 * np.sin(wx * 0.33) - 1.8 * np.sin(wx * 0.9 + 1.0) - 1.4 * np.sin(wx * 2.3)
    top = np.where(wx > 1500, top + (wx - 1500) * 0.62, top)
    a = cov((top - wy) * K) * cov((wy - 540) * K) * cov((1228 - wx) * K)
    n = noise(h, w, 31, 10.0)
    rgb = np.dstack([26 + n, 34 + n * 1.2, 22 + n])
    return from_arr(rgb, a)


def lamp2():
    c = Canvas(1340, 376, 1460, 542, k=K, ss=3)
    dg = (44, 44, 48, 255)
    c.line([(1367, 540), (1367, 392), (1374, 386), (1452, 383)], dg, 1.8)
    c.rect(1440, 381, 1456, 386, dg)
    c.line([(1367, 420), (1420, 398)], dg, 1.0)
    c.rect(1352, 498, 1378, 534, (236, 200, 40, 255))
    for yy in (504, 510, 516, 522, 528):
        c.line([(1356, yy), (1374, yy)], (190, 40, 40, 255), 1.0)
    return c
""", """def hill2():
    \"\"\"wooded double hill behind the lamp: two rounded crowns (peaks 495 / 499, saddle at x 1438) with a clumpy dark canopy\"\"\"
    x0, y0, x1, y1 = 1224, 484, 1562, 541
    w, h = (x1 - x0) * K, (y1 - y0) * K
    x, y = grid(w, h)
    wx, wy = x / K + x0, y / K + y0
    b1 = 540 - 45 * np.sqrt(np.clip(1 - ((wx - 1335) / 105.0) ** 2, 0, 1))
    b2 = 540 - 41 * np.sqrt(np.clip(1 - ((wx - 1493) / 64.0) ** 2, 0, 1))
    top = np.minimum(b1, b2) + 1.8 * np.sin(wx * 0.55) + 1.4 * np.sin(wx * 1.3 + 1.0) + 1.0 * np.sin(wx * 2.9 + 0.4)
    a = cov((top - wy) * K) * cov((wy - 540) * K)
    rng = np.random.default_rng(31)
    small = rng.normal(0, 1, (h // 6 + 2, w // 6 + 2)).astype(np.float32)
    clump = np.asarray(Image.fromarray(small).resize((w, h), Image.BICUBIC))
    n = noise(h, w, 32, 6.0) + clump * 9.0
    shade = np.clip((wy - top) / 30.0, 0, 1)
    rgb = np.dstack([36 + n - 10 * shade, 46 + n * 1.15 - 12 * shade, 32 + n * 0.9 - 9 * shade])
    return from_arr(rgb, a)


def lamp2():
    c = Canvas(1340, 360, 1470, 542, k=K, ss=3)
    dg = (34, 34, 38, 255)
    c.line([(1367, 540), (1367, 392), (1375, 385), (1452, 381)], dg, 2.6)
    c.rect(1438, 378, 1458, 384.5, dg)
    c.line([(1367, 424), (1424, 392)], dg, 1.5)
    for (bx, by) in ((1368, 388), (1404, 381), (1431, 378)):               # birds sitting on the arm
        c.ellipse(bx - 4.5, by - 6, bx + 4.5, by - 1, fill=dg)
        c.circle(bx + 3.6, by - 7, 2.0, fill=dg)
    c.rect(1354, 498, 1378, 534, (232, 196, 40, 255))
    for yy in (504, 510, 516, 522, 528):
        c.line([(1357, yy), (1375, yy)], (150, 60, 30, 255), 1.0)
    return c


def jura(size, wght=400):
    \"\"\"Jura (variable font) at a given weight - the rounded-square face of the 'dotnet build' line and of the text panel\"\"\"
    f = ImageFont.truetype(font_path('Jura|Light'), int(round(size)))
    try:
        f.set_variation_by_axes([wght])
    except Exception:
        pass
    return f


def jura_fit(s, width, color, wght=500, flip=False):
    \"\"\"one line of Jura scaled so that the text is `width` world px wide\"\"\"
    w100 = jura(100, wght).getlength(s)
    size = 100.0 * width / w100
    im = text_img(s, jura(size * K, wght), rgba(color), pad=3)
    return im.transpose(Image.FLIP_TOP_BOTTOM) if flip else im


def dots4():
    c = Canvas(1705, 352, 1788, 370, k=K, ss=3)
    for i in range(4):
        c.circle(1713 + i * 22.0, 361, 5.2, outline=(40, 40, 44, 255), width=1.0)
    return c


def none_label():
    \"\"\"small grey pill 'None will revive' that blinks below / above the ruler on 91-92\"\"\"
    c = Canvas(2560, 418, 2792, 456, k=K, ss=3)
    c.rrect(2563, 420, 2789, 454, 8, fill=(150, 150, 152, 255))
    fnt = jura(19.0 * c.f, 480)
    im = text_img('None will revive', fnt, (250, 250, 250, 255), pad=2)
    px_, py_ = c.P(2676, 437)
    c.paste(im, px_ - im.width / 2, py_ - im.height / 2)
    return c
"""))

# ---------------------------------------------------------------- metallic bar / text panel
pairs.append(("""    w, h = 1162, 64
    x, y = grid(w, h)
    v = grad_stops(x / w, [(0.0, (4, 4, 4)), (0.18, (250, 250, 250)), (0.45, (170, 170, 170)), (0.62, (110, 110, 110)), (0.70, (12, 12, 12)),
                           (0.80, (12, 12, 12)), (0.86, (150, 150, 150)), (1.0, (236, 236, 236))])
    return from_arr(v, np.ones((h, w), np.float32))
""", """    w, h = 1162, 64
    x, y = grid(w, h)
    wx = 1390.0 + x
    # black up to 1790, a long ramp to white at 2140, a glossy black cap 2143-2365, then white fading to light grey
    v = grad_stops(x / w, [(0.0, (3, 3, 3)), (0.344, (3, 3, 3)), (0.643, (250, 250, 250)), (0.6465, (250, 250, 250)), (0.648, (4, 4, 4)),
                           (0.838, (4, 4, 4)), (0.8395, (246, 246, 246)), (1.0, (224, 224, 224))])
    hl = np.exp(-((wx - 2254.0) / 70.0) ** 2) * np.exp(-((y - 50.0) / 9.0) ** 2) * 70.0 * ((wx > 2150) & (wx < 2358))
    return from_arr(v + hl[..., None], np.ones((h, w), np.float32))
"""))
pairs.append(("""def text_bar():
    c = Canvas(1880, 474, 2432, 548, k=K, ss=3)
    c.rrect(1886, 478, 2427, 545, 10, fill=(160, 160, 160, 255))
    rows = ['Dreams are the only place we can escape from reality', 'dreams collapse onto the timeline',
            'slowly I am still towards the future', 'the journey of time, to it can only move forward']
    for i, row in enumerate(rows):
        words = row.split(' ')
        fnt = font('tahoma.ttf', 7.0 * c.f)
        widths = [fnt.getlength(w_) / c.f for w_ in words]
        gap = (522.0 - sum(widths)) / max(len(words) - 1, 1)
        x = 1896.0
        for w_, ww_ in zip(words, widths):
            c.text(x, 482 + i * 15.6, w_, 'tahoma.ttf', 7.0, (36, 36, 36, 255))
            x += ww_ + gap
    return c
""", """def text_bar():
    \"\"\"grey panel sitting on the ruler (1883..2432 x 478.5..532) with four justified rows of black Jura (row pitch 14.65)\"\"\"
    c = Canvas(1880, 476, 2436, 536, k=K, ss=3)
    c.rect(1883, 478.5, 2432, 532, fill=(126, 126, 126, 255))
    rows = ['Dreams are the only place we can escape from reality.', 'In dreams, consciousness collapses onto the timeline.',
            'Slowly it drifts towards the future.', 'The journey in dreams follows the law of time, it can only move forward.']
    fnt = jura(11.6 * c.f, 440)
    asc = fnt.getmetrics()[0]
    for i, row in enumerate(rows):
        words = row.split(' ')
        widths = [fnt.getlength(w_) / c.f for w_ in words]
        gap = (540.0 - sum(widths)) / max(len(words) - 1, 1)
        x = 1888.0
        base = 486.4 + i * 14.65                                   # baseline of the row
        for w_, ww_ in zip(words, widths):
            px_, py_ = c.P(x, base)
            c.d.text((px_, py_ - asc), w_, font=fnt, fill=(12, 12, 12, 255))
            x += ww_ + gap
    return c
"""))

# ---------------------------------------------------------------- build(): hill / lamp / caption
pairs.append(("""    # ---------------- hill / lamp behind the mint blocks ----------------
    sc.add('A_hill', hill2, 1224, 480).span(44).flash(44, PK, 1)
    sc.addc('A_lamp', lamp2).span(44).flashes([(44, PK), (45, None), (46, (226, 20, 60)), (47, None)])
""", """    # ---------------- hill behind the mint blocks (the lamp stands in front of them, see below) ----------------
    sc.add('A_hill', hill2, 1224, 484).span(44).flash(44, PK, 1)
"""))
pairs.append(("""    sc.addc('A_thumbs', thumbs_row).span(59).wipe(59, 3, angle=-90)
    sc.add('A_jp', jp_line, 1140, 296).span(37).wipe(37, 4, angle=-90)
""", """    sc.addc('A_thumbs', thumbs_row).span(59).wipe(59, 3, angle=-90)
    sc.addc('A_lamp', lamp2).span(44).flashes([(44, PK), (45, None), (46, (226, 20, 60)), (47, None)])
    # caption line: appears with the paper sheet on 27, 367 px left of its place, creeps right (27-31), jumps home on 38
    L = sc.add('A_jp', jp_line, 1137, 296)
    jx, jy = L.pivot
    L.span(27).key('position', [(27, [jx - 367.0, jy], HOLD), (28, [jx - 354.0, jy], HOLD), (29, [jx - 339.0, jy], HOLD), (30, [jx - 324.0, jy], HOLD),
                                (31, [jx - 277.5, jy], HOLD), (38, [jx, jy], HOLD)])
"""))

# ---------------------------------------------------------------- build(): the mirrored group
old_group = s_marker = None
pairs.append(("""    # ================= mirrored bars group =================
    # guides: thin blue lines that criss-cross while the camera is pulled far out
    for i, (x_, y_, w_, h_, f0, f1) in enumerate(((1690, -700, 1.6, 2500, 69, 98), (600, 330, 4200, 1.6, 69, 98), (600, 748, 4200, 1.6, 69, 98),
                                                  (2110, -700, 1.6, 2500, 79, 98), (600, 150, 4200, 1.6, 86, 98))):
        sc.add('A_guide%d' % i, guide, x_, y_, w_, h_, k=1, crop=False).span(f0, f1).set(pano=False)
    L = sc.add('A_stripes', stripes, 1300, -400, k=1, crop=False)
    L.span(85, 89).set(pano=False)

    sc.addc('A_circ_top', circles_set, False).span(70).wipe(70, 3, angle=-90)
    sc.addc('A_circ_bot', circles_set, True).span(86).wipe(86, 3, angle=-90)

    sc.addc('A_textbar', text_bar).span(84)
    # 75-83: a black-white-black metallic bar runs along the ruler first (head grows right, then the tail follows)
    from sec_a import _two_wipes
    L = sc.add('A_cylbar', cyl_bar, 1390, 541, k=1)
    L.span(75, 84).set(pano=False)
    _two_wipes(L, 1390.0, 1162.0, [(75, 2100), (76, 2393), (77, 2460), (78, 2528), (79, 2552)],
               [(75, 1390), (79, 1500), (80, 1630), (81, 1760), (82, 1886)])
    sc.add('A_w1', solid_rect, 1715, 395, 98, 147, (255, 255, 255)).span(79)
    sc.add('A_w2', solid_rect, 1852, 326, 98, 216, (255, 255, 255), pivot=(1901, 540)).span(70).key(
        'scale', [(70, [100, 30], LIN), (72, [100, 100], LIN)])
    sc.add('A_grayrect', gray_rect, 1978, 198).span(78).flash(78, (150, 150, 150), 1)
    sc.add('A_violet', violet_rect, 2115, 198).span(82)
    sc.addc('A_tile_z', glyph_tile, 'Z', 'Montserrat-BlackItalic.ttf', 50, 57, 84, dx=6, dy=-8, rot=0).span(79)
""", """    # ================= mirrored bars group =================
    T_CMD = r'C:\\World\\CE\\<File2xxx> dotnet build'
    # ---- phase 1 (70-83): a flickering sketch of the group around x 1640-2030, doubled in a mirror below the ruler.
    #      None of it is where the finished group ends up; every element was read off world-aligned crops of the source.
    P1 = range(70, 86)

    def vis(L, frames):
        L.key('opacity', [(f, 100.0 if f in frames else 0.0, HOLD) for f in P1])
        return L

    def mirrored(name, fn, x, y, *args, frames=None, rot=0.0, **kw):
        top = sc.add(name, fn, x, y, *args, **kw)
        bot = sc.clone(name + '_m', top)
        bot.y = 1080.0 - (top.y + top.wh)
        bot.pivot = (top.pivot[0], 1080.0 - top.pivot[1])
        bot.set(scale=[100.0, -100.0])
        for L, r_ in ((top, rot), (bot, -rot)):
            if rot:
                L.set(rotation=r_)
            L.span(70, 84).set(pano=False)
            if frames is not None:
                vis(L, frames)
        return top, bot

    mirrored('A_p1_text', jura_fit, 1669, 266, T_CMD, 376.0, (58, 58, 62), 520, frames=set(range(71, 83)))
    mirrored('A_p1_brk', text_asset, 1676, 343, '[', 'arialbd.ttf', 30, (46, 34, 34), frames=set(range(70, 83)))
    mirrored('A_p1_dots', dots4, 1705, 352, frames=set(range(74, 83)))
    mirrored('A_p1_c1', circle_outline, 1789 - 93.6, 414 - 93.6, 91.0, 1.2, (24, 24, 28), frames={70, 72, 74, 75, 76, 77, 78, 79, 80, 82}, crop=False)
    mirrored('A_p1_c2', circle_outline, 1879 - 93.6, 414 - 93.6, 91.0, 1.2, (24, 24, 28), frames={74, 76, 78, 79, 81, 82}, crop=False)
    L = sc.add('A_p1_tower', solid_rect, 1696, 203, 100, 678, (252, 252, 252))
    vis(L.span(70, 84).set(pano=False), {75, 77, 79, 80, 81, 82})
    mirrored('A_p1_gray', gray_rect, 1823, 76, frames={78, 80, 82})
    mirrored('A_p1_violet', violet_rect, 1929, 68, frames={82})
    mirrored('A_p1_k', glyph_tile, 1826 - 39.5, 398 - 39.5, 'k', 'timesbi.ttf', 79, 79, 86, dy=-7, frames={79, 80, 81, 82}, rot=-25.0)
    mirrored('A_p1_ii', text_asset, 1731, 422, 'ii', 'arialbd.ttf', 24, (34, 34, 38), frames=set(range(77, 83)))
    # selection guides that jump from frame to frame (one vertical, a mirrored pair of horizontals)
    gcol = (24, 44, 170)
    vx = {73: 1675, 77: 1745, 79: 1827, 80: 1925, 81: 1906, 84: 1861, 85: 1861}
    L = sc.add('A_p1_vline', guide, 1675, -700, 1.8, 2500, gcol, k=1, crop=False)
    L.pivot = (1675.9, 550.0)
    L.span(70, 86).set(pano=False)
    L.key('position', [(f, [float(vx.get(f, 1675)), 550.0], HOLD) for f in P1])
    vis(L, set(vx))
    for nm, ys in (('A_p1_hline', {79: 397, 80: 361, 81: 361}), ('A_p1_hline_m', {79: 685, 80: 719, 81: 719})):
        L = sc.add(nm, guide, 600, 397, 4200, 1.8, gcol, k=1, crop=False)
        L.pivot = (2700.0, 397.9)
        L.span(70, 84).set(pano=False)
        L.key('position', [(f, [2700.0, float(ys.get(f, 397))], HOLD) for f in P1])
        vis(L, set(ys))

    # ---- phase 2 (86-): the finished group
    # guides: thin blue lines that criss-cross while the camera is pulled far out
    for i, (x_, y_, w_, h_, f0, f1) in enumerate(((1690, -700, 1.6, 2500, 86, 98), (600, 330, 4200, 1.6, 86, 98), (600, 748, 4200, 1.6, 86, 98),
                                                  (2110, -700, 1.6, 2500, 86, 98), (600, 150, 4200, 1.6, 86, 98))):
        sc.add('A_guide%d' % i, guide, x_, y_, w_, h_, k=1, crop=False).span(f0, f1).set(pano=False)
    L = sc.add('A_stripes', stripes, 1300, -400, k=1, crop=False)
    L.span(85, 89).set(pano=False)

    sc.addc('A_circ_top', circles_set, False).span(86)
    sc.addc('A_circ_bot', circles_set, True).span(86).wipe(86, 3, angle=-90)

    sc.addc('A_textbar', text_bar).span(82)
    # 75-82: a black-white metallic bar runs along the ruler first (head grows right, then the tail follows it out)
    from sec_a import _two_wipes
    L = sc.add('A_cylbar', cyl_bar, 1390, 543, k=1)
    L.span(75, 83).set(pano=False)
    _two_wipes(L, 1390.0, 1162.0, [(75, 2277), (76, 2414), (77, 2500), (78, 2540), (79, 2552)],
               [(75, 1390), (80, 1690), (81, 2000), (82, 2308)])
    sc.add('A_w1', solid_rect, 1715, 395, 98, 147, (255, 255, 255)).span(86)
    sc.add('A_w2', solid_rect, 1852, 326, 98, 216, (255, 255, 255), pivot=(1901, 540)).span(86)
    sc.add('A_grayrect', gray_rect, 1978, 198).span(86)
    sc.add('A_violet', violet_rect, 2115, 198).span(86)
    sc.addc('A_tile_z', glyph_tile, 'Z', 'Montserrat-BlackItalic.ttf', 50, 57, 84, dx=6, dy=-8, rot=0).span(86)
"""))
pairs.append(("    sc.addc('A_tile_re', glyph_tile, 'Re', 'Press Start 2P|Regular', 34, 26, 11).span(79)\n",
              "    sc.addc('A_tile_re', glyph_tile, 'Re', 'Press Start 2P|Regular', 34, 26, 11).span(86)\n"))
pairs.append(("""    sc.addc('A_tile_k', glyph_tile, 'k', 'timesbi.ttf', 76, 74, 92, dy=-8).span(79)
""", """    sc.addc('A_tile_k', glyph_tile, 'k', 'timesbi.ttf', 76, 74, 92, dy=-8).span(86)
"""))
pairs.append(("""    sc.add('A_cone', cone, 1879, 468).span(73).pop(73, 2, 0.4)
    sc.add('A_ocr', ocr_text, 1830, 398, r'C:\\World\\CE\\<File2xxx> dotnet build', 21.0, (86, 86, 90)).span(71).set(opacity=78)
""", """    L = sc.add('A_cone', cone, 1879, 470)
    cx_, cy_ = L.pivot
    L.span(72).key('position', [(72, [cx_ + 12.0, cy_ + 89.0], HOLD), (73, [cx_, cy_], HOLD)])       # first frame: hangs under the ruler
    sc.add('A_ocr', jura_fit, 1822, 397, T_CMD, 414.0, (78, 78, 82), 520).span(86).set(opacity=86)
"""))
pairs.append(("""    first = {'A_blueA': 88, 'A_blueA2': 90, 'A_blueC': 88, 'A_blueD': 87, 'A_blueE': 87}
    for (nm, x_, y_, w_, h_) in blue:
        L = sc.add(nm, solid_rect, x_, y_, w_, h_, BL)
        f0 = first[nm]
        L.span(f0).blink([f0, 89, 90] if f0 < 89 else [f0])
    sc.add('A_ocr_mirror', ocr_text, 1832, 686, r'C:\\World\\CE\\<File2xxx> dotnet build', 21.0, BL, flip=True).span(90)
""", """    first = {'A_blueA': 88, 'A_blueA2': 97, 'A_blueC': 97, 'A_blueD': 97, 'A_blueE': 97}       # the mirrored towers only turn up on 97
    for (nm, x_, y_, w_, h_) in blue:
        L = sc.add(nm, solid_rect, x_, y_, w_, h_, BL)
        f0 = first[nm]
        L.span(f0).blink([f0, 89, 90] if f0 < 89 else [f0])
    sc.add('A_ocr_mirror', jura_fit, 1822, 668, T_CMD, 414.0, BL, 520, True).span(90)
"""))
pairs.append(("""    L = sc.add('A_target_copy', target_photo, 2247, 556)
    L.span(86, 90).set(pano=False)
    sc.add('A_target_blue', target_blue, 2247, 556).span(90)
""", """    # the mirrored twin sits 510 px further left at first (88-96) and jumps under the target on 97
    L = sc.add('A_target_copy', target_photo, 1737, 556)
    L.span(88, 90).set(pano=False)
    L = sc.add('A_target_blue', target_blue, 2247, 556)
    tx, ty = L.pivot
    L.span(90).key('position', [(90, [tx - 510.0, ty], HOLD), (97, [tx, ty], HOLD)])
    L = sc.addc('A_none', none_label)
    nx_, ny_ = L.pivot
    L.span(91, 93).set(pano=False).key('position', [(91, [nx_, ny_ + 273.0], HOLD), (92, [nx_, ny_], HOLD)])
"""))
pairs.append(("""    # frames 84-85 are the chrome close-up: the towers step aside for those two frames
    for nm in ('A_w1', 'A_w2', 'A_grayrect', 'A_violet', 'A_tile_z', 'A_tile_re', 'A_tile_k', 'A_ocr', 'A_circ_top'):
        L = sc.get(nm)
        op = L.static.get('opacity', 100.0)
        L.key('opacity', [(L.t_in, op, HOLD), (84, 0.0, HOLD), (86, op, HOLD)])

""", ""))
patch('sec_a2.py', pairs)
print('v9 sec_a2 patches applied')
