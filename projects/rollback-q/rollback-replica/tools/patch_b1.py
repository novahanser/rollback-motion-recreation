import os
SC = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts'
p = os.path.join(SC, 'sec_b.py')
s = open(p, encoding='utf-8').read()
a = s.index("    pts = []\n    for i in range(121):")
b = s.index("    c.line(pts, col, 1.0)\n    c.text(3013, Y(180), '[*]'")
new = '''    pts = []
    for i in range(121):
        t = i / 120.0
        x = 2750 + 900 * t
        if t < 0.33:
            y = 330 - 65 * math.sin(t / 0.33 * math.pi)
        elif t < 0.78:
            y = 330 + 110 * (1 - math.cos((t - 0.33) / 0.45 * math.pi)) / 2
        else:
            y = 440
        pts.append((x, Y(y)))
'''
s = s[:a] + new + s[b:]
old = "        L.span(f0).wipe(f0, 3, angle=ang_ + 90.0)"
assert old in s
s = s.replace(old, "        L.span(f0).wipe(f0, 3, angle=ang_ - 90.0)")
old = "sc.addc('B_folders', folders).span(119).wipe(119, 3, angle=180)"
assert old in s
s = s.replace(old, "sc.addc('B_folders', folders).span(119).wipe(119, 3, angle=0)")
open(p, 'w', encoding='utf-8').write(s)

p = os.path.join(SC, 'sec_a2.py')
s = open(p, encoding='utf-8').read()
old = "glyph_tile, 'Z', 'ariblk.ttf', 50, 57, 78, dx=4, dy=-6, rot=0)"
assert old in s
s = s.replace(old, "glyph_tile, 'Z', 'Montserrat-BlackItalic.ttf', 50, 57, 84, dx=6, dy=-8, rot=0)")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
