import numpy as np
from PIL import Image
import sys

a = np.asarray(Image.open('pano/pano.png').convert('L')).astype(float)


def period(x0, x1, y0, y1):
    band = a[y0:y1, x0:x1].mean(axis=0)
    band = band - band.mean()
    ac = np.correlate(band, band, 'full')[len(band) - 1:]
    ac /= ac[0]
    n = min(len(ac) - 1, 220)
    pk = [i for i in range(3, n) if ac[i] > ac[i - 1] and ac[i] > ac[i + 1] and ac[i] > 0.25]
    return pk[:10], [round(float(ac[i]), 2) for i in pk[:10]]


for (x0, x1) in ((130, 530), (3300, 3800), (5560, 6100), (9900, 10400), (7000, 7400)):
    print(x0, period(x0, x1, 526, 539))

# ascii of ruler
for x0 in (3300, 9950):
    print('--- x0', x0)
    seg = a[522:556, x0:x0 + 150]
    for i, r in enumerate(seg):
        print('%3d ' % (522 + i) + ''.join('#' if v < 90 else ('+' if v < 150 else '.') for v in r))
