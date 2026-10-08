"""Trilha + efeitos sonoros do AD Inter (síntese 100% procedural, sem samples).

Uso: python3 tools/audio.py sfx.json saida.wav

- Os eventos de SFX vêm do mesmo cronograma do ad.html (exportados pelo render.mjs).
- A música é uma batida house/pop a 120 BPM em Ré maior, com a virada (drop) em 2,0 s,
  respiro em 10–12 s (enquanto o Pix "processa"), retorno no "Pix enviado!" (12,0 s)
  e resolução IV→I no endcard.
"""
import json
import sys

import numpy as np
from scipy import signal

SR = 48000
rng = np.random.default_rng(2026)


# ----------------------------------------------------------------------------- util
def tt(n):
    return np.arange(n) / SR


def ns(sec):
    return int(round(sec * SR))


def noise(n, r=rng):
    return r.standard_normal(n)


def sos_bp(lo, hi, order=2):
    return signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")


def lp(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc, btype="low", fs=SR, output="sos"), x)


def hp(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc, btype="high", fs=SR, output="sos"), x)


def bp(x, lo, hi, order=2):
    return signal.sosfilt(sos_bp(lo, hi, order), x)


def pan_st(x, pan):
    """pan -1..1 (equal power) → array (2, n). pan pode ser vetor."""
    a = (np.asarray(pan) + 1) * np.pi / 4
    return np.vstack([x * np.cos(a), x * np.sin(a)])


def sweep_bp(x, f0, f1, q=1.6, curve=None, block=128):
    """Passa-faixa variável no tempo (biquad RBJ), frequência f0→f1 (log)."""
    n = len(x)
    y = np.zeros(n)
    zi = np.zeros(2)
    for s in range(0, n, block):
        e = min(n, s + block)
        p = (s + e) / 2 / n
        if curve is not None:
            p = curve(p)
        f = f0 * (f1 / f0) ** p
        w0 = 2 * np.pi * min(f, SR * 0.45) / SR
        al = np.sin(w0) / (2 * q)
        b = np.array([al, 0, -al])
        a = np.array([1 + al, -2 * np.cos(w0), 1 - al])
        y[s:e], zi = signal.lfilter(b / a[0], a / a[0], x[s:e], zi=zi)
    return y


def norm(x, peak=1.0):
    m = np.max(np.abs(x)) + 1e-12
    return x / m * peak


def adsr_exp(n, att, tau):
    t = tt(n)
    return (1 - np.exp(-t / max(att, 1e-4))) * np.exp(-t / tau)


def make_ir(sec=1.6, pre=0.015, damp=5000, seed=5):
    r = np.random.default_rng(seed)
    n = ns(sec)
    t = tt(n)
    env = np.exp(-t * 6.9 / sec)
    L = lp(r.standard_normal(n) * env, damp)
    R = lp(r.standard_normal(n) * env, damp)
    pad = np.zeros(ns(pre))
    ir = np.vstack([np.concatenate([pad, L]), np.concatenate([pad, R])])
    return ir / np.sqrt((ir ** 2).sum() / 2)


IR = make_ir()


def reverb(st, wet=0.2, ir=IR):
    out = np.vstack([signal.fftconvolve(st[0], ir[0]), signal.fftconvolve(st[1], ir[1])])
    out = out[:, : st.shape[1]] if out.shape[1] > st.shape[1] else out
    dry = np.zeros_like(out)
    dry[:, : st.shape[1]] = st
    return dry * (1 - wet * 0.5) + out * wet * 0.35


# ----------------------------------------------------------------------------- SFX
def sfx_click(pitch=1.0, **_):
    n = ns(0.07)
    t = tt(n)
    tr = hp(noise(n) * np.exp(-t / 0.0012), 2500)
    body = np.sin(2 * np.pi * 2300 * pitch * t) * np.exp(-t / 0.007) + 0.45 * np.sin(2 * np.pi * 4700 * pitch * t) * np.exp(-t / 0.003)
    low = np.sin(2 * np.pi * 190 * pitch * t) * np.exp(-t / 0.012)
    return norm(0.8 * tr + 0.55 * body + 0.35 * low)


def sfx_tick(pitch=1.0, tonal=False, base=1174.66, **_):
    if tonal:
        f = base * pitch  # nota base (Ré6 na v1) × razão da escala
        n = ns(0.35)
        t = tt(n)
        mod = np.sin(2 * np.pi * f * 3.0 * t) * 1.2 * np.exp(-t / 0.03)
        x = np.sin(2 * np.pi * f * t + mod) * np.exp(-t / 0.09) + 0.3 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.04)
        x += 0.5 * hp(noise(n) * np.exp(-t / 0.001), 3000)
        return norm(x) * 0.9
    n = ns(0.06)
    t = tt(n)
    f = 3200 * pitch
    x = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.01) + 0.6 * hp(noise(n) * np.exp(-t / 0.0008), 4000)
    return norm(x)


def sfx_pop(pitch=1.0, **_):
    n = ns(0.12)
    t = tt(n)
    f0 = 480 * pitch
    f = f0 * (1 + 1.3 * np.exp(-t / 0.011))
    ph = 2 * np.pi * np.cumsum(f) / SR
    env = (1 - np.exp(-t / 0.0012)) * np.exp(-t / 0.038)
    x = (np.sin(ph) + 0.22 * np.sin(2 * ph)) * env
    x += 0.15 * hp(noise(n) * np.exp(-t / 0.0015), 2000)
    return norm(lp(x, 6000))


def sfx_type(seed=0, space=False, **_):
    r = np.random.default_rng(1000 + int(seed))
    n = ns(0.09)
    t = tt(n)
    v = r.uniform(0.85, 1.15)
    click = bp(r.standard_normal(n), 1800 * v, 6000 * v) * np.exp(-t / 0.0025)
    thock = bp(r.standard_normal(n), 250 * v, 900 * v) * np.exp(-t / (0.016 if space else 0.010))
    rel = np.zeros(n)
    d = ns(r.uniform(0.035, 0.05))
    rel[d:] = bp(r.standard_normal(n - d), 2500, 7000) * np.exp(-tt(n - d) / 0.0015) * 0.35
    x = 0.9 * click + (1.3 if space else 0.8) * thock + rel
    return norm(x) * r.uniform(0.75, 1.0)


def sfx_whoosh(dur=0.5, f0=400, f1=3000, pan=0.0, panTo=None, **_):
    n = ns(dur)
    p = np.linspace(0, 1, n)
    env = np.sin(np.pi * np.clip(p, 0, 1) ** 0.75) ** 1.6
    x = sweep_bp(noise(n), f0, f1, q=1.4) * env
    air = lp(noise(n), 900) * env * 0.5
    sig = norm(x + air)
    pv = pan if panTo is None else pan + (panTo - pan) * p
    return pan_st(sig, pv)


def sfx_dash(dur=0.3, pan=0.0, spin=False, **_):
    n = ns(dur)
    p = np.linspace(0, 1, n)
    env = np.where(p < 0.18, (p / 0.18) ** 2, np.exp(-(p - 0.18) * 6))
    x = sweep_bp(noise(n), 700, 7000, q=1.1, curve=lambda q: q ** 0.6) * env
    x += 0.6 * hp(noise(n), 5000) * env ** 2
    if spin:
        rate = 34 * (1 - p) + 8
        am = 0.55 + 0.45 * np.sin(2 * np.pi * np.cumsum(rate) / SR)
        x = x * am + 0.4 * sweep_bp(noise(n), 300, 2500, q=2) * env * am
    return pan_st(norm(x), pan + 0.6 * (p - 0.5) * (1 if pan >= 0 else -1))


def sfx_swish(**_):
    return sfx_whoosh(dur=0.35, f0=2500, f1=6000, pan=0.5, panTo=0.1) * 0.6


def sfx_air(dur=1.3, **_):
    n = ns(dur)
    p = np.linspace(0, 1, n)
    env = np.sin(np.pi * p ** 0.55) ** 1.5
    L = sweep_bp(noise(n), 250, 1800, q=0.8) * env
    R = sweep_bp(noise(n), 260, 1900, q=0.8) * env
    st = np.vstack([L, R])
    return st / np.max(np.abs(st))


def sfx_reverse(dur=0.45, **_):
    n = ns(dur)
    p = np.linspace(0, 1, n)
    env = p ** 3
    x = sweep_bp(noise(n), 300, 7000, q=1.0, curve=lambda q: q ** 1.5) * env
    x += 0.35 * np.sin(2 * np.pi * np.cumsum(80 + 300 * p ** 2) / SR) * env
    x[-ns(0.004):] *= np.linspace(1, 0, ns(0.004))
    return pan_st(norm(x), np.zeros(n))


def sfx_riser(dur=1.0, **_):
    n = ns(dur)
    p = np.linspace(0, 1, n)
    env = p ** 2.2
    x = sweep_bp(noise(n), 400, 9000, q=1.2, curve=lambda q: q ** 1.3) * env
    f = 180 * 2 ** (2.5 * p)
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = (np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph)) * env * 0.35
    trem = 0.75 + 0.25 * np.sin(2 * np.pi * np.cumsum(4 + 20 * p) / SR)
    x = (x + tone) * trem
    x[-ns(0.003):] *= np.linspace(1, 0, ns(0.003))
    L = x
    R = np.roll(x, 24)
    return np.vstack([L, R]) / np.max(np.abs(x))


def sfx_impact(soft=False, **_):
    n = ns(1.0 if soft else 1.8)
    t = tt(n)
    f = 38 + 70 * np.exp(-t / 0.05)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (0.22 if soft else 0.4))
    crack = lp(noise(n), 2500) * np.exp(-t / 0.05)
    thud = bp(noise(n), 80, 300) * np.exp(-t / 0.12)
    x = 1.0 * boom + 0.45 * crack + 0.5 * thud
    st = pan_st(norm(np.tanh(1.6 * x)), np.zeros(n))
    return reverb(st, wet=0.35)[:, :n]


def sfx_snap(**_):
    n = ns(1.2)
    t = tt(n)
    crack = hp(noise(n), 1500) * np.exp(-t / 0.018)
    body = bp(noise(n), 350, 1400) * np.exp(-t / 0.05)
    # cauda metálica inarmônica (não define tom)
    tail = sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate((2210.0, 3170.0, 4630.0, 6110.0))) * np.exp(-t / 0.25) * 0.12
    x = 1.0 * crack + 0.6 * body + tail
    st = pan_st(norm(x), np.zeros(n))
    return reverb(st, wet=0.45)[:, :n]


def sfx_ding(notes=(1760.0, 2349.3), **_):
    out = np.zeros(ns(1.6))
    for k, (f, dt) in enumerate(zip(notes, (0.0, 0.075))):
        n = ns(1.5)
        t = tt(n)
        mod = np.sin(2 * np.pi * f * 3.5 * t) * 2.0 * np.exp(-t / 0.12)
        x = np.sin(2 * np.pi * f * t + mod) * np.exp(-t / 0.42) + 0.25 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.12)
        x *= 1 - np.exp(-t / 0.001)
        s = ns(dt)
        out[s : s + n] += x[: len(out) - s] * (0.9 if k else 0.8)
    st = pan_st(norm(out), np.zeros(len(out)))
    return reverb(st, wet=0.4)[:, : len(out)]


def sfx_sparkle(seed=3, notes=None, **_):
    r = np.random.default_rng(seed)
    total = ns(1.2)
    st = np.zeros((2, total))
    notes = notes or [2349.3, 2637.0, 2960.0, 3520.0, 3951.1, 4698.6]  # padrão: Ré maior pentatônica (agudos)
    for i in range(9):
        f = notes[r.integers(len(notes))]
        n = ns(0.3)
        t = tt(n)
        x = np.sin(2 * np.pi * f * t) * (1 - np.exp(-t / 0.002)) * np.exp(-t / 0.07)
        s = ns(i * 0.055 + r.uniform(0, 0.02))
        st[:, s : s + n] += pan_st(x, r.uniform(-0.8, 0.8))[:, : total - s] * (1 - i / 12)
    return reverb(st / np.max(np.abs(st)), wet=0.5)[:, :total]


def sfx_glitch(dur=0.32, **_):
    r = np.random.default_rng(77)
    n = ns(dur)
    st = np.zeros((2, n))
    s = 0
    while s < n:
        L = ns(r.uniform(0.012, 0.04))
        e = min(n, s + L)
        m = e - s
        kind = r.integers(4)
        t = tt(m)
        if kind == 0:
            f = r.uniform(120, 1800)
            x = np.sign(np.sin(2 * np.pi * f * t))
        elif kind == 1:
            x = np.repeat(r.standard_normal(m // 24 + 1), 24)[:m]  # sample & hold
        elif kind == 2:
            x = np.round(r.standard_normal(m) * 2) / 2  # bitcrush
        else:
            x = np.zeros(m) if r.random() < 0.5 else np.sin(2 * np.pi * r.uniform(2000, 5000) * t)
        x = x * r.uniform(0.4, 1.0)
        x[: ns(0.001)] *= np.linspace(0, 1, ns(0.001))[: min(ns(0.001), m)]
        st[:, s:e] += pan_st(x, r.uniform(-0.9, 0.9))
        s = e
    st[0] = lp(st[0], 9000)
    st[1] = lp(st[1], 9000)
    return st / np.max(np.abs(st))


def sfx_mouse(**_):
    n = ns(0.2)
    t = tt(n)
    out = np.zeros(n)
    for dt, f, g in [(0.0, 2600, 1.0), (0.085, 3300, 0.6)]:
        s = ns(dt)
        m = n - s
        tm = tt(m)
        x = hp(noise(m) * np.exp(-tm / 0.0012), 2500) + 0.8 * np.sin(2 * np.pi * f * tm) * np.exp(-tm / 0.005)
        x += 0.4 * np.sin(2 * np.pi * 350 * tm) * np.exp(-tm / 0.008)
        out[s:] += x * g
    return norm(out)


SYNTH = {
    "click": sfx_click, "tick": sfx_tick, "pop": sfx_pop, "type": sfx_type, "whoosh": sfx_whoosh,
    "dash": sfx_dash, "swish": sfx_swish, "air": sfx_air, "reverse": sfx_reverse, "riser": sfx_riser,
    "impact": sfx_impact, "snap": sfx_snap, "ding": sfx_ding, "sparkle": sfx_sparkle, "glitch": sfx_glitch, "mouse": sfx_mouse,
}
# ganho base por tipo (balanço entre famílias de sons)
BASE = {
    "click": 0.62, "tick": 0.48, "pop": 0.58, "type": 0.95, "whoosh": 0.85, "dash": 0.85, "swish": 0.5, "air": 0.6,
    "reverse": 0.7, "riser": 0.55, "impact": 0.62, "snap": 0.7, "ding": 0.6, "sparkle": 0.4, "glitch": 0.55, "mouse": 0.85,
}


def render_sfx(events, dur):
    bus = np.zeros((2, ns(dur + 2)))
    for ev in events:
        typ = ev["type"]
        x = SYNTH[typ](**{k: v for k, v in ev.items() if k not in ("t", "type", "gain")})
        if x.ndim == 1:
            x = pan_st(x, ev.get("pan", 0.0))
        g = ev.get("gain", 1.0) * BASE[typ]
        s = ns(ev["t"])
        e = min(bus.shape[1], s + x.shape[1])
        bus[:, s:e] += x[:, : e - s] * g
    return bus


# ----------------------------------------------------------------------------- música
BPM = 120
BEAT = 60 / BPM
BAR = 4 * BEAT


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# acordes por compasso (2 s cada): D, D, A, Bm, G, D(respiro), A, Bm, G, D
CHORDS = {
    "D": [62, 66, 69, 73], "A": [57, 61, 64, 71], "Bm": [59, 62, 66, 69], "G": [55, 59, 62, 66],
}
ROOT = {"D": 38, "A": 33, "Bm": 35, "G": 31}
PROG = ["D", "D", "A", "Bm", "G", "D", "A", "Bm", "G", "D"]


def kick(n=None):
    n = n or ns(0.4)
    t = tt(n)
    f = 46 + 110 * np.exp(-t / 0.03)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.18)
    x += 0.3 * hp(noise(n) * np.exp(-t / 0.002), 1500)
    return np.tanh(1.5 * x)


def clap():
    n = ns(0.35)
    t = tt(n)
    env = np.zeros(n)
    for d in (0.0, 0.009, 0.019):
        s = ns(d)
        env[s:] += np.exp(-tt(n - s) / (0.006 if d < 0.019 else 0.11))
    return bp(noise(n), 900, 3500) * env


def hat(open_=False):
    n = ns(0.3 if open_ else 0.06)
    t = tt(n)
    return hp(noise(n), 7000) * np.exp(-t / (0.09 if open_ else 0.012))


def saw(f, t, detune=0.0):
    ph = (f * (1 + detune)) * t
    return 2 * (ph - np.floor(ph + 0.5))


def pad_chord(notes, dur, cutoff):
    n = ns(dur)
    t = tt(n)
    x = np.zeros(n)
    for m in notes:
        f = midi(m)
        for d in (-0.006, 0.0, 0.0065):
            x += saw(f, t + rng.uniform(0, 1), d)
    x = lp(x, cutoff, 2)
    env = np.minimum(1, t / 0.08) * np.minimum(1, (dur - t) / 0.12).clip(0, 1)
    return x * env / len(notes)


def pluck(f, dur=0.3):
    n = ns(dur)
    t = tt(n)
    x = (np.sin(2 * np.pi * f * t) + 0.35 * saw(f, t)) * np.exp(-t / 0.08) * (1 - np.exp(-t / 0.002))
    return lp(x, 4500)


def bass_note(f, dur):
    n = ns(dur)
    t = tt(n)
    x = np.sin(2 * np.pi * f * t) + 0.35 * lp(saw(f, t), 600)
    env = (1 - np.exp(-t / 0.004)) * np.exp(-t / 0.22)
    return x * env


def place(bus, x, t0, g=1.0, pan=0.0):
    s = ns(t0)
    if s >= bus.shape[1]:
        return
    if x.ndim == 1:
        x = pan_st(x, pan)
    e = min(bus.shape[1], s + x.shape[1])
    bus[:, s:e] += x[:, : e - s] * g


def render_music(T, dur):
    N = ns(dur + 2)
    drums = np.zeros((2, N))
    bassb = np.zeros((2, N))
    padb = np.zeros((2, N))
    arpb = np.zeros((2, N))
    kicks = []
    K = kick()
    for bar, ch in enumerate(PROG):
        b0 = bar * BAR
        full = bar in (1, 2, 3, 4, 6, 7)
        if bar == 9:  # resolução final: bumbo nos tempos 1 e 3, hats leves
            for beat in (0, 2):
                place(drums, K, b0 + beat * BEAT, 0.7)
                kicks.append(b0 + beat * BEAT)
            place(bassb, bass_note(midi(ROOT[ch]), 1.2), b0, 0.6)
        if bar >= 8:
            for k in range(8):
                place(drums, hat(), b0 + k * BEAT / 2 + BEAT / 4, 0.1, 0.3)
        # ---- bateria
        for beat in range(4):
            tb = b0 + beat * BEAT
            if full:
                place(drums, K, tb, 0.95)
                kicks.append(tb)
                if beat in (1, 3):
                    place(drums, clap(), tb, 0.38, 0.05)
            if bar >= 1 and bar <= 7:
                place(drums, hat(), tb + BEAT / 2, 0.22 if full else 0.16, 0.25)
                if full and beat == 3 and bar % 2 == 0:
                    place(drums, hat(True), tb + BEAT / 2, 0.14, 0.25)
            if bar == 5:  # respiro: hats em 16 avos crescendo até o "Pix enviado!"
                for k in range(4):
                    place(drums, hat(), tb + k * BEAT / 4, 0.05 + 0.03 * beat, -0.2)
        # ---- baixo (colcheias no contratempo)
        if bar >= 1 and bar <= 7 and bar != 5:
            for k in range(8):
                if k % 2 == 1 or k == 0:
                    place(bassb, bass_note(midi(ROOT[ch]), 0.24), b0 + k * BEAT / 2, 0.55)
        # ---- pad
        cutoff = 700 + 1800 * (bar >= 1) + (600 if bar in (6, 7) else 0)
        if bar == 0:
            cutoff = 900
        if bar >= 8:
            cutoff = 2200
        place(padb, pad_chord(CHORDS[ch], BAR + 0.15, cutoff), b0, 0.5)
        # ---- arpejo plucado (colcheias), entra no drop
        if bar >= 1:
            notes = CHORDS[ch] + [CHORDS[ch][1] + 12]
            pattern = [0, 2, 1, 3, 4, 2, 3, 1]
            for k in range(8):
                if bar == 9 and k > 2:
                    break
                m = notes[pattern[k]] + 12
                place(arpb, pluck(midi(m)), b0 + k * BEAT / 2, 0.22 if bar != 5 else 0.14, 0.35 * (1 if k % 2 else -1))
    # intro: pluck suave antes do drop (cena branca)
    for k, m in enumerate([74, 78, 81, 85, 81, 78]):
        place(arpb, pluck(midi(m)), 0.5 + k * 0.25, 0.12, 0.3 * (1 if k % 2 else -1))
    # sidechain (bombeia o pad e o baixo com o bumbo)
    t = tt(N)
    duck = np.ones(N)
    for tk in kicks:
        s = ns(tk)
        m = min(N - s, ns(0.45))
        duck[s : s + m] = np.minimum(duck[s : s + m], 1 - 0.6 * np.exp(-tt(m) / 0.11))
    padb *= duck
    bassb *= duck
    # música abaixa enquanto a tela escura cresce (tensão) e volta junto com o impacto do endcard
    gate = np.ones(N)
    a, b = ns(T["expand"] + 0.05), ns(T["end"])
    gate[a:b] = np.linspace(1, 0.15, b - a)
    pad_wet = reverb(padb, wet=0.35)[:, :N]
    arp_wet = reverb(arpb, wet=0.45)[:, :N]
    drums_w = reverb(drums, wet=0.12)[:, :N]
    music = 0.55 * pad_wet + 0.6 * bassb + 0.9 * drums_w + 0.75 * arp_wet
    music *= gate
    # final: fade nos últimos 0,6 s
    f0 = ns(dur - 0.6)
    music[:, f0 : ns(dur)] *= np.linspace(1, 0, ns(dur) - f0) ** 1.5
    music[:, ns(dur) :] = 0
    return music


# ----------------------------------------------------------------------------- mix
def limiter(x, ceiling=0.87, look=0.005, release=0.08):
    """Limitador com look-ahead: ganho = min(1, teto/|x|), suavizado."""
    peak = np.abs(x).max(axis=0)
    g = np.minimum(1, ceiling / np.maximum(peak, 1e-9))
    L = ns(look)
    # mínimo móvel (look-ahead) → o ganho já está baixo quando o pico chega
    from numpy.lib.stride_tricks import sliding_window_view
    gp = np.concatenate([g, np.ones(L)])
    g = sliding_window_view(gp, L + 1).min(axis=1)[: len(g)]
    # release exponencial (ataque instantâneo)
    a = np.exp(-1 / (release * SR))
    out = np.empty_like(g)
    cur = 1.0
    for i in range(0, len(g), 64):  # em blocos para não ficar lento
        blk = g[i : i + 64]
        m = blk.min()
        cur = m if m < cur else cur * a ** 64 + m * (1 - a ** 64)
        out[i : i + 64] = min(cur, m) if m < cur else cur
    out = np.minimum(out, g)
    out = signal.lfilter([0.2], [1, -0.8], out)  # suaviza degraus dos blocos
    out = np.minimum(out, g)
    return x * out

def main(inp, out):
    data = json.load(open(inp))
    T, dur, events = data["T"], data["dur"], data["sfx"]
    sfx = render_sfx(events, dur)
    sfx = reverb(sfx, wet=0.12)[:, : sfx.shape[1]]
    music = render_music(T, dur)
    n = min(sfx.shape[1], music.shape[1])
    sfx, music = sfx[:, :n], music[:, :n]
    rms = lambda x: np.sqrt(np.mean(x ** 2) + 1e-12)
    music *= 10 ** (-23 / 20) / rms(music)
    # ducking: a trilha abaixa até ~6 dB quando os efeitos tocam
    env = np.abs(sfx).max(axis=0)
    env = signal.lfilter([1 - np.exp(-1 / (0.12 * SR))], [1, -np.exp(-1 / (0.12 * SR))], env)
    duck = 1 - 0.5 * np.clip(env / 0.25, 0, 1)
    mix = sfx + music * duck
    mix = hp(mix, 25)
    mix = lp(mix, 17500)
    mix = limiter(mix * 10 ** (4 / 20), ceiling=10 ** (-2.2 / 20))
    mix = mix[:, : ns(dur)]
    import wave

    pcm = (np.clip(mix.T, -1, 1) * 32767 * 0.97).astype("<i2")
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"audio ok: {out} ({mix.shape[1] / SR:.2f}s, {len(events)} efeitos)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
