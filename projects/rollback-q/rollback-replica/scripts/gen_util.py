"""Helpers around the AI-generated source images in ../gen and camera-space conversions."""
import os, json
import numpy as np
from PIL import Image, ImageOps, ImageFilter
import lib
from lib import GEN, HERE
import cam as camlib

CAM = camlib.build()


def s2w(f, X, Y):
    """screen px (1920x1080) at frame f -> world coords"""
    c = CAM[int(f)]
    return (c['cx'] + (X - 960.0) / c['s'], 540.0 + (Y - 540.0) / c['s'])


def w2s(f, x, y):
    c = CAM[int(f)]
    return ((x - c['cx']) * c['s'] + 960.0, (y - 540.0) * c['s'] + 540.0)


def zoom(f):
    return CAM[int(f)]['s']


def pin_keys(path, interp=lib.LIN):
    """path: [(frame, X, Y)] screen positions, linearly interpolated per frame -> world position keys"""
    keys = []
    for (f0, x0, y0), (f1, x1, y1) in zip(path[:-1], path[1:]):
        for f in range(int(f0), int(f1)):
            t = (f - f0) / float(f1 - f0)
            wx, wy = s2w(f, x0 + (x1 - x0) * t, y0 + (y1 - y0) * t)
            keys.append((f, [wx, wy], lib.LIN))
    f, x, y = path[-1]
    wx, wy = s2w(f, x, y)
    keys.append((f, [wx, wy], lib.LIN))
    return keys


def pin(L, path, size_path=None):
    """glue layer L to a screen-space path; optional size_path [(frame, scale)] is screen-relative scale
    (1.0 = natural size at the zoom of the first path frame)."""
    L.key('position', pin_keys(path))
    if size_path:
        s0 = zoom(path[0][0])
        ks = []
        for (f0, a), (f1, b) in zip(size_path[:-1], size_path[1:]):
            for f in range(int(f0), int(f1)):
                t = (f - f0) / float(f1 - f0)
                v = (a + (b - a) * t) * s0 / zoom(f) * 100.0
                ks.append((f, [v, v], lib.LIN))
        f, a = size_path[-1]
        v = a * s0 / zoom(f) * 100.0
        ks.append((f, [v, v], lib.LIN))
        L.key('scale', ks)
    return L


def gen(name):
    return Image.open(os.path.join(GEN, name)).convert('RGBA')


def quadrant(name, qx, qy, inset=6):
    im = gen(name)
    w, h = im.width // 2, im.height // 2
    return im.crop((qx * w + inset, qy * h + inset, (qx + 1) * w - inset, (qy + 1) * h - inset))


def components(im, min_area=2000, pad=4):
    """split a transparent sprite sheet into separate sprites (bbox list, left->right, top->bottom rows)"""
    a = np.asarray(im)[..., 3] > 24
    h, w = a.shape
    seen = np.zeros_like(a, bool)
    boxes = []
    small = a[::4, ::4]
    sh, sw = small.shape
    sseen = np.zeros_like(small, bool)
    for y in range(sh):
        for x in range(sw):
            if small[y, x] and not sseen[y, x]:
                stack = [(y, x)]
                sseen[y, x] = True
                x0 = x1 = x
                y0 = y1 = y
                n = 0
                while stack:
                    cy, cx = stack.pop()
                    n += 1
                    x0, x1, y0, y1 = min(x0, cx), max(x1, cx), min(y0, cy), max(y1, cy)
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < sh and 0 <= nx < sw and small[ny, nx] and not sseen[ny, nx]:
                            sseen[ny, nx] = True
                            stack.append((ny, nx))
                if n * 16 >= min_area:
                    boxes.append((max(x0 * 4 - pad, 0), max(y0 * 4 - pad, 0), min(x1 * 4 + 4 + pad, w), min(y1 * 4 + 4 + pad, h)))
    boxes.sort(key=lambda b: (round(b[1] / 200.0), b[0]))
    return boxes


def gray(im):
    a = im.convert('RGBA')
    g = ImageOps.grayscale(a.convert('RGB'))
    out = Image.merge('RGBA', (g, g, g, a.split()[3]))
    return out


def threshold(im, t=128, fg=(0, 0, 0), bg=None):
    """1-bit look: pixels darker than t -> fg (opaque); lighter -> bg (or transparent)"""
    g = np.asarray(ImageOps.grayscale(im.convert('RGB'))).astype(np.float32)
    al = np.asarray(im.convert('RGBA'))[..., 3].astype(np.float32) / 255.0
    m = (g < t).astype(np.float32)
    out = np.zeros(g.shape + (4,), np.uint8)
    if bg is None:
        out[..., 0], out[..., 1], out[..., 2] = fg
        out[..., 3] = (m * al * 255).astype(np.uint8)
    else:
        for i in range(3):
            out[..., i] = (m * fg[i] + (1 - m) * bg[i]).astype(np.uint8)
        out[..., 3] = (al * 255).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def line_art(name, color=(60, 60, 60), lo=70, hi=225, gamma=1.0):
    """dark lines on white -> coloured lines with alpha"""
    im = gen(name)
    g = np.asarray(ImageOps.grayscale(im.convert('RGB'))).astype(np.float32)
    al = np.clip((hi - g) / float(hi - lo), 0, 1) ** gamma
    out = np.zeros(g.shape + (4,), np.uint8)
    out[..., 0], out[..., 1], out[..., 2] = color
    out[..., 3] = (al * 255).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def fit(im, w, h):
    """centre-crop + resize to exactly (w, h) px"""
    return ImageOps.fit(im, (int(w), int(h)), Image.LANCZOS, centering=(0.5, 0.5))
