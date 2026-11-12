# -*- coding: utf-8 -*-
"""把工作目录里所有 <id>_audit.json 汇总成 CSV，并打印一张表。用法: python -I audit_table.py <out.csv>"""
import os, sys, json, glob, csv
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
W = os.environ.get("MOTION_WORK") or os.path.join(os.getcwd(), "motion_work")   # 中间结果目录，可用环境变量 MOTION_WORK 改
rows = []
for f in sorted(glob.glob(os.path.join(W, "*_audit.json"))):
    a = json.load(open(f, encoding="utf-8")); vid = a["id"]
    A = a.get("A", {}); B = a.get("B"); C = a["C"]; D = a["D"]; E = a["E"]
    def g(kind, key, sub=None):
        x = A.get(kind)
        if not x: return ""
        if sub:
            x = x.get(sub)
            if not x: return ""
        return x.get(key, "")
    best = ""
    if B:
        n = a["n_cut"]; Rb = B["R_by_period"]
        sig = [(float(v), k) for k, v in Rb.items() if np.exp(-n * float(v) ** 2) < 0.01]
        if sig:
            sig.sort(reverse=True); best = f"{sig[0][1]}拍 R={sig[0][0]:.2f}"
            more = [f"{k}拍 {v:.2f}" for v, k in sig[1:3]]
            if more: best += "（另 " + "、".join(more) + "）"
        else:
            best = "无显著"
    spec = C["spectrum"]; prom = "、".join(f"{k}帧 {v}" for k, v in spec.items() if v >= 2.0)
    rows.append(dict(id=vid, cuts=a["n_cut"], pulses=a["n_pulse"], cut_lock=best,
                     cut_accent_lift=g("cut", "lift", "accent"), cut_accent_z=g("cut", "z", "accent"),
                     pulse_accent_lift=g("pulse", "lift", "accent"), pulse_accent_z=g("pulse", "z", "accent"),
                     motion_high=D.get("motion_high"), motion_rms=D.get("motion_rms"), cuts_rms=D.get("cuts_rms"),
                     section_hit=f"{E['hit']}/{E['n']}", section_chance=E["chance"], step_prominent=prom,
                     step_frac_3=C["frac"]["3"], step_frac_any=round(sum(C["frac"].values()), 3)))
with open(sys.argv[1], "w", newline="", encoding="utf-8-sig") as fo:
    w = csv.DictWriter(fo, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print("| 编号 | 硬切 | 切点的拍周期锁定（p<0.01） | 切点×重音 | 画面内事件×重音 | 运动量~高频能量 | 段落交界命中 | 突出的步进周期 |")
print("|---|---:|---|---:|---:|---:|---|---|")
for r in rows:
    def lz(l, z):
        return f"{l:.2f}（z {z:+.1f}）" if l != "" else "—"
    mh = "—" if r["motion_high"] is None else f"{r['motion_high']:+.2f}"
    print(f"| {r['id']} | {r['cuts']} | {r['cut_lock'] or '未估速度'} | {lz(r['cut_accent_lift'], r['cut_accent_z'])} | {lz(r['pulse_accent_lift'], r['pulse_accent_z'])} | {mh} | {r['section_hit']}（随机 {r['section_chance'] * 100:.0f}%） | {r['step_prominent'] or '无'} |")
