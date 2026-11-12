import numpy as np, wave, json
w = wave.open('src/audio_mono.wav', 'rb'); sr = w.getframerate(); n = w.getnframes()
x = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
print('sr', sr, 'dur', n / sr)
N = 1024; hop = 147  # 147 samples @22050 = 1/150 s
win = np.hanning(N)
frames = 1 + (len(x) - N) // hop
S = np.zeros((frames, N // 2 + 1), np.float32)
for i in range(frames):
    S[i] = np.abs(np.fft.rfft(x[i * hop:i * hop + N] * win))
L = np.log1p(30 * S)
flux = np.maximum(L[1:] - L[:-1], 0)
freqs = np.fft.rfftfreq(N, 1 / sr)
low = flux[:, freqs < 200].sum(axis=1); mid = flux[:, (freqs >= 200) & (freqs < 2500)].sum(axis=1); high = flux[:, freqs >= 2500].sum(axis=1)
tot = flux.sum(axis=1)
t = (np.arange(len(tot)) + 1) * hop / sr + N / 2 / sr
def peaks(env, thr_rel=0.30, mind=0.07):
    env = env / env.max(); out = []
    md = int(mind * sr / hop)
    for i in range(2, len(env) - 2):
        if env[i] > thr_rel and env[i] == env[max(0, i - md):i + md + 1].max():
            out.append((round(float(t[i]), 3), round(float(env[i]), 2)))
    return out
pk = peaks(tot, 0.22)
print('onsets (time s -> frame @24fps, strength):')
print(' '.join('%.2fs/f%.1f(%.2f)' % (a, a * 24, b) for a, b in pk))
pl = peaks(low, 0.25, 0.12)
print('low-band (kick) onsets:'); print(' '.join('f%.1f(%.2f)' % (a * 24, b) for a, b in pl))
# tempo by autocorrelation of onset envelope
env = tot - tot.mean(); ac = np.correlate(env, env, 'full')[len(env) - 1:]; ac /= ac[0]
fps_env = sr / hop
best = sorted([(ac[int(round(fps_env * 60 / bpm))], bpm) for bpm in np.arange(60, 220, 0.5)], reverse=True)[:8]
print('tempo candidates (acf, bpm):', [(round(float(a), 3), float(b)) for a, b in best])
rms = np.array([np.sqrt((x[i * 919:(i + 1) * 919] ** 2).mean()) for i in range(len(x) // 919)])  # per video frame
print('rms per frame (x100):'); print(' '.join('%d' % int(v * 100) for v in rms))
json.dump({'onsets': pk, 'low': pl}, open('audio_onsets.json', 'w'))
