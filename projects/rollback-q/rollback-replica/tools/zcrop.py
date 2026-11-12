"""python tools/zcrop.py OUT X0 Y0 X1 Y1 SCALE [GRID]  -> gridded crop of the reference panorama"""
import sys
from PIL import Image, ImageDraw
out=sys.argv[1]; x0,y0,x1,y1=[int(v) for v in sys.argv[2:6]]; sc=float(sys.argv[6]); grid=int(sys.argv[7]) if len(sys.argv)>7 else 100
p=Image.open('pano/pano.png')
im=p.crop((x0,y0,x1,y1)).resize((int((x1-x0)*sc),int((y1-y0)*sc)),Image.LANCZOS)
d=ImageDraw.Draw(im)
gx=(x0//grid+1)*grid
while gx<x1:
    X=(gx-x0)*sc; d.line([X,0,X,im.height],fill=(0,190,0),width=1); d.text((X+2,2),str(gx),fill=(0,120,0)); gx+=grid
gy=(y0//grid+1)*grid
while gy<y1:
    Y=(gy-y0)*sc; d.line([0,Y,im.width,Y],fill=(0,190,0),width=1); d.text((2,Y+2),str(gy),fill=(0,120,0)); gy+=grid
im.save(out,quality=90); print(out,im.size)
