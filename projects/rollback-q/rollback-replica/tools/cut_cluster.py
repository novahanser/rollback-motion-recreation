"""inspect / cut the GPT 'chain-cluster' image into separate cutouts (no glow)"""
import os, sys
import numpy as np
from PIL import Image, ImageFilter
G = r'C:\Users\bg931\Documents\New project\rollback-replica\gen'
im = Image.open(os.path.join(G, 'chain-cluster.png')).convert('RGBA')
a = np.asarray(im).astype(np.float32)
al = a[..., 3]
print('size', im.size, 'alpha hist', np.histogram(al, bins=[0, 1, 30, 80, 140, 200, 250, 256])[0])
rgb = a[..., :3]
lum = rgb.mean(-1)
sat = rgb.max(-1) - rgb.min(-1)
# opaque object pixels: fully opaque in the source; the glow is the semi-transparent fringe
thr = float(sys.argv[1]) if len(sys.argv) > 1 else 235.0
m = al >= thr
m_img = Image.fromarray((m * 255).astype(np.uint8))
# remove 1px speckles, close tiny gaps
m_img = m_img.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
m2 = np.asarray(m_img) > 127
out = a.copy()
out[..., 3] = np.where(m2, 255, 0)
res = Image.fromarray(out.astype(np.uint8), 'RGBA')
res.save(os.path.join(G, 'chain-cluster_cut.png'))
# preview on a mid-gray checker
W, H = im.size
bg = Image.new('RGBA', (W, H), (120, 120, 120, 255))
yy, xx = np.mgrid[0:H, 0:W]
chk = (((xx // 32) + (yy // 32)) % 2 == 0)
b = np.asarray(bg).copy(); b[chk] = (150, 150, 150, 255)
bg = Image.fromarray(b, 'RGBA')
bg.alpha_composite(res)
bg.convert('RGB').save('sheets/cluster_cut_preview.jpg', quality=90)
print('saved')
