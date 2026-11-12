"""python tools/cmp_pano.py X0 X1 OUT [scale] : reference panorama (top) vs replica preview (bottom)"""
import sys
from PIL import Image, ImageDraw
x0, x1 = int(sys.argv[1]), int(sys.argv[2]); out = sys.argv[3]
sc = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
ref = Image.open('pano/pano.png').convert('RGB').crop((x0, 0, x1, 1080))
mine = Image.open(r'C:\Users\bg931\Documents\New project\rollback-replica\out\pano_preview.jpg').convert('RGB').crop((x0, 0, x1, 1080))
w = int((x1 - x0) * sc); h = int(1080 * sc)
sheet = Image.new('RGB', (w, h * 2 + 6), (255, 0, 0))
sheet.paste(ref.resize((w, h), Image.LANCZOS), (0, 0)); sheet.paste(mine.resize((w, h), Image.LANCZOS), (0, h + 6))
d = ImageDraw.Draw(sheet); d.text((4, 4), 'REFERENCE', fill=(255, 0, 0)); d.text((4, h + 10), 'REPLICA', fill=(255, 0, 0))
sheet.save(out, quality=90); print(out, sheet.size)
