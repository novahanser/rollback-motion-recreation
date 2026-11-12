import json, numpy as np
from PIL import Image
cam={d['f']:d for d in json.load(open(r'C:\Users\bg931\Documents\New project\rollback-replica\scripts\cam.json'))}
def L(f):
    return np.asarray(Image.open(f'frames_full/f_{f:04d}.jpg').convert('L').resize((960,540),Image.BILINEAR)).astype(np.float32)
def edges(a):
    gx=np.abs(np.diff(a,axis=1))[:-1,:]; gy=np.abs(np.diff(a,axis=0))[:,:-1]
    return gx+gy
ref=256
A=edges(L(ref))
# template: film portrait frame region (half-res coords)
tx0,ty0,tx1,ty1=230,150,480,400
T=A[ty0:ty1,tx0:tx1]; T=T-T.mean()
prev=(0,0)
for f in range(250,270):
    B=edges(L(f))
    best=None
    for dy in range(-12,13,2):
        for dx in range(-420,200,2):
            x0=tx0+dx; y0=ty0+dy
            if x0<0 or y0<0 or x0+T.shape[1]>B.shape[1] or y0+T.shape[0]>B.shape[0]: continue
            P=B[y0:y0+T.shape[0],x0:x0+T.shape[1]]
            sc=float((T*(P-P.mean())).sum()/ (np.linalg.norm(T)*np.linalg.norm(P-P.mean())+1e-6))
            if best is None or sc>best[0]: best=(sc,dx,dy)
    sc,dx,dy=best
    s=cam[f]['s']
    # template centre world x at ref
    cxr=cam[ref]['cx']; sr=cam[ref]['s']
    xc=(tx0+tx1)   # full-res centre x of template at ref (half-res*2 /2 *2)
    wx=(xc-960)/sr+cxr
    xs=(tx0+tx1)+2*dx
    cx_new=wx-(xs-960)/s
    print(f'f{f} score={sc:.3f} dx={2*dx:5d}px dy={2*dy:4d}px  cam.cx={cam[f]["cx"]:.1f} -> measured cx={cx_new:.1f}')
