# -*- coding: utf-8 -*-
"""审查用的出图工具（依赖同目录的 vis.py）。

  python -I vis2.py cuts <id> <out.jpg> <n> [起始秒 结束秒]   n 个切点，每个一行：切前 2 帧、切前 1 帧、切点帧、切后 1 帧
  python -I vis2.py cutsat <id> <out.jpg> <帧号...>           指定切点帧号
  python -I vis2.py top <id> <out.jpg> <n> [起始秒 结束秒]    镜头内部运动量最大的 n 帧，取画面中央原始分辨率裁切，用来看有没有运动模糊
"""
import sys, os, json
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
import vis  # noqa: E402


def load(vid):
    m = vis.meta(vid)
    S = json.load(open(os.path.join(vis.WORK, vid + "_summary.json"), encoding="utf-8"))
    M = dict(np.load(os.path.join(vis.WORK, vid + "_metrics.npz")))
    return m, S, M


def sheet(rows, out, cellw):
    """rows: list of list of (label, PIL)"""
    cw, ch = rows[0][0][1].size
    ncol = max(len(r) for r in rows); gap = 3
    img = Image.new("RGB", (ncol * cw + (ncol + 1) * gap, len(rows) * ch + (len(rows) + 1) * gap), (40, 40, 40))
    d = ImageDraw.Draw(img); fnt = vis.font(13)
    for r, row in enumerate(rows):
        for c, (lab, im) in enumerate(row):
            x = gap + c * (cw + gap); y = gap + r * (ch + gap)
            img.paste(im, (x, y)); vis.label(d, (x + 3, y + 2), lab, fnt)
    img.save(out, quality=88)
    print(out, img.size, len(rows), "rows")


def cut_rows(m, frames, cellw=390):
    rows = []
    n = len(m["pts"])
    for c in frames:
        f0 = max(0, c - 2)
        ims = vis.read_frames(m, f0, 4, cellw)
        rows.append([(f"f{f0 + i} {vis.tc(float(m['pts'][min(n - 1, f0 + i)]))}" + ("  <cut" if f0 + i == c else ""), im) for i, im in enumerate(ims)])
    return rows


def cmd_cuts(a):
    vid, out, n = a[0], a[1], int(a[2])
    m, S, M = load(vid)
    t0 = float(a[3]) if len(a) > 3 else 0.0; t1 = float(a[4]) if len(a) > 4 else 1e9
    cuts = [e["frame"] for e in S["events"] if e["kind"] == "cut" and t0 <= e["t"] <= t1]
    # 去掉紧跟在另一个切点后面的（闪切串只取第一个）
    keep = []
    for c in cuts:
        if not keep or c - keep[-1] > 8:
            keep.append(c)
    if len(keep) > n:
        idx = np.linspace(0, len(keep) - 1, n).round().astype(int)
        keep = [keep[i] for i in idx]
    sheet(cut_rows(m, keep), out, 390)
    print("cuts shown:", keep)


def cmd_cutsat(a):
    vid, out = a[0], a[1]
    m, S, M = load(vid)
    sheet(cut_rows(m, [int(x) for x in a[2:]]), out, 390)


def cmd_top(a):
    vid, out, n = a[0], a[1], int(a[2])
    m, S, M = load(vid)
    t0 = float(a[3]) if len(a) > 3 else 0.0; t1 = float(a[4]) if len(a) > 4 else 1e9
    d = M["d_abs"].copy(); dh = M["d_hist"]; pts = M["pts"]
    cuts = [e["frame"] for e in S["events"] if e["kind"] != "pulse"]
    for c in cuts:
        d[max(0, c - 1):c + 2] = 0
    d[dh > 0.25] = 0
    d[(pts < t0) | (pts > t1)] = 0
    sel = []
    for i in np.argsort(d)[::-1]:
        if d[i] <= 0:
            break
        if all(abs(int(i) - j) > 20 for j in sel):
            sel.append(int(i))
        if len(sel) >= n:
            break
    sel.sort()
    W, H = m["width"], m["height"]
    cw = min(960, W // 2); chh = int(cw * 9 / 16)
    crop = [0.5 - cw / W / 2, 0.5 - chh / H / 2, 0.5 + cw / W / 2, 0.5 + chh / H / 2]
    cells = []
    for f in sel:
        im = vis.read_frames(m, f, 1, 780, crop)[0]
        cells.append((f"f{f} {vis.tc(float(pts[f]))} d={M['d_abs'][f] * 1000:.0f}", im))
    rows = [cells[i:i + 2] for i in range(0, len(cells), 2)]
    sheet(rows, out, 780)
    print("frames:", sel)


if __name__ == "__main__":
    {"cuts": cmd_cuts, "cutsat": cmd_cutsat, "top": cmd_top}[sys.argv[1]](sys.argv[2:])
