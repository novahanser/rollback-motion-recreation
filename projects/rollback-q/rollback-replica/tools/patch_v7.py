"""v7: the two big sprocket strips go behind the chibi parade, parade thinned to 16 copies, city silhouette stretched taller."""
import io, os
D = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts'


def patch(name, pairs):
    p = os.path.join(D, name)
    s = io.open(p, encoding='utf-8').read()
    for old, new in pairs:
        assert s.count(old) == 1, (name, s.count(old), old[:70])
        s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
    print(name, 'ok')


patch('filmrun.py', [
    ("PARADE_L = [153, 295, 400, 501, 573, 614, 679, 758, 833, 883, 945, 1023, 1148, 1239, 1331, 1427, 1530, 1665, 1770]",
     "PARADE_L = [153, 295, 400, 501, 573, 679, 758, 883, 1023, 1148, 1239, 1331, 1427, 1530, 1665, 1770]"),
    ("def parade_seg(i):\n    return parade_row().crop(", "def parade_seg(i, ver=2):\n    return parade_row().crop("),
    ("        L = sc.add('F_par_%s' % nm, parade_seg, 0, 0, i, k=1, crop=False)", "        L = sc.add('F_par_%s' % nm, parade_seg, 0, 0, i, 2, k=1, crop=False)"),
])

patch('sec_d.py', [
    ("""def build_lens(sc):
    \"\"\"lens rings: added early (from sec_c, before the film-run parade) so the chibis and every film strip stay in front\"\"\"
    sec0 = sc.sec""",
     """def _is_back(c):
    \"\"\"the two wide sprocket strips (with their holes and gold edge print): they pass *behind* the chibi parade\"\"\"
    if c[0] == 'rect' and c[1] in (8535, 9335) and c[2] == 0:
        return True
    if c[0] == 'holes' and c[1] in ([8626], [9377]):
        return True
    return c[0] == 'text' and c[1] in (8563, 8566)


def build_lens(sc):
    \"\"\"lens rings + the two wide sprocket strips: added early (from sec_c, before the film-run parade) so the chibis stay in front\"\"\"
    sec0 = sc.sec"""),
    ("""        L.span(200).key('rotation', ks)
    sc.sec = sec0""",
     """        L.span(200).key('rotation', ks)
    sc.addc('D_filmE_back', film_set, [c for c in FILM_E if _is_back(c)], 8531, 0, 8664, 1084).span(200)
    sc.addc('D_filmF_back', film_set, [c for c in FILM_F if _is_back(c)], 9331, 0, 9419, 1084).span(200)
    sc.sec = sec0"""),
    ("    sc.addc('D_filmE', film_set, FILM_E, 8246, 0, 8664, 1084).span(200)",
     "    sc.addc('D_filmE', film_set, [c for c in FILM_E if not _is_back(c)], 8246, 0, 8664, 1084).span(200)"),
    ("    sc.addc('D_filmF', film_set, FILM_F, 8591, 0, 9499, 1084).span(200)",
     "    sc.addc('D_filmF', film_set, [c for c in FILM_F if not _is_back(c)], 8591, 0, 9499, 1084).span(200)"),
])

patch('sec_c.py', [
    ("    L = sc.add('C_cityfill', la_city_fill, 5510, -178, k=CITY_K)\n",
     "    L = sc.add('C_cityfill', la_city_fill, 5510, -178, k=CITY_K)\n    L.pivot = (L.x + L.ww / 2, 562.0)\n    L.set(scale=[100.0, 118.0])              # the source skyline is taller: stretch from the ground line\n"),
    ("    L = sc.add('C_city', la_city, 5510, -178, k=CITY_K)\n",
     "    L = sc.add('C_city', la_city, 5510, -178, k=CITY_K)\n    L.pivot = (L.x + L.ww / 2, 562.0)\n    L.set(scale=[100.0, 118.0])\n"),
])
print('v7 patches applied')
