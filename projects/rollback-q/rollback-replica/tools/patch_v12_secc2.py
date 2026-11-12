import io
P = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts\sec_c.py'
s = io.open(P, encoding='utf-8').read()
def repl(old, new):
    global s
    assert s.count(old) == 1, (old[:70], s.count(old))
    s = s.replace(old, new)
# backdrop pieces: pre-scaled images instead of a non-uniform layer scale
repl("def bd_piece(kind, mode):\n", "def bd_piece(kind, mode, sx=1.0, sy=1.0):\n")
repl("""        out[..., 3] = (np.clip((205.0 - lum) / 110.0, 0, 1) * (al >= 128) * 255).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def cables():""", """        out[..., 3] = (np.clip((205.0 - lum) / 110.0, 0, 1) * (al >= 128) * 255).astype(np.uint8)
    im = Image.fromarray(out, 'RGBA')
    return im.resize((int(round(im.width * sx * K)), int(round(im.height * sy * K))), Image.LANCZOS)      # (sx, sy) = world px per sheet px


def cables():""")
repl("""        L = sc.add('C_bdfill_' + kind, bd_piece, wx_, wy_, kind, 'fill', k=1.0 / sx_, crop=False)
        L.pivot = (wx_, wy_)
        L.set(scale=[100.0, 100.0 * sy_ / sx_])
        L.span(150)""", """        L = sc.add('C_bdfill_' + kind, bd_piece, wx_, wy_, kind, 'fill', sx_, sy_, crop=False)
        L.span(150)""")
repl("""        L = sc.add('C_bdline_' + kind, bd_piece, wx_, wy_, kind, 'lines', k=1.0 / sx_, crop=False)
        L.pivot = (wx_, wy_)
        L.set(scale=[100.0, 100.0 * sy_ / sx_])
        L.span(150)""", """        L = sc.add('C_bdline_' + kind, bd_piece, wx_, wy_, kind, 'lines', sx_, sy_, crop=False)
        L.span(150)""")
# static (panorama) positions for the keyed sign / toggle / lantern
repl("""    L = sc.addc('C_baton', lantern, pivot=(0, 0))
    L.span(166)""", """    L = sc.addc('C_baton', lantern, pivot=(0, 0))
    L.x += 6398.0
    L.y += 541.0
    L.pivot = (6398.0, 541.0)
    L.span(166)""")
repl("""    L = sc.addc('C_sign', no_parking, pivot=(0, 0))
    L.span(166)""", """    L = sc.addc('C_sign', no_parking, pivot=(0, 0))
    L.x += 6518.0
    L.y += 559.5
    L.pivot = (6518.0, 559.5)
    L.span(166)""")
repl("""    L = sc.addc('C_toggle', toggle, pivot=(0, 0))
    L.span(166)""", """    L = sc.addc('C_toggle', toggle, pivot=(0, 0))
    L.x += 6714.0
    L.y += 599.5
    L.pivot = (6714.0, 599.5)
    L.span(166)""")
# denser wire blobs
repl("""    for (cx_, cy_, rx, ry, n, m) in ((6074.0, 524.0, 106.0, 100.0, 13, 5), (6296.0, 532.0, 122.0, 118.0, 15, 7)):""",
     """    for (cx_, cy_, rx, ry, n, m) in ((6074.0, 524.0, 106.0, 100.0, 16, 8), (6296.0, 532.0, 122.0, 118.0, 18, 10)):""")
repl("""        c.line(out + [out[0]], col, 1.25, joint=None)
        inner = [(cx_ + rx * 0.8 * (rng.random() - 0.5), cy_ + ry * 0.8 * (rng.random() - 0.5)) for _ in range(m)]
        for j_, p in enumerate(inner):
            for i_ in rng.choice(n, size=4, replace=False):
                c.line([p, out[int(i_)]], col, 0.85)
            c.line([p, inner[(j_ + 1) % m]], col, 0.85)""", """        c.line(out + [out[0]], col, 1.4, joint=None)
        inner = [(cx_ + rx * 1.1 * (rng.random() - 0.5), cy_ + ry * 1.1 * (rng.random() - 0.5)) for _ in range(m)]
        for j_, p in enumerate(inner):
            for i_ in rng.choice(n, size=5, replace=False):
                c.line([p, out[int(i_)]], col, 0.95)
            c.line([p, inner[(j_ + 1) % m]], col, 0.95)
            c.line([p, inner[(j_ + 3) % m]], col, 0.8)
        for i_ in range(0, n, 2):                                   # a few chords across the outline
            c.line([out[i_], out[(i_ + n // 3) % n]], col, 0.8)""")
repl("""    img = from_arr(lerp_color((178, 206, 242), (252, 253, 255), t), np.ones((h, w), np.float32) * 0.92)""",
     """    img = from_arr(lerp_color((204, 222, 246), (253, 254, 255), t ** 0.7), np.ones((h, w), np.float32) * 0.92)""")
io.open(P, 'w', encoding='utf-8').write(s)
print('ok')
