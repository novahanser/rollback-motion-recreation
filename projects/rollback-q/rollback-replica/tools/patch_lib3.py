import json, shutil, os
SP = r'C:\Users\bg931\AppData\Local\Temp\claude\ba7d08790bd34c96\d8b35439-ddcc-45d2-b42a-ca01366e379b\scratchpad'
SC = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts'
shutil.copy(os.path.join(SP, 'fonts.json'), os.path.join(SC, 'fonts_index.json'))

p = os.path.join(SC, 'lib.py')
s = open(p, encoding='utf-8').read()
a = s.index("def font(name, size):")
b = s.index("# ----------------------------------------------------------------------------- image helpers")
new = '''_FONT_INDEX = None


def _font_index():
    global _FONT_INDEX
    if _FONT_INDEX is None:
        p_ = os.path.join(HERE, 'fonts_index.json')
        _FONT_INDEX = json.load(open(p_, encoding='utf-8')) if os.path.exists(p_) else []
    return _FONT_INDEX


def font_path(name):
    """file name ('arial.ttf') or 'Family|Style' looked up in fonts_index.json"""
    if '|' in name:
        fam, style = name.split('|', 1)
        for f in _font_index():
            if f[1].lower() == fam.lower() and f[2].lower() == style.lower():
                return os.path.join(f[3], f[0])
        for f in _font_index():
            if fam.lower() in f[1].lower() and style.lower() in f[2].lower():
                return os.path.join(f[3], f[0])
        return os.path.join(FONTS, 'arial.ttf')
    for base in (FONTS, UFONTS):
        p_ = os.path.join(base, name)
        if os.path.exists(p_):
            return p_
    return os.path.join(FONTS, 'arial.ttf')


def font(name, size):
    return ImageFont.truetype(font_path(name), int(round(size)))


'''
s = s[:a] + new + s[b:]
s = s.replace("LIBV = 'v1'", "LIBV = 'v2'")
open(p, 'w', encoding='utf-8').write(s)

# section A: font + remove layers that moved to sec_a2
p = os.path.join(SC, 'sec_a.py')
s = open(p, encoding='utf-8').read()
for old in ("    sc.add('A_hill', hill, 1376, 484).span(44).flash(44, PK, 1)\n",
            "    sc.addc('A_lamp', lamp).span(44).flash(44, PK, 1)\n",
            "    sc.addc('A_redlines', red_lines).span(47).wipe(47, 3, angle=-90)\n"):
    assert old in s, old
    s = s.replace(old, "")
assert "'Farewell', 'Roboto-ThinItalic.ttf', 68" in s
s = s.replace("'Farewell', 'Roboto-ThinItalic.ttf', 68", "'Farewell', 'Josefin Sans|Thin Italic', 82")
assert "return text_asset('开始', 'simsun.ttc', 40, (10, 10, 10), sx=2.4, blur_x=5)" in s
s = s.replace("return text_asset('开始', 'simsun.ttc', 40, (10, 10, 10), sx=2.4, blur_x=5)",
              "return text_asset('开始', 'simsun.ttc', 30, (10, 10, 10), sx=3.4)")
open(p, 'w', encoding='utf-8').write(s)

p = os.path.join(SC, 'sec_a2.py')
s = open(p, encoding='utf-8').read()
s = s.replace("'PressStart2P-Regular.ttf'", "'Press Start 2P|Regular'")
open(p, 'w', encoding='utf-8').write(s)

# build order: add sec_a2
p = os.path.join(SC, 'build.py')
s = open(p, encoding='utf-8').read()
s = s.replace("SECTIONS = ['intro', 'sec_a', 'sec_b', 'sec_c', 'sec_d', 'fx']", "SECTIONS = ['sec_a', 'sec_a2', 'sec_b', 'sec_c', 'sec_d', 'fx']")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
