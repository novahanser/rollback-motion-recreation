# -*- coding: utf-8 -*-
"""列出落在音频重音（起音强度前 4%）±1 帧内的画面内事件。用法: python -I accents.py <id>"""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
import audit
W = audit.WORK; vid = sys.argv[1]
meta = json.load(open(os.path.join(W, vid + "_meta.json"), encoding="utf-8"))
S = json.load(open(os.path.join(W, vid + "_summary.json"), encoding="utf-8"))
M = dict(np.load(os.path.join(W, vid + "_metrics.npz"))); A = dict(np.load(os.path.join(W, vid + "_audio.npz")))
pts = M["pts"].astype(float); fps = meta["fps"]; sr = float(A["env_sr"])
Af = audit.per_frame(A["envn"].astype(float), sr, pts, fps)
acc = audit.strong_onsets(Af, 96)
near = acc.copy(); near[1:] |= acc[:-1]; near[:-1] |= acc[1:]
pul = [e for e in S["events"] if e["kind"] == "pulse"]
hit = [e for e in pul if near[e["frame"]]]
print(vid, f"pulses {len(pul)}, on accents {len(hit)}; accent frames total {int(acc.sum())}")
print("  on-accent pulses (frame@time d×1000): " + "  ".join(f"{e['frame']}@{int(e['t'] // 60)}:{e['t'] % 60:04.1f}({e['d'] * 1000:.0f})" for e in hit))
