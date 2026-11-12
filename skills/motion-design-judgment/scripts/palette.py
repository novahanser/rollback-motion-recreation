# -*- coding: utf-8 -*-
"""从一段视频里量强调色：让 ffmpeg 按 BT.709 直接输出 RGB，统计高彩度像素的主色。

用法: python -I palette.py <视频> [最小彩度=85] [输出个数=14]
做法: 全部帧缩到 480 宽（面积平均），取 RGB 最大最小值之差不小于阈值的像素，按 5 bit/通道分箱累计；
      把相邻的箱合并成簇（色差 < 28），输出每个簇的中位色、占全片像素的比例、出现最多的帧段。
"""
import os, sys, subprocess, json
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
FF = os.environ.get("FFMPEG_DIR", "")
FFMPEG = os.path.join(FF, "ffmpeg") if FF else "ffmpeg"
FFPROBE = os.path.join(FF, "ffprobe") if FF else "ffprobe"


def main():
    path = sys.argv[1]
    thr = int(sys.argv[2]) if len(sys.argv) > 2 else 85
    topn = int(sys.argv[3]) if len(sys.argv) > 3 else 14
    info = json.loads(subprocess.check_output([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries",
                                               "stream=width,height,color_space", "-of", "json", path]))["streams"][0]
    w0, h0 = info["width"], info["height"]
    w = 480; h = int(round(h0 * w / w0 / 2)) * 2
    print(f"{os.path.basename(path)}  {w0}x{h0}  color_space tag: {info.get('color_space', '(none)')}")
    cmd = [FFMPEG, "-v", "error", "-i", path, "-map", "0:v:0", "-vf", f"scale={w}:{h}:in_color_matrix=bt709:flags=area,format=rgb24", "-f", "rawvideo", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    fsz = w * h * 3
    cnt = np.zeros(32768, np.int64); acc = np.zeros((32768, 3), np.float64)
    per = []                                             # 每帧每箱的计数（稀疏存前几名）
    n = 0
    while True:
        buf = p.stdout.read(fsz)
        if len(buf) < fsz:
            break
        im = np.frombuffer(buf, np.uint8).reshape(-1, 3).astype(np.int32)
        ch = im.max(1) - im.min(1)
        px = im[ch >= thr]
        if len(px):
            key = ((px[:, 0] >> 3) << 10) | ((px[:, 1] >> 3) << 5) | (px[:, 2] >> 3)
            c = np.bincount(key, minlength=32768)
            cnt += c
            for k in range(3):
                acc[:, k] += np.bincount(key, weights=px[:, k], minlength=32768)
            per.append(c.astype(np.int32))
        else:
            per.append(np.zeros(32768, np.int32))
        n += 1
    per = np.array(per)
    tot = n * w * h
    order = np.argsort(cnt)[::-1]
    clusters = []
    for b in order[:400]:
        if cnt[b] == 0:
            break
        col = acc[b] / cnt[b]
        for c in clusters:
            if np.abs(c["col"] - col).max() < 28:
                wsum = c["n"] + cnt[b]
                c["col"] = (c["col"] * c["n"] + col * cnt[b]) / wsum; c["n"] = wsum; c["bins"].append(b)
                break
        else:
            clusters.append(dict(col=col, n=int(cnt[b]), bins=[b]))
    clusters.sort(key=lambda c: -c["n"])
    print(f"frames {n}; high-chroma (>= {thr}) pixels: {cnt.sum() / tot * 100:.1f}% of all pixels")
    for c in clusters[:topn]:
        f = per[:, c["bins"]].sum(1)
        on = np.where(f > 0.004 * w * h)[0]
        rng = f"f{on.min()}—{on.max()}（{len(on)} 帧）" if len(on) else "零星"
        r, g, b = (int(round(v)) for v in c["col"])
        print(f"  #{r:02X}{g:02X}{b:02X}  ({r:3d},{g:3d},{b:3d})  {c['n'] / tot * 100:5.2f}% of pixels   {rng}")


if __name__ == "__main__":
    main()
