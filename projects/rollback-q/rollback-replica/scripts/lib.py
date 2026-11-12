"""Core helpers for the Rollback replica build.

  * drawing primitives (numpy + PIL, supersampled / analytic anti-aliasing)
  * Scene / Layer: a world-space layer list with keyframe helpers
  * exporters: static panorama preview + After Effects project JSON
"""
import os, json, math, hashlib, inspect
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, 'assets')
GEN = os.path.join(ROOT, 'gen')
FPS = 24
NFRAMES = 272
W, H = 1920, 1080
LIBV = 'v2'

# palette sampled from the reference
BG = (230, 230, 230)
PINK = (240, 18, 110)
PINK2 = (235, 4, 109)
BLUE = (10, 132, 255)
ROYAL = (13, 62, 216)
PERI = (105, 130, 246)
MINT = (25, 230, 180)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YEL = (238, 196, 60)

FONTS = r'C:\Windows\Fonts'
UFONTS = os.path.expanduser(r'~\AppData\Local\Microsoft\Windows\Fonts')


_FONT_INDEX = None


def _font_index():
    global _FONT_INDEX
    if _FONT_INDEX is None:
        p_ = os.path.join(HERE, 'fonts_index.json')
        _FONT_INDEX = json.load(open(p_, encoding='utf-8')) if os.path.exists(p_) else []
    return _FONT_INDEX


def font_path(name):
    """file name ('arial.ttf') or 'Family|Style' looked up in fonts_index.json"""
    if '|' in name:
        fam, style = name.split('|', 1)
        for f in _font_index():
            if f[1].lower() == fam.lower() and f[2].lower() == style.lower():
                return os.path.join(f[3], f[0])
        for f in _font_index():
            if fam.lower() in f[1].lower() and style.lower() in f[2].lower():
                return os.path.join(f[3], f[0])
        return os.path.join(FONTS, 'arial.ttf')
    for base in (FONTS, UFONTS):
        p_ = os.path.join(base, name)
        if os.path.exists(p_):
            return p_
    return os.path.join(FONTS, 'arial.ttf')


def font(name, size):
    return ImageFont.truetype(font_path(name), int(round(size)))


# ----------------------------------------------------------------------------- image helpers
def new(w, h, color=(0, 0, 0, 0)):
    return Image.new('RGBA', (int(round(w)), int(round(h))), color)


def rgba(c, a=255):
    return (int(c[0]), int(c[1]), int(c[2]), int(a))


def from_arr(rgb, alpha):
    """rgb: HxWx3 float(0..255) or tuple colour; alpha: HxW float 0..1"""
    h, w = alpha.shape
    out = np.zeros((h, w, 4), np.uint8)
    if isinstance(rgb, tuple):
        out[..., 0], out[..., 1], out[..., 2] = rgb[0], rgb[1], rgb[2]
    else:
        out[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    out[..., 3] = np.clip(alpha * 255.0 + 0.5, 0, 255).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def grid(w, h):
    y, x = np.mgrid[0:int(h), 0:int(w)].astype(np.float32)
    return x + 0.5, y + 0.5


def cov(sd, aa=1.0):
    """coverage from a signed distance (negative inside)"""
    return np.clip(0.5 - sd / aa, 0.0, 1.0)


def sd_circle(x, y, cx, cy, r):
    return np.hypot(x - cx, y - cy) - r


def sd_ring(x, y, cx, cy, r0, r1):
    d = np.hypot(x - cx, y - cy)
    return np.maximum(r0 - d, d - r1)


def sd_box(x, y, cx, cy, hw, hh, r=0.0):
    dx = np.abs(x - cx) - (hw - r)
    dy = np.abs(y - cy) - (hh - r)
    return np.hypot(np.maximum(dx, 0), np.maximum(dy, 0)) + np.minimum(np.maximum(dx, dy), 0) - r


def sd_segment(x, y, ax, ay, bx, by, hw):
    px, py = x - ax, y - ay
    dx, dy = bx - ax, by - ay
    t = np.clip((px * dx + py * dy) / (dx * dx + dy * dy + 1e-9), 0, 1)
    return np.hypot(px - t * dx, py - t * dy) - hw


def ang(x, y, cx, cy):
    """angle in degrees, 0 = +x (right), counter-clockwise positive (screen up), range [0,360)"""
    return (np.degrees(np.arctan2(-(y - cy), x - cx)) + 360.0) % 360.0


def sector_mask(x, y, cx, cy, a0, a1, aa=1.0):
    """soft mask of the angular wedge from a0 to a1 (degrees CCW, a1 > a0, span < 360)"""
    a = ang(x, y, cx, cy)
    d = np.hypot(x - cx, y - cy)
    span = (a1 - a0) % 360.0 or 360.0
    rel = (a - a0) % 360.0
    # distance in px to the nearest wedge edge
    inside = rel <= span
    e0 = np.minimum(rel, 360.0 - rel)
    e1 = np.minimum(np.abs(rel - span), 360.0 - np.abs(rel - span))
    e = np.minimum(e0, e1)
    dist = np.sin(np.radians(np.minimum(e, 90.0))) * d
    sd = np.where(inside, -dist, dist)
    return cov(sd, aa)


def lerp_color(c0, c1, t):
    t = t[..., None]
    return np.array(c0, np.float32) * (1 - t) + np.array(c1, np.float32) * t


def grad_stops(t, stops):
    """t HxW in 0..1, stops [(pos, (r,g,b)), ...] -> HxWx3"""
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,), np.float32)
    ps = [s[0] for s in stops]
    cs = [np.array(s[1], np.float32) for s in stops]
    for i in range(len(stops) - 1):
        m = (t >= ps[i]) & (t <= ps[i + 1])
        tt = (t - ps[i]) / max(ps[i + 1] - ps[i], 1e-6)
        seg = cs[i] * (1 - tt[..., None]) + cs[i + 1] * tt[..., None]
        out = np.where(m[..., None], seg, out)
    out = np.where((t < ps[0])[..., None], cs[0], out)
    out = np.where((t > ps[-1])[..., None], cs[-1], out)
    return out


def noise(h, w, seed=0, sigma=1.0):
    rng = np.random.default_rng(seed)
    return rng.normal(0, sigma, (int(h), int(w))).astype(np.float32)


def grain(img, amount=8, seed=1):
    a = np.asarray(img).astype(np.float32)
    n = noise(a.shape[0], a.shape[1], seed, amount)
    a[..., :3] = np.clip(a[..., :3] + n[..., None], 0, 255)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def blur(img, r):
    return img.filter(ImageFilter.GaussianBlur(r))


def over(dst, src, xy=(0, 0)):
    """alpha-composite src onto dst at xy (in place, returns dst)"""
    layer = Image.new('RGBA', dst.size, (0, 0, 0, 0))
    layer.paste(src, (int(round(xy[0])), int(round(xy[1]))))
    dst.alpha_composite(layer)
    return dst


def ss_draw(w, h, fn, ss=3):
    """supersampled ImageDraw: fn(draw, scale) -> RGBA at (w,h)"""
    im = Image.new('RGBA', (int(w * ss), int(h * ss)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fn(d, ss)
    return im.resize((int(w), int(h)), Image.LANCZOS)


def text_img(s, fnt, fill=(0, 0, 0, 255), pad=4, tracking=0, stroke=0, stroke_fill=None):
    """render a single line of text tightly cropped (+pad)"""
    if tracking:
        widths = [fnt.getlength(ch) for ch in s]
        tw = int(sum(widths) + tracking * (len(s) - 1)) + 2 * pad + 4
    else:
        tw = int(fnt.getlength(s)) + 2 * pad + 4
    asc, desc = fnt.getmetrics()
    th = asc + desc + 2 * pad
    im = Image.new('RGBA', (max(tw, 1), max(th, 1)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if tracking:
        x = pad
        for ch, wch in zip(s, widths):
            d.text((x, pad), ch, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
            x += wch + tracking
    else:
        d.text((pad, pad), s, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    bb = im.getbbox()
    if bb:
        im = im.crop((max(bb[0] - pad, 0), max(bb[1] - pad, 0), min(bb[2] + pad, im.width), min(bb[3] + pad, im.height)))
    return im


def text_block(lines, fnt, fill=(0, 0, 0, 255), leading=1.25, align='left', pad=4, tracking=0):
    ims = [text_img(l if l else ' ', fnt, fill, pad=0, tracking=tracking) if l.strip() else None for l in lines]
    asc, desc = fnt.getmetrics()
    lh = int((asc + desc) * leading)
    w = max([im.width for im in ims if im] + [1]) + 2 * pad
    out = Image.new('RGBA', (w, lh * len(lines) + 2 * pad), (0, 0, 0, 0))
    for i, im in enumerate(ims):
        if im is None:
            continue
        x = pad if align == 'left' else (w - im.width - pad if align == 'right' else (w - im.width) // 2)
        out.alpha_composite(im, (x, pad + i * lh))
    return out


def rotate(img, deg, expand=True):
    return img.rotate(deg, resample=Image.BICUBIC, expand=expand)


def scale_img(img, sx, sy=None):
    sy = sx if sy is None else sy
    return img.resize((max(1, int(round(img.width * sx))), max(1, int(round(img.height * sy)))), Image.LANCZOS)


def tint_alpha(img, color):
    """keep alpha, replace colour"""
    a = np.asarray(img).copy()
    a[..., 0], a[..., 1], a[..., 2] = color[0], color[1], color[2]
    return Image.fromarray(a, 'RGBA')


def key_white(img, lo=40, hi=235):
    """dark-on-white art -> alpha from darkness (keeps colour as black-ish original)"""
    a = np.asarray(img.convert('RGB')).astype(np.float32)
    lum = a.mean(axis=2)
    alpha = np.clip((hi - lum) / max(hi - lo, 1), 0, 1)
    out = np.zeros(a.shape[:2] + (4,), np.uint8)
    out[..., :3] = np.clip(a * 0.0 + (a - (1 - alpha[..., None]) * 255.0) / np.maximum(alpha[..., None], 1e-3), 0, 255)
    out[..., 3] = (alpha * 255).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def load(path):
    return Image.open(path).convert('RGBA')



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


# ----------------------------------------------------------------------------- scene model
LIN, HOLD, BEZ = 'linear', 'hold', 'bezier'


class Layer:
    def __init__(self, scene, name, img_size, k, x, y, pivot=None, sec='A', screen=False, kind='footage'):
        self.scene = scene
        self.name = name
        self.k = k
        self.size = img_size                      # asset px
        self.x, self.y = x, y                     # world top-left
        self.ww, self.wh = img_size[0] / k, img_size[1] / k
        # pivot in world coords (default centre)
        self.pivot = pivot if pivot is not None else (x + self.ww / 2, y + self.wh / 2)
        self.sec = sec
        self.screen = screen
        self.kind = kind                          # footage | solid | adjust
        self.file = None
        self.color = None
        self.t_in = 0
        self.t_out = NFRAMES
        self.keys = {}                            # prop -> [(frame, value, interp)]
        self.static = {'rotation': 0.0, 'opacity': 100.0, 'scale': [100.0, 100.0]}
        self.effects = []                         # [{match, props:{matchName: value|keys}}]
        self.blend = 'normal'
        self.label = 0
        self.pano = True                          # include in the static panorama preview
        self.below = False                        # screen layer that must sit under the world layer

    # --- timing
    def span(self, f_in, f_out=None):
        self.t_in = f_in
        if f_out is not None:
            self.t_out = f_out
        return self

    def at(self, f_in, f_out=None):
        return self.span(f_in, f_out)

    # --- raw keys
    def key(self, prop, keys):
        self.keys.setdefault(prop, [])
        self.keys[prop] += [(float(f), v, i) for (f, v, i) in keys]
        self.keys[prop].sort(key=lambda kk: kk[0])
        return self

    def set(self, **kw):
        for k_, v in kw.items():
            if k_ in ('blend', 'label', 'pano'):
                setattr(self, k_, v)
            else:
                self.static[k_] = v
        return self

    # --- animation helpers (frames)
    def pop(self, f, d=3, s0=0.0, over=None, interp=BEZ):
        """scale from s0 to 100% (optionally overshooting)"""
        if self.t_in == 0:
            self.t_in = f
        ks = [(f, [s0 * 100, s0 * 100], interp)]
        if over:
            ks.append((f + d * 0.7, [over * 100, over * 100], interp))
        ks.append((f + d, [100, 100], interp))
        return self.key('scale', ks)

    def grow(self, f, d=3, sx0=1.0, sy0=0.0, interp=BEZ):
        if self.t_in == 0:
            self.t_in = f
        return self.key('scale', [(f, [sx0 * 100, sy0 * 100], interp), (f + d, [100, 100], interp)])

    def fade(self, f, d=3, a0=0.0, a1=100.0):
        if a0 == 0 and self.t_in == 0:
            self.t_in = f
        return self.key('opacity', [(f, a0, LIN), (f + d, a1, LIN)])

    def slide(self, f, d, dx=0.0, dy=0.0, interp=BEZ):
        """arrive from an offset (world px)"""
        if self.t_in == 0:
            self.t_in = f
        px, py = self.pivot
        return self.key('position', [(f, [px + dx, py + dy], interp), (f + d, [px, py], interp)])

    def move(self, keys, interp=LIN):
        """absolute pivot positions: [(frame, x, y)]"""
        return self.key('position', [(f, [x, y], interp) for (f, x, y) in keys])

    def spin(self, f, d, a0, interp=BEZ):
        if self.t_in == 0:
            self.t_in = f
        return self.key('rotation', [(f, a0, interp), (f + d, 0.0, interp)])

    def blink(self, frames, on=100.0, off=0.0):
        """hold-key opacity toggles: frames = [f_on, f_off, f_on, ...]"""
        ks = []
        v = on
        for f in frames:
            ks.append((f, v, HOLD))
            v = off if v == on else on
        return self.key('opacity', ks)

    def flash(self, f, color, n=2):
        """solid-colour silhouette for the first n frames (Tint effect: both map colours = colour, amount 100 -> 0)"""
        return self.flashes([(f, color), (f + n, None)])

    def flashes(self, steps):
        """steps: [(frame, colour or None)] sequence of silhouette colours; None = the real texture"""
        self.t_in = steps[0][0] if self.t_in == 0 else min(self.t_in, steps[0][0])
        col_keys, amt_keys = [], []
        for f, c in steps:
            if c is None:
                amt_keys.append((f, 0.0, HOLD))
            else:
                amt_keys.append((f, 100.0, HOLD))
                col_keys.append((f, [c[0] / 255.0, c[1] / 255.0, c[2] / 255.0, 1.0], HOLD))
        props = {'ADBE Tint-0003': amt_keys}
        if len(col_keys) == 1:
            props['ADBE Tint-0001'] = col_keys[0][1]
            props['ADBE Tint-0002'] = col_keys[0][1]
        elif col_keys:
            props['ADBE Tint-0001'] = col_keys
            props['ADBE Tint-0002'] = list(col_keys)
        self.effects.append({'match': 'ADBE Tint', 'props': props})
        return self

    def wipe(self, f, d, angle=90.0, feather=0.0, interp=LIN, reverse=False):
        """linear wipe reveal; angle = AE wipe angle (90 = reveal left->right ... see AE)"""
        if self.t_in == 0:
            self.t_in = f
        a, b = (0.0, 100.0) if reverse else (100.0, 0.0)
        self.effects.append({'match': 'ADBE Linear Wipe', 'props': {
            'ADBE Linear Wipe-0001': [(f, a, interp), (f + d, b, interp)],
            'ADBE Linear Wipe-0002': angle, 'ADBE Linear Wipe-0003': feather}})
        return self

    def radial(self, f, d, start=0.0, cw=True, center=None, interp=LIN):
        if self.t_in == 0:
            self.t_in = f
        props = {'ADBE Radial Wipe-0001': [(f, 100.0, interp), (f + d, 0.0, interp)],
                 'ADBE Radial Wipe-0002': start, 'ADBE Radial Wipe-0004': 1 if cw else 2}
        if center is not None:
            props['ADBE Radial Wipe-0003'] = [center[0], center[1]]
        self.effects.append({'match': 'ADBE Radial Wipe', 'props': props})
        return self

    def fx(self, match, **props):
        self.effects.append({'match': match, 'props': props})
        return self


class Scene:
    def __init__(self):
        self.layers = []          # bottom -> top
        self.cache_path = os.path.join(ASSETS, '.cache.json')
        self.cache = json.load(open(self.cache_path)) if os.path.exists(self.cache_path) else {}
        self.sec = 'A'
        self.kdef = 2
        self.world_keys = {}      # extra keys for the RB_WORLD layer in RB_MAIN (e.g. opacity)
        os.makedirs(ASSETS, exist_ok=True)

    # --- assets
    def asset(self, name, fn, *args, crop=True, **kw):
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

    def add(self, name, fn, x, y, *args, k=None, pivot=None, sec=None, screen=False, crop=True, **kw):
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

    def clone(self, name, src):
        """another layer using the same footage as `src`"""
        L = Layer(self, name, src.size, src.k, src.x, src.y, sec=src.sec, screen=src.screen)
        L.file = src.file
        self.layers.append(L)
        return L

    def solid(self, name, color, w=W, h=H, x=0, y=0, sec=None, screen=True, kind='solid'):
        L = Layer(self, name, (w, h), 1, x, y, sec=sec or self.sec, screen=screen, kind=kind)
        L.color = color
        L.pano = False
        self.layers.append(L)
        return L

    def adjust(self, name, f_in, f_out, sec='FX'):
        L = self.solid(name, (255, 255, 255), kind='adjust', sec=sec)
        L.span(f_in, f_out)
        return L

    def get(self, name):
        for L in self.layers:
            if L.name == name:
                return L
        raise KeyError(name)

    # --- static panorama preview (final state, no animation)
    def pano_preview(self, path, x0=0, x1=11000, y0=0, y1=1080, scale=1.0, bg=BG):
        out = Image.new('RGBA', (int((x1 - x0) * scale), int((y1 - y0) * scale)), bg + (255,))
        for L in self.layers:
            if L.kind != 'footage' or L.screen or not L.pano:
                continue
            if L.x + L.ww < x0 or L.x > x1:
                continue
            im = Image.open(L.file).convert('RGBA')
            sc = scale / L.k
            im = im.resize((max(1, int(round(im.width * sc))), max(1, int(round(im.height * sc)))), Image.LANCZOS)
            if L.static.get('opacity', 100) < 100:
                a = np.asarray(im).copy()
                a[..., 3] = (a[..., 3].astype(np.float32) * L.static['opacity'] / 100.0).astype(np.uint8)
                im = Image.fromarray(a, 'RGBA')
            px, py = int(round((L.x - x0) * scale)), int(round((L.y - y0) * scale))
            rot = L.static.get('rotation', 0.0)
            if rot:
                pvx, pvy = (L.pivot[0] - x0) * scale, (L.pivot[1] - y0) * scale
                diag = int(math.hypot(im.width, im.height)) + 4
                tmp = Image.new('RGBA', (2 * diag, 2 * diag), (0, 0, 0, 0))
                tmp.paste(im, (int(round(diag + px - pvx)), int(round(diag + py - pvy))))
                tmp = tmp.rotate(-rot, resample=Image.BICUBIC, center=(diag, diag))
                cx0, cy0 = int(round(pvx - diag)), int(round(pvy - diag))
                bx0, by0 = max(cx0, 0), max(cy0, 0)
                bx1, by1 = min(cx0 + 2 * diag, out.width), min(cy0 + 2 * diag, out.height)
                if bx1 > bx0 and by1 > by0:
                    out.alpha_composite(tmp.crop((bx0 - cx0, by0 - cy0, bx1 - cx0, by1 - cy0)), (bx0, by0))
                continue
            if L.blend == 'multiply':
                base = out.crop((px, py, px + im.width, py + im.height))
                ia = np.asarray(im).astype(np.float32) / 255.0
                ba = np.asarray(base.convert('RGBA')).astype(np.float32) / 255.0
                if ba.shape[:2] == ia.shape[:2]:
                    res = ba.copy()
                    m = ia[..., 3:4]
                    res[..., :3] = ba[..., :3] * (1 - m) + ba[..., :3] * ia[..., :3] * m
                    out.paste(Image.fromarray((res * 255).astype(np.uint8), 'RGBA'), (px, py))
                    continue
            layer = Image.new('RGBA', out.size, (0, 0, 0, 0))
            layer.paste(im, (px, py))
            out.alpha_composite(layer)
        out.convert('RGB').save(path, quality=92)
        return out
