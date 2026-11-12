"""python tools/wmask.py OUT THR f1 f2 ... : near-white mask (min channel > THR) small multiples with 100px grid"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
out=sys.argv[1]; thr=int(sys.argv[2]); fs=[int(x) for x in sys.argv[3:]]
cols=3; cw=640; ch=360; rows=(len(fs)+cols-1)//cols
font=ImageFont.truetype('arial.ttf',12)
sheet=Image.new('RGB',(cols*cw,rows*ch),(255,0,80))
for i,f in enumerate(fs):
    a=np.asarray(Image.open(f'frames_full/f_{f:04d}.jpg').convert('RGB')).astype(int)
    m=(a.min(-1)>thr)
    im=Image.fromarray((m*255).astype(np.uint8)).resize((cw,ch),Image.BILINEAR).convert('RGB')
    d=ImageDraw.Draw(im); sc=cw/1920
    for gx in range(100,1920,100):
        d.line([gx*sc,0,gx*sc,ch],fill=(0,90,0) if gx%500 else (0,200,0))
    for gy in range(100,1080,100):
        d.line([0,gy*sc,cw,gy*sc],fill=(0,90,0) if gy%500 else (0,200,0))
    d.text((3,1),f'f{f}',fill=(255,255,0),font=font)
    sheet.paste(im,((i%cols)*cw,(i//cols)*ch))
sheet.save(out,quality=90); print(out,sheet.size)
