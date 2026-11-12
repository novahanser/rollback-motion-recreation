# -*- coding: utf-8 -*-
"""一条命令跑完一个视频的基础扫描。

用法: python -I scan_all.py <视频路径> <编号> [bpm]

依次运行 scan_video.py、scan_audio.py、report.py；给了 bpm 再运行 audit.py。
中间结果写到工作目录（默认是当前目录下的 motion_work/，可用环境变量 MOTION_WORK 改）。
没有音轨的视频只会跑 scan_video.py；之后可以用 vis.py、motion.py、typesize.py，其余脚本需要音频扫描的结果。
"""
import os, sys, subprocess

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.environ.get("MOTION_WORK") or os.path.join(os.getcwd(), "motion_work")


def run(script, *args):
    cmd = [sys.executable, "-I", os.path.join(HERE, script), *args]
    print(">", script, " ".join(args), flush=True)
    return subprocess.run(cmd, env=dict(os.environ, MOTION_WORK=WORK)).returncode


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    video, vid = sys.argv[1], sys.argv[2]
    bpm = sys.argv[3] if len(sys.argv) > 3 else None
    os.makedirs(WORK, exist_ok=True)
    if run("scan_video.py", video, WORK, vid):
        sys.exit("scan_video.py failed")
    if run("scan_audio.py", video, WORK, vid):
        print("没有可用的音轨，或音频扫描失败：跳过 report.py 和 audit.py。")
        return
    if run("report.py", vid):
        sys.exit("report.py failed")
    if bpm:
        run("audit.py", vid, bpm)
    else:
        print("没有给 bpm：先看 report.py 输出里的速度候选，用 acf.py 核对倍数关系，再运行 audit.py <编号> <bpm>。")


if __name__ == "__main__":
    main()
