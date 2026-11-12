import os
SC = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts'


def patch(fn, pairs):
    p = os.path.join(SC, fn)
    s = open(p, encoding='utf-8').read()
    for old, new in pairs:
        assert old in s, (fn, old[:80])
        s = s.replace(old, new, 1)
    open(p, 'w', encoding='utf-8').write(s)


# ---------------- lib: below flag, clone, world keys ----------------
patch('lib.py', [
    ("        self.pano = True                          # include in the static panorama preview\n",
     "        self.pano = True                          # include in the static panorama preview\n"
     "        self.below = False                        # screen layer that must sit under the world layer\n"),
    ("        self.sec = 'A'\n        self.kdef = 2\n",
     "        self.sec = 'A'\n        self.kdef = 2\n        self.world_keys = {}      # extra keys for the RB_WORLD layer in RB_MAIN (e.g. opacity)\n"),
    ("    def solid(self, name, color, w=W, h=H, x=0, y=0, sec=None, screen=True, kind='solid'):",
     "    def clone(self, name, src):\n"
     "        \"\"\"another layer using the same footage as `src`\"\"\"\n"
     "        L = Layer(self, name, src.size, src.k, src.x, src.y, sec=src.sec, screen=src.screen)\n"
     "        L.file = src.file\n"
     "        self.layers.append(L)\n"
     "        return L\n\n"
     "    def solid(self, name, color, w=W, h=H, x=0, y=0, sec=None, screen=True, kind='solid'):"),
])

# ---------------- exporter ----------------
patch('ae_export.py', [
    ("    below = [L for i, L in enumerate(scene.layers) if L.screen and i < first_world]\n"
     "    above = [L for i, L in enumerate(scene.layers) if L.screen and i > first_world]\n",
     "    below = [L for i, L in enumerate(scene.layers) if L.screen and (i < first_world or L.below)]\n"
     "    above = [L for i, L in enumerate(scene.layers) if L.screen and i > first_world and not L.below]\n"),
    ("               'transformGroup': _transform([OX, OY + 540.0], pos_keys[0][1], [100, 100], 0, 100,\n"
     "                                            {'position': pos_keys, 'scale': sc_keys})})",
     "               'transformGroup': _transform([OX, OY + 540.0], pos_keys[0][1], [100, 100], 0, 100,\n"
     "                                            dict({'position': pos_keys, 'scale': sc_keys}, **getattr(scene, 'world_keys', {})))})"),
])

# ---------------- film_set: skip zero-thickness bands ----------------
patch('sec_c.py', [
    ("            c.rect(a, b, cc, b + tt, fill=rgba(col))\n"
     "            c.rect(a, dd - tb, cc, dd, fill=rgba(col))\n"
     "            c.rect(a, b, a + tl, dd, fill=rgba(col))\n"
     "            c.rect(cc - tr, b, cc, dd, fill=rgba(col))\n",
     "            if tt > 0:\n                c.rect(a, b, cc, b + tt, fill=rgba(col))\n"
     "            if tb > 0:\n                c.rect(a, dd - tb, cc, dd, fill=rgba(col))\n"
     "            if tl > 0:\n                c.rect(a, b, a + tl, dd, fill=rgba(col))\n"
     "            if tr > 0:\n                c.rect(cc - tr, b, cc, dd, fill=rgba(col))\n"),
])

# ---------------- section D tweaks ----------------
patch('sec_d.py', [
    ("    L.span(224, 240).set(pano=False)\n    panel.append(L)\n    L = sc.add('D_rollback', title, 10035, 50, 'Rollback')\n    L.span(240)",
     "    L.span(224, 241).set(pano=False)\n    panel.append(L)\n    L = sc.add('D_rollback', title, 10035, 50, 'Rollback')\n    L.span(241)"),
    ("    ch_w = None\n    for i in range(12):\n        L = sc.add('D_chibi%02d' % i, chibi, 8910 + i * 47.5 - (10 if i % 3 == 1 else 0), 425)\n        L.span(224)\n",
     "    first = sc.add('D_chibi00', chibi, 8910, 425)\n    first.span(224)\n"
     "    for i in range(1, 12):\n        L = sc.clone('D_chibi%02d' % i, first)\n"
     "        L.x = first.x + i * 47.5 - (10 if i % 3 == 1 else 0)\n"
     "        L.pivot = (L.x + L.ww / 2, L.y + L.wh / 2)\n        L.span(224)\n"),
])

# ---------------- fx: column tearing direction ----------------
patch('fx.py', [("'ADBE Wave Warp-0003': 3.0, 'ADBE Wave Warp-0004': 0.0,", "'ADBE Wave Warp-0003': 3.0, 'ADBE Wave Warp-0004': 90.0,")])

# ---------------- base: vignette flash on frame 2, white ruler on the black frames ----------------
patch('base.py', [
    ("import numpy as np\nfrom lib import *\n", "import numpy as np\nfrom lib import *\nimport shapes0 as S0\n"),
    ("    sc.solid('BG_blue', (105, 130, 246)).blink([0, 70, 72, 74, 79, 81, 85], on=0, off=100)\n",
     "    sc.solid('BG_blue', (105, 130, 246)).blink([0, 70, 72, 74, 79, 81, 85], on=0, off=100)\n"
     "    L = sc.add('BG_vignette', S0.vignette, 0, 0, k=0.5, screen=True, crop=False)\n"
     "    L.span(2, 3)\n    L.pano = False\n"),
    ("        L.pano = True\n    return sc",
     "        L.pano = True\n"
     "        if i in (0, 1):      # frames 1-2 sit on black: show the ruler in white\n"
     "            L.fx('ADBE Invert', **{'ADBE Invert-0002': [(0, 100.0, HOLD), (1, 0.0, HOLD), (3, 100.0, HOLD)]})\n"
     "    return sc"),
])

# ---------------- section A tweaks ----------------
patch('sec_a.py', [
    ("return S0.holo_disc(830.0, k=1, seed=11, rim=True, sat=0.8)", "return S0.holo_disc(830.0, k=1, seed=11, rim=True, sat=0.5)"),
    ("    L.span(25).key('scale', [(25, [55, 55], LIN), (27, [100, 100], LIN)])", "    L.span(36).key('scale', [(36, [55, 55], LIN), (39, [100, 100], LIN)])"),
    ("circle_outline, 980 - 130, 437 - 130, 64.0, 128.0, PK", "circle_outline, 980 - 94, 437 - 94, 46.0, 92.0, PK"),
])
patch('sec_a2.py', [
    ("    # transient tall grey 'scrollbars' (88-94)",
     "    # frames 84-85 are the chrome close-up: the towers step aside for those two frames\n"
     "    for nm in ('A_w1', 'A_w2', 'A_grayrect', 'A_violet', 'A_tile_z', 'A_tile_re', 'A_tile_k', 'A_ocr', 'A_circ_top'):\n"
     "        L = sc.get(nm)\n"
     "        op = L.static.get('opacity', 100.0)\n"
     "        L.key('opacity', [(L.t_in, op, HOLD), (84, 0.0, HOLD), (86, op, HOLD)])\n\n"
     "    # transient tall grey 'scrollbars' (88-94)"),
])
print('ok')
