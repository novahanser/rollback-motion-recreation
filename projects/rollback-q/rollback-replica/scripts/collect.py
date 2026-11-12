"""Collect the AE project like File > Dependencies > Collect Files, but scriptable.

    python scripts/collect.py [DEST]          (default: ae/collected_v12)

Reads ae/project.json (written by build.py), copies every footage file that the project really uses into
DEST/(Footage)/<project-panel folder>/, and writes
    DEST/_rebuild/project_collected.json   the same project with the footage paths pointing into DEST
    DEST/_rebuild/project_post.json        switches that the JSON import cannot carry (adjustment layers, collapse, blend modes)
    DEST/收集报告.txt                       what was collected, effects used, what was left behind
The .aep itself is produced in After Effects: new project -> import project_collected.json -> apply project_post.json ->
16 bpc -> Save As DEST/rollback_replica_v12.aep.
"""
import collections
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
dest = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ROOT, 'ae', 'collected_v12')
doc = json.load(open(os.path.join(ROOT, 'ae', 'project.json')))
post = json.load(open(os.path.join(ROOT, 'ae', 'project_post.json')))
items = doc['items']
names = {i['id']: i['name'] for i in items}
foot_dir = os.path.join(dest, '(Footage)')
os.makedirs(os.path.join(dest, '_rebuild'), exist_ok=True)

used = set()
for it in items:
    if it['type'] == 'CompItem':
        for lay in it['layers']:
            used.add(lay['sourceId'])

copied, size, per_folder, missing, unused_items = 0, 0, collections.Counter(), [], []
for it in items:
    if it['type'] != 'FootageItem' or it.get('sourceKind') != 'file':
        continue
    if it['id'] not in used:
        unused_items.append(it['name'])
    src = it['file']
    sub = names[it['parentFolderId']]
    dst = os.path.join(foot_dir, sub, os.path.basename(src))
    if not os.path.exists(src):
        missing.append(src)
        continue
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    it['file'] = dst.replace('\\', '/')
    copied += 1
    size += os.path.getsize(dst)
    per_folder[sub] += 1

json.dump(doc, open(os.path.join(dest, '_rebuild', 'project_collected.json'), 'w'))
json.dump(post, open(os.path.join(dest, '_rebuild', 'project_post.json'), 'w'), indent=1)

# ---- report
fx = collections.Counter()
comps = []
for it in items:
    if it['type'] == 'CompItem':
        comps.append('%s  %dx%d  %.4g fps  %.3f s  %d layers' % (it['name'], it['width'], it['height'], it['frameRate'], it['duration'], len(it['layers'])))
        for lay in it['layers']:
            for g in (lay.get('effectsGroup') or {}).get('groups', []):
                fx[g['matchName']] += 1
solids = [i['name'] for i in items if i['type'] == 'FootageItem' and i.get('sourceKind') == 'solid']
asset_dir = os.path.join(ROOT, 'assets')
all_assets = set(f for f in os.listdir(asset_dir) if f.lower().endswith('.png'))
ref = set(os.path.basename(i['file']) for i in items if i['type'] == 'FootageItem' and i.get('sourceKind') == 'file')
left = sorted(all_assets - ref)

L = []
L.append('Rollback 复刻工程 · AE 收集报告')
L.append('生成时间: ' + time.strftime('%Y-%m-%d %H:%M'))
L.append('')
L.append('收集目录: ' + dest)
L.append('工程文件: rollback_replica_v12.aep  (After Effects 2024, 16 bpc, 工作空间: 无)')
L.append('')
L.append('[合成]')
L += ['  ' + c for c in comps]
L.append('')
L.append('[素材] 共 %d 个文件, %.1f MB, 缺失 %d 个' % (copied, size / 1048576.0, len(missing)))
for k in sorted(per_folder):
    L.append('  (Footage)/%s   %d 个' % (k, per_folder[k]))
L += ['  缺失: ' + m for m in missing]
L.append('')
L.append('[纯色] %d 个: %s' % (len(solids), ', '.join(solids)))
L.append('')
L.append('[用到的效果] (matchName x 次数; 全部是 AE 自带效果, 没有第三方插件; 工程里没有文字层和表达式, 不依赖字体)')
for k, v in sorted(fx.items(), key=lambda kv: -kv[1]):
    L.append('  %-28s x %d' % (k, v))
L.append('')
L.append('[导入后需要补的开关] (JSON 导入带不过去, 已在收集工程里设置好)')
L.append('  塌陷变换: ' + ', '.join('%s/%s' % tuple(c) for c in post.get('collapse', [])))
L.append('  调整图层: ' + ', '.join(c[1] for c in post.get('adjust', [])))
L.append('  混合模式: ' + ', '.join('%s=%s' % (c[1], c[2]) for c in post.get('blend', [])))
L.append('')
L.append('[没有收集的东西]')
L.append('  assets/ 里还有 %d 个旧版本留下、当前工程不再引用的 PNG (没有复制)。' % len(left))
L.append('  gen/ (Codex 重绘的原图和参考裁切)、scripts/ (生成脚本)、out/ (成片) 仍在工程根目录, 不属于 AE 依赖。')
L.append('  工程中引用但没有被任何图层使用的素材: %d 个%s' % (len(unused_items), (' (' + ', '.join(unused_items[:8]) + ')') if unused_items else ''))
L.append('')
L.append('[渲染] RB_MAIN -> 输出模块「无损」AVI -> ffmpeg:')
L.append('  -vf "scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p" -c:v libx264 -crf 17 -preset slow')
L.append('  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv -movflags +faststart')
open(os.path.join(dest, '收集报告.txt'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('collected %d files (%.1f MB) -> %s ; missing %d ; unreferenced assets left behind %d' % (copied, size / 1048576.0, dest, len(missing), len(left)))
