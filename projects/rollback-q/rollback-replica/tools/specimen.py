"""Type specimen sheets: crops of every text element (panorama world coords or video frame coords), zoomed."""
import sys
from PIL import Image, ImageDraw, ImageFont
PANO = Image.open('pano/pano.png').convert('RGB')
def fr(f): return Image.open(f'frames_full/f_{f:04d}.jpg').convert('RGB')
font = ImageFont.truetype('arial.ttf', 15)
# (id, source, box, zoom)   source: 'p' pano | int frame
S = [
 ('01 Farewell', 'p', (425, 0, 560, 140), 2.5), ('02 4月26日', 'p', (380, 190, 455, 212), 5), ('03 2026', 'p', (622, 444, 690, 470), 5),
 ('04 2030', 'p', (1038, 546, 1102, 574), 5), ('05 code', 'p', (1150, 0, 1480, 175), 2.2), ('06 (WELL-3)', 'p', (1318, 230, 1425, 258), 5),
 ('07 jp line', 'p', (1138, 294, 1475, 314), 3.2), ('08 (SLEEP-2)', 'p', (1532, 320, 1652, 348), 5), ('09 (CANT-1)', 'p', (1318, 422, 1425, 446), 5),
 ('10 thumb labels', 'p', (1560, 492, 1722, 532), 4), ('11 spaced EN', 'p', (1125, 700, 1385, 760), 3.5), ('12 dotnet build', 'p', (1822, 394, 2215, 426), 3.5),
 ('13 Z tile', 'p', (1788, 333, 1850, 400), 4), ('14 Re tile', 'p', (1710, 383, 1756, 420), 5), ('15 CE tile', 'p', (2146, 502, 2222, 552), 4),
 ('16 2050', 'p', (2306, 548, 2374, 576), 5), ('17 Are yo', 'p', (2696, 192, 2750, 222), 5), ('18 words band', 'p', (1930, 478, 2300, 536), 3.2),
 ('19 one/[*]', 'p', (2750, 160, 3050, 255), 2.5), ('20 [5921]', 'p', (3335, 345, 3395, 367), 5), ('21 2/00 22C', 'p', (3466, 546, 3566, 592), 5),
 ('22 ASCII tree', 'p', (3462, 622, 3682, 800), 3), ('23 [cloud1]', 'p', (4722, 508, 4780, 528), 6), ('24 [記憶]', 'p', (5050, 562, 5150, 594), 5),
 ('25 dictionary', 'p', (4572, 596, 5210, 700), 2.2), ('26 Definete memory', 'p', (4716, 850, 4956, 884), 4), ('27 (1)', 'p', (5282, 478, 5336, 514), 5),
 ('28 arc text', 'p', (4486, 846, 4690, 1004), 2.6), ('29 counter UI', 'p', (5072, 560, 5460, 645), 2.6),
]
S2 = [
 ('30 (2)', 'p', (5530, 130, 5615, 175), 4), ('31 crash dialog', 'p', (5612, 188, 5848, 352), 2.6), ('32 (crash)', 'p', (5826, 212, 5884, 242), 5),
 ('33 (elevator)', 'p', (5930, 356, 6056, 404), 4), ('34 (4)', 'p', (6250, 490, 6316, 540), 4), ('35 (3)', 'p', (5915, 840, 5995, 920), 3),
 ('36 METAL', 'p', (6305, 660, 6425, 704), 4), ('37 4320', 'p', (6800, 310, 6866, 344), 5), ('38 red text on line', 'p', (6650, 190, 6890, 330), 3),
 ('39 time cannot..', 'p', (6722, 574, 6848, 614), 4.5), ('40 AE keyframe data', 'p', (6296, 745, 6486, 990), 2.6), ('41 table', 'p', (5668, 776, 5956, 852), 3.2),
 ('42 将来の交差点', 'p', (7090, 482, 7180, 506), 5), ('43 EBX', 'p', (6985, 110, 7100, 170), 3), ('44 KODAK', 'p', (7715, 110, 7895, 170), 2.6),
 ('45 KODAK EPP 6005', 'p', (7555, 228, 7715, 256), 4), ('46 FUJI RVP vert', 'p', (6945, 230, 6990, 400), 2.8), ('47 KODAK PORTRA 400', 'p', (7230, 352, 7360, 376), 5),
 ('48 2A arrow', 'p', (7000, 910, 7115, 970), 3), ('49 RVP > 2', 'p', (7505, 536, 7545, 676), 3), ('50 FUJI RVP horiz', 'p', (9175, 80, 9325, 114), 4),
 ('51 CAFAAI-BEFB', 'p', (9500, 86, 9630, 114), 4), ('52 Rollback', 'p', (10030, 50, 10790, 160), 1.6), ('53 word columns', 'p', (10105, 276, 10795, 372), 2.2),
 ('54 Pull', 'p', (10712, 592, 10802, 628), 5), ('55 ROLBACK mirrored', 'p', (10694, 630, 10802, 664), 5), ('56 mirrored code', 'p', (10028, 728, 10420, 850), 2.6),
 ('57 PROGRESS REPORT', 'p', (10300, 660, 10380, 684), 6), ('58 small para', 'p', (9862, 636, 9940, 732), 4),
]
S3 = [
 ('60 f0 开始', 0, (860, 110, 1440, 210), 2.2), ('61 f1 START+开始', 1, (250, 100, 760, 185), 2.6), ('62 f7 set 1', 7, (900, 580, 1050, 640), 5),
 ('63 f9 2025', 9, (560, 725, 660, 770), 6), ('64 f84 text bar', 84, (150, 235, 1240, 365), 1.6), ('65 f86 Waiting', 86, (1140, 880, 1560, 990), 3),
 ('66 f99 (connect)', 99, (820, 560, 1120, 680), 3.4), ('67 f206 digits', 206, (0, 250, 1920, 830), 0.95), ('68 f230 Forward', 230, (1150, 0, 1920, 130), 2.2),
 ('69 f238 flip', 238, (1150, 0, 1920, 130), 2.2), ('70 f240 flip', 240, (1250, 0, 1920, 130), 2.4), ('71 f241 flip', 241, (1250, 0, 1920, 130), 2.4),
 ('72 f224 digits', 224, (1150, 200, 1920, 480), 2.0),
]
def build(spec, out, W=1900, HMAX=1260):
    tiles = []
    for (lab, src, box, z) in spec:
        im = (PANO if src == 'p' else fr(src)).crop(box)
        im = im.resize((max(1, int(im.width * z)), max(1, int(im.height * z))), Image.LANCZOS)
        t = Image.new('RGB', (max(im.width, 150) + 8, im.height + 26), (30, 30, 60))
        t.paste(im, (4, 22)); ImageDraw.Draw(t).text((4, 2), lab, fill=(255, 230, 0), font=font)
        tiles.append(t)
    pages = []; cur = []; x = y = 0; rowh = 0
    for t in tiles:
        if x + t.width > W:
            x = 0; y += rowh + 4; rowh = 0
        if y + t.height > HMAX and cur:
            pages.append(cur); cur = []; x = y = 0; rowh = 0
        cur.append((t, (x, y))); x += t.width + 4; rowh = max(rowh, t.height)
    if cur: pages.append(cur)
    for i, pg in enumerate(pages):
        h = max(p[1] + t.height for t, p in pg)
        sheet = Image.new('RGB', (W, h), (30, 30, 60))
        for t, p in pg: sheet.paste(t, p)
        fn = out.replace('.jpg', '_%d.jpg' % i)
        sheet.save(fn, quality=92); print(fn, sheet.size)
build(S, 'sheets/type_a.jpg'); build(S2, 'sheets/type_b.jpg'); build(S3, 'sheets/type_c.jpg')
