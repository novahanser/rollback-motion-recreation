# Rollback 长卷动态设计 · 复刻工程

原片：`D:\fable 复刻\41174437194-1-100027.mp4`（1920×1080，24 fps，272 帧，无声）。

## 成品（当前版本 v12）
| 文件 | 说明 |
|---|---|
| `out/rollback_replica_v12.mp4` | 复刻成片（AE 无损输出 → x264，bt709） |
| `out/compare_original_vs_replica_v12.mp4` | 上原片 / 下复刻的同步对比（带帧号） |
| `out/compare_v12/compare_01…08.jpg` | 64 个关键帧的上下对比图 |
| `out/pano_preview.jpg` | 复刻的 11000×1080 静态长卷 |
| `ae/rollback_replica.aep` | After Effects 2024 工程（`RB_MAIN` 为成片合成，`RB_WORLD` 为长卷） |
| `ae/collected_v12/` | 收集好的独立工程：`rollback_replica_v12.aep` + `(Footage)/`（516 个素材，按段落分文件夹）+ `收集报告.txt`；由 `scripts/collect.py` 生成 |
| `拆解分析.md` | 镜头表、相机曲线、逐元素实测运动、全局效果、字体、迭代记录、仍有差距的地方 |

旧版本（v5、v8、v11）的成片和对比留在 `out/` 里没有删。

## 结构
- `scripts/cam.py`：逐帧相机表（缩放 `s`、世界中心 `cx`），由原片实测；含 57–71、98–103 帧的配准修正。
- `scripts/ruler_off.py`：标尺刻度相对理想网格的逐帧偏移（由 `tools/make_ruler_off.py` 生成）。
- `scripts/lib.py`：绘图工具、`Layer` / `Scene`（世界坐标 + 关键帧助手）。
- `scripts/sec_a.py … sec_d.py`、`filmrun.py`、`fx.py`、`base.py`：各段元素与动画。
- `scripts/horn.py`：线框喇叭（双曲面线架）的姿态表和逐帧绘制。
- `scripts/chain3d.py`：珠链的三维旋转（轨道 / 透视 / 抽帧节奏的拟合值，逐帧渲染融合的铬珠）。
- `scripts/ae_export.py`：场景 → AE 工程 JSON（项目面板：`01_合成` / `02_素材`（按文件名前缀分段落子文件夹）/ `03_纯色`）。
- `scripts/collect.py`：把工程真正用到的素材收集到 `ae/collected_v12/` 并写出路径改好的工程 JSON 和收集报告。
- `gen/`：Codex imagegen（GPT 图像）生成的素材原图；`gen/ref/`：提交给它的原片参考裁切图；`assets/`：脚本产出的分层 PNG。
- `tools/`：测量脚本（标尺审计、世界坐标对齐的对比拼图 `wmont.py` / `wpair.py`、带网格的屏幕裁切 `sgrid.py`、珠链高光跟踪与拟合 `track_beads.py` / `fit_beads*.py` / `chain_track.py`、唱片跟踪等），以及各版本的补丁脚本 `patch_v*.py`。它们按「原片逐帧图在 `frames_full/`、渲染逐帧图在 `render/frames_<版本>/`」的相对路径工作，使用前先把视频拆成帧。

按原片参考重绘的素材：`pink-tube2`（绳子）、`chrome-shape2`（金属体）、`chain-cluster`（桌面图标组）、`buildings2`（白色小楼）、`sunset-city`（黄昏照片）、`deck-view`（开场甲板照片）、`chibi2`（小人）；v12 新增 `target-cutout`（靶子抠图）、`tongue-card2`（舌头卡片）、`escalator-bw`（扶梯）、`church-bw`（教堂）、`backdrop-lines` / `lower-lines`（C 段两张线稿）、`pole-lean`（斜电线杆）。`bead-chain2`、`bead-sprite`、`city-sil`、`target`、`lineart-machine` 已不再使用（珠链改为程序渲染）。

## 重新生成
```bash
python scripts/build.py pano
```
然后在 AE 里：删除旧的 `RB_REPLICA` 文件夹 → 用 aftereffects MCP 的 `ae_project_import_json` 导入 `ae/project.json` →
按 `ae/project_post.json` 补上调整层开关 / 塌陷开关 / 混合模式 → 用「无损」模板渲染 `RB_MAIN` → ffmpeg 转 H.264（参数见 `拆解分析.md` 第 11 节）。

依赖：Python 3 + Pillow + numpy；字体见 `拆解分析.md` 第 7 节（v9 起另外用到 Jura 和 Playfair Display）。
