import sys, numpy as np
from PIL import Image
def L(f): return np.asarray(Image.open(f'frames_full/f_{f:04d}.jpg').convert('RGB')).astype(np.float32)
for ft, fa, fb in ((165,164,166),(96,95,97)):
    t=L(ft); a=L(fa); b=L(fb)
    m=(t.mean(-1)>128)
    print('frame',ft,'white frac',m.mean())
    # bg colour of neighbour frame = mode
    for nm,n in (('prev',a),('next',b)):
        q=(n//8).astype(np.int32); key=q[...,0]*1024+q[...,1]*32+q[...,2]
        vals,cnt=np.unique(key,return_counts=True); k=vals[cnt.argmax()]
        bg=np.array([k//1024*8+4,(k//32)%32*8+4,k%32*8+4],np.float32)
        d=np.abs(n-bg).max(-1)
        lum=n@np.array([0.299,0.587,0.114],np.float32)
        print(' ',nm,'bg',bg)
        for lo,hi in ((0,6),(6,12),(12,20),(20,30),(30,45),(45,70),(70,110),(110,256)):
            s=(d>=lo)&(d<hi)
            print('   diff %3d-%3d: n=%8d white=%.2f'%(lo,hi,s.sum(),m[s].mean() if s.sum() else -1))
        for lo,hi in ((0,40),(40,80),(80,120),(120,160),(160,200),(200,225),(225,240),(240,256)):
            s=(lum>=lo)&(lum<hi)
            print('   lum  %3d-%3d: n=%8d white=%.2f'%(lo,hi,s.sum(),m[s].mean() if s.sum() else -1))
