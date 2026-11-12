import numpy as np
from PIL import Image
a=np.asarray(Image.open('pano/pano.png').convert('L')).astype(float)
# tick x positions from band rows 534..537 & 542..545 in clean stretches: detect dark runs
band=(a[534:538].mean(axis=0)+a[542:546].mean(axis=0))/2
def ticks(x0,x1,thr=110):
    xs=[];inrun=False
    for x in range(x0,x1):
        dk=band[x]<thr
        if dk and not inrun: st=x;inrun=True
        if not dk and inrun:
            inrun=False
            seg=band[st:x]; w=(thr-seg).clip(0); xs.append((np.arange(st,x)*w).sum()/w.sum())
    return np.array(xs)
for (x0,x1) in ((100,230),(2760,2900),(3260,3640),(5560,5700),(9950,10110),(10500,10990)):
    t=ticks(x0,x1)
    if len(t)>3:
        d=np.diff(t)
        k=np.arange(len(t))
        A=np.vstack([k,np.ones(len(k))]).T
        slope,inter=np.linalg.lstsq(A,t,rcond=None)[0]
        print(x0,x1,'n',len(t),'median d',np.median(d).round(3),'fit period',slope.round(4),'phase',inter.round(2), 'resid',np.abs(t-(slope*k+inter)).max().round(2))
# global fit: assume ticks at x = x_first + k*P for integer k; fit P using far-apart stretches
t1=ticks(3260,3640); t2=ticks(9950,10110); t3=ticks(100,230)
for P in (7.32,7.3243,7.33,7.3333,7.34,7.35):
    def ph(t): return np.angle(np.exp(2j*np.pi*t/P).mean())/(2*np.pi)*P
    print(P, round(ph(t1),3), round(ph(t2),3), round(ph(t3),3))
