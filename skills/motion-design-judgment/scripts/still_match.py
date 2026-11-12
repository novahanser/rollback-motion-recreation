# -*- coding: utf-8 -*-
"""把一张静态图和视频里某个时间点附近的帧逐帧对照，找出最接近的帧，并估计图与帧之间的缩放、平移（即裁切关系）。

用法: python -I still_match.py <图片> <编号> <约略秒数> [前后帧数=15] [输出前缀]

做法:
  1. 在约略时间前后各取若干帧（原始分辨率）。
  2. 图片与每一帧做 ORB 特征匹配，用 RANSAC 拟合相似变换（缩放、旋转、平移），把图片变换到帧的坐标系。
  3. 在两者重叠的区域里算平均绝对差（先各自转灰度并做轻微模糊，避免压缩噪声主导）。
  4. 报告差最小的帧、变换参数、图片覆盖了帧的哪一块（或超出多少）、重叠区域里 RGB 的平均差。
  5. 可选输出：并排图（上：帧；中：对齐后的图片；下：差的绝对值×3）。

颜色的比较只在重叠区域做；图片是 JPEG，视频是平台转码，几级以内的差别不说明问题。
"""
import os, sys
import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
import vis  # noqa: E402


def imread_u(path):
    data = np.fromfile(path, dtype=np.uint8)
    im = cv2.imdecode(data, cv2.IMREAD_COLOR)
    return cv2.cvtColor(im, cv2.COLOR_BGR2RGB)


def fit(still_g, frame_g, orb):
    k1, d1 = orb.detectAndCompute(still_g, None)
    k2, d2 = orb.detectAndCompute(frame_g, None)
    if d1 is None or d2 is None or len(k1) < 20 or len(k2) < 20:
        return None
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    m = bf.match(d1, d2)
    if len(m) < 20:
        return None
    p1 = np.float32([k1[x.queryIdx].pt for x in m]); p2 = np.float32([k2[x.trainIdx].pt for x in m])
    A, inl = cv2.estimateAffinePartial2D(p1, p2, method=cv2.RANSAC, ransacReprojThreshold=3.0, maxIters=5000, confidence=0.999)
    if A is None:
        return None
    return A, int(inl.sum()), len(m)


def main():
    still_path, vid, t0 = sys.argv[1], sys.argv[2], float(sys.argv[3])
    half = int(sys.argv[4]) if len(sys.argv) > 4 else 15
    outp = sys.argv[5] if len(sys.argv) > 5 else None
    m = vis.meta(vid)
    n0, _ = vis.parse_pos(m, str(t0))
    still = imread_u(still_path)
    sh, sw = still.shape[:2]
    W, H = m["width"], m["height"]
    a = max(0, n0 - half); cnt = min(len(m["pts"]) - a, 2 * half + 1)
    frames = [np.array(f) for f in vis.read_frames(m, a, cnt, W)]
    orb = cv2.ORB_create(nfeatures=6000)
    sg = cv2.cvtColor(still, cv2.COLOR_RGB2GRAY)
    res = []
    for i, fr in enumerate(frames):
        fg = cv2.cvtColor(fr, cv2.COLOR_RGB2GRAY)
        r = fit(sg, fg, orb)
        if r is None:
            res.append((a + i, None)); continue
        A, ninl, nm = r
        warped = cv2.warpAffine(still, A, (W, H), flags=cv2.INTER_AREA, borderValue=(0, 0, 0))
        mask = cv2.warpAffine(np.full((sh, sw), 255, np.uint8), A, (W, H), flags=cv2.INTER_NEAREST) > 0
        g1 = cv2.GaussianBlur(cv2.cvtColor(warped, cv2.COLOR_RGB2GRAY), (5, 5), 0).astype(np.float32)
        g2 = cv2.GaussianBlur(fg, (5, 5), 0).astype(np.float32)
        d = np.abs(g1 - g2)[mask].mean() if mask.any() else 1e9
        res.append((a + i, dict(A=A, inl=ninl, nm=nm, d=float(d), cover=float(mask.mean()), warped=warped, mask=mask)))
    ok = [(n, r) for n, r in res if r is not None]
    if not ok:
        print("no match"); return
    ok.sort(key=lambda x: x[1]["d"])
    print(f"{os.path.basename(still_path)} ({sw}x{sh}) vs {vid} around {t0:.2f}s (f{n0}), frame {W}x{H}, fps {m['fps']:g}")
    print("  frame: mean|Δgray| (inliers/matches)  — sorted by frame")
    line = []
    for n, r in res:
        line.append(f"f{n}:{'—' if r is None else format(r['d'], '.1f')}")
    print("   " + "  ".join(line))
    # 差最小的几帧各自的变换：帧里的画面如果在缩放或平移，这里会看到逐帧的变化
    near = sorted(ok[:10], key=lambda x: x[0])
    print("  per-frame transform of the closest frames (scale, shift x, shift y, mean|Δgray|):")
    print("   " + "  ".join(f"f{nn}:{float(np.hypot(rr['A'][0, 0], rr['A'][1, 0])):.4f},{rr['A'][0, 2]:+.1f},{rr['A'][1, 2]:+.1f},{rr['d']:.1f}" for nn, rr in near))
    n, r = ok[0]
    A = r["A"]; s = float(np.hypot(A[0, 0], A[1, 0])); rot = float(np.degrees(np.arctan2(A[1, 0], A[0, 0])))
    # 图片四角落在帧坐标系里的位置
    c = np.array([[0, 0, 1], [sw, 0, 1], [0, sh, 1], [sw, sh, 1]], np.float32) @ A.T
    x0, y0 = c[:, 0].min(), c[:, 1].min(); x1, y1 = c[:, 0].max(), c[:, 1].max()
    t = float(m["pts"][n])
    print(f"  best: f{n} ({int(t // 60)}:{t % 60:05.2f})  mean|Δgray| {r['d']:.2f}  inliers {r['inl']}/{r['nm']}")
    print(f"  transform still->frame: scale {s:.4f}, rotation {rot:+.3f}°, shift ({A[0, 2]:+.1f}, {A[1, 2]:+.1f}) px")
    print(f"  still covers frame x {x0:.1f}..{x1:.1f} of {W}, y {y0:.1f}..{y1:.1f} of {H}  (coverage {r['cover'] * 100:.1f}% of frame)")
    fr = frames[n - a].astype(np.int32); wp = r["warped"].astype(np.int32); mk = r["mask"]
    dd = np.abs(fr - wp)[mk]
    print(f"  overlap RGB mean|Δ|: R {dd[:, 0].mean():.1f} G {dd[:, 1].mean():.1f} B {dd[:, 2].mean():.1f}; mean signed (still−frame): "
          f"R {(wp - fr)[mk][:, 0].mean():+.1f} G {(wp - fr)[mk][:, 1].mean():+.1f} B {(wp - fr)[mk][:, 2].mean():+.1f}")
    # 高彩度像素上的差
    ch = fr.max(2) - fr.min(2); sel = mk & (ch >= 85)
    if sel.sum() > 500:
        print(f"  on frame's high-chroma px ({sel.mean() * 100:.1f}%): frame mean {tuple(int(v) for v in fr[sel].mean(0).round())}  still mean {tuple(int(v) for v in wp[sel].mean(0).round())}")
    if outp:
        diff = np.clip(np.abs(fr - wp) * 3, 0, 255).astype(np.uint8); diff[~mk] = 40
        stack = np.vstack([frames[n - a], r["warped"], diff])
        sc = 1500 / W
        out = cv2.resize(stack, (1500, int(stack.shape[0] * sc)), interpolation=cv2.INTER_AREA)
        cv2.imencode(".jpg", cv2.cvtColor(out, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])[1].tofile(outp + f"_f{n}.jpg")
        np.save(outp + "_A.npy", A)
        print("  saved", outp + f"_f{n}.jpg")


if __name__ == "__main__":
    main()
