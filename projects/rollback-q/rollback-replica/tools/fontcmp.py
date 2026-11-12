"""Font comparison sheets: reference crop + candidate renders."""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
FS = json.load(open('fonts.json', encoding='utf-8'))
PANO = Image.open('pano/pano.png').convert('RGB')
def fr(f): return Image.open(f'frames_full/f_{f:04d}.jpg').convert('RGB')
lab = ImageFont.truetype('arial.ttf', 14)
def find(fam, style=None):
    c = [f for f in FS if f[1].lower() == fam.lower() and (style is None or f[2].lower() == style.lower())]
    if not c: c = [f for f in FS if fam.lower() in f[1].lower() and (style is None or style.lower() in f[2].lower())]
    return os.path.join(c[0][3], c[0][0]) if c else None
def render(text, path, size, sx=1.0, stroke=0, fill=(0, 0, 0)):
    f = ImageFont.truetype(path, size)
    w = int(f.getlength(text)) + 20; asc, desc = f.getmetrics()
    im = Image.new('RGB', (w, asc + desc + 12), (230, 230, 230))
    ImageDraw.Draw(im).text((10, 6), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=fill)
    if sx != 1.0: im = im.resize((int(im.width * sx), im.height), Image.LANCZOS)
    return im
def sheet(out, ref, text, cands, size=64, W=1900):
    tiles = []
    t = Image.new('RGB', (ref.width + 8, ref.height + 22), (30, 30, 60)); t.paste(ref, (4, 20)); ImageDraw.Draw(t).text((4, 2), 'REFERENCE', fill=(255, 80, 80), font=lab); tiles.append(t)
    for c in cands:
        fam, style, sx = (c + (None, 1.0))[:3] if isinstance(c, tuple) else (c, None, 1.0)
        stroke = c[3] if isinstance(c, tuple) and len(c) > 3 else 0
        p = find(fam, style)
        if not p: print('missing', fam, style); continue
        try: im = render(text, p, size, sx or 1.0, stroke)
        except Exception as e: print('fail', fam, e); continue
        t = Image.new('RGB', (im.width + 8, im.height + 22), (30, 30, 60)); t.paste(im, (4, 20))
        ImageDraw.Draw(t).text((4, 2), f'{fam} {style or ""} sx={sx}', fill=(255, 230, 0), font=lab); tiles.append(t)
    x = y = 0; rowh = 0; pos = []
    for t in tiles:
        if x + t.width > W: x = 0; y += rowh + 4; rowh = 0
        pos.append((x, y)); x += t.width + 4; rowh = max(rowh, t.height)
    sh = Image.new('RGB', (W, y + rowh), (30, 30, 60))
    for t, p in zip(tiles, pos): sh.paste(t, p)
    sh.save(out, quality=92); print(out, sh.size)
def crop(src, box, z):
    im = (PANO if src == 'p' else fr(src)).crop(box)
    return im.resize((int(im.width * z), int(im.height * z)), Image.LANCZOS)
which = sys.argv[1]
if which == 'title':
    sheet('sheets/fc_title.jpg', crop('p', (10030, 50, 10790, 160), 1.25), 'Rollback',
          [('Ultra', None, 1.0), ('Ultra', None, 1.15), ('Rockwell Extra Bold', None, 1.25), ('Roboto Slab', 'Black', 1.3), ('Wide Latin', None, 0.6), ('Elephant', None, 1.2),
           ('Cooper Black', None, 1.2), ('Abril Fatface', None, 1.25), ('Poster Sans', None, 1.0), ('Bree', None, 1.2)], size=110)
elif which == 'thin':
    sheet('sheets/fc_thin.jpg', crop('p', (425, 0, 560, 140), 2.2).rotate(-78, expand=True, fillcolor=(230, 230, 230)), 'Farewell',
          [('Roboto', 'Thin Italic'), ('RF Tone Ultralight Italic',), ('Galatea-ThinItalic',), ('Scholar Sans Thin Italic',), ('Montserrat', 'Thin Italic'),
           ('Helvetica Light', None), ('Inter', 'Thin'), ('FONTSPRING DEMO - Kappa Display Thin Italic',), ('Noah Grotesque', None), ('Tf Grotesk', None)], size=120)
elif which == 'wide':
    sheet('sheets/fc_wide.jpg', crop('p', (1532, 320, 1652, 348), 5), '(SLEEP-2)',
          [('Helvetica', None, 1.3), ('Arial', None, 1.35), ('Eurostile LT Std', None, 1.0), ('Unbounded', None, 1.0), ('Tf Grotesk', None, 1.2), ('Noah Grotesque', None, 1.2),
           ('AmplitudeWide-Regular',), ('AmplitudeWide-Book',), ('Montserrat', 'Regular', 1.0), ('Inter', 'Regular', 1.3), ('Roboto', 'Regular', 1.3)], size=80)
elif which == 'tech':
    sheet('sheets/fc_tech.jpg', crop('p', (1822, 394, 2215, 426), 3.2), r'C:\World\CE\<File2xxx> dotnet build',
          [('Agency FB', None), ('Eurostile LT Std', None), ('Bahnschrift', None), ('Orbitron', None), ('BankGothic Lt BT', None), ('Interstate Mono - Lgt',), ('OCR A Extended',),
           ('VT323',), ('Tf Grotesk',), ('Unbounded', None), ('B612 Mono',), ('Oswald', None), ('Pathway Gothic One',)], size=64)
elif which == 'misc':
    sheet('sheets/fc_num.jpg', crop('p', (3466, 546, 3566, 592), 5), '2100 22 CENTURY',
          [('Montserrat', 'Light'), ('Montserrat', 'Regular'), ('Century Gothic', None), ('Poppins', 'Light'), ('Helvetica Light', None), ('Inter', 'Light'), ('Noah Grotesque', None)], size=60)
    sheet('sheets/fc_digits.jpg', crop(206, (0, 250, 1100, 830), 0.5), '20347',
          [('Courier New', 'Regular'), ('Courier New', 'Regular', 1.0, 3), ('Courier New', 'Bold'), ('Lucida Sans Typewriter', None), ('Cutive Mono',), ('IBM Plex Mono', 'Light'), ('PT Mono',)], size=220)
    sheet('sheets/fc_fat.jpg', crop('p', (4716, 850, 4956, 884), 4), 'Definete memory',
          [('Elephant', None), ('Abril Fatface', None), ('Bodoni MT', 'Black'), ('Playfair Display', 'Black'), ('Cooper Black', None), ('Bernard MT Condensed', None), ('Ultra', None), ('Modern No. 20', None)], size=64)
    sheet('sheets/fc_red.jpg', crop('p', (6650, 190, 6890, 330), 3).rotate(-24, expand=True, fillcolor=(230, 230, 230)), 'She begins a journey across an immense river of time',
          [('Consolas', None), ('Lucida Sans Typewriter', None), ('Cutive Mono',), ('Ubuntu Mono', None), ('JetBrains Mono', None), ('B612 Mono',), ('Courier New', 'Regular'), ('PT Mono',), ('Roboto Mono', 'Regular'), ('IBM Plex Mono', None)], size=40)
