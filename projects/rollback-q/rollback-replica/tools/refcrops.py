"""cut reference crops of the original for the image generator (saved into the project's gen/ref folder)"""
import os
from PIL import Image
REF = 'C:/Users/bg931/Documents/New project/rollback-replica/gen/ref'
os.makedirs(REF, exist_ok=True)


def crop(f, box, name, up=2):
    im = Image.open('frames_full/f_%04d.jpg' % f).convert('RGB').crop(box)
    im = im.resize((im.width * up, im.height * up), Image.LANCZOS)
    im.save(os.path.join(REF, name + '.png'))
    print(name, im.size)


crop(50, (600, 520, 1560, 900), 'tube_f50')
crop(46, (640, 540, 1420, 880), 'tube_f46')
crop(207, (60, 240, 330, 840), 'chibi_f207')
crop(213, (60, 240, 640, 840), 'chibi_f213', 1)
crop(118, (640, 290, 1300, 520), 'chain_f118')
crop(150, (1040, 40, 1900, 580), 'city_f150', 1)
crop(160, (900, 0, 1900, 600), 'city_f160', 1)
p = Image.open('pano/pano.png').convert('RGB')
p.crop((3860, 230, 4330, 540)).resize((940, 620), Image.LANCZOS).save(os.path.join(REF, 'chain_pano.png'))
p.crop((5720, 0, 6680, 620)).save(os.path.join(REF, 'city_pano.png'))
ims = [Image.open(os.path.join(REF, n + '.png')) for n in ('tube_f50', 'chain_f118', 'chibi_f207', 'city_f150')]
tiles = []
for i in ims:
    j = i.copy()
    j.thumbnail((640, 520))
    tiles.append(j)
sheet = Image.new('RGB', (sum(t.width for t in tiles), 520), (40, 40, 40))
x = 0
for t in tiles:
    sheet.paste(t, (x, 0))
    x += t.width
sheet.save('sheets/ref_crops.jpg', quality=85)
print(sheet.size)
