import json, numpy as np, colorsys
from PIL import Image
cam={d['f']:d for d in json.load(open(r'C:\Users\bg931\Documents\New project\rollback-replica\scripts\cam.json'))}
def runs(mask, minlen=6):
    out=[]; x=0; n=len(mask)
    while x<n:
        if mask[x]:
            x0=x
            while x<n and mask[x]: x+=1
            if x-x0>=minlen: out.append((x0,x-1))
        else: x+=1
    return out
for f in range(14,31):
    c=cam[f]; s=c['s']; cx=c['cx']
    a=np.asarray(Image.open(f'frames_full/f_{f:04d}.jpg').convert('RGB')).astype(np.float32)/255
    def row(wy):
        ys=int(round((wy-540)*s+540)); return a[max(ys-2,0):ys+3].mean(0), ys
    def W(xs): return round((xs-960)/s+cx,1)
    msg=[f'f{f} s={s:.4f} cx={cx:.1f}']
    for name,wy in (('mag',440),('cyan',488),('cyan2',525)):
        r,ys=row(wy)
        mx=r.max(1); mn=r.min(1); sat=(mx-mn)/np.maximum(mx,1e-3)
        R,G,B=r[:,0],r[:,1],r[:,2]
        if name=='mag':
            m=(sat>0.35)&(R>0.45)&(B>0.45)&(G<0.6*np.maximum(R,B))     # magenta / violet
        else:
            m=(sat>0.2)&(((G>0.7)&(B>0.75)&(R<0.75))|((R>0.7)&(B>0.6)&(G<0.75)&(G>0.45)))   # cyan or pale pink
        rr=runs(m)
        msg.append(f'  {name}@ys{ys}: '+' '.join(f'[{W(x0)}..{W(x1)}]' for x0,x1 in rr))
    print('\n'.join(msg))
