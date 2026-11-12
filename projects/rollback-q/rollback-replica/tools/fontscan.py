import os, sys, json
from PIL import ImageFont
dirs=[r'C:\Windows\Fonts', os.path.expanduser(r'~\AppData\Local\Microsoft\Windows\Fonts')]
out=[]
for d in dirs:
    if not os.path.isdir(d): continue
    for fn in sorted(os.listdir(d)):
        if not fn.lower().endswith(('.ttf','.otf','.ttc')): continue
        p=os.path.join(d,fn)
        try:
            f=ImageFont.truetype(p,20)
            out.append((fn, f.getname()[0], f.getname()[1], d))
        except Exception as e:
            pass
json.dump(out,open('fonts.json','w',encoding='utf-8'),ensure_ascii=False)
print(len(out),'fonts')
