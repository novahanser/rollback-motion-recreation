import os
SC = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts'
p = os.path.join(SC, 'lib.py')
s = open(p, encoding='utf-8').read()
old = "a[..., 3] = (a[..., 3] * L.static['opacity'] / 100.0).astype(np.uint8)"
assert old in s
s = s.replace(old, "a[..., 3] = (a[..., 3].astype(np.float32) * L.static['opacity'] / 100.0).astype(np.uint8)")
open(p, 'w', encoding='utf-8').write(s)

p = os.path.join(SC, 'sec_a2.py')
s = open(p, encoding='utf-8').read()
# 1) text bar goes under the towers
a = s.index("    L = sc.addc('A_textbar', text_bar)")
b = s.index("    sc.add('A_ocr', ocr_text, 1830, 398")
bar_block = s[a:b]
s = s[:a] + s[b:]
anchor = "    sc.add('A_w1', solid_rect, 1715, 395, 98, 147, (255, 255, 255)).span(79)\n"
assert anchor in s
s = s.replace(anchor, bar_block + anchor)
# 2) target crops: keep the grass strip, fuller blue twin
old = "    im = gen('target.png')\n    return fit(im, 450 * K, 340 * K)"
assert old in s
s = s.replace(old, "    im = gen('target.png')\n    return ImageOps.fit(im, (450 * K, 340 * K), Image.LANCZOS, centering=(0.5, 0.1))")
old = "    im = fit(im, 450 * K, 350 * K).transpose(Image.FLIP_TOP_BOTTOM)"
assert old in s
s = s.replace(old, "    im = ImageOps.fit(im, (450 * K, 350 * K), Image.LANCZOS, centering=(0.5, 0.1)).transpose(Image.FLIP_TOP_BOTTOM)")
old = "    m = ((lum < 150) | (sat > 70)).astype(np.float32)"
assert old in s
s = s.replace(old, "    m = ((lum < 170) | (sat > 46)).astype(np.float32)")
s = s.replace("from lib import *\n", "from lib import *\nfrom PIL import ImageOps\n", 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
