"""sec_d.py v3: title geometry, mirrored wide Q, justified mirrored code, softer lens rings, measured chibi row,
panel stretch during the ending, denser pattern block."""
import io
P = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts\sec_d.py'
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


rep("from sec_c import film_set, dot_text, FILM, REDBASE, GOLD, YEL, BGC, outlined\n",
    "from sec_c import film_set, dot_text, FILM, REDBASE, GOLD, YEL, BGC, outlined\nfrom filmrun import chibi\n")

# ---- pattern block: denser, closer to the busy 1-bit tile sheet of the source
cut('def patterns(seed=5):', 'def chibi(h_world=240.0, pix=4):', r'''def patterns(seed=5):
    rng = np.random.default_rng(seed)
    c = Canvas(8908, 188, 9340, 866, k=K, ss=2)
    bk, wh = (8, 8, 8, 255), (250, 250, 250, 255)
    c.rect(8912, 232, 9335, 862, fill=wh)
    # tiny grid of cells with triangles (top-left)
    for i in range(14):
        for j in range(10):
            x_, y_ = 8930 + i * 9.5, 250 + j * 9.5
            if rng.random() < 0.6:
                c.rect(x_, y_, x_ + 8, y_ + 8, outline=bk, width=0.5)
            if rng.random() < 0.3:
                c.poly([(x_, y_ + 8), (x_ + 4, y_), (x_ + 8, y_ + 8)], bk)
    # vertical stripes
    for i in range(12):
        c.rect(9130 + i * 7.2, 200, 9133.6 + i * 7.2, 270, fill=bk)
    # big pixel pattern (QR-like)
    for i in range(9):
        for j in range(7):
            if rng.random() < 0.5:
                c.rect(9112 + i * 12.5, 274 + j * 12.5, 9124.5 + i * 12.5, 286.5 + j * 12.5, fill=bk)
    for (qx, qy) in ((9112, 274), (9199.5, 274), (9112, 349)):                     # finder squares
        c.rect(qx, qy, qx + 25, qy + 25, fill=bk)
        c.rect(qx + 5, qy + 5, qx + 20, qy + 20, fill=wh)
        c.rect(qx + 9, qy + 9, qx + 16, qy + 16, fill=bk)
    # checkerboard
    for i in range(11):
        for j in range(5):
            if (i + j) % 2 == 0:
                c.rect(9204 + i * 12, 366 + j * 12, 9216 + i * 12, 378 + j * 12, fill=bk)
    # thick chevron rows
    for r in range(6):
        pts = []
        for i in range(17):
            pts.append((8926 + i * 9.0, 350 + r * 12 + (0 if i % 2 else 9)))
        c.line(pts, bk, 4.2, joint=None)
    # horizontal stripe blocks + fine grid (lower half, mostly behind the chibi row)
    for r in range(9):
        c.rect(8915, 610 + r * 8, 8945, 614 + r * 8, fill=bk)
    for r in range(7):
        c.rect(9100, 632 + r * 7, 9150, 635.5 + r * 7, fill=bk)
    for i in range(16):
        c.line([(8952 + i * 9, 640), (8952 + i * 9, 700)], bk, 0.6)
    for j in range(8):
        c.line([(8952, 640 + j * 8.5), (9087, 640 + j * 8.5)], bk, 0.6)
    for r in range(14):
        c.rect(8920 + r * 13, 708, 8926 + r * 13, 760, fill=bk)
    for i in range(22):
        if rng.random() < 0.55:
            c.rect(8950 + (i % 11) * 12, 770 + (i // 11) * 12, 8961 + (i % 11) * 12, 781 + (i // 11) * 12, fill=bk)
    # UI rulers
    for (x0_, y0_, x1_) in ((8930, 238, 9160), (8950, 818, 9165)):
        c.rect(x0_, y0_, x1_, y0_ + 12, fill=(60, 60, 60, 255))
        for i in range(int((x1_ - x0_) / 6)):
            c.line([(x0_ + i * 6, y0_ + 12), (x0_ + i * 6 - 5, y0_)], (220, 220, 220, 255), 0.6)
        c.rrect(x0_ + 70, y0_ + 2, x0_ + 96, y0_ + 10, 2, fill=wh)
    c.circle(9110, 300, 22, outline=bk, width=0.8)
    c.circle(9098, 656, 14, outline=bk, width=0.8)
    c.line([(9000, 420), (9230, 396)], bk, 0.7)
    c.line([(9250, 330), (9330, 350), (9300, 400)], bk, 0.7)
    for (nx, ny) in ((9000, 420), (9230, 396), (9250, 330), (9330, 350), (9300, 400)):
        c.circle(nx, ny, 2.6, fill=wh, outline=bk, width=0.7)
    # dark blocks
    c.rect(9160, 232, 9335, 250, fill=bk)
    c.rect(9080, 690, 9118, 840, fill=(30, 30, 30, 255))
    c.rect(8912, 700, 8935, 760, fill=bk)
    im = c.done()
    # gradient cylinder bottom-right
    x0_, y0_, x1_, y1_ = 9118, 660, 9332, 858
    w, h = (x1_ - x0_) * K, (y1_ - y0_) * K
    x, y = grid(w, h)
    v = grad_stops(y / h, [(0, (230, 230, 230)), (0.18, (30, 30, 30)), (0.5, (236, 236, 236)), (0.8, (60, 60, 60)), (1, (200, 200, 200))])
    cyl = from_arr(v, np.ones((h, w), np.float32))
    im.alpha_composite(cyl, (int((x0_ - 8908) * K), int((y0_ - 188) * K)))
    # light grey panel top-right
    d = ImageDraw.Draw(im)
    d.rectangle([int((9226 - 8908) * K), int((200 - 188) * K), int((9335 - 8908) * K), int((262 - 188) * K)], fill=(244, 244, 244, 255), outline=(60, 60, 60, 255))
    for i in range(5):
        yy = int((212 + i * 9 - 188) * K)
        d.line([int((9234 - 8908) * K), yy, int((9326 - 8908) * K), yy], fill=(90, 90, 90, 255), width=1)
    return im


''')
cut('def chibi(h_world=240.0, pix=4):', 'def portrait():', '')

# ---- lens rings: softer brushed-metal tones
rep("    v = 128 + 120 * np.cos(n * a + ph) * (0.6 + 0.4 * np.cos((n + 1) * a + ph * 1.7))\n    v = np.clip(v, 8, 250)\n",
    "    v = 156 + 72 * np.cos(n * a + ph) * (0.6 + 0.4 * np.cos((n + 1) * a + ph * 1.7))\n"
    "    v = v + 10 * np.sin(d * 0.9)                     # fine concentric brushing\n    v = np.clip(v, 52, 244)\n")

# ---- title: taller Rockwell Extra Bold fitted to the measured width of 'Rollback' (739 world px), tight tracking
cut('def title(s):', 'def slab(s, size):', r'''def _title_raw(s):
    fnt = font(TITLE_FONT, 131 * K)
    return text_img(s, fnt, (8, 8, 8, 255), pad=6, tracking=-3.0 * K, stroke=int(1.0 * K), stroke_fill=(8, 8, 8, 255))


def title(s):
    ref = _title_raw('Rollback')
    st = 739.0 * K / ref.width                                # same horizontal stretch for both words
    im = _title_raw(s)
    return im.resize((int(im.width * st), im.height), Image.LANCZOS)


''')

# ---- Q: wide, mirrored (tail at the lower left)
cut('def q_glyph():', 'def hourglass():', r'''def q_glyph(w=172.0, h=100.0):
    fnt = font(TITLE_FONT, 150 * K)
    im = text_img('Q', fnt, (8, 8, 8, 255), pad=6, stroke=int(1.0 * K), stroke_fill=(8, 8, 8, 255))
    im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im.resize((int(w * K), int(h * K)), Image.LANCZOS)


''')

# ---- mirrored code block: right-aligned lines, comment lines justified to individual widths
cut('def mirrored_code():', 'def collage():', r'''def mirrored_code():
    words = ['fall', 'pain', 'prayer', 'sins', 'faith', 'hope', 'soul', 'grace']
    tails = ['is a mistake', 'is a disgrace', 'is hard to raise', 'are mine to face', 'is worn and frayed', 'begins to fade', 'still longs for grace', 'is in this place']
    widths = [750, 390, 390, 383, 583, 390, 390, 440]
    x0, x1 = 10028, 10830
    c = Canvas(x0, 720, x1, 1004, k=K, ss=3)
    col = (14, 14, 14, 255)
    fs = 9.8
    xr = x1 - 8.0                                              # every line ends here (-> left edge after the flip)

    def justified(y, toks, width):
        n = len(toks)
        for i, t in enumerate(toks):
            c.text(xr - width + width * i / float(max(n - 1, 1)), y, t, 'arial.ttf', fs, col, anchor='la' if i < n - 1 else 'ra')

    def plain(y, s):
        c.text(xr, y, s, 'arial.ttf', fs, col, anchor='ra', tracking=-0.3)

    y = 724.0
    for wd, tl, wj in zip(words, tails, widths):
        toks = ['#', 'I', 'know', 'my', wd if wd != 'grace' else 'God'] + tl.split(' ')
        justified(y, toks, wj)
        y += 11.8
        plain(y, 'self.record.append("%s")' % wd)
        y += 11.8
    y += 10
    justified(y, ['if', 'len(self.record)', '>=', '8:'], 250)
    y += 11.8
    plain(y, 'self.record.clear()')
    y += 11.8
    justified(y, ['#', 'rollback', 'complete', '\u2014', 'restart'], 253)
    y += 23.6
    justified(y, ['def', 'emit(self):'], 198)
    y += 11.8
    justified(y, ['return', "'-", 'rollback', 'Q', '-', '//', 'each', 'iteration', 'carries', 'the', 'same', "weight'"], 548)
    return c.done().transpose(Image.FLIP_LEFT_RIGHT)


''')

# ---- digits strip now lives in filmrun.py
cut('def digits_strip(seed=3):', '# ----------------------------------------------------------------------------- build', '')

# ---- build: chibi row (measured centres), no world digits
cut("    first = sc.add('D_chibi00', chibi, 8910, 425)", "    # ---------------- title panel", r'''    ROWX = [8948, 9017, 9089, 9126, 9199, 9244, 9303, 9344, 9385, 9435]            # centres measured on frame 227
    first = sc.add('D_chibi00', chibi, 0, 0, 200.0)
    for i, cx_ in enumerate(ROWX):
        L = first if i == 0 else sc.clone('D_chibi%02d' % i, first)
        L.x, L.y = cx_ - L.ww / 2, 526 - L.wh / 2
        L.pivot = (cx_, 526.0)
        # still under the global invert on 224-225: pre-invert so they keep their own colours
        L.span(224).fx('ADBE Invert', **{'ADBE Invert-0002': [(224, 0.0, HOLD), (226, 100.0, HOLD)]})

''')
rep("    L = sc.add('D_forward', title, 10035, 50, 'Forward')", "    L = sc.add('D_forward', title, 10035, 38, 'Forward')")
rep("    L = sc.add('D_rollback', title, 10035, 50, 'Rollback')", "    L = sc.add('D_rollback', title, 10035, 38, 'Rollback')")
rep("    panel.append(sc.add('D_q1', q_glyph, 10605, 168).span(224))", "    panel.append(sc.add('D_q1', q_glyph, 10617, 161).span(224))")
rep("    sc.add('D_q2', q_glyph, 9838, 738).span(224)", "    sc.add('D_q2', q_glyph, 9833, 739, 111.0, 55.0).span(224)")
rep("    panel.append(sc.add('D_code', mirrored_code, 10028, 726).span(224))", "    panel.append(sc.add('D_code', mirrored_code, 10028, 720).span(224))")

# ---- flip keys + horizontal stretch of the whole panel while the picture dies (265-271)
cut("    for L in panel:\n        L.pivot = (FLIP_X, L.pivot[1])", "    # ---------------- bits left of the panel", r'''    # ending: the panel smears out horizontally (anchor near its right end) -> (pivot world x, x-stretch) per frame
    END = [(265, 10524.6, 1.234), (266, 10593.8, 1.276), (267, 10706.5, 1.459), (268, 10871.6, 1.694), (269, 11000.4, 2.215),
           (270, 10865.2, 3.4), (271, 10057.0, 6.0)]
    for L in panel:
        L.pivot = (FLIP_X, L.pivot[1])
        sx0 = L.static.get('scale', [100.0, 100.0])
        sy = sx0[1]
        sg = 1 if sx0[0] >= 0 else -1
        L.key('scale', [(236, [100 * sg, sy], HOLD), (237, [30 * sg, sy], HOLD), (238, [-40 * sg, sy], HOLD), (239, [-100 * sg, sy], HOLD),
                        (240, [-128 * sg, sy], HOLD), (241, [160 * sg, sy], HOLD), (242, [108 * sg, sy], HOLD), (243, [100 * sg, sy], HOLD)]
              + [(f, [100 * sg * st, sy], HOLD) for f, x_, st in END])
        L.key('position', [(236, [FLIP_X, L.pivot[1]], HOLD)] + [(f, [x_, L.pivot[1]], HOLD) for f, x_, st in END])

''')

io.open(P, 'w', encoding='utf-8', newline='\n').write(src)
print('sec_d.py patched,', n_done[0], 'edits,', len(src.splitlines()), 'lines')
