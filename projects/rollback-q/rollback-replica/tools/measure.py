"""Colour-segmentation measurement helpers on the reference panorama."""
import numpy as np, sys
from PIL import Image
PANO = np.asarray(Image.open('pano/pano.png').convert('RGB')).astype(np.int32)

def mask_color(rgb, tol, x0=0, x1=11000, y0=0, y1=1080):
    a = PANO[y0:y1, x0:x1]
    d = np.abs(a - np.array(rgb)).max(axis=2)
    return d <= tol

def components(m, min_area=200):
    """connected components (4-neigh) via run-length union-find; returns list of (area, x0, y0, x1, y1)"""
    h, w = m.shape
    parent = {}
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    runs_prev = []
    nid = 0
    info = {}
    for y in range(h):
        row = m[y]
        d = np.diff(np.concatenate([[0], row.astype(np.int8), [0]]))
        st = np.where(d == 1)[0]; en = np.where(d == -1)[0]
        runs = []
        for s, e in zip(st, en):
            lab = None
            for (ps, pe, pl) in runs_prev:
                if ps < e and pe > s:
                    r = find(pl)
                    if lab is None: lab = r
                    elif r != lab: parent[r] = lab
            if lab is None:
                lab = nid; parent[lab] = lab; nid += 1
                info[lab] = [0, w, h, 0, 0]
            lab = find(lab)
            runs.append((s, e, lab))
            inf = info.setdefault(lab, [0, w, h, 0, 0])
            inf[0] += e - s; inf[1] = min(inf[1], s); inf[2] = min(inf[2], y); inf[3] = max(inf[3], e); inf[4] = max(inf[4], y + 1)
        runs_prev = runs
    # merge infos by root
    out = {}
    for lab, inf in info.items():
        r = find(lab)
        o = out.setdefault(r, [0, w, h, 0, 0])
        o[0] += inf[0]; o[1] = min(o[1], inf[1]); o[2] = min(o[2], inf[2]); o[3] = max(o[3], inf[3]); o[4] = max(o[4], inf[4])
    res = [tuple(v) for v in out.values() if v[0] >= min_area]
    return sorted(res, key=lambda t: -t[0])

def fit_circle(xs, ys):
    A = np.c_[2 * xs, 2 * ys, np.ones(len(xs))]
    b = xs ** 2 + ys ** 2
    c, *_ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy = c[0], c[1]
    r = np.sqrt(c[2] + cx * cx + cy * cy)
    return cx, cy, r

def report(name, rgb, tol, x0, x1, y0=0, y1=1080, min_area=300, top=12):
    m = mask_color(rgb, tol, x0, x1, y0, y1)
    comps = components(m, min_area)
    print(f'== {name} rgb={rgb} tol={tol}: {len(comps)} comps')
    for (area, a, b, c, d) in comps[:top]:
        print(f'   area={area:7d} bbox x[{a + x0},{c + x0}] y[{b + y0},{d + y0}]  w={c - a} h={d - b}')
    return m, comps

if __name__ == '__main__':
    X0, X1 = 0, 2750
    # sample exact colours first
    for (x, y) in ((450, 300), (760, 200), (1000, 300), (980, 437), (1450, 310), (1800, 650), (700, 700), (2110, 300), (2170, 300)):
        print((x, y), PANO[y, x])
    mp, cp = report('pink', (240, 18, 110), 40, 150, 1150, 60, 600)
    mb, cb = report('blue', (10, 132, 255), 45, 0, 2750)
    mm, cm = report('mint', (25, 230, 180), 45, 1200, 1800)
    # ring fit: pink outer boundary = leftmost pink x per row
    ys, xs_out, xs_in = [], [], []
    for yy in range(mp.shape[0]):
        r = np.where(mp[yy])[0]
        if len(r) > 20:
            ys.append(yy + 60); xs_out.append(r[0] + 150)
    ys = np.array(ys, float); xs_out = np.array(xs_out, float)
    sel = ys > 200
    print('pink outer circle fit (rows>200):', [round(v, 1) for v in fit_circle(xs_out[sel], ys[sel])])
