import numpy as np, json
import landmark as L
tr = json.load(open('track_ruler.json'))
for (f, rect) in ((250, (9150, 10700, 60, 1020)), (245, (9150, 10700, 60, 1020)), (140, (4300, 6400, 60, 1020)), (60, (600, 2300, 60, 1020)), (180, (5800, 7500, 60, 1020)), (115, (3650, 4700, 250, 900)), (45, (700, 1650, 250, 900))):
    s0 = tr[f]['s']
    best = None
    for s in np.linspace(s0 * 0.97, s0 * 1.03, 61):
        r = L.locate(f, rect, [s], DS=1)
        if r and (best is None or r[0] > best[0]): best = r
    print(f, 'ruler s', s0, 'per', tr[f]['per'], '-> best s', round(best[1], 4), 'cx', round(best[2], 1), 'score', round(best[0], 3), 'implied P0', round(tr[f]['per'] / best[1], 4))
