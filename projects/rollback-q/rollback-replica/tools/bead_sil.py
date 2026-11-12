"""silhouette of the bead chain in the original (flood fill from outside, the white outline is the barrier)
python tools/bead_sil.py f0 f1  -> sheets/sil_%d.png (mask, screen crop BOXS) + preview"""
import sys
import numpy as np
from PIL import Image, ImageFilter
BOXS = (660, 300, 1024, 544)
def silhouette(f):
    im = np.asarray(Image.open('frames_full/f_%04d.jpg' % f).convert('RGB').crop(BOXS)).astype(int)
    h, w = im.shape[:2]
    white = (im.min(axis=2) > 180)
    barrier = np.asarray(Image.fromarray((white * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))) > 0
    reach = np.zeros((h, w), bool)
    stack = [(y, x) for y in range(h) for x in (0, w - 1)] + [(y, x) for x in range(w) for y in (0, h - 1)]
    # inner hole of the ring: seeds along the major axis around the centre
    for t in np.linspace(-0.45, 0.45, 19):
        stack.append((int(409.4 + 125.5 * t * 0.267 - BOXS[1] + 4), int(853.8 + 125.5 * t * 0.9636 - BOXS[0])))
    while stack:
        y, x = stack.pop()
        if y < 0 or y >= h or x < 0 or x >= w or reach[y, x] or barrier[y, x]:
            continue
        reach[y, x] = True
        stack.extend(((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)))
    sil = ~reach
    # the barrier was dilated by 1 px: the true silhouette includes the outline, so keep as is
    return sil
if __name__ == '__main__':
    f0, f1 = int(sys.argv[1]), int(sys.argv[2])
    cells = []
    for f in range(f0, f1 + 1):
        s = silhouette(f)
        Image.fromarray((s * 255).astype(np.uint8)).save('sheets/sil_%d.png' % f)
        o = Image.open('frames_full/f_%04d.jpg' % f).convert('RGB').crop(BOXS)
        a = np.asarray(o).copy(); a[~s] = (a[~s] * 0.35).astype(np.uint8)
        cells.append(Image.fromarray(a))
        print(f, 'area', int(s.sum()))
    sheet = Image.new('RGB', (len(cells) * (cells[0].width + 2), cells[0].height))
    for i, c in enumerate(cells):
        sheet.paste(c, (i * (c.width + 2), 0))
    sheet = sheet.resize((sheet.width * 2, sheet.height * 2), Image.LANCZOS)
    sheet.save('sheets/sil_prev.jpg', quality=90); print(sheet.size)
