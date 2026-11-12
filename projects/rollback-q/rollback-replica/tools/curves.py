"""Measure element motion curves from the source video (world-space colour masks)."""
import numpy as np, json
from PIL import Image
cam = json.load(open(r'C:\Users\bg931\Documents\New project\rollback-replica\scripts\cam.json'))
def world_patch(f, x0, y0, x1, y1, step=1.0):
    c = cam[f]; s = c['s']; cx = c['cx']
    a = np.asarray(Image.open(f'frames_full/f_{f:04d}.jpg').convert('RGB')).astype(np.int32)
    xs = np.arange(x0, x1, step); ys = np.arange(y0, y1, step)
    X, Y = np.meshgrid(xs, ys)
    SX = np.round((X - cx) * s + 960).astype(int); SY = np.round((Y - 540) * s + 540).astype(int)
    ok = (SX >= 0) & (SX < 1920) & (SY >= 0) & (SY < 1080)
    out = np.zeros(X.shape + (3,), np.int32) - 999
    out[ok] = a[SY[ok], SX[ok]]
    return X, Y, out, ok
def near(img, rgb, tol): return np.abs(img - np.array(rgb)).max(axis=2) <= tol
def angs(X, Y, cx, cy): return (np.degrees(np.arctan2(-(Y - cy), X - cx)) + 360) % 360
print('== pink ring (centre 700,540): frame, area, angular range (CCW from +x), r_out')
for f in range(51, 63):
    X, Y, im, ok = world_patch(f, 200, 60, 1200, 560, 2)
    m = near(im, (232, 8, 109), 45)
    R = np.hypot(X - 700, Y - 540); m &= (R > 150) & (R < 470)
    if m.sum() < 30: print(f, 'none'); continue
    A = angs(X, Y, 700, 540)[m]
    print(f, 'area', int(m.sum() * 4), 'ang p5..p95 %.0f..%.0f' % (np.percentile(A, 3), np.percentile(A, 97)), 'r p5..p98 %.0f..%.0f' % (np.percentile(R[m], 3), np.percentile(R[m], 98)))
print('== blue sector: angular range')
for f in range(56, 69):
    X, Y, im, ok = world_patch(f, 600, 60, 1200, 560, 2)
    m = near(im, (31, 134, 240), 45); R = np.hypot(X - 700, Y - 540); m &= (R > 180) & (R < 440)
    if m.sum() < 30: print(f, 'none'); continue
    A = angs(X, Y, 700, 540)[m]
    print(f, 'area', int(m.sum() * 4), 'ang %.0f..%.0f' % (np.percentile(A, 2), np.percentile(A, 98)), 'r %.0f..%.0f' % (np.percentile(R[m], 2), np.percentile(R[m], 98)))
print('== crescent (dark below ruler, centre 722,510): angular range 180=left 270=bottom 360=right')
for f in range(32, 44):
    X, Y, im, ok = world_patch(f, 380, 545, 1060, 840, 2)
    lum = im.mean(axis=2); sat = im.max(axis=2) - im.min(axis=2)
    R = np.hypot(X - 722, Y - 510); m = ok & (lum < 150) & (sat < 25) & (R > 215) & (R < 305)
    if m.sum() < 30: print(f, 'none'); continue
    A = angs(X, Y, 722, 510)[m]
    print(f, 'area', int(m.sum() * 4), 'ang %.0f..%.0f' % (np.percentile(A, 2), np.percentile(A, 98)), 'lum %.0f' % lum[m].mean())
print('== vinyl black disc radius (centre 980,437)')
for f in range(55, 64):
    X, Y, im, ok = world_patch(f, 760, 215, 1200, 540, 2)
    m = ok & (im.max(axis=2) < 60); R = np.hypot(X - 980, Y - 437)
    lab = near(im, (221, 37, 120), 45) & (R < 130)
    print(f, 'black area', int(m.sum() * 4), 'r98 %.0f' % (np.percentile(R[m], 98) if m.sum() > 30 else 0), '| label area', int(lab.sum() * 4), 'r98 %.0f' % (np.percentile(R[lab], 98) if lab.sum() > 30 else 0))
print('== mint blocks bbox (world)')
for f in range(51, 70):
    X, Y, im, ok = world_patch(f, 1250, 200, 1750, 540, 2)
    m = near(im, (30, 232, 185), 60)
    if m.sum() < 30: print(f, 'none'); continue
    xs = X[m]; ys = Y[m]
    print(f, 'area', int(m.sum() * 4), 'x %.0f..%.0f y %.0f..%.0f' % (np.percentile(xs, 1), np.percentile(xs, 99), np.percentile(ys, 1), np.percentile(ys, 99)))
print('== blue bars (world x 1700..2230, y>541): bbox + area')
for f in range(84, 100):
    X, Y, im, ok = world_patch(f, 1700, 541, 2230, 930, 2)
    m = near(im, (31, 134, 240), 50)
    if m.sum() < 30: print(f, 'none'); continue
    xs = X[m]; ys = Y[m]
    print(f, 'area', int(m.sum() * 4), 'x %.0f..%.0f y %.0f..%.0f' % (np.percentile(xs, 1), np.percentile(xs, 99), np.percentile(ys, 1), np.percentile(ys, 99)))
print('== pink beam (world x 6300..7400): bbox')
for f in range(164, 176):
    X, Y, im, ok = world_patch(f, 6300, 150, 7450, 700, 2)
    m = near(im, (232, 8, 109), 50)
    if m.sum() < 30: print(f, 'none'); continue
    xs = X[m]; ys = Y[m]
    print(f, 'area', int(m.sum() * 4), 'x %.0f..%.0f y %.0f..%.0f' % (np.percentile(xs, 1), np.percentile(xs, 99), np.percentile(ys, 1), np.percentile(ys, 99)))
