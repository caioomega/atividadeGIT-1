"""Synthesize the music bed + sound design for the Protefort reel.
usage: python3 audio.py <sfx.json> <cues.js> <outdir>
Writes music.wav and sfx.wav (48 kHz, 16-bit stereo)."""
import sys, json, re, os
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 48000
rng = np.random.default_rng(11)
sfx_path, cues_path, outdir = sys.argv[1:4]
meta = json.load(open(sfx_path))
DUR = meta['duration']
cues = {k: float(v) for k, v in re.findall(r'"?(\w+)"?:\s*([\d.]+)', open(cues_path).read())}
N = int((DUR + 1.0) * SR)

# ---------------- DSP helpers ----------------
def tt(d): return np.arange(int(d * SR)) / SR
def ns(n): return int(n * SR)
def white(d): return rng.standard_normal(ns(d))
def pink(d):
    b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]; a = [1, -2.494956002, 2.017265875, -0.522189400]
    x = signal.lfilter(b, a, rng.standard_normal(ns(d) + 2000))[2000:]
    return x / (np.std(x) + 1e-9)
def sos(kind, f, order=2): return signal.butter(order, f, kind, fs=SR, output='sos')
def bp(x, lo, hi, order=2): return signal.sosfilt(sos('bandpass', [lo, min(hi, SR / 2 - 100)], order), x)
def hp(x, f, order=2): return signal.sosfilt(sos('highpass', f, order), x)
def lp(x, f, order=2): return signal.sosfilt(sos('lowpass', min(f, SR / 2 - 100), order), x)
def reson(x, f, q):
    b, a = signal.iirpeak(min(f, SR / 2 - 200), q, fs=SR); return signal.lfilter(b, a, x)
def ex(d, tau): return np.exp(-tt(d) / tau)
def att(d, a=0.002): return np.minimum(1, tt(d) / a)
def glide(f0, f1, d, shape=5.0):
    t = tt(d); k = t / d
    return f1 + (f0 - f1) * np.exp(-k * shape)
def osc(freq):  # freq: array (Hz) -> sine
    return np.sin(2 * np.pi * np.cumsum(freq) / SR)
def saw(freq, maxh=6000):
    ph = np.cumsum(freq) / SR; y = np.zeros_like(ph); f0 = float(np.max(freq))
    for k in range(1, max(2, int(maxh / f0))): y += np.sin(2 * np.pi * k * ph) / k
    return y * 0.6
def svf(x, fc, q=0.6):
    y = np.zeros_like(x); low = band = 0.0
    for i in range(len(x)):
        f = 2 * np.sin(np.pi * min(fc[i], SR / 6) / SR)
        high = x[i] - low - q * band; band += f * high; low += f * band; y[i] = band
    return y
def norm(x, peak=1.0):
    m = np.max(np.abs(x)); return x / m * peak if m > 0 else x
def pan_st(x, pan=0.0):
    if x.ndim == 2: l, r = x[:, 0], x[:, 1]
    else: l = r = x
    gl = np.cos((pan + 1) * np.pi / 4) * 1.414; gr = np.sin((pan + 1) * np.pi / 4) * 1.414
    return np.stack([l * min(1, gl), r * min(1, gr)], 1)
def autopan(x, a=-0.7, b=0.7):
    p = np.linspace(a, b, len(x))
    return np.stack([x * np.cos((p + 1) * np.pi / 4), x * np.sin((p + 1) * np.pi / 4)], 1) * 1.2
def make_ir(d=1.6, tl=0.55, th=0.22, pre=0.012):
    t = tt(d)
    def ch():
        n = rng.standard_normal(len(t))
        y = lp(n, 3000) * np.exp(-t / tl) + hp(n, 3000) * np.exp(-t / th) * 0.6
        y[:ns(pre)] = 0
        for dl, g in [(0.017, 0.5), (0.029, 0.35), (0.041, 0.28), (0.063, 0.2)]:
            if ns(dl) < len(y): y[ns(dl)] += g * 6
        return y
    return np.stack([ch(), ch()], 1) * 0.06
IR_ROOM, IR_HALL = make_ir(0.7, 0.18, 0.09), make_ir(2.2, 0.7, 0.3)
def verb(st, wet=0.25, ir=None, hpf=280):
    ir = IR_HALL if ir is None else ir
    if st.ndim == 1: st = np.stack([st, st], 1)
    pad = np.zeros((len(ir[:, 0]), 2)); src = np.vstack([st, pad])
    send = hp(src, hpf) if hpf else src   # keep the low end dry and tight
    out = np.stack([signal.fftconvolve(send[:, c], ir[:, c])[:len(src)] for c in range(2)], 1)
    return src + out * wet
def varispeed(x, p):
    if abs(p - 1) < 1e-3: return x
    idx = np.arange(0, len(x) - 1, p)
    if x.ndim == 1: return np.interp(idx, np.arange(len(x)), x)
    return np.stack([np.interp(idx, np.arange(len(x)), x[:, c]) for c in range(2)], 1)
def bell_env(d, peak=0.45, rise=2.2, fall=6.0):
    k = tt(d) / d
    return np.where(k < peak, (k / peak) ** rise, np.exp(-(k - peak) / (1 - peak) * fall))
def grains(d, n, lo, hi, mean_t, glen=(0.002, 0.009), amp_tau=None):
    out = np.zeros((ns(d), 2))
    for _ in range(n):
        t0 = min(d * 0.95, rng.exponential(mean_t)); gl = rng.uniform(*glen)
        g = bp(white(gl + 0.01), rng.uniform(lo, hi * 0.8), hi)[:ns(gl)] * np.hanning(ns(gl))
        a = rng.uniform(0.3, 1.0) * (np.exp(-t0 / amp_tau) if amp_tau else 1)
        i = ns(t0); j = min(len(out), i + len(g))
        out[i:j] += pan_st(g[:j - i] * a, rng.uniform(-0.8, 0.8))
    return out

# ---------------- sound palette (base takes) ----------------
def whoosh(d, f0, f1, f2, peak=0.42, q=0.5, low=0.5, hiss=0.15, a=-0.75, b=0.75):
    k = tt(d) / d
    fc = np.where(k < peak, f0 * (f1 / f0) ** (k / peak), f1 * (f2 / f1) ** ((k - peak) / (1 - peak)))
    e = bell_env(d, peak, 2.0, 5.5)
    L = svf(pink(d), fc, q) + lp(pink(d), 320) * low * 0.25 + hp(white(d), 5500) * hiss * e
    R = svf(pink(d), fc * 1.04, q) + lp(pink(d), 320) * low * 0.25 + hp(white(d), 5500) * hiss * e
    st = np.stack([norm(L * e), norm(R * e)], 1)
    p = np.linspace(a, b, len(k))
    st[:, 0] *= np.cos((p + 1) * np.pi / 4) * 1.3; st[:, 1] *= np.sin((p + 1) * np.pi / 4) * 1.3
    return st
def s_whip(): return verb(whoosh(0.62, 220, 2400, 420, 0.4, 0.42, 0.9, 0.18), 0.18)
def s_dash(): return verb(whoosh(0.28, 700, 4200, 1700, 0.38, 0.5, 0.35, 0.22), 0.12)
def s_swish(): return whoosh(0.24, 2000, 7000, 3800, 0.4, 0.55, 0.05, 0.3, -0.3, 0.3) * 0.8
def s_whoosh_down():
    d = 0.4; w = whoosh(d, 4200, 2200, 300, 0.25, 0.5, 0.6, 0.2, -0.2, 0.2)
    s = osc(glide(420, 70, d, 3)) * (tt(d) / d) ** 2 * 0.35
    return w + np.stack([s, s], 1)
def s_zip(up=True):
    d = 0.22; k = tt(d) / d
    f = 280 * (2400 / 280) ** (k ** 1.4) if up else 2400 * (260 / 2400) ** (k ** 0.7)
    tone = lp(saw(f, 5000), 4500) * 0.5
    nz = svf(pink(d), f * 1.6, 0.6) * 0.6
    e = np.minimum(1, k / 0.15) * np.minimum(1, (1 - k) / 0.08)
    return verb(pan_st(norm(tone + nz) * e, 0), 0.15)
def s_whomp():
    d = 0.55; k = tt(d) / d; e = bell_env(d, 0.4, 1.6, 4)
    fc = 160 + 900 * np.sin(np.pi * k) ** 2
    L = svf(pink(d), fc, 0.7); R = svf(pink(d), fc * 1.05, 0.7)
    sub = osc(60 + 50 * np.sin(np.pi * k)) * 0.6
    st = np.stack([norm(L) + sub, norm(R) + sub], 1) * e[:, None]
    return verb(np.tanh(st * 1.4), 0.25)
def s_tap(f):
    d = 0.06; imp = np.zeros(ns(d)); imp[:24] = np.hanning(24) * rng.choice([-1, 1], 24)
    y = reson(imp, f, 14) * 1.0 + reson(imp, f * 2.1, 18) * 0.35 + reson(imp, 420, 5) * 0.25
    return verb(norm(y * ex(d, 0.012)) * 0.8, 0.12, IR_ROOM)
def s_click():
    d = 0.14; y = np.zeros(ns(d))
    for t0, a, fm in [(0.0, 1.0, 1.0), (0.068, 0.7, 1.16)]:
        dd = 0.05; imp = bp(white(dd), 1800, 9000) * ex(dd, 0.0012)
        body = reson(imp, 3800 * fm, 9) * 0.6 + reson(imp, 950 * fm, 6) * 0.5
        seg = (imp * 0.8 + body) * a; i = ns(t0); y[i:i + len(seg)] += seg[:len(y) - i]
    return verb(norm(y) * 0.85, 0.1, IR_ROOM)
def s_pop():
    d = 0.14; f = 360 + (1350 - 360) * (1 - np.exp(-tt(d) / 0.012))
    y = (osc(f) + 0.18 * osc(f * 2)) * att(d, 0.001) * ex(d, 0.028)
    y[:40] += np.hanning(40) * 0.6
    return verb(norm(y) * 0.85, 0.14, IR_ROOM)
def s_boop():
    d = 0.22; f = glide(820, 905, d, 6)
    y = (osc(f) + 0.12 * osc(f * 3) + 0.25 * osc(f * 2)) * att(d, 0.003) * ex(d, 0.05)
    return verb(norm(y) * 0.7, 0.2)
def bell(f, d=1.2, tau=0.5):
    t = tt(d); y = np.zeros_like(t)
    for m, a, tm in [(1, 1, 1), (2.0, 0.45, 0.6), (3.01, 0.22, 0.35), (4.17, 0.12, 0.2), (5.43, 0.08, 0.12)]:
        y += a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / (tau * tm))
    return y * att(d, 0.002)
def s_check():
    d = 0.9; y = np.zeros(ns(d)); b1 = bell(1046.5, d, 0.22); y += b1
    b2 = bell(1568, d - 0.06, 0.25); y[ns(0.06):] += b2[:len(y) - ns(0.06)] * 0.75
    return verb(norm(y) * 0.7, 0.4)
def s_ding():
    d = 1.6; y = np.zeros(ns(d))
    for t0, f, a in [(0, 1318.5, 1), (0.06, 1975.5, 0.75), (0.12, 2637, 0.4)]:
        b = bell(f, d - t0, 0.5); y[ns(t0):] += b[:len(y) - ns(t0)] * a
    return verb(norm(y) * 0.7, 0.55)
def s_shimmer():
    d = 1.2; out = np.zeros((ns(d), 2))
    scale = [1, 9 / 8, 5 / 4, 3 / 2, 5 / 3, 2]
    for _ in range(80):
        t0 = d * rng.beta(1.2, 3.2); f = 2093 * rng.choice(scale) * rng.choice([1, 2])
        gl = rng.uniform(0.02, 0.08); g = np.sin(2 * np.pi * f * tt(gl)) * np.hanning(ns(gl))
        a = rng.uniform(0.2, 1) * (1 - t0 / d) ** 1.5; i = ns(t0); j = min(len(out), i + len(g))
        out[i:j] += pan_st(g[:j - i] * a, rng.uniform(-0.9, 0.9))
    wash = hp(white(d), 8000) * bell_env(d, 0.15, 1.5, 4) * 0.08
    out += np.stack([wash, wash[::-1]], 1)
    return verb(norm(out) * 0.8, 0.8)
def s_sonar():
    d = 1.3; y = np.zeros((ns(d), 2)); base = (osc(np.full(ns(0.5), 1250.0)) + 0.2 * osc(np.full(ns(0.5), 2500.0))) * att(0.5, 0.003) * ex(0.5, 0.12)
    for k, (t0, a, pn) in enumerate([(0, 1, 0), (0.22, 0.45, -0.6), (0.44, 0.22, 0.6), (0.66, 0.1, -0.5)]):
        seg = lp(base, 4000 - k * 900) * a; i = ns(t0); j = min(len(y), i + len(seg))
        y[i:j] += pan_st(seg[:j - i], pn)
    return verb(y * 0.7, 0.35)
def s_tick():
    d = 0.06; imp = np.zeros(ns(d)); imp[:16] = np.hanning(16)
    y = reson(imp, 1500, 22) + reson(imp, 3300, 25) * 0.4
    return verb(norm(y * ex(d, 0.018)) * 0.7, 0.08, IR_ROOM)
def s_marker():
    d = 0.3; k = tt(d) / d; fc = 1600 * (4800 / 1600) ** k
    rough = 0.55 + 0.45 * lp(np.abs(white(d)), 70) / 0.5
    y = svf(white(d), fc, 0.8) * np.clip(rough, 0.1, 1.5)
    e = np.minimum(1, k / 0.06) * np.minimum(1, (1 - k) / 0.15)
    return verb(autopan(norm(y) * e * 0.9, -0.5, 0.5), 0.1)
def s_suck():
    d = 0.5; burst = verb(pan_st(lp(pink(0.08), 5000) * ex(0.08, 0.02)), 1.0)[:ns(d)]
    w = whoosh(d, 600, 3500, 3500, 0.98, 0.6, 0.4, 0.2, 0.4, -0.4)
    rev = np.vstack([burst, np.zeros((max(0, ns(d) - len(burst)), 2))])[:ns(d)][::-1] * 3 + w * 0.6
    e = (tt(d) / d) ** 2.5
    out = rev * e[:, None]; out[-ns(0.006):] *= np.linspace(1, 0, ns(0.006))[:, None]
    return norm(out)
def s_riser(d=1.0):
    k = tt(d) / d; fc = 300 * (7000 / 300) ** (k ** 1.3)
    nz = svf(pink(d), fc, 0.5) * (0.6 + 0.4 * np.sin(2 * np.pi * np.cumsum(4 + 14 * k ** 2) / SR))
    f = 110 * 4 ** (k ** 1.2)
    sw = saw(f, 6000) + saw(f * 1.007, 6000)
    tone = (lp(sw, 600) * (1 - k ** 2) + lp(sw, 5600) * k ** 2) * 0.3
    y = norm(nz + tone) * k ** 2.4
    y[-ns(0.008):] *= np.linspace(1, 0, ns(0.008))
    return verb(autopan(y, -0.3, 0.3), 0.3)
def s_debris():
    d = 0.8; g = grains(d, 60, 1500, 7500, 0.12, (0.002, 0.01), 0.25)
    for _ in range(5):
        t0 = rng.uniform(0, 0.15); dd = 0.03; th = osc(glide(rng.uniform(140, 240), 80, dd, 3)) * ex(dd, 0.008)
        i = ns(t0); g[i:i + len(th)] += pan_st(th, rng.uniform(-0.6, 0.6)) * 0.6
    return verb(norm(g) * 0.8, 0.3)
def s_hit():
    d = 0.7
    punch = osc(glide(210, 55, d, 9)) * ex(d, 0.08)
    snap = bp(white(d), 1200, 6000) * ex(d, 0.012) * 0.8
    body = bp(white(d), 200, 1400) * ex(d, 0.05) * 0.6
    y = np.tanh((punch * 1.3 + snap + body) * 1.5)
    return verb(pan_st(norm(y)), 0.3, IR_ROOM) * 0.9 + verb(pan_st(norm(y) * 0.3), 0.6)[:ns(d) + len(IR_ROOM)]
def s_impact():
    d = 2.2
    sub = osc(glide(75, 32, d, 3)) * ex(d, 0.6) * att(d, 0.003)
    punch = osc(glide(170, 48, d, 12)) * ex(d, 0.09)
    crack = hp(white(d), 1500) * ex(d, 0.01) * 0.9
    body = bp(white(d), 120, 900) * ex(d, 0.15) * 0.6
    y = np.tanh((sub * 1.1 + punch + crack + body) * 1.7)
    st = pan_st(norm(y))
    deb = s_debris(); st[:len(deb)] += deb[:len(st)] * 0.35
    return verb(st, 0.45)
def s_stamp():
    d = 0.9
    thud = osc(glide(140, 52, d, 8)) * ex(d, 0.09)
    slap = bp(white(d), 600, 3500) * ex(d, 0.018) * 0.9
    y = pan_st(np.tanh((thud + slap) * 1.6))
    rat = grains(d, 25, 2000, 6000, 0.05, (0.002, 0.006), 0.1) * 0.4
    return verb(norm(y + rat), 0.3)
def s_step():
    d = 0.4; y = np.zeros((ns(d), 2))
    for t0, a in [(0, 1.0), (0.11, 0.55)]:
        dd = 0.12; th = osc(glide(100, 48, dd, 5)) * ex(dd, 0.03) * a
        gr = grains(dd, 14, 1200, 4500, 0.025, (0.002, 0.008), 0.05)[:, 0] * a * 0.7
        seg = th + gr; i = ns(t0); y[i:i + len(seg)] += pan_st(seg, 0)[:len(y) - i]
    return verb(norm(y) * 0.85, 0.12, IR_ROOM)

def takes(fn, n=3): return [fn() for _ in range(n)]
PAL = {
    'whip': takes(s_whip), 'dash': takes(s_dash), 'swish': takes(s_swish), 'whoosh_down': takes(s_whoosh_down, 2),
    'zip': [s_zip(True)], 'zipdown': [s_zip(False)], 'whomp': takes(s_whomp, 2),
    'tap': [s_tap(f) for f in (2300, 2650, 3000, 3400, 2850)], 'click': takes(s_click, 2), 'pop': takes(s_pop, 2),
    'boop': [s_boop()], 'check': [s_check()], 'ding': [s_ding()], 'shimmer': takes(s_shimmer, 3), 'sonar': [s_sonar()],
    'tick': [s_tick()], 'marker': takes(s_marker, 2), 'suck': takes(s_suck, 2), 'debris': takes(s_debris, 3),
    'hit': takes(s_hit, 2), 'impact': takes(s_impact, 2), 'stamp': [s_stamp()], 'step': takes(s_step, 4),
}
# loudness targets (peak short-term RMS, dB) -> every take is calibrated to sit in a professional balance
TARGET = {'impact': -6, 'hit': -9, 'stamp': -9, 'whip': -12.5, 'whomp': -15, 'dash': -14, 'whoosh_down': -14.5,
          'zip': -16.5, 'zipdown': -16.5, 'suck': -16, 'riser': -15, 'debris': -19, 'marker': -16, 'pop': -16, 'click': -19.5,
          'step': -16, 'ding': -17, 'check': -17.5, 'shimmer': -19, 'sonar': -19.5, 'boop': -19.5, 'swish': -19, 'tap': -21, 'tick': -21.5}
def st_rms_db(x, w=0.05):
    m = x.mean(1) if x.ndim == 2 else x; n = int(w * SR)
    return 20 * np.log10(np.sqrt(np.convolve(m ** 2, np.ones(n) / n, 'same').max()) + 1e-12)
CAL = {k: 10 ** ((TARGET[k] - st_rms_db(v[0])) / 20) for k, v in PAL.items()}
CAL['riser'] = 10 ** ((TARGET['riser'] - st_rms_db(s_riser(1.0))) / 20)
VOL = CAL
END_ALIGNED = {'suck', 'riser'}          # event time = end of sound
PEAK_ALIGNED = {'whip': 0.4 * 0.62, 'dash': 0.38 * 0.28, 'swish': 0.4 * 0.24, 'whomp': 0.4 * 0.55}  # lead in to the peak

sfx = np.zeros((N, 2)); count = {}
for ev in meta['events']:
    typ = ev['type']
    if typ == 'riser': base = s_riser(ev.get('d', 1.0))
    else:
        lst = PAL[typ]; k = count.get(typ, 0); count[typ] = k + 1; base = lst[k % len(lst)]
    p = ev.get('p', 1.0) * (rng.uniform(0.97, 1.03) if typ not in ('check', 'ding', 'tick', 'boop') else 1.0)
    x = varispeed(base, p) * VOL.get(typ, 0.4) * ev['g']
    x = pan_st(x, ev.get('pan', 0.0)) if 'pan' in ev else x
    t = ev['t']
    if typ == 'riser': t -= ev.get('d', 1.0) / p
    elif typ in END_ALIGNED: t -= len(x) / SR
    elif typ in PEAK_ALIGNED: t -= PEAK_ALIGNED[typ] / p
    i = int(t * SR)
    if i < 0: x = x[-i:]; i = 0
    j = min(N, i + len(x)); sfx[i:j] += x[:j - i]

# gentle bus compression (RMS follower) so small UI sounds sit next to the big hits
def compress(st, thr=0.25, ratio=3.0, att_ms=3, rel_ms=120):
    lvl = np.sqrt(signal.lfilter([1 - np.exp(-1 / (SR * 0.005))], [1, -np.exp(-1 / (SR * 0.005))], np.mean(st ** 2, 1)))
    g = np.ones_like(lvl); over = lvl > thr
    g[over] = (thr * (lvl[over] / thr) ** (1 / ratio)) / lvl[over]
    a, r = np.exp(-1 / (SR * att_ms / 1000)), np.exp(-1 / (SR * rel_ms / 1000)); sm = np.empty_like(g); cur = 1.0
    for i in range(0, len(g), 32):
        tgt = g[i:i + 32].min(); cur = a * cur + (1 - a) * tgt if tgt < cur else r * cur + (1 - r) * tgt
        sm[i:i + 32] = cur
    return st * sm[:, None]
sfx = compress(sfx, thr=0.35, ratio=2.5)

# ---------------- music ----------------
BPM = 124.0; beat = 60 / BPM; t0 = cues['pesado']
music = np.zeros((N, 2)); kick_env = np.ones(N)
def add(buf, x, t, gain=1.0):
    i = int(round(t * SR))
    if i < 0: x = x[-i:]; i = 0
    j = min(len(buf), i + len(x))
    if j > i: buf[i:j] += x[:j - i] * gain
def kick():
    d = 0.42; y = osc(glide(160, 46, d, 6)) * ex(d, 0.16) + bp(white(d), 1500, 6000) * ex(d, 0.003) * 0.3
    return np.tanh(y * 1.3)
def clap():
    d = 0.35; y = np.zeros(ns(d))
    for o in (0, 0.011, 0.022):
        b = bp(white(0.02), 900, 3500); i = ns(o); y[i:i + len(b)] += b * np.linspace(1, 0, len(b))
    tail = bp(white(d), 900, 3200) * ex(d, 0.07); i = ns(0.03); y[i:] += tail[:len(y) - i]
    return norm(y)
def hat(open_=False):
    d = 0.25 if open_ else 0.06
    return norm(hp(white(d), 7500, 4) * ex(d, 0.09 if open_ else 0.015))
K, CL, HC, HO = kick(), clap(), hat(), hat(True)
prog = [(110.0, [220.0, 261.63, 329.63]), (87.31, [174.61, 220.0, 261.63]), (130.81, [261.63, 329.63, 392.0]), (98.0, [196.0, 246.94, 293.66])]
def stab(freqs, d=0.22):
    y = sum(saw(np.full(ns(d), f * dt), 7000) for f in freqs for dt in (0.995, 1.0, 1.006))
    return lp(y, 2600) * ex(d, 0.07) * att(d, 0.004)
def bass_note(f, d):
    y = lp(saw(np.full(ns(d), f), 7000) + 0.5 * np.sin(2 * np.pi * f * tt(d)), 700) * att(d, 0.005) * np.exp(-tt(d) / (d * 1.2))
    return np.tanh(y * 1.8)
def pad(freqs, d):
    y = sum(saw(np.full(ns(d), f * dt), 4000) for f in freqs for dt in (0.993, 1.0, 1.008))
    return lp(y, 1400) * np.minimum(1, tt(d) / 0.6) * np.minimum(1, (d - tt(d)) / 0.4)
st2 = lambda x, p=0.0: pan_st(x, p)
drums = np.zeros((N, 2)); bassb = np.zeros((N, 2)); synth = np.zeros((N, 2))
brk0, brk1 = cues['protecao'] - 0.25, cues['protefort']
end_hit = cues['end'] - 2.0
bar = 0
while True:
    tb = t0 + bar * 4 * beat
    if tb > DUR: break
    root, ch = prog[bar % 4]
    for b in range(4):
        tbeat = tb + b * beat
        if tbeat > end_hit + 0.01 or brk0 <= tbeat < brk1: continue
        add(drums, st2(K), tbeat, 0.95)
        i = int(tbeat * SR); L = int(0.3 * SR)
        if i < N: kick_env[i:i + L] = np.minimum(kick_env[i:i + L], 0.25 + 0.75 * (np.arange(min(L, N - i)) / L) ** 0.7)
        if b in (1, 3): add(drums, st2(CL, 0.05), tbeat, 0.5)
        add(drums, st2(HC, -0.3), tbeat + beat * 0.25, 0.16)
        add(drums, st2(HO, 0.3), tbeat + beat * 0.5, 0.22)
        add(drums, st2(HC, -0.3), tbeat + beat * 0.75, 0.12)
        add(bassb, st2(bass_note(root, beat * 0.45)), tbeat + beat * 0.5, 0.42)
        add(synth, st2(stab(ch), 0.15 * (1 if b % 2 else -1)), tbeat + beat * 0.5, 0.11)
    bar += 1
bd = brk1 - brk0
add(synth, st2(pad(prog[0][1], bd + 0.2)), brk0, 0.07)
for k in range(16):
    add(drums, st2(CL), brk0 + bd * (1 - (1 - k / 16) ** 1.3), 0.12 + 0.3 * k / 16)
rs = svf(white(bd), np.linspace(300, 6000, ns(bd)), 0.5) * np.linspace(0, 1, ns(bd)) ** 2
add(music, st2(norm(rs) * 0.25), brk0)
if t0 > 0.2:
    r = svf(white(t0), np.linspace(500, 7000, ns(t0)), 0.5) * np.linspace(0.2, 1, ns(t0)) ** 2
    add(music, st2(norm(r) * 0.22), 0)
add(synth, st2(pad(prog[0][1], 2.2) * np.exp(-tt(2.2) / 0.7)), end_hit, 0.12)
add(drums, st2(K), end_hit, 1.0)
add(drums, verb(st2(CL), 0.8), end_hit, 0.4)
sc = kick_env[:, None]
def fit(x): return x[:N] if len(x) >= N else np.vstack([x, np.zeros((N - len(x), 2))])
music += drums + fit(verb(bassb * sc, 0.05, IR_ROOM)) + fit(verb(synth * sc, 0.35))
fo = int(0.8 * SR); e = int(DUR * SR)
music[e - fo:e] *= np.linspace(1, 0, fo)[:, None] ** 1.5
music = music[:e]; sfx = sfx[:e]

def wr(name, x, peak=0.89):
    wavfile.write(os.path.join(outdir, name), SR, (norm(x, peak) * 32767).astype(np.int16))
wr('music.wav', music)
wr('sfx.wav', sfx, peak=min(0.89, float(np.max(np.abs(sfx)))))
print('ok', DUR, len(meta['events']), 'events', dict(sorted(count.items())))
