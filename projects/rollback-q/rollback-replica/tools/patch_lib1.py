p = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts\lib.py'
s = open(p, encoding='utf-8').read()

canvas = '''
# ----------------------------------------------------------------------------- world-space canvas
class Canvas:
    """Draw in world coordinates; internal buffer is supersampled (k*ss px per world px)."""

    def __init__(self, x0, y0, x1, y1, k=2, ss=3):
        self.x0, self.y0, self.x1, self.y1 = float(x0), float(y0), float(x1), float(y1)
        self.k, self.ss = k, ss
        self.f = k * ss
        self.w = max(1, int(math.ceil((x1 - x0) * self.f)))
        self.h = max(1, int(math.ceil((y1 - y0) * self.f)))
        self.im = Image.new('RGBA', (self.w, self.h), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def P(self, x, y):
        return ((x - self.x0) * self.f, (y - self.y0) * self.f)

    def pts(self, pts):
        return [self.P(x, y) for (x, y) in pts]

    def poly(self, pts, fill=None, outline=None, width=1.0):
        self.d.polygon(self.pts(pts), fill=fill)
        if outline:
            self.line(list(pts) + [pts[0]], outline, width)
        return self

    def line(self, pts, fill=(0, 0, 0, 255), width=1.0, joint='curve'):
        self.d.line(self.pts(pts), fill=fill, width=max(1, int(round(width * self.f))), joint=joint)
        return self

    def dashed(self, a, b, fill=(0, 0, 0, 255), width=1.0, dash=6.0, gap=4.0):
        ax, ay = a
        bx, by = b
        L = math.hypot(bx - ax, by - ay)
        if L < 1e-6:
            return self
        ux, uy = (bx - ax) / L, (by - ay) / L
        t = 0.0
        while t < L:
            e = min(t + dash, L)
            self.line([(ax + ux * t, ay + uy * t), (ax + ux * e, ay + uy * e)], fill, width)
            t += dash + gap
        return self

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=1.0):
        p0, p1 = self.P(x0, y0), self.P(x1, y1)
        self.d.rectangle([p0[0], p0[1], p1[0] - 1, p1[1] - 1], fill=fill, outline=outline,
                         width=max(1, int(round(width * self.f))) if outline else 0)
        return self

    def rrect(self, x0, y0, x1, y1, r, fill=None, outline=None, width=1.0):
        p0, p1 = self.P(x0, y0), self.P(x1, y1)
        self.d.rounded_rectangle([p0[0], p0[1], p1[0] - 1, p1[1] - 1], radius=r * self.f, fill=fill, outline=outline,
                                 width=max(1, int(round(width * self.f))) if outline else 0)
        return self

    def circle(self, cx, cy, r, fill=None, outline=None, width=1.0):
        p0, p1 = self.P(cx - r, cy - r), self.P(cx + r, cy + r)
        self.d.ellipse([p0[0], p0[1], p1[0], p1[1]], fill=fill, outline=outline,
                       width=max(1, int(round(width * self.f))) if outline else 0)
        return self

    def ellipse(self, x0, y0, x1, y1, fill=None, outline=None, width=1.0):
        p0, p1 = self.P(x0, y0), self.P(x1, y1)
        self.d.ellipse([p0[0], p0[1], p1[0], p1[1]], fill=fill, outline=outline,
                       width=max(1, int(round(width * self.f))) if outline else 0)
        return self

    def arc(self, cx, cy, r, a0, a1, fill=(0, 0, 0, 255), width=1.0):
        """a0..a1 in degrees, CCW from +x (screen up positive)"""
        p0, p1 = self.P(cx - r, cy - r), self.P(cx + r, cy + r)
        self.d.arc([p0[0], p0[1], p1[0], p1[1]], start=-a1, end=-a0, fill=fill, width=max(1, int(round(width * self.f))))
        return self

    def pie(self, cx, cy, r, a0, a1, fill=None):
        p0, p1 = self.P(cx - r, cy - r), self.P(cx + r, cy + r)
        self.d.pieslice([p0[0], p0[1], p1[0], p1[1]], start=-a1, end=-a0, fill=fill)
        return self

    def text(self, x, y, s, fname='arial.ttf', size=12, fill=(0, 0, 0, 255), anchor='la', tracking=0.0, rot=0.0, sx=1.0):
        """size/tracking in world px; anchor: l/m/r + a(top)/m/d(bottom); rot degrees CCW; sx = horizontal stretch"""
        fnt = font(fname, size * self.f)
        im = text_img(s, fnt, fill, pad=2, tracking=tracking * self.f)
        if sx != 1.0:
            im = im.resize((max(1, int(im.width * sx)), im.height), Image.LANCZOS)
        if rot:
            im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
        px, py = self.P(x, y)
        ax = {'l': 0, 'm': im.width / 2, 'r': im.width}[anchor[0]]
        ay = {'a': 0, 'm': im.height / 2, 'd': im.height}[anchor[1]]
        self.paste(im, px - ax, py - ay)
        return self

    def paste(self, im, px, py):
        """alpha-composite an RGBA image at buffer pixel (px, py) (may be partly outside)"""
        px, py = int(round(px)), int(round(py))
        x0, y0 = max(px, 0), max(py, 0)
        x1, y1 = min(px + im.width, self.w), min(py + im.height, self.h)
        if x1 <= x0 or y1 <= y0:
            return self
        sub = im.crop((x0 - px, y0 - py, x1 - px, y1 - py))
        self.im.alpha_composite(sub, (x0, y0))
        self.d = ImageDraw.Draw(self.im)
        return self

    def image(self, im, x, y, w=None, h=None):
        """place an RGBA image with its top-left at world (x, y), scaled to world width w (/height h)"""
        if w is None and h is None:
            w = im.width / self.k
        if h is None:
            h = w * im.height / im.width
        if w is None:
            w = h * im.width / im.height
        im2 = im.resize((max(1, int(round(w * self.f))), max(1, int(round(h * self.f)))), Image.LANCZOS)
        px, py = self.P(x, y)
        return self.paste(im2, px, py)

    def done(self):
        w, h = max(1, self.w // self.ss), max(1, self.h // self.ss)
        return self.im.resize((w, h), Image.LANCZOS) if self.ss > 1 else self.im


def crop_alpha(img, pad=2):
    bb = img.getbbox()
    if not bb:
        return img.crop((0, 0, 1, 1)), (0, 0)
    x0, y0 = max(bb[0] - pad, 0), max(bb[1] - pad, 0)
    x1, y1 = min(bb[2] + pad, img.width), min(bb[3] + pad, img.height)
    return img.crop((x0, y0, x1, y1)), (x0, y0)

'''
marker = "# ----------------------------------------------------------------------------- scene model"
assert marker in s
s = s.replace(marker, canvas + "\n" + marker)

a0 = s.index("    def asset(self, name, fn, *args, **kw):")
a1 = s.index("    def add(self, name, fn, x, y, *args")
new_asset = '''    def asset(self, name, fn, *args, crop=True, **kw):
        """build (or reuse cached) PNG for `name`; returns dict(path, size, off, origin, k)"""
        path = os.path.join(ASSETS, name + '.png')
        try:
            src = inspect.getsource(fn)
        except Exception:
            src = repr(fn)
        hsh = hashlib.md5((src + repr(args) + repr(sorted(kw.items())) + repr(crop) + LIBV).encode('utf-8')).hexdigest()
        ent = self.cache.get(name)
        if ent and ent.get('hash') == hsh and os.path.exists(path):
            ent = dict(ent)
            ent['path'] = path
            return ent
        res = fn(*args, **kw)
        origin, k = None, None
        if isinstance(res, Canvas):
            origin, k = [res.x0, res.y0], res.k
            img = res.done()
        else:
            img = res
        off = (0, 0)
        if crop:
            img, off = crop_alpha(img)
        img.save(path)
        ent = {'hash': hsh, 'size': list(img.size), 'off': list(off), 'origin': origin, 'k': k}
        self.cache[name] = ent
        json.dump(self.cache, open(self.cache_path, 'w'))
        ent = dict(ent)
        ent['path'] = path
        return ent

'''
s = s[:a0] + new_asset + s[a1:]

b0 = s.index("    def add(self, name, fn, x, y, *args")
b1 = s.index("    def solid(self, name, color")
new_add = '''    def add(self, name, fn, x, y, *args, k=None, pivot=None, sec=None, screen=False, crop=True, **kw):
        """add an image layer; (x, y) = world position of the image's top-left (before auto-crop)."""
        k = k or self.kdef
        ent = self.asset(name, fn, *args, crop=crop, **kw)
        x, y = x + ent['off'][0] / k, y + ent['off'][1] / k
        L = Layer(self, name, tuple(ent['size']), k, x, y, pivot=pivot, sec=sec or self.sec, screen=screen)
        L.file = ent['path']
        self.layers.append(L)
        return L

    def addc(self, name, fn, *args, pivot=None, sec=None, screen=False, crop=True, **kw):
        """add a layer drawn on a world-space Canvas (fn returns the Canvas)."""
        ent = self.asset(name, fn, *args, crop=crop, **kw)
        k = ent['k']
        x, y = ent['origin'][0] + ent['off'][0] / k, ent['origin'][1] + ent['off'][1] / k
        L = Layer(self, name, tuple(ent['size']), k, x, y, pivot=pivot, sec=sec or self.sec, screen=screen)
        L.file = ent['path']
        self.layers.append(L)
        return L

'''
s = s[:b0] + new_add + s[b1:]
s = s.replace("W, H = 1920, 1080\n", "W, H = 1920, 1080\nLIBV = 'v1'\n", 1)
open(p, 'w', encoding='utf-8').write(s)

pb = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts\base.py'
b = open(pb, encoding='utf-8').read()
b = b.replace("ruler_tile, x0, RULER_Y - 15, x0, x0 + tile, k=4)", "ruler_tile, x0, RULER_Y - 15, x0, x0 + tile, k=4, crop=False)")
open(pb, 'w', encoding='utf-8').write(b)
print('patched', len(s))
