# -*- coding: utf-8 -*-
"""在一条视频里找「两种灰相间的棋盘格」出现的时间段。

用法: python -I find_checker.py <编号> [步长帧=12] [阈值=0.006]

做法: 每隔若干帧取一帧（宽度统一到 1920），在稀疏的采样点上检查：
  这个点与右边 c、下边 c 处的点明暗相差明显，与斜对角 c 处、以及 2c 处的点明暗相近，而且这几处都接近无彩。
  对一组候选格子大小 c 各算一次，取满足条件的采样点占比最高的那个。
占比超过阈值的帧按时间合并成段输出。半调网点、细密的方格纸、像素字也可能被报出来，结果要抽帧确认。
"""
import os, sys, json, subprocess
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
import vis  # noqa: E402

FFMPEG = vis.FFMPEG
WORK = vis.WORK
CS = (5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18, 20, 22, 24, 28, 32, 40)


def score(rgb):
    g = rgb.astype(np.int16).sum(2) // 3
    sat = rgb.max(2).astype(np.int16) - rgb.min(2).astype(np.int16)
    ok = (sat < 22) & (g > 90)
    H, W = g.shape; st = 4
    best = (0.0, 0)
    for c in CS:
        h = H - 2 * c; w = W - 2 * c
        a = g[0:h:st, 0:w:st]; r = g[0:h:st, c:c + w:st]; d = g[c:c + h:st, 0:w:st]; dg = g[c:c + h:st, c:c + w:st]
        r2 = g[0:h:st, 2 * c:2 * c + w:st]; d2 = g[2 * c:2 * c + h:st, 0:w:st]
        o = ok[0:h:st, 0:w:st] & ok[0:h:st, c:c + w:st] & ok[c:c + h:st, 0:w:st] & ok[c:c + h:st, c:c + w:st]
        cond = o & (np.abs(a - r) > 24) & (np.abs(a - d) > 24) & (np.abs(a - dg) < 14) & (np.abs(a - r2) < 14) & (np.abs(a - d2) < 14) \
            & (np.sign(a - r) == np.sign(a - d))
        s = float(cond.mean())
        if s > best[0]:
            best = (s, c)
    return best


def main():
    vid = sys.argv[1]; step = int(sys.argv[2]) if len(sys.argv) > 2 else 12; thr = float(sys.argv[3]) if len(sys.argv) > 3 else 0.006
    meta = json.load(open(os.path.join(WORK, vid + "_meta.json"), encoding="utf-8"))
    W0, H0, fps = meta["width"], meta["height"], meta["fps"]
    W = 1920; H = int(round(H0 * W / W0 / 2)) * 2
    cmd = [FFMPEG, "-v", "error", "-i", meta["path"], "-map", "0:v:0", "-vf", f"select=not(mod(n\\,{step})),scale={W}:{H}:flags=area,format=rgb24",
           "-fps_mode", "passthrough", "-f", "rawvideo", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    fsz = W * H * 3; hits = []; i = 0
    while True:
        buf = p.stdout.read(fsz)
        if len(buf) < fsz:
            break
        s, c = score(np.frombuffer(buf, np.uint8).reshape(H, W, 3))
        n = i * step
        if s >= thr:
            hits.append((n, s, c))
        i += 1
    print(f"{vid}: sampled {i} frames (every {step}), scale to {W}x{H}; frames with checker share >= {thr}: {len(hits)}")
    segs = []
    for n, s, c in hits:
        if segs and n - segs[-1]["b"] <= step * 3:
            sg = segs[-1]; sg["b"] = n; sg["smax"] = max(sg["smax"], s); sg["cs"].append(c); sg["n"] += 1
            if s >= sg["smax"]:
                sg["at"] = n
        else:
            segs.append(dict(a=n, b=n, smax=s, cs=[c], n=1, at=n))
    for sg in segs:
        ta, tb = sg["a"] / fps, sg["b"] / fps
        cs = sorted(set(sg["cs"]))
        print(f"  {int(ta // 60)}:{ta % 60:04.1f}—{int(tb // 60)}:{tb % 60:04.1f}  f{sg['a']}—f{sg['b']}  hits {sg['n']}  max share {sg['smax'] * 100:.1f}% at f{sg['at']}  cell(px@1920w) {cs[0] if len(cs) == 1 else str(cs[0]) + '-' + str(cs[-1])}")


if __name__ == "__main__":
    main()
