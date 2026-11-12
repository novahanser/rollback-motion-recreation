"""python tools/cmp_video.py RENDER.mp4 TAG OUT f1 f2 ...   -> pairs (original above replica), 4 pairs per row"""
import sys, os, subprocess
from PIL import Image, ImageDraw, ImageFont
FF = r'C:\Program Files\Adobe\Adobe After Effects 2024\Support Files\Scripts\ScriptUI Panels\ffmpeg.exe'
mp4, tag, out = sys.argv[1:4]; fs = [int(x) for x in sys.argv[4:]]
d = f'render/frames_{tag}'
if not os.path.isdir(d) or len(os.listdir(d)) < 270 or os.path.getmtime(mp4) > os.path.getmtime(d):
    os.makedirs(d, exist_ok=True)
    subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y', '-i', mp4, '-q:v', '3', '-start_number', '0', f'{d}/f_%04d.jpg'], check=True)
    os.utime(d, None)
cw, ch = 480, 270; cols = 4
rows = (len(fs) + cols - 1) // cols
font = ImageFont.truetype('arial.ttf', 16)
sheet = Image.new('RGB', (cols * cw + (cols + 1) * 4, rows * (2 * ch + 8) + 4), (255, 0, 80))
for i, f in enumerate(fs):
    x = 4 + (i % cols) * (cw + 4); y = 4 + (i // cols) * (2 * ch + 8)
    a = Image.open(f'frames_full/f_{f:04d}.jpg').convert('RGB').resize((cw, ch), Image.LANCZOS)
    p = f'{d}/f_{f:04d}.jpg'
    b = Image.open(p).convert('RGB').resize((cw, ch), Image.LANCZOS) if os.path.exists(p) else Image.new('RGB', (cw, ch), (0, 0, 0))
    sheet.paste(a, (x, y)); sheet.paste(b, (x, y + ch + 2))
    dr = ImageDraw.Draw(sheet); dr.rectangle([x, y, x + 62, y + 20], fill=(0, 0, 0)); dr.text((x + 3, y + 1), f'f{f}', fill=(255, 255, 0), font=font)
sheet.save(out, quality=88); print(out, sheet.size)
