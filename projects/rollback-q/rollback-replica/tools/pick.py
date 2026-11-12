"""python tools/pick.py OUT COLS CELLW f1 f2 ...  (grid lines every 200px in frame coords)"""
import sys
from PIL import Image, ImageDraw, ImageFont
out=sys.argv[1]; cols=int(sys.argv[2]); cw=int(sys.argv[3]); fs=[int(x) for x in sys.argv[4:]]
ch=cw*9//16; rows=(len(fs)+cols-1)//cols
sheet=Image.new('RGB',(cols*cw,rows*ch),(40,40,40))
try: font=ImageFont.truetype('arial.ttf',15)
except: font=ImageFont.load_default()
for i,f in enumerate(fs):
    im=Image.open(f'frames_full/f_{f:04d}.jpg').convert('RGB').resize((cw,ch),Image.LANCZOS)
    d=ImageDraw.Draw(im)
    sc=cw/1920
    for gx in range(200,1920,200):
        d.line([gx*sc,0,gx*sc,6],fill=(0,160,0)); d.line([gx*sc,ch-6,gx*sc,ch],fill=(0,160,0))
        d.text((gx*sc+2,ch-18),str(gx),fill=(0,130,0),font=font)
    for gy in range(200,1080,200):
        d.line([0,gy*sc,6,gy*sc],fill=(0,160,0)); d.text((8,gy*sc-8),str(gy),fill=(0,130,0),font=font)
    d.rectangle([0,0,70,20],fill=(0,0,0)); d.text((4,2),f'f{f}',fill=(255,255,0),font=font)
    sheet.paste(im,((i%cols)*cw,(i//cols)*ch))
sheet.save(out,quality=90); print(out,sheet.size)
