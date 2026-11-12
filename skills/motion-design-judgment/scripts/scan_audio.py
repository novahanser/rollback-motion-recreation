# -*- coding: utf-8 -*-
"""音频扫描：起音包络、整体速度估计（BPM 候选）、节拍相位、分段响度。

用法: python -I scan_audio.py <video> <outdir> <id>
输出: <outdir>/<id>_audio.npz (onset 包络 150Hz, rms/低频/高频能量 每 0.5 秒), <id>_audio.json
"""
import sys, os, json, subprocess
import numpy as np

FF = os.environ.get("FFMPEG_DIR", "")   # ffmpeg 不在 PATH 里时，把环境变量 FFMPEG_DIR 指到它所在的目录
FFMPEG = os.path.join(FF, "ffmpeg") if FF else "ffmpeg"
FFPROBE = os.path.join(FF, "ffprobe") if FF else "ffprobe"
SR = 22050
HOP = 147          # 150 Hz 包络
NFFT = 1024
ENV_SR = SR / HOP


def load_audio(path):
    cmd = [FFMPEG, "-v", "error", "-i", path, "-map", "0:a:0", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"]
    raw = subprocess.check_output(cmd)
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def stft_mag(x):
    win = np.hanning(NFFT).astype(np.float32)
    nfr = 1 + (len(x) - NFFT) // HOP
    out = np.empty((nfr, NFFT // 2 + 1), dtype=np.float32)
    step = 4096
    for s in range(0, nfr, step):
        e = min(nfr, s + step)
        idx = (np.arange(s, e)[:, None] * HOP) + np.arange(NFFT)[None, :]
        out[s:e] = np.abs(np.fft.rfft(x[idx] * win, axis=1)).astype(np.float32)
    return out


def band_matrix(nb=40, fmin=30.0, fmax=10000.0):
    freqs = np.fft.rfftfreq(NFFT, 1.0 / SR)
    edges = np.geomspace(fmin, fmax, nb + 1)
    M = np.zeros((nb, len(freqs)), dtype=np.float32)
    for i in range(nb):
        sel = (freqs >= edges[i]) & (freqs < edges[i + 1])
        if not sel.any():
            sel[np.argmin(np.abs(freqs - (edges[i] + edges[i + 1]) / 2))] = True
        M[i, sel] = 1.0
    return M, edges


def onset_env(mag):
    M, edges = band_matrix()
    bands = mag @ M.T
    lb = np.log1p(100.0 * bands)
    flux = np.maximum(lb[1:] - lb[:-1], 0.0)
    env = flux.sum(axis=1)
    env = np.concatenate([[0.0], env]).astype(np.float32)
    # 低频(<=150Hz) 与高频(>=4kHz) 的通量，分别近似底鼓和镲/噪声
    lo = flux[:, edges[:-1] < 150].sum(axis=1); hi = flux[:, edges[:-1] >= 4000].sum(axis=1)
    lo = np.concatenate([[0.0], lo]).astype(np.float32); hi = np.concatenate([[0.0], hi]).astype(np.float32)
    return env, lo, hi, bands


def local_norm(env, win=int(ENV_SR * 1.0)):
    k = np.ones(win, dtype=np.float32) / win
    m = np.convolve(env, k, mode="same")
    e = np.maximum(env - m, 0.0)
    s = e.std() + 1e-9
    return e / s


def comb_score(env, period, nphase=None):
    """对给定周期（包络采样数，可为小数），返回最佳相位与得分。"""
    n = len(env)
    P = period
    nph = int(np.ceil(P)) if nphase is None else nphase
    best = (-1.0, 0.0)
    kmax = int((n - 1 - P) / P)
    ks = np.arange(kmax)
    for ph in np.linspace(0, P, nph, endpoint=False):
        pos = ph + ks * P
        i0 = np.floor(pos).astype(np.int64); fr = pos - i0
        v = env[i0] * (1 - fr) + env[np.minimum(i0 + 1, n - 1)] * fr
        sc = float(v.mean())
        if sc > best[0]:
            best = (sc, float(ph))
    return best


def estimate_tempo(envn):
    n = len(envn)
    # 自相关（FFT）
    f = np.fft.rfft(envn, 2 * n)
    acf = np.fft.irfft(f * np.conj(f))[:n]
    acf /= acf[0] + 1e-9
    cands = []
    bpms = np.arange(60.0, 250.01, 0.25)
    sc = np.zeros_like(bpms)
    for i, b in enumerate(bpms):
        L = 60.0 / b * ENV_SR
        s = 0.0
        for m, wgt in ((1, 1.0), (2, 0.8), (3, 0.5), (4, 0.6)):
            x = L * m
            i0 = int(np.floor(x)); fr = x - i0
            if i0 + 1 < n:
                s += wgt * (acf[i0] * (1 - fr) + acf[i0 + 1] * fr)
        sc[i] = s
    order = np.argsort(sc)[::-1]
    picked = []
    for idx in order:
        b = bpms[idx]
        if all(abs(b - p) > 3.0 for p, _ in picked):
            picked.append((float(b), float(sc[idx])))
        if len(picked) >= 6:
            break
    # 精细化：在每个候选附近做梳状相关
    refined = []
    for b, s in picked:
        best = (-1.0, b, 0.0)
        for bb in np.arange(b - 0.6, b + 0.6001, 0.01):
            P = 60.0 / bb * ENV_SR
            score, ph = comb_score(envn, P, nphase=24)
            if score > best[0]:
                best = (score, float(bb), ph)
        P = 60.0 / best[1] * ENV_SR
        score, ph = comb_score(envn, P, nphase=int(np.ceil(P)))
        refined.append(dict(bpm=round(best[1], 3), acf_score=round(s, 4), comb_score=round(score, 4), phase_s=round(ph / ENV_SR, 4)))
    return refined, acf


def main():
    path, outdir, vid = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    x = load_audio(path)
    mag = stft_mag(x)
    env, lo, hi, bands = onset_env(mag)
    envn = local_norm(env)
    refined, acf = estimate_tempo(envn)
    # 分段能量（0.5 s）
    seg = int(ENV_SR * 0.5)
    nseg = len(env) // seg
    pw = (mag ** 2)
    freqs = np.fft.rfftfreq(NFFT, 1.0 / SR)
    tot = pw.sum(axis=1); low = pw[:, freqs < 150].sum(axis=1); high = pw[:, freqs >= 4000].sum(axis=1)
    def segm(a):
        return a[:nseg * seg].reshape(nseg, seg).mean(axis=1)
    rms_db = 10 * np.log10(segm(tot) + 1e-9); low_db = 10 * np.log10(segm(low) + 1e-9); high_db = 10 * np.log10(segm(high) + 1e-9)
    onset_rate = segm(envn)
    np.savez_compressed(os.path.join(outdir, vid + "_audio.npz"), env=env, envn=envn.astype(np.float32), lo=lo, hi=hi,
                        rms_db=rms_db.astype(np.float32), low_db=low_db.astype(np.float32), high_db=high_db.astype(np.float32),
                        onset_rate=onset_rate.astype(np.float32), env_sr=np.float32(ENV_SR))
    info = dict(id=vid, duration=round(len(x) / SR, 3), env_sr=ENV_SR, tempo_candidates=refined)
    with open(os.path.join(outdir, vid + "_audio.json"), "w", encoding="utf-8") as fo:
        json.dump(info, fo, ensure_ascii=False, indent=1)
    print(vid, "audio", round(len(x) / SR, 2), "s; tempo:", [(r["bpm"], r["comb_score"]) for r in refined[:4]])


if __name__ == "__main__":
    main()
