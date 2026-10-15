"""Trilha "moda de viola" + efeitos rústicos do vídeo Café Santa Luzia (síntese procedural).

Uso:
  python3 tools/audio.py build/sfx.json build/audio.wav [locucao.wav]

- Trilha: toada caipira a 88 BPM em Mi maior (cebolão). Viola caipira com cordas duplas
  (Karplus-Strong) fazendo melodia em terças, violão de nylon no ritmo de toada, sanfona com
  palhetas desafinadas (musette), ganzá e bumbo leve.
- Efeitos: ambiente de roça (vento, passarinhos, grilos, galo ao longe), papel, carimbo de
  madeira, grãos de café, café sendo servido, tilintar de porcelana, fita desenrolando, brilho.
- Locução (opcional): se passada, a trilha abaixa sob a voz (ducking) e tudo é masterizado junto.
"""
import json
import sys
import wave

import numpy as np
from scipy import signal

SR = 48000
rng = np.random.default_rng(1973)


# ----------------------------------------------------------------------------- util
def tt(n):
    return np.arange(n) / SR


def ns(sec):
    return int(round(sec * SR))


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc, "low", fs=SR, output="sos"), x)


def hp(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi, order=2):
    return signal.sosfilt(signal.butter(order, [lo, hi], "band", fs=SR, output="sos"), x)


def peak(x, f0, gain_db, q=1.0):
    """EQ de pico (RBJ)."""
    A = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / SR
    al = np.sin(w0) / (2 * q)
    b = [1 + al * A, -2 * np.cos(w0), 1 - al * A]
    a = [1 + al / A, -2 * np.cos(w0), 1 - al / A]
    return signal.lfilter(np.array(b) / a[0], np.array(a) / a[0], x)


def pan_st(x, pan):
    a = (np.asarray(pan) + 1) * np.pi / 4
    return np.vstack([x * np.cos(a), x * np.sin(a)])


def norm(x, pk=1.0):
    return x / (np.max(np.abs(x)) + 1e-12) * pk


def make_ir(sec, damp, seed, pre=0.012):
    r = np.random.default_rng(seed)
    n = ns(sec)
    env = np.exp(-tt(n) * 6.9 / sec)
    L = lp(r.standard_normal(n) * env, damp)
    R = lp(r.standard_normal(n) * env, damp)
    pad = np.zeros(ns(pre))
    ir = np.vstack([np.concatenate([pad, L]), np.concatenate([pad, R])])
    return ir / np.sqrt((ir ** 2).sum() / 2)


ROOM = make_ir(0.9, 4500, 3)   # sala de madeira (instrumentos)
HALL = make_ir(2.2, 6000, 4)   # espaço aberto (ambiente, brilhos)


def reverb(st, wet, ir):
    n = st.shape[1]
    out = np.vstack([signal.fftconvolve(st[0], ir[0])[:n], signal.fftconvolve(st[1], ir[1])[:n]])
    return st * (1 - wet * 0.4) + out * wet * 0.35


def place(bus, x, t0, g=1.0, pan=0.0):
    s = ns(t0)
    if s >= bus.shape[1] or s + (x.shape[-1]) <= 0:
        return
    if x.ndim == 1:
        x = pan_st(x, pan)
    a = max(0, -s)
    s = max(0, s)
    e = min(bus.shape[1], s + x.shape[1] - a)
    bus[:, s:e] += x[:, a:a + e - s] * g


# ----------------------------------------------------------------------------- cordas (Karplus-Strong)
def ks(f, dur, decay=0.996, bright=5000, pos=0.18, seed=0):
    """Corda dedilhada: Karplus-Strong com atraso fracionário (allpass) via lfilter."""
    r = np.random.default_rng(seed)
    n = ns(dur)
    P = SR / f
    D = P - 0.5                      # o filtro de média já atrasa meia amostra
    N = int(np.floor(D - 0.5))
    d = D - N
    c = (1 - d) / (1 + d)
    exc_len = max(4, int(P))
    exc = lp(r.uniform(-1, 1, exc_len * 2), bright)[:exc_len]
    # posição da palhetada: filtro pente
    k = max(1, int(pos * P))
    exc = exc - np.concatenate([np.zeros(k), exc[:-k]]) * 0.9
    x = np.zeros(n)
    x[:exc_len] = exc
    g = decay
    a = np.zeros(N + 3)
    a[0], a[1] = 1.0, c
    a[N] -= g / 2 * c
    a[N + 1] -= g / 2 * (1 + c)
    a[N + 2] -= g / 2
    y = hp(signal.lfilter([1.0, c], a, x), 35)   # tira o DC que o laço sustenta
    # amortecimento final suave (abafa a corda no fim)
    rel = ns(0.05)
    y[-rel:] *= np.linspace(1, 0, rel)
    return y


def viola_note(m, dur, vel=1.0, seed=0, course="unison"):
    """Viola caipira: cada ordem tem 2 cordas (uníssono levemente desafinado, ou oitava)."""
    f = midi(m)
    a = ks(f, dur, decay=0.9975, bright=7500, pos=0.14, seed=seed)
    if course == "octave":
        b = ks(f * 2 * 2 ** (2 / 1200), dur, decay=0.997, bright=8000, pos=0.12, seed=seed + 1) * 0.55
    else:
        b = ks(f * 2 ** (4 / 1200), dur, decay=0.9975, bright=7000, pos=0.16, seed=seed + 1) * 0.85
    off = ns(0.006)
    b = np.concatenate([np.zeros(off), b[:-off]])
    return (a + b) * vel


def violao_note(m, dur, vel=1.0, seed=0):
    f = midi(m)
    return ks(f, dur, decay=0.9955, bright=2600, pos=0.2, seed=seed) * vel


def body(x, kind):
    """Ressonância do corpo do instrumento."""
    if kind == "viola":
        x = peak(x, 220, 3, 1.2)
        x = peak(x, 2800, 2.5, 1.0)
        x = hp(x, 90)
    else:
        x = peak(x, 110, 3, 1.0)
        x = peak(x, 240, 2, 1.0)
        x = lp(x, 6000)
    return x


# ----------------------------------------------------------------------------- sanfona
def sanfona(notes, dur, vel=1.0):
    n = ns(dur)
    t = tt(n)
    out = np.zeros(n)
    for m in notes:
        f0 = midi(m)
        for det in (-7, 0, 7):          # três palhetas: "musette"
            f = f0 * 2 ** (det / 1200)
            ph = rng.uniform(0, 2 * np.pi)
            for h in range(1, 16):
                if f * h > 6000:
                    break
                amp = (1 / h) * (1.0 if h % 2 else 0.7)
                out += amp * np.sin(2 * np.pi * f * h * t + ph * h)
    out /= len(notes) * 3
    # fole: entrada suave, leve "respiração"
    env = np.minimum(1, t / 0.12) * np.minimum(1, (dur - t) / 0.25).clip(0, 1)
    env *= 0.85 + 0.15 * np.sin(2 * np.pi * 0.6 * t)
    out = peak(lp(out * env, 4200), 1300, 4, 1.4)
    return out * vel


# ----------------------------------------------------------------------------- percussão
def ganza(n, accent):
    t = tt(n)
    env = (1 - np.exp(-t / 0.006)) * np.exp(-t / (0.05 if accent else 0.03))
    return bp(rng.standard_normal(n), 3500, 11000) * env * (1.0 if accent else 0.55)


def bumbo():
    n = ns(0.35)
    t = tt(n)
    f = 52 + 60 * np.exp(-t / 0.025)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)
    x += 0.15 * lp(rng.standard_normal(n), 900) * np.exp(-t / 0.01)
    return x


# ----------------------------------------------------------------------------- trilha
BPM = 88
BEAT = 60 / BPM
BAR = 4 * BEAT
CH = {"E": [40, 47, 52, 56, 59, 64], "A": [45, 52, 57, 61, 64], "B7": [47, 51, 57, 59, 63, 66]}
ROOT = {"E": (40, 47), "A": (45, 52), "B7": (47, 42)}
PROG = ["E", "E", "B7", "E", "A", "E", "B7", "E", "A", "B7", "E"]
SCALE_E = [64, 66, 68, 69, 71, 73, 75, 76, 78, 80, 81, 83]  # Mi maior (E4..B5)

# melodia (voz de cima) por compasso: (tempo, nota, duração em tempos)
MEL = {
    1: [(0, 71, 1), (1, 68, .5), (1.5, 69, .5), (2, 71, 1), (3, 73, .5), (3.5, 71, .5)],
    2: [(0, 69, 1), (1, 66, .5), (1.5, 68, .5), (2, 69, 1.5), (3.5, 71, .5)],
    3: [(0, 68, 2), (2, 64, .5), (2.5, 66, .5), (3, 68, .5), (3.5, 69, .5)],
    4: [(0, 73, 1), (1, 71, .5), (1.5, 69, .5), (2, 73, 1), (3, 76, 1)],
    5: [(0, 71, 1.5), (1.5, 68, .5), (2, 71, 1), (3, 69, .5), (3.5, 68, .5)],
    6: [(0, 66, 1), (1, 69, .5), (1.5, 68, .5), (2, 66, 1.5), (3.5, 71, .5)],
    7: [(0, 68, 2.5), (3, 71, .5), (3.5, 73, .5)],
    8: [(0, 76, 1), (1, 73, .5), (1.5, 76, .5), (2, 73, 1), (3, 69, 1)],
    9: [(0, 71, 1), (1, 69, .5), (1.5, 66, .5), (2, 69, .5), (2.5, 68, .5), (3, 66, 1)],
}


def third_below(m):
    """Terça diatônica abaixo, na escala de Mi maior (o "dueto" da música caipira)."""
    sc = sorted(set([s - 12 for s in SCALE_E] + SCALE_E + [s + 12 for s in SCALE_E]))
    i = min(range(len(sc)), key=lambda k: abs(sc[k] - m))
    return sc[max(0, i - 2)]


def render_music(dur):
    N = ns(dur + 3)
    viola = np.zeros((2, N))
    violao = np.zeros((2, N))
    sanf = np.zeros((2, N))
    perc = np.zeros((2, N))
    seed = [0]

    def sd():
        seed[0] += 1
        return seed[0]

    # introdução: arpejo de viola (ponteado) em Mi
    for k, m in enumerate([52, 59, 64, 68, 71, 68, 64, 76]):
        place(viola, viola_note(m, 2.2, .55, sd(), "octave" if m < 60 else "unison"), 0.35 + k * BEAT / 2, 1, -0.25 + 0.07 * k)
    for bar, ch in enumerate(PROG):
        b0 = bar * BAR
        last = bar == len(PROG) - 1
        # violão: toada (baixo no 1 e no 3, acorde nos contratempos)
        if 1 <= bar and not last:
            r1, r5 = ROOT[ch]
            place(violao, violao_note(r1, 1.6, 1.0, sd()), b0, 1, -0.15)
            place(violao, violao_note(r5, 1.6, .8, sd()), b0 + 2 * BEAT, 1, -0.15)
            top = [m for m in CH[ch] if m >= 52][:3]
            for bt, v in ((0.5, .55), (1.0, .4), (1.5, .55), (2.5, .55), (3.0, .4), (3.5, .55)):
                for j, m in enumerate(top):
                    place(violao, violao_note(m, 0.9, v * .55, sd()), b0 + bt * BEAT + j * 0.008, 1, -0.05)
        # viola: melodia em terças (duas vozes) + rasqueado leve nos compassos cheios
        if bar in MEL:
            for (bt, m, du) in MEL[bar]:
                ts = b0 + bt * BEAT
                place(viola, viola_note(m, du * BEAT + 1.0, .85, sd()), ts, 1, 0.22)
                place(viola, viola_note(third_below(m), du * BEAT + 1.0, .62, sd()), ts + 0.012, 1, 0.32)
        if 3 <= bar <= 8 and bar % 2 == 1:
            for j, m in enumerate(sorted(CH[ch])[1:]):
                place(viola, viola_note(m, 1.4, .22, sd(), "octave" if m < 57 else "unison"), b0 + 3.5 * BEAT + j * 0.012, 1, 0.1)
        if last:
            # acorde final rasqueado, deixa soar
            for j, m in enumerate(sorted(CH["E"])):
                place(viola, viola_note(m, 3.4, .75, sd(), "octave" if m < 57 else "unison"), b0 + j * 0.022, 1, -0.2 + 0.08 * j)
                place(violao, violao_note(m - 12 if m > 60 else m, 3.2, .5, sd()), b0 + 0.01 + j * 0.03, 1, -0.1)
        # sanfona: colchão nos compassos 4–9
        if 4 <= bar <= 9:
            notes = {"E": [56, 59, 64], "A": [57, 61, 64], "B7": [57, 59, 63]}[ch]
            place(sanf, sanfona(notes, BAR + 0.1, .5), b0, 1, 0.0)
        # ganzá e bumbo (compassos 3–9)
        if 3 <= bar <= 9:
            for k in range(16):
                place(perc, ganza(ns(0.12), k % 4 == 2), b0 + k * BEAT / 4, .35, 0.35)
            for bt in (0, 2):
                place(perc, bumbo(), b0 + bt * BEAT, .55, 0)
    V = np.vstack([body(viola[0], "viola"), body(viola[1], "viola")])
    G = np.vstack([body(violao[0], "violao"), body(violao[1], "violao")])
    mix = 0.9 * V + 0.75 * G + 0.45 * sanf + 0.5 * perc
    mix = reverb(mix, 0.32, ROOM)
    f0 = ns(dur - 1.2)
    mix[:, f0:ns(dur)] *= np.linspace(1, 0, ns(dur) - f0) ** 1.4
    mix[:, ns(dur):] = 0
    return mix


# ----------------------------------------------------------------------------- efeitos
def chirp_bird(kind, r):
    if kind == "bemtevi":   # "bem-te-VI"
        parts = [(0.0, 2300, 2600, 0.09), (0.16, 2500, 2700, 0.07), (0.3, 2600, 3400, 0.22)]
    elif kind == "trill":
        parts = [(k * 0.045, 4200 + r.uniform(-200, 200), 3600, 0.03) for k in range(r.integers(6, 12))]
    else:                   # assobio curto
        f = r.uniform(2800, 4800)
        parts = [(0.0, f, f * r.uniform(1.1, 1.4), r.uniform(0.06, 0.14)), (0.18, f * 1.1, f * 0.9, 0.08)]
    n = ns(max(p[0] + p[3] for p in parts) + 0.05)
    out = np.zeros(n)
    for (t0, f0, f1, d) in parts:
        m = ns(d)
        t = tt(m)
        f = np.linspace(f0, f1, m) * (1 + 0.02 * np.sin(2 * np.pi * 38 * t))
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** 0.7
        s = ns(t0)
        out[s:s + m] += x
    return out


def sfx_ambience(dur=6.0, birdsOnly=False, seed=11, **_):
    r = np.random.default_rng(seed)
    n = ns(dur)
    t = tt(n)
    st = np.zeros((2, n))
    if not birdsOnly:
        wind = np.vstack([lp(r.standard_normal(n), 700), lp(r.standard_normal(n), 720)])
        wind *= (0.55 + 0.45 * np.sin(2 * np.pi * 0.11 * t + 1)) * 0.5
        st += wind
    kinds = ["bemtevi", "trill", "whistle", "whistle", "trill"]
    k = 0
    tb = 0.4
    while tb < dur - 0.5:
        b = chirp_bird(kinds[k % len(kinds)], r) * r.uniform(0.25, 0.6)
        pan = r.uniform(-0.8, 0.8)
        place(st, b, tb, 1, pan)
        tb += r.uniform(0.35, 0.95)
        k += 1
    fade = ns(0.6)
    st[:, :fade] *= np.linspace(0, 1, fade)
    st[:, -fade:] *= np.linspace(1, 0, fade)
    return reverb(st, 0.35, HALL)


def sfx_crickets(dur=2.6, **_):
    n = ns(dur)
    t = tt(n)
    gate = (np.sin(2 * np.pi * 28 * t) > 0.2).astype(float) * (np.sin(2 * np.pi * 1.4 * t) > -0.2)
    x = np.sin(2 * np.pi * 4700 * t) * lp(gate, 400)
    x *= np.minimum(1, (dur - t) / 0.8).clip(0, 1)
    return reverb(pan_st(x * 0.4, -0.5), 0.5, HALL)


def sfx_rooster(**_):
    """Galo ao longe: "có-có-ri-cóóó" (fonte dente-de-serra + formantes), distante e com eco."""
    sylls = [(0.0, 0.11, 560, 600), (0.16, 0.11, 600, 640), (0.33, 0.14, 700, 760), (0.52, 0.75, 880, 640)]
    n = ns(1.45)
    t = tt(n)
    f = np.full(n, 600.0)
    amp = np.zeros(n)
    for (t0, d, fa, fb) in sylls:
        s, m = ns(t0), ns(d)
        f[s:s + m] = np.linspace(fa, fb, m)
        e = np.sin(np.pi * np.linspace(0, 1, m)) ** 0.6
        if d > 0.5:
            e = np.minimum(1, np.linspace(0, 1, m) * 8) * np.linspace(1, 0, m) ** 0.5
            f[s:s + m] *= 1 + 0.025 * np.sin(2 * np.pi * 7 * tt(m))
        amp[s:s + m] = e
    ph = 2 * np.pi * np.cumsum(f * (1 + 0.004 * rng.standard_normal(n))) / SR
    saw = sum(np.sin(k * ph) / k for k in range(1, 14))
    src = saw + 0.25 * rng.standard_normal(n)
    v = bp(src, 650, 950) * 1.0 + bp(src, 1250, 1650) * 0.7 + bp(src, 2400, 3000) * 0.35
    x = lp(v * amp, 3200)
    return reverb(pan_st(norm(x), 0.55), 0.6, HALL)


def sfx_shimmer(seed=2, **_):
    r = np.random.default_rng(seed)
    total = ns(1.6)
    st = np.zeros((2, total))
    notes = [1318.5, 1661.2, 1975.5, 2489.0, 2637.0, 3322.4]  # Mi maior pentatônica (agudos)
    for i in range(8):
        f = notes[r.integers(len(notes))]
        n = ns(0.5)
        t = tt(n)
        x = np.sin(2 * np.pi * f * t) * (1 - np.exp(-t / 0.003)) * np.exp(-t / 0.12)
        place(st, x * (1 - i / 11), i * 0.07 + r.uniform(0, 0.02), 1, r.uniform(-0.7, 0.7))
    return reverb(st / (np.abs(st).max() + 1e-9), 0.55, HALL)


def sfx_paper(seed=1, **_):
    r = np.random.default_rng(seed)
    n = ns(0.55)
    t = tt(n)
    env = np.sin(np.pi * np.clip(t / 0.55, 0, 1)) ** 1.5
    swish = bp(r.standard_normal(n), 1500, 7000) * env * 0.5
    crk = np.zeros(n)
    idx = r.choice(n, 90, replace=False)
    crk[idx] = r.uniform(-1, 1, 90)
    crk = bp(crk, 2000, 9000) * 3 * env
    return pan_st(norm(swish + crk), r.uniform(-0.3, 0.3))


def sfx_swish(dur=0.8, **_):
    n = ns(dur)
    p = np.linspace(0, 1, n)
    env = np.sin(np.pi * p ** 0.7) ** 2
    x = lp(rng.standard_normal(n), 2500) * env
    return pan_st(norm(x), -0.6 + 1.2 * p)


def sfx_tok(note=72, **_):
    """Batida de madeira afinada (tipo marimba/caixeta)."""
    f = midi(note)
    n = ns(0.5)
    t = tt(n)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.12) + 0.35 * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-t / 0.025)
    x += 0.25 * hp(rng.standard_normal(n), 2000) * np.exp(-t / 0.002)
    x *= 1 - np.exp(-t / 0.0015)
    return pan_st(norm(x), rng.uniform(-0.4, 0.4))


def sfx_stamp(light=False, **_):
    n = ns(0.7)
    t = tt(n)
    f = (140 if light else 95) + 50 * np.exp(-t / 0.02)
    thump = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (0.07 if light else 0.11))
    knock = lp(rng.standard_normal(n), 1800 if light else 1300) * np.exp(-t / 0.025)
    wood = np.sin(2 * np.pi * 420 * t) * np.exp(-t / 0.04) * 0.4
    x = thump + 0.6 * knock + wood
    return reverb(pan_st(norm(np.tanh(1.4 * x)), 0), 0.25, ROOM)


def sfx_unfurl(**_):
    n = ns(0.75)
    t = tt(n)
    p = t / t[-1]
    rate = 55 * (1 - p) + 8
    am = 0.6 + 0.4 * np.sin(2 * np.pi * np.cumsum(rate) / SR)
    env = np.sin(np.pi * p ** 0.6) ** 1.2
    x = bp(rng.standard_normal(n), 900, 6000) * am * env
    return pan_st(norm(x), -0.5 + p)


def sfx_beans(dur=1.4, scatter=False, seed=7, **_):
    """Grãos de café chacoalhando/rolando: muitos cliques ressonantes curtos."""
    r = np.random.default_rng(seed)
    n = ns(dur)
    st = np.zeros((2, n))
    rate_env = (np.exp(-tt(n) / 0.18) * 1.5 + 0.1) if scatter else np.sin(np.pi * np.linspace(0, 1, n)) ** 0.8
    t = 0.0
    while t < dur - 0.02:
        lam = 140 * rate_env[min(n - 1, ns(t))] + 2
        t += r.exponential(1 / lam)
        m = ns(0.02)
        tm = tt(m)
        f = r.uniform(1800, 6500) if r.random() < 0.8 else r.uniform(500, 1200)
        click = np.sin(2 * np.pi * f * tm) * np.exp(-tm / r.uniform(0.0015, 0.004))
        place(st, click * r.uniform(0.2, 1.0), t, 1, r.uniform(-0.6, 0.6))
    return reverb(st / (np.abs(st).max() + 1e-9), 0.2, ROOM)


def sfx_pour(dur=1.1, seed=5, **_):
    """Café caindo na xícara: jato (ruído) + bolhas (senos que sobem rápido)."""
    r = np.random.default_rng(seed)
    n = ns(dur)
    t = tt(n)
    env = np.minimum(1, t / 0.08) * np.minimum(1, (dur - t) / 0.25).clip(0, 1)
    stream = bp(r.standard_normal(n), 600, 3200) * (0.6 + 0.4 * lp(r.standard_normal(n), 12)) * env * 0.35
    bub = np.zeros(n)
    tb = 0.0
    while tb < dur - 0.05:
        tb += r.exponential(1 / 70)
        m = ns(r.uniform(0.012, 0.035))
        tm = tt(m)
        f0 = r.uniform(450, 1500)
        f = f0 * (1 + 2.5 * tm / tm[-1])
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tm / (tm[-1] / 3))
        s = ns(tb)
        e = min(n, s + m)
        bub[s:e] += x[:e - s] * r.uniform(0.3, 1.0) * env[min(n - 1, s)]
    x = stream + 0.5 * bub
    # o som "enche": abafa conforme a xícara enche
    x = lp(x, 5000) * 0.8 + lp(x, 1800) * 0.2
    return reverb(pan_st(norm(x), 0.05), 0.2, ROOM)


def sfx_clink(spoon=False, **_):
    def one(sc=1.0):
        n = ns(0.9)
        t = tt(n)
        parts = [(2950, .35, 1.0), (4610, .24, .6), (7230, .14, .4), (9870, .09, .25)]
        x = sum(a * np.sin(2 * np.pi * f * sc * t) * np.exp(-t / d) for f, d, a in parts)
        x += 0.3 * hp(rng.standard_normal(n), 4000) * np.exp(-t / 0.0015)
        return x
    if spoon:
        n = ns(1.0)
        out = np.zeros(n)
        for k, (t0, g) in enumerate(((0.0, 1.0), (0.11, 0.7), (0.21, 0.5))):
            x = one(1.05 + 0.02 * k)
            s = ns(t0)
            e = min(n, s + len(x))
            out[s:e] += x[:e - s] * g
        x = out
    else:
        x = one()
    return reverb(pan_st(norm(x), 0.1), 0.3, ROOM)


def sfx_thud(**_):
    n = ns(0.6)
    t = tt(n)
    f = 70 + 60 * np.exp(-t / 0.02)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.09)
    x += 0.7 * lp(rng.standard_normal(n), 2400) * np.exp(-t / 0.035)  # papel/embalagem
    return reverb(pan_st(norm(np.tanh(1.3 * x)), 0), 0.2, ROOM)


SYNTH = {
    "ambience": sfx_ambience, "crickets": sfx_crickets, "rooster": sfx_rooster, "shimmer": sfx_shimmer,
    "paper": sfx_paper, "swish": sfx_swish, "tok": sfx_tok, "stamp": sfx_stamp, "unfurl": sfx_unfurl,
    "beans": sfx_beans, "pour": sfx_pour, "clink": sfx_clink, "thud": sfx_thud,
}
BASE = {
    "ambience": 0.32, "crickets": 0.25, "rooster": 0.22, "shimmer": 0.3, "paper": 0.4, "swish": 0.35,
    "tok": 0.4, "stamp": 0.75, "unfurl": 0.4, "beans": 0.45, "pour": 0.55, "clink": 0.45, "thud": 0.8,
}


def render_sfx(events, dur):
    bus = np.zeros((2, ns(dur + 3)))
    for ev in events:
        x = SYNTH[ev["type"]](**{k: v for k, v in ev.items() if k not in ("t", "type", "gain")})
        if x.ndim == 1:
            x = pan_st(x, 0)
        place(bus, x, ev["t"], ev.get("gain", 1.0) * BASE[ev["type"]])
    return bus


# ----------------------------------------------------------------------------- mix
def follower(x, attack, release):
    a_att, a_rel = np.exp(-1 / (attack * SR)), np.exp(-1 / (release * SR))
    return np.maximum(signal.lfilter([1 - a_rel], [1, -a_rel], x), signal.lfilter([1 - a_att], [1, -a_att], x))


def limiter(x, ceiling, release=0.08):
    from numpy.lib.stride_tricks import sliding_window_view
    pk = np.abs(x).max(axis=0)
    g = np.minimum(1, ceiling / np.maximum(pk, 1e-9))
    L = ns(0.005)
    g = sliding_window_view(np.concatenate([g, np.ones(L)]), L + 1).min(axis=1)[: len(g)]
    a = np.exp(-1 / (release * SR))
    sm = signal.lfilter([1 - a], [1, -a], g)
    return x * np.minimum(sm, g)


def load_wav(path):
    import subprocess
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).T.astype(np.float64)


def main(sfx_json, out, vo_path=None):
    data = json.load(open(sfx_json))
    dur = data["dur"]
    N = ns(dur)
    rms = lambda x: np.sqrt(np.mean(x ** 2) + 1e-12)
    music = render_music(dur)[:, :N]
    music *= 10 ** (-21 / 20) / rms(music)
    sfx = render_sfx(data["sfx"], dur)[:, :N]
    mix_music = music.copy()
    vo = None
    if vo_path:
        vo = load_wav(vo_path)
        vo = np.pad(vo, ((0, 0), (0, max(0, N - vo.shape[1]))))[:, :N]
        vo *= 10 ** (-17 / 20) / rms(vo[:, np.abs(vo).max(axis=0) > 1e-3])
        env = follower(np.abs(vo).max(axis=0), 0.02, 0.35)
        duck = 10 ** (-9 * np.clip(env / 0.08, 0, 1) / 20)       # trilha -9 dB sob a voz
        mix_music *= duck
        sfx *= 10 ** (-3 * np.clip(env / 0.08, 0, 1) / 20)       # efeitos -3 dB sob a voz
    mix = mix_music + sfx + (vo if vo is not None else 0)
    mix = hp(mix, 30)
    mix = limiter(mix * 10 ** (2.5 / 20), 10 ** (-2.3 / 20))
    pcm = (np.clip(mix.T, -1, 1) * 32767).astype("<i2")
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"audio ok: {out} ({N / SR:.2f}s, {len(data['sfx'])} efeitos, locução: {'sim' if vo is not None else 'não'})")


if __name__ == "__main__":
    main(*sys.argv[1:4])
