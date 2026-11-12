"""reference crops (upscaled) of the source frames for the second batch of GPT redraws"""
import os
from PIL import Image
OUT = r'C:\Users\bg931\Documents\New project\rollback-replica\gen\ref'
JOBS = [
    ('bld_f46.png', 46, (470, 320, 1353, 667), 2.0),
    ('bld_f42.png', 42, (602, 320, 1484, 667), 2.0),
    ('cluster_f118.png', 118, (675, 268, 1415, 572), 2.5),
    ('cluster_f110.png', 110, (675, 268, 1260, 572), 2.5),
    ('sunset_f36.png', 36, (0, 0, 1920, 1080), 1.0),
    ('sunset_f46.png', 46, (130, 465, 450, 775), 3.0),
]
for name, f, box, sc in JOBS:
    im = Image.open('frames_full/f_%04d.jpg' % f).convert('RGB').crop(box)
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    im.save(os.path.join(OUT, name))
    print(name, im.size)
