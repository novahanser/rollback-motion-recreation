# -*- coding: utf-8 -*-
"""逐帧扫描一个视频，输出低分辨率指标、每秒缩略图和每秒量化色彩直方图。

用法: python -I scan_video.py <video> <outdir> <id>
输出:
  <outdir>/<id>_metrics.npz   逐帧指标
  <outdir>/<id>_colorhist.npy 每秒 4bit/通道量化色彩直方图 (秒, 4096)
  <outdir>/<id>_thumbs/tNNNN.jpg 每秒一张缩略图 (取每秒的第一帧)
  <outdir>/<id>_meta.json     基本参数
"""
import sys, os, json, subprocess
import numpy as np
from PIL import Image

FF = os.environ.get("FFMPEG_DIR", "")   # ffmpeg 不在 PATH 里时，把环境变量 FFMPEG_DIR 指到它所在的目录
FFMPEG = os.path.join(FF, "ffmpeg") if FF else "ffmpeg"
FFPROBE = os.path.join(FF, "ffprobe") if FF else "ffprobe"
STD_FPS = [18.0, 23.976024, 24.0, 25.0, 29.970030, 30.0, 50.0, 59.940060, 60.0]


def probe(path):
    out = subprocess.check_output([
        FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries",
        "stream=width,height,r_frame_rate:format=duration", "-of", "json", path])
    j = json.loads(out)
    st = j["streams"][0]
    num, den = st["r_frame_rate"].split("/")
    fps_raw = float(num) / float(den)
    fps = min(STD_FPS, key=lambda f: abs(f - fps_raw))
    if abs(fps - fps_raw) > 0.05:
        fps = fps_raw
    return int(st["width"]), int(st["height"]), fps_raw, fps, float(j["format"]["duration"])


def probe_pts(path):
    out = subprocess.check_output([
        FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries",
        "packet=pts_time", "-of", "csv=p=0", path]).decode("ascii", "ignore")
    pts = []
    for line in out.splitlines():
        line = line.strip().strip(",")
        if not line or line == "N/A":
            continue
        try:
            pts.append(float(line))
        except ValueError:
            pass
    pts.sort()
    return np.array(pts, dtype=np.float64)


def main():
    path, outdir, vid = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    thumbdir = os.path.join(outdir, vid + "_thumbs")
    os.makedirs(thumbdir, exist_ok=True)
    w, h, fps_raw, fps, dur = probe(path)
    pts = probe_pts(path)
    ah = 180
    aw = int(round(w / h * ah / 2)) * 2
    cmd = [FFMPEG, "-v", "error", "-i", path, "-map", "0:v:0", "-fps_mode", "passthrough",
           "-vf", f"scale={aw}:{ah}:flags=area", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=aw * ah * 3 * 8)
    fsz = aw * ah * 3
    cols = {k: [] for k in ["d_abs", "d2", "d_hist", "chg", "luma", "lstd", "sat", "white", "black", "color", "edge"]}
    prev = None; prev2 = None; prev_hist = None
    nsec = int(dur) + 3
    chist = np.zeros((nsec, 4096), dtype=np.uint32)
    n = 0
    last_thumb_sec = -1
    while True:
        buf = p.stdout.read(fsz)
        if len(buf) < fsz:
            break
        fr = np.frombuffer(buf, dtype=np.uint8).reshape(ah, aw, 3)
        f = fr.astype(np.float32)
        gray = 0.2126 * f[..., 0] + 0.7152 * f[..., 1] + 0.0722 * f[..., 2]
        mx = f.max(axis=2); mn = f.min(axis=2)
        chroma = mx - mn
        t = pts[n] if n < len(pts) else n / fps
        sec = int(t)
        # 指标
        if prev is None:
            d_abs = 0.0; chg = 0.0
        else:
            ad = np.abs(gray - prev)
            d_abs = float(ad.mean() / 255.0)
            chg = float((ad > 24).mean())
        d2 = 0.0 if prev2 is None else float(np.abs(gray - prev2).mean() / 255.0)
        q = (fr >> 6).astype(np.int32)
        hist = np.bincount((q[..., 0] << 4 | q[..., 1] << 2 | q[..., 2]).ravel(), minlength=64).astype(np.float32)
        hist /= hist.sum()
        d_hist = 0.0 if prev_hist is None else float(np.abs(hist - prev_hist).sum() / 2.0)
        cols["d_abs"].append(d_abs); cols["d2"].append(d2); cols["d_hist"].append(d_hist); cols["chg"].append(chg)
        cols["luma"].append(float(gray.mean() / 255.0)); cols["lstd"].append(float(gray.std() / 255.0))
        cols["sat"].append(float((chroma / np.maximum(mx, 1.0)).mean()))
        cols["white"].append(float(((gray > 215) & (chroma < 30)).mean()))
        cols["black"].append(float((gray < 35).mean()))
        cols["color"].append(float((chroma > 60).mean()))
        gx = np.abs(np.diff(gray, axis=1)).mean(); gy = np.abs(np.diff(gray, axis=0)).mean()
        cols["edge"].append(float((gx + gy) / 255.0))
        if sec < nsec:
            q4 = (fr >> 4).astype(np.int32)
            chist[sec] += np.bincount((q4[..., 0] << 8 | q4[..., 1] << 4 | q4[..., 2]).ravel(), minlength=4096).astype(np.uint32)
        if sec != last_thumb_sec:
            Image.fromarray(fr).save(os.path.join(thumbdir, f"t{sec:04d}.jpg"), quality=88)
            last_thumb_sec = sec
        prev2 = prev; prev = gray; prev_hist = hist
        n += 1
    p.wait()
    arrs = {k: np.array(v, dtype=np.float32) for k, v in cols.items()}
    arrs["pts"] = pts[:n] if len(pts) >= n else np.arange(n) / fps
    np.savez_compressed(os.path.join(outdir, vid + "_metrics.npz"), **arrs)
    np.save(os.path.join(outdir, vid + "_colorhist.npy"), chist)
    meta = dict(id=vid, path=path, width=w, height=h, fps_raw=fps_raw, fps=fps, duration=dur,
                frames=n, pts_count=int(len(pts)), analysis_w=aw, analysis_h=ah)
    with open(os.path.join(outdir, vid + "_meta.json"), "w", encoding="utf-8") as fo:
        json.dump(meta, fo, ensure_ascii=False, indent=1)
    print(vid, "frames", n, "pts", len(pts), "fps", fps, "dur", round(dur, 2), "size", w, h)


if __name__ == "__main__":
    main()
