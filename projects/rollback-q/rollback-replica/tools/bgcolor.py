import numpy as np, json
from PIL import Image
out=[]
prev=None
for f in range(272):
    a=np.asarray(Image.open(f'frames_s/f_{f+1:04d}.jpg').convert('RGB').resize((240,135)))
    q=(a//8).astype(np.int32)
    key=q[...,0]*1024+q[...,1]*32+q[...,2]
    vals,counts=np.unique(key,return_counts=True)
    order=np.argsort(counts)[::-1]
    tops=[]
    for i in order[:2]:
        v=vals[i]; m=key==v
        col=a[m].mean(axis=0).round().astype(int)
        tops.append((tuple(int(c) for c in col), round(counts[i]/key.size,2)))
    out.append(tops)
    s=f"{f:3d} " + '  '.join(f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}:{p:.2f}" for c,p in tops)
    print(s)
json.dump(out,open('bgcolor.json','w'))
