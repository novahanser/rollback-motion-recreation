# -*- coding: utf-8 -*-
"""抽帧与拼图工具。

  python -I vis.py sheet  <id> <start_s> <step_s> <count> <cols> <out.jpg> [cellw]
  python -I vis.py frame  <id> <t秒|fN帧号> <out.jpg> [maxw] [x0,y0,x1,y1 (0-1 比例裁切)]
  python -I vis.py strip  <id> <t秒|fN帧号> <nframes> <step> <cols> <out.jpg> [cellw] [x0,y0,x1,y1]
  python -I vis.py grid   <id> <cols> <cellw> <out.jpg> <位置1> <位置2> ... [crop=x0,y0,x1,y1]   (位置写秒数或 fN 帧号)
  python -I vis.py colorbar <id> <out.png>
  python -I vis.py imgsheet <out.jpg> <cols> <cellw> <img1> <img2> ...   (任意图片拼图，带文件名标签)
"""
import sys, os, json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FF = os.environ.get("FFMPEG_DIR", "")   # ffmpeg 不在 PATH 里时，把环境变量 FFMPEG_DIR 指到它所在的目录
FFMPEG = os.path.join(FF, "ffmpeg") if FF else "ffmpeg"
FFPROBE = os.path.join(FF, "ffprobe") if FF else "ffprobe"
WORK = os.environ.get("MOTION_WORK") or os.path.join(os.getcwd(), "motion_work")   # 中间结果目录，可用环境变量 MOTION_WORK 改


def font(sz):
    for name in (r"C:\Windows\Fonts\consolab.ttf", r"C:\Windows\Fonts\arial.ttf", "/System/Library/Fonts/Menlo.ttc",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", "DejaVuSansMono-Bold.ttf"):
        try:
            return ImageFont.truetype(name, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def meta(vid):
    with open(os.path.join(WORK, vid + "_meta.json"), encoding="utf-8") as f:
        m = json.load(f)
    m["pts"] = np.load(os.path.join(WORK, vid + "_metrics.npz"))["pts"]
    return m


def tc(t):
    return f"{int(t // 60)}:{t % 60:05.2f}"


def label(draw, xy, text, fnt):
    x, y = xy
    bb = draw.textbbox((x, y), text, font=fnt)
    draw.rectangle((bb[0] - 2, bb[1] - 2, bb[2] + 2, bb[3] + 2), fill=(0, 0, 0))
    draw.text((x, y), text, font=fnt, fill=(255, 255, 0))


def parse_pos(m, s):
    pts = m["pts"]
    if s.startswith("f"):
        n = int(s[1:])
    else:
        n = int(np.searchsorted(pts, float(s) - 1e-6))
    n = max(0, min(len(pts) - 1, n))
    return n, float(pts[n])


def parse_crop(s):
    return [float(v) for v in s.split(",")]


def cmd_sheet(a):
    vid, start, step, count, cols, out = a[0], int(a[1]), int(a[2]), int(a[3]), int(a[4]), a[5]
    cellw = int(a[6]) if len(a) > 6 else 260
    tdir = os.path.join(WORK, vid + "_thumbs")
    secs = [start + i * step for i in range(count)]
    secs = [s for s in secs if os.path.exists(os.path.join(tdir, f"t{s:04d}.jpg"))]
    if not secs:
        print("no thumbs"); return
    im0 = Image.open(os.path.join(tdir, f"t{secs[0]:04d}.jpg"))
    cellh = round(cellw * im0.height / im0.width)
    rows = (len(secs) + cols - 1) // cols
    gap = 3
    sheet = Image.new("RGB", (cols * cellw + (cols + 1) * gap, rows * cellh + (rows + 1) * gap), (40, 40, 40))
    d = ImageDraw.Draw(sheet); fnt = font(13)
    for i, s in enumerate(secs):
        im = Image.open(os.path.join(tdir, f"t{s:04d}.jpg")).resize((cellw, cellh), Image.LANCZOS)
        x = gap + (i % cols) * (cellw + gap); y = gap + (i // cols) * (cellh + gap)
        sheet.paste(im, (x, y))
        label(d, (x + 3, y + 2), f"{s // 60}:{s % 60:02d}", fnt)
    sheet.save(out, quality=88)
    print(out, sheet.size, len(secs), "cells")


def read_frames(m, n0, count, outw, crop=None):
    """从帧号 n0 起顺序读 count 帧，返回 PIL 列表（已缩放/裁切）。"""
    pts = m["pts"]
    t0 = max(0.0, float(pts[n0]) - 0.004)
    W, H = m["width"], m["height"]
    vf = []
    if crop:
        x0, y0, x1, y1 = crop
        cw = int((x1 - x0) * W) // 2 * 2; ch = int((y1 - y0) * H) // 2 * 2
        vf.append(f"crop={cw}:{ch}:{int(x0 * W)}:{int(y0 * H)}")
        sw, sh = cw, ch
    else:
        sw, sh = W, H
    ow = min(outw, sw) // 2 * 2
    oh = int(round(sh * ow / sw / 2)) * 2
    vf.append(f"scale={ow}:{oh}:flags=lanczos")
    cmd = [FFMPEG, "-v", "error", "-ss", f"{t0:.4f}", "-i", m["path"], "-map", "0:v:0", "-fps_mode", "passthrough",
           "-frames:v", str(count), "-vf", ",".join(vf), "-pix_fmt", "rgb24", "-f", "rawvideo", "-"]
    raw = subprocess.check_output(cmd)
    fsz = ow * oh * 3
    return [Image.frombuffer("RGB", (ow, oh), raw[i * fsz:(i + 1) * fsz], "raw", "RGB", 0, 1).copy()
            for i in range(len(raw) // fsz)]


def cmd_frame(a):
    vid, pos, out = a[0], a[1], a[2]
    maxw = int(a[3]) if len(a) > 3 else 1568
    crop = parse_crop(a[4]) if len(a) > 4 else None
    m = meta(vid)
    n, t = parse_pos(m, pos)
    im = read_frames(m, n, 1, maxw, crop)[0]
    im.save(out, quality=92)
    print(out, im.size, f"frame {n} t={tc(t)}")


def cmd_strip(a):
    vid, pos, nfr, step, cols, out = a[0], a[1], int(a[2]), int(a[3]), int(a[4]), a[5]
    cellw = int(a[6]) if len(a) > 6 else 390
    crop = parse_crop(a[7]) if len(a) > 7 else None
    m = meta(vid)
    n0, t0 = parse_pos(m, pos)
    frames = read_frames(m, n0, nfr * step, cellw, crop)[::step]
    cw, ch = frames[0].size
    rows = (len(frames) + cols - 1) // cols
    gap = 3
    sheet = Image.new("RGB", (cols * cw + (cols + 1) * gap, rows * ch + (rows + 1) * gap), (40, 40, 40))
    d = ImageDraw.Draw(sheet); fnt = font(13)
    for i, im in enumerate(frames):
        x = gap + (i % cols) * (cw + gap); y = gap + (i // cols) * (ch + gap)
        sheet.paste(im, (x, y))
        n = n0 + i * step
        t = float(m["pts"][min(n, len(m["pts"]) - 1)])
        label(d, (x + 3, y + 2), f"f{n} {tc(t)}", fnt)
    sheet.save(out, quality=90)
    print(out, sheet.size, f"frames {n0}..{n0 + (len(frames) - 1) * step} step {step}")


def cmd_grid(a):
    """grid <id> <cols> <cellw> <out> <pos1> <pos2> ... [crop=x0,y0,x1,y1]"""
    vid, cols, cellw, out = a[0], int(a[1]), int(a[2]), a[3]
    crop = None; poss = []
    for x in a[4:]:
        if x.startswith("crop="):
            crop = parse_crop(x[5:])
        else:
            poss.append(x)
    m = meta(vid)
    frames = []
    for pz in poss:
        n, t = parse_pos(m, pz)
        frames.append((n, t, read_frames(m, n, 1, cellw, crop)[0]))
    cw, ch = frames[0][2].size
    rows = (len(frames) + cols - 1) // cols
    gap = 3
    sheet = Image.new("RGB", (cols * cw + (cols + 1) * gap, rows * ch + (rows + 1) * gap), (40, 40, 40))
    d = ImageDraw.Draw(sheet); fnt = font(14)
    for i, (n, t, im) in enumerate(frames):
        x = gap + (i % cols) * (cw + gap); y = gap + (i // cols) * (ch + gap)
        sheet.paste(im, (x, y))
        label(d, (x + 3, y + 2), f"f{n} {tc(t)}", fnt)
    sheet.save(out, quality=90)
    print(out, sheet.size, len(frames), "frames")


def cmd_colorbar(a):
    vid, out = a[0], a[1]
    ch = np.load(os.path.join(WORK, vid + "_colorhist.npy")).astype(np.float64)
    nz = np.where(ch.sum(axis=1) > 0)[0]
    ch = ch[: nz.max() + 1]
    idx = np.arange(4096)
    r = (idx >> 8) * 17; g = ((idx >> 4) & 15) * 17; b = (idx & 15) * 17
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
    order = np.argsort(luma, kind="stable")
    H = 240; px = max(2, min(8, 1500 // len(ch)))
    img = np.zeros((H, len(ch) * px, 3), dtype=np.uint8)
    cols = np.stack([r, g, b], axis=1).astype(np.uint8)[order]
    for s in range(len(ch)):
        h = ch[s][order]
        tot = h.sum()
        if tot <= 0:
            continue
        cum = np.cumsum(h) / tot
        ys = np.minimum((cum * H).astype(int), H)
        y0 = 0
        column = np.zeros((H, 3), dtype=np.uint8)
        prev = 0
        nzb = np.where(h > 0)[0]
        for bi in nzb:
            y1 = ys[bi]
            if y1 > prev:
                column[prev:y1] = cols[bi]
                prev = y1
        img[:, s * px:(s + 1) * px] = column[::-1][:, None, :]
    im = Image.fromarray(img)
    # 刻度：每 10 秒一条
    canvas = Image.new("RGB", (im.width, H + 18), (30, 30, 30))
    canvas.paste(im, (0, 0))
    d = ImageDraw.Draw(canvas); fnt = font(11)
    for s in range(0, len(ch), 10):
        d.line((s * px, H, s * px, H + 4), fill=(255, 255, 255))
        if s % 30 == 0:
            d.text((s * px + 2, H + 4), f"{s // 60}:{s % 60:02d}", font=fnt, fill=(255, 255, 255))
    canvas.save(out)
    print(out, canvas.size, f"{px}px/s")


def cmd_imgsheet(a):
    out, cols, cellw = a[0], int(a[1]), int(a[2])
    paths = a[3:]
    ims = []
    for p in paths:
        im = Image.open(p).convert("RGB")
        h = round(im.height * cellw / im.width)
        ims.append((os.path.basename(p), im.resize((cellw, h), Image.LANCZOS)))
    rows = (len(ims) + cols - 1) // cols
    rowh = [max(im.height for _, im in ims[r * cols:(r + 1) * cols]) for r in range(rows)]
    gap = 4
    sheet = Image.new("RGB", (cols * cellw + (cols + 1) * gap, sum(rowh) + (rows + 1) * gap), (40, 40, 40))
    d = ImageDraw.Draw(sheet); fnt = font(13)
    y = gap
    for r in range(rows):
        for c, (name, im) in enumerate(ims[r * cols:(r + 1) * cols]):
            x = gap + c * (cellw + gap)
            sheet.paste(im, (x, y))
            label(d, (x + 3, y + 2), name[:34], fnt)
        y += rowh[r] + gap
    sheet.save(out, quality=90)
    print(out, sheet.size)


if __name__ == "__main__":
    c = sys.argv[1]; args = sys.argv[2:]
    {"grid": cmd_grid, "sheet": cmd_sheet, "frame": cmd_frame, "strip": cmd_strip, "colorbar": cmd_colorbar, "imgsheet": cmd_imgsheet}[c](args)
