# -*- coding: utf-8 -*-
"""估计一段连续画面的整体运动曲线（相似变换：缩放、旋转、平移），用来判断缓动类型。

用法: python -I motion.py <id> <f0> <f1> [宽=640]
输出每帧相对上一帧的 缩放%（>0 放大）、旋转°、平移 x/y（占画面宽度的 ‰）、内点数。
内点少（<25）的帧不可信：画面是纯色块、被切点打断，或各层运动不一致。
"""
import sys, os
import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
import vis  # noqa: E402


def main():
    vid, f0, f1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    W = int(sys.argv[4]) if len(sys.argv) > 4 else 640
    m = vis.meta(vid)
    frames = vis.read_frames(m, f0, f1 - f0 + 1, W)
    gray = [cv2.cvtColor(np.array(im), cv2.COLOR_RGB2GRAY) for im in frames]
    orb = cv2.ORB_create(1500)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    kp_prev, des_prev = orb.detectAndCompute(gray[0], None)
    print(f"{vid} f{f0}-{f1} ({m['fps']:g} fps)  frame: scale% rot° tx‰ ty‰ inliers")
    rows = []
    for i in range(1, len(gray)):
        kp, des = orb.detectAndCompute(gray[i], None)
        s = r = tx = ty = float("nan"); inl = 0
        if des is not None and des_prev is not None and len(kp) >= 8 and len(kp_prev) >= 8:
            mt = bf.match(des_prev, des)
            if len(mt) >= 8:
                src = np.float32([kp_prev[x.queryIdx].pt for x in mt]); dst = np.float32([kp[x.trainIdx].pt for x in mt])
                A, mask = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=2.0)
                if A is not None:
                    inl = int(mask.sum())
                    s = (np.hypot(A[0, 0], A[1, 0]) - 1) * 100
                    r = np.degrees(np.arctan2(A[1, 0], A[0, 0]))
                    # 以画面中心为参照的平移
                    cx, cy = gray[i].shape[1] / 2, gray[i].shape[0] / 2
                    px = A[0, 0] * cx + A[0, 1] * cy + A[0, 2] - cx; py = A[1, 0] * cx + A[1, 1] * cy + A[1, 2] - cy
                    tx = px / gray[i].shape[1] * 1000; ty = py / gray[i].shape[1] * 1000
        rows.append((f0 + i, s, r, tx, ty, inl))
        kp_prev, des_prev = kp, des
    for k in range(0, len(rows), 6):
        print("  " + " | ".join(f"f{f}: {s:+5.1f} {r:+5.1f} {tx:+5.0f} {ty:+5.0f} ({n})" for f, s, r, tx, ty, n in rows[k:k + 6]))


if __name__ == "__main__":
    main()
