# -*- coding: utf-8 -*-
"""逐帧比较两段已经对齐的视频（例如参考片段和它的复刻），判断「像不像」以及差在哪一类。

用法: python -I compare_clips.py <参考编号> <被比编号> [参考起始帧=0] [分段数=8]

两段视频都要先用 scan_video.py 扫描过。被比视频的第 0 帧对应参考视频的第「参考起始帧」帧，
比较的长度取两者重叠的部分。两段的帧率要相同。

输出:
  1. 逐帧的亮度、帧间差、白/黑/高彩度面积的相关系数 —— 时间骨架和明暗结构对不对
  2. 大事件（帧间差的突出峰值）的对齐 —— 参考里有的，被比里在 ±1 帧内找到几个；多出来几个
  3. 平均亮度、高彩度面积、细节密度的对比 —— 整体偏亮偏暗、彩色多了少了、细节够不够
  4. 分段的细节密度和高彩度面积 —— 差距集中在哪一段

颜色是否一致不在这里比（这里只看面积），用 cmp_color.py。
对齐是否正确可以先看第 1 项：帧间差的相关很低，多半是起始帧没对上。
"""
import os, sys
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
WORK = os.environ.get("MOTION_WORK") or os.path.join(os.getcwd(), "motion_work")   # 中间结果目录，可用环境变量 MOTION_WORK 改


def load(vid):
    return dict(np.load(os.path.join(WORK, vid + "_metrics.npz")))


def peaks(d):
    """帧间差的突出峰值：明显高于前后 8 帧的中位数，且是前后 2 帧里最大的。"""
    out = []
    for i in range(2, len(d) - 2):
        w = np.concatenate([d[max(0, i - 8):i], d[i + 1:i + 9]])
        if d[i] >= 0.012 and d[i] >= 2.5 * np.median(w) + 0.006 and d[i] >= d[i - 2:i + 3].max():
            out.append(i)
    return out


def corr(a, b):
    if a.std() == 0 or b.std() == 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    ref_id, test_id = sys.argv[1], sys.argv[2]
    off = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    nseg = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    R, T = load(ref_id), load(test_id)
    n = min(len(R["luma"]) - off, len(T["luma"]))
    if n < 12:
        sys.exit("重叠的帧太少，检查参考起始帧")
    r = {k: R[k][off:off + n].astype(np.float64) for k in ("luma", "d_abs", "white", "black", "color", "edge")}
    t = {k: T[k][:n].astype(np.float64) for k in ("luma", "d_abs", "white", "black", "color", "edge")}
    print(f"{ref_id} 第 {off}—{off + n - 1} 帧  对  {test_id} 第 0—{n - 1} 帧（共 {n} 帧）")

    print("1. 逐帧相关: " + "  ".join(f"{name} {corr(r[k][1:], t[k][1:]):.3f}" for name, k in
                                  (("亮度", "luma"), ("帧间差", "d_abs"), ("白色面积", "white"), ("黑色面积", "black"), ("高彩度面积", "color"))))

    pr, pt = peaks(r["d_abs"]), peaks(t["d_abs"])
    found = [f for f in pr if any(abs(f - g) <= 1 for g in pt)]
    miss = [f for f in pr if f not in found]
    extra = [g for g in pt if not any(abs(f - g) <= 1 for f in pr)]
    print(f"2. 大事件: 参考 {len(pr)} 个，被比 {len(pt)} 个；参考的事件在 ±1 帧内找到 {len(found)}/{len(pr)}")
    print(f"   没对上的（参考的帧号，从比较起点算）: {miss}")
    print(f"   多出来的（被比的帧号）: {extra}")

    def ratio(k):
        a, b = r[k].mean(), t[k].mean()
        return f"{a:.4f} 对 {b:.4f}（{(b / a - 1) * 100:+.0f}%）" if a > 0 else f"{a:.4f} 对 {b:.4f}"
    print(f"3. 平均亮度 {ratio('luma')} | 高彩度面积 {ratio('color')} | 细节密度 {ratio('edge')}")

    print("4. 分段（帧号从比较起点算）: 细节密度 参考/被比（差） | 高彩度面积 参考/被比（差）")
    step = max(1, n // nseg)
    for a in range(0, n, step):
        b = min(n, a + step)
        if b - a < max(4, step // 2):
            break
        e1, e2 = r["edge"][a:b].mean(), t["edge"][a:b].mean()
        c1, c2 = r["color"][a:b].mean(), t["color"][a:b].mean()
        de = f"{(e2 / e1 - 1) * 100:+.0f}%" if e1 > 0 else "—"
        dc = f"{(c2 / c1 - 1) * 100:+.0f}%" if c1 > 0.002 else "—"
        print(f"   f{a:4d}—{b - 1:4d}: {e1:.4f}/{e2:.4f}（{de}） | {c1:.3f}/{c2:.3f}（{dc}）")


if __name__ == "__main__":
    main()
