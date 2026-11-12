"""python tools/chain_test.py OUT f1 f2 ...   original crop (top) vs the composited bracelet over the same crop (bottom), 3x"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, r'C:\Users\bg931\Documents\New project\rollback-replica\scripts')
import chain3d

out = sys.argv[1]
fs = [int(v) for v in sys.argv[2:]]
font = ImageFont.truetype('arial.ttf', 14)
box = (670, 310, 1014, 534); S = 3
cells = []
for f in fs:
    o = Image.open('frames_full/f_%04d.jpg' % f).convert('RGB').crop(box).resize(((box[2] - box[0]) * S, (box[3] - box[1]) * S), Image.LANCZOS)
    ch = chain3d.chain_frame(chain3d.src_index(f))
    bw, bh = chain3d.BOX[2], chain3d.BOX[3]
    ch = ch.resize((int(bw * S), int(bh * S)), Image.LANCZOS)
    r = Image.new('RGBA', o.size, (20, 44, 190, 255))
    ImageDraw.Draw(r).rectangle([0, int(0.55 * o.height), o.width, o.height], fill=(168, 168, 168, 255))
    r.alpha_composite(ch, (int((chain3d.BOX[0] - bw / 2 - box[0]) * S), int((chain3d.BOX[1] - bh / 2 - box[1]) * S)))
    r = r.convert('RGB')
    for im, tag in ((o, 'O'), (r, 'R')):
        d = ImageDraw.Draw(im, 'RGBA')
        for x in range(box[0], box[2] + 1, 20):
            d.line([((x - box[0]) * S, 0), ((x - box[0]) * S, im.height)], fill=(255, 255, 0, 70), width=1)
        for y in range(box[1], box[3] + 1, 20):
            d.line([(0, (y - box[1]) * S), (im.width, (y - box[1]) * S)], fill=(0, 255, 0, 70), width=1)
        d.rectangle([0, 0, 64, 18], fill=(0, 0, 0, 255)); d.text((3, 2), '%s f%d' % (tag, f), fill=(255, 255, 0, 255), font=font)
    cell = Image.new('RGB', (o.width, o.height * 2 + 4), (255, 0, 80))
    cell.paste(o, (0, 0)); cell.paste(r, (0, o.height + 4))
    cells.append(cell)
sheet = Image.new('RGB', (len(cells) * (cells[0].width + 4) + 4, cells[0].height + 8), (255, 0, 80))
for i, c in enumerate(cells):
    sheet.paste(c, (4 + i * (c.width + 4), 4))
sheet.save(out, quality=92); print(out, sheet.size)
