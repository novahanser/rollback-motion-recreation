import os
SC = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts'

# ---- lib: static rotation in the panorama preview
p = os.path.join(SC, 'lib.py')
s = open(p, encoding='utf-8').read()
old = """            px, py = int(round((L.x - x0) * scale)), int(round((L.y - y0) * scale))
"""
new = """            px, py = int(round((L.x - x0) * scale)), int(round((L.y - y0) * scale))
            rot = L.static.get('rotation', 0.0)
            if rot:
                pvx, pvy = (L.pivot[0] - x0) * scale, (L.pivot[1] - y0) * scale
                diag = int(math.hypot(im.width, im.height)) + 4
                tmp = Image.new('RGBA', (2 * diag, 2 * diag), (0, 0, 0, 0))
                tmp.paste(im, (int(round(diag + px - pvx)), int(round(diag + py - pvy))))
                tmp = tmp.rotate(-rot, resample=Image.BICUBIC, center=(diag, diag))
                cx0, cy0 = int(round(pvx - diag)), int(round(pvy - diag))
                bx0, by0 = max(cx0, 0), max(cy0, 0)
                bx1, by1 = min(cx0 + 2 * diag, out.width), min(cy0 + 2 * diag, out.height)
                if bx1 > bx0 and by1 > by0:
                    out.alpha_composite(tmp.crop((bx0 - cx0, by0 - cy0, bx1 - cx0, by1 - cy0)), (bx0, by0))
                continue
"""
assert old in s
s = s.replace(old, new, 1)
open(p, 'w', encoding='utf-8').write(s)

# ---- sec_b: curved chain, outline-only spiky shape, kanji font
p = os.path.join(SC, 'sec_b.py')
s = open(p, encoding='utf-8').read()
old = """def ruler_bar():"""
new = """def chain_arc():
    \"\"\"bend the straight bubble chain along an arc (like a caterpillar curling down to the right)\"\"\"
    sheet = gen('y2k-sheet.png')
    boxes = components(sheet, min_area=6000)
    boxes.sort(key=lambda b: (b[1] > sheet.height * 0.45, b[0]))
    src = np.asarray(sheet.crop(boxes[0])).astype(np.float32)
    sh, sw = src.shape[:2]
    x0, y0, x1, y1 = 3895, 255, 4335, 525
    w, h = (x1 - x0) * K, (y1 - y0) * K
    x, y = grid(w, h)
    wx, wy = x / K + x0, y / K + y0
    C = (4060.0, 640.0)
    Rm, thick = 300.0, 96.0
    th = np.degrees(np.arctan2(-(wy - C[1]), wx - C[0]))            # CCW from +x
    r = np.hypot(wx - C[0], wy - C[1])
    t0, t1 = 132.0, 40.0                                            # arc from upper-left to right
    u = (t0 - th) / (t0 - t1)
    v = (Rm + thick / 2 - r) / thick
    ok = (u >= 0) & (u <= 1) & (v >= 0) & (v <= 1)
    sx = np.clip((u * (sw - 1)).astype(int), 0, sw - 1)
    sy = np.clip((v * (sh - 1)).astype(int), 0, sh - 1)
    out = src[sy, sx]
    out[..., 3] = out[..., 3] * ok
    return Image.fromarray(out.astype(np.uint8), 'RGBA')


def ruler_bar():"""
assert old in s
s = s.replace(old, new, 1)
old = """    chain = sc.add('B_chain', sprite, 3905, 318, 0, 415.0, pivot=(3910, 400))
    chain.span(106).set(rotation=-10.0).wipe(106, 3, angle=-90)"""
assert old in s
s = s.replace(old, """    chain = sc.add('B_chain', chain_arc, 3895, 255)
    chain.span(106).wipe(106, 3, angle=-90)""")
old = "    c.poly(pts, (244, 244, 244, 255), (150, 150, 150, 255), 0.9)\n    return c\n\n\n# ----------------------------------------------------------------------------- build"
assert old in s
s = s.replace(old, "    c.line(pts + [pts[0]], (150, 150, 150, 255), 0.9)\n    return c\n\n\n# ----------------------------------------------------------------------------- build")
old = "fnt = font('Source Han Serif SC|Heavy', 62 * c.f)"
assert old in s
s = s.replace(old, "fnt = font('SourceHanSerifSC-Heavy.otf', 62 * c.f)")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
