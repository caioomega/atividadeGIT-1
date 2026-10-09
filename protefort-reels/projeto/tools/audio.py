"""Synthesize the music bed + SFX for the Protefort reel.
usage: python3 audio.py <sfx.json> <cues.js> <outdir>
Writes music.wav, sfx.wav (48 kHz stereo float->16 bit)."""
import sys, json, re, os
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 48000
rng = np.random.default_rng(7)
sfx_path, cues_path, outdir = sys.argv[1:4]
meta = json.load(open(sfx_path))
DUR = meta['duration']
cues = {k: float(v) for k, v in re.findall(r'"?(\w+)"?:\s*([\d.]+)', open(cues_path).read())}
N = int((DUR + 1.0) * SR)

def tt(d): return np.arange(int(d * SR)) / SR
def env_exp(d, tau): return np.exp(-tt(d) / tau)
def noise(d): return rng.standard_normal(int(d * SR))
def bp(x, lo, hi, order=2): return signal.sosfilt(signal.butter(order, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def hp(x, f, order=2): return signal.sosfilt(signal.butter(order, f, 'highpass', fs=SR, output='sos'), x)
def lp(x, f, order=2): return signal.sosfilt(signal.butter(order, f, 'lowpass', fs=SR, output='sos'), x)
def sweep_sine(f0, f1, d, curve=4.0):
    t = tt(d); f = f1 + (f0 - f1) * np.exp(-t * curve / d * 3)
    return np.sin(2 * np.pi * np.cumsum(f) / SR)
def saw(f, d, maxh=7000):
    t = tt(d); y = np.zeros_like(t)
    for k in range(1, int(maxh / f) + 1): y += np.sin(2 * np.pi * k * f * t) / k
    return y * 0.6
def svf_sweep(x, fc, q=0.7):
    """time-varying state-variable bandpass; fc is an array (Hz) per sample"""
    y = np.zeros_like(x); low = band = 0.0
    for i in range(len(x)):
        f = 2 * np.sin(np.pi * min(fc[i], SR / 6) / SR)
        high = x[i] - low - q * band
        band += f * high; low += f * band
        y[i] = band
    return y
def norm(x, peak=1.0): m = np.max(np.abs(x)) or 1; return x / m * peak
def stereo(x, pan=0.0):
    l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
    return np.stack([x * l, x * r], 1)
def ir(d=1.3, tau=0.35):
    t = tt(d); e = np.exp(-t / tau)
    return np.stack([lp(noise(d), 6000) * e, lp(noise(d), 6000) * e], 1) * 0.08
IR = ir()
def reverb(st, wet=0.25):
    out = np.stack([signal.fftconvolve(st[:, c], IR[:, c])[:len(st)] for c in range(2)], 1)
    return st + out * wet

# ---------------- SFX palette ----------------
def mk_whoosh(d=0.42, f0=350, f1=3200, f2=700, gain=1.0):
    n = noise(d); t = tt(d); k = t / d
    fc = np.where(k < 0.55, f0 + (f1 - f0) * (k / 0.55) ** 1.5, f1 + (f2 - f1) * ((k - 0.55) / 0.45))
    y = svf_sweep(n, fc, q=0.55)
    e = np.sin(np.pi * np.clip(k, 0, 1)) ** 1.6
    y = norm(y * e) * gain
    pan = np.linspace(-0.7, 0.7, len(y))
    return np.stack([y * np.cos((pan + 1) * np.pi / 4), y * np.sin((pan + 1) * np.pi / 4)], 1)
def mk_whoosh_down():
    w = mk_whoosh(0.34, 3600, 2400, 260)
    s = sweep_sine(500, 70, 0.34, 2) * np.linspace(0, 1, int(0.34 * SR)) ** 2 * 0.35
    return w + stereo(s)
def mk_impact():
    d = 1.4
    sub = sweep_sine(110, 34, d, 3) * env_exp(d, 0.42)
    crack = lp(noise(d), 2500) * env_exp(d, 0.05) * 0.9
    body = bp(noise(d), 120, 900) * env_exp(d, 0.18) * 0.7
    y = np.tanh((sub * 1.2 + crack + body) * 1.6)
    return reverb(stereo(norm(y)), 0.5)
def mk_pop():
    d = 0.16
    y = sweep_sine(1100, 380, d, 5) * env_exp(d, 0.035) + bp(noise(d), 2000, 6000) * env_exp(d, 0.004) * 0.4
    return reverb(stereo(norm(y) * 0.8), 0.2)
def mk_click():
    d = 0.06
    y = np.sin(2 * np.pi * 2300 * tt(d)) * env_exp(d, 0.008) + bp(noise(d), 3000, 9000) * env_exp(d, 0.003)
    return stereo(norm(y) * 0.7)
def mk_tick():
    d = 0.04
    return stereo(norm(np.sin(2 * np.pi * 3100 * tt(d)) * env_exp(d, 0.006)) * 0.5)
def bell(f, d=1.2):
    t = tt(d); y = np.zeros_like(t)
    for m, a, tau in [(1, 1, 0.5), (2.0, 0.5, 0.3), (3.01, 0.25, 0.18), (5.4, 0.12, 0.08)]:
        y += a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / tau)
    return y * np.minimum(1, t / 0.003)
def mk_ding():
    d = 1.4; y = np.zeros(int(d * SR))
    b1 = bell(1318.5); y[:len(b1)] += b1
    o = int(0.07 * SR); b2 = bell(1975.5, d - 0.07); y[o:o + len(b2)] += b2 * 0.8
    return reverb(stereo(norm(y) * 0.7), 0.45)
def mk_stamp():
    d = 0.6
    y = sweep_sine(160, 55, d, 4) * env_exp(d, 0.12) + bp(noise(d), 500, 2500) * env_exp(d, 0.03) * 0.9
    return reverb(stereo(norm(np.tanh(y * 1.5))), 0.35)
def mk_step():
    d = 0.25
    y = sweep_sine(120, 50, d, 4) * env_exp(d, 0.06) + lp(noise(d), 1200) * env_exp(d, 0.02) * 0.5
    return stereo(norm(y) * 0.8)
def mk_swoosh():
    return mk_whoosh(0.55, 900, 5200, 2200, 0.7)

PAL = {k: f() for k, f in {
    'whoosh': mk_whoosh, 'whoosh_down': mk_whoosh_down, 'impact': mk_impact, 'pop': mk_pop, 'click': mk_click,
    'tick': mk_tick, 'ding': mk_ding, 'stamp': mk_stamp, 'step': mk_step, 'swoosh': mk_swoosh}.items()}
VOL = {'whoosh': 0.42, 'whoosh_down': 0.42, 'impact': 0.9, 'pop': 0.5, 'click': 0.4, 'tick': 0.32, 'ding': 0.45, 'stamp': 0.75, 'step': 0.45, 'swoosh': 0.38}

sfx = np.zeros((N, 2))
for ev in meta['events']:
    s = PAL[ev['type']] * VOL[ev['type']] * ev['g']
    i = int(ev['t'] * SR)
    if ev['type'] in ('whoosh', 'swoosh'):  # whooshes peak in the middle: lead them in
        i = max(0, i - int(0.12 * SR))
    j = min(N, i + len(s)); sfx[i:j] += s[:j - i]

# ---------------- music ----------------
BPM = 124.0
beat = 60 / BPM
t0 = cues['pesado']                       # bar 0 downbeat lands on the hook impact
music = np.zeros((N, 2)); kick_env = np.ones(N)
def add(buf, x, t, gain=1.0):
    i = int(round(t * SR))
    if i < 0: x = x[-i:]; i = 0
    j = min(len(buf), i + len(x))
    if j > i: buf[i:j] += x[:j - i] * gain

def kick():
    d = 0.42
    y = sweep_sine(160, 46, d, 6) * env_exp(d, 0.16) + bp(noise(d), 1500, 6000) * env_exp(d, 0.003) * 0.3
    return np.tanh(y * 1.3)
def clap():
    d = 0.35; y = np.zeros(int(d * SR))
    for k, o in enumerate([0, 0.011, 0.022]):
        b = bp(noise(0.02), 900, 3500); i = int(o * SR); y[i:i + len(b)] += b * np.linspace(1, 0, len(b))
    tail = bp(noise(d), 900, 3200) * env_exp(d, 0.07)
    i = int(0.03 * SR); y[i:] += tail[:len(y) - i]
    return norm(y)
def hat(open_=False):
    d = 0.25 if open_ else 0.06
    return norm(hp(noise(d), 7500, 4) * env_exp(d, 0.09 if open_ else 0.015))
K, CL, HC, HO = kick(), clap(), hat(), hat(True)

prog = [(110.0, [220.0, 261.63, 329.63]),    # Am
        (87.31, [174.61, 220.0, 261.63]),    # F
        (130.81, [261.63, 329.63, 392.0]),   # C
        (98.0, [196.0, 246.94, 293.66])]     # G
def stab(freqs, d=0.22):
    y = sum(saw(f * dt, d) for f in freqs for dt in (0.995, 1.0, 1.006))
    y = lp(y, 2600) * env_exp(d, 0.07) * np.minimum(1, tt(d) / 0.004)
    return y
def bass_note(f, d):
    y = lp(saw(f, d) + 0.5 * np.sin(2 * np.pi * f * tt(d)), 700) * np.minimum(1, tt(d) / 0.005) * np.exp(-tt(d) / (d * 1.2))
    return np.tanh(y * 1.8)
def pad(freqs, d):
    y = sum(saw(f * dt, d, 4000) for f in freqs for dt in (0.993, 1.0, 1.008))
    a = np.minimum(1, tt(d) / 0.6) * np.minimum(1, (d - tt(d)) / 0.4)
    return lp(y, 1400) * a

drums = np.zeros((N, 2)); bassb = np.zeros((N, 2)); synth = np.zeros((N, 2))
brk0, brk1 = cues['protecao'] - 0.25, cues['protefort']   # breakdown window
end_hit = cues['end'] - 2.0
bar = 0
while True:
    tb = t0 + bar * 4 * beat
    if tb > DUR: break
    root, ch = prog[bar % 4]
    for b in range(4):
        tbeat = tb + b * beat
        in_brk = brk0 <= tbeat < brk1
        if tbeat > end_hit + 0.01 or in_brk: continue
        add(drums, stereo(K), tbeat, 0.95)
        i = int(tbeat * SR); L = int(0.3 * SR)
        if i < N: kick_env[i:i + L] = np.minimum(kick_env[i:i + L], 0.25 + 0.75 * (np.arange(min(L, N - i)) / L) ** 0.7)
        if b in (1, 3): add(drums, stereo(CL, 0.05), tbeat, 0.5)
        add(drums, stereo(HC, -0.3), tbeat + beat * 0.25, 0.16)
        add(drums, stereo(HO, 0.3), tbeat + beat * 0.5, 0.22)
        add(drums, stereo(HC, -0.3), tbeat + beat * 0.75, 0.12)
        add(bassb, stereo(bass_note(root, beat * 0.45)), tbeat + beat * 0.5, 0.42)
        add(synth, stereo(stab(ch), 0.15 * (1 if b % 2 else -1)), tbeat + beat * 0.5, 0.11)
    bar += 1

# breakdown: pad + snare roll + riser into the PROTEFORT drop
bd = brk1 - brk0
add(synth, stereo(pad(prog[0][1], bd + 0.2)), brk0, 0.07)
nroll = 16
for k in range(nroll):
    tk = brk0 + bd * (1 - (1 - k / nroll) ** 1.3)
    add(drums, stereo(CL), tk, 0.12 + 0.3 * k / nroll)
rd = bd
rs = svf_sweep(noise(rd), np.linspace(300, 6000, int(rd * SR)) ** 1.0, 0.5) * np.linspace(0, 1, int(rd * SR)) ** 2
add(music, stereo(norm(rs) * 0.25), brk0)
# intro riser into the hook
ir_d = t0
if ir_d > 0.2:
    r = svf_sweep(noise(ir_d), np.linspace(500, 7000, int(ir_d * SR)), 0.5) * np.linspace(0.2, 1, int(ir_d * SR)) ** 2
    add(music, stereo(norm(r) * 0.22), 0)
# final chord hit
add(synth, stereo(pad(prog[0][1], 2.2) * np.exp(-tt(2.2) / 0.7)), end_hit, 0.12)
add(drums, stereo(K), end_hit, 1.0)
add(drums, reverb(stereo(CL), 0.8), end_hit, 0.4)

sc = kick_env[:, None]
music += drums + reverb(bassb * sc, 0.05) + reverb(synth * sc, 0.35)
# fade out the tail
fo = int(0.8 * SR); e = int(DUR * SR)
music[e - fo:e] *= np.linspace(1, 0, fo)[:, None] ** 1.5
music[e:] = 0; sfx[e:] = 0
music = music[:e]; sfx = sfx[:e]

def wr(name, x, peak=0.89):
    x = norm(x, peak)
    wavfile.write(os.path.join(outdir, name), SR, (x * 32767).astype(np.int16))
wr('music.wav', music)
wr('sfx.wav', sfx)
print('ok', DUR, len(meta['events']), 'events')
