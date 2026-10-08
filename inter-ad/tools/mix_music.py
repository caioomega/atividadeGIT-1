"""Mixa uma música enviada (ex.: DARK AURA FUNK – elude) com os efeitos sonoros do AD.

Uso: python3 tools/mix_music.py sfx.json musica.mp3 INICIO saida.wav

- Recorta [INICIO, INICIO + duração do AD] da música (fade-in curto, fade-out no fim).
- Sintetiza os SFX (mesmas funções de tools/audio.py).
- Ducking: a música abaixa até ~7 dB a cada efeito, para os SFX "furarem" a batida.
- Limitador no master (teto -2,3 dBFS de amostra → true peak ≈ -1 dBFS).
"""
import json
import os
import subprocess
import sys
import wave

import numpy as np
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio as A  # noqa: E402

SR = A.SR

# ganhos por família de efeito nesta versão (música alta e comprimida → efeitos mais à frente)
BASE_FUNK = {
    "click": 0.85, "tick": 0.62, "pop": 0.8, "type": 1.25, "whoosh": 1.0, "dash": 1.0, "swish": 0.6, "air": 0.75,
    "reverse": 0.85, "riser": 0.6, "impact": 0.7, "snap": 1.0, "ding": 0.85, "sparkle": 0.55, "glitch": 0.6, "mouse": 1.1,
}


def load_music(path, start, dur):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", f"{start:.4f}", "-t", f"{dur + 0.5:.4f}", "-i", path,
         "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
        capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).T.astype(np.float64)


def follower(x, attack, release):
    """Seguidor de envelope (ataque/relaxamento em segundos)."""
    a_att, a_rel = np.exp(-1 / (attack * SR)), np.exp(-1 / (release * SR))
    # ataque rápido via máximo móvel + relaxamento exponencial (vetorizado com lfilter)
    rel = signal.lfilter([1 - a_rel], [1, -a_rel], x)
    att = signal.lfilter([1 - a_att], [1, -a_att], x)
    return np.maximum(rel, att)


def main(sfx_json, music_path, start, out):
    data = json.load(open(sfx_json))
    dur, events = data["dur"], data["sfx"]
    N = A.ns(dur)

    music = load_music(music_path, float(start), dur)
    if music.shape[1] < N:
        music = np.pad(music, ((0, 0), (0, N - music.shape[1])))
    music = music[:, :N]
    fi, fo = A.ns(0.015), A.ns(0.35)
    music[:, :fi] *= np.linspace(0, 1, fi)
    music[:, N - fo:] *= np.linspace(1, 0, fo) ** 1.5

    A.BASE.update(BASE_FUNK)
    sfx = A.render_sfx(events, dur)[:, :N]
    sfx = A.reverb(sfx, wet=0.1)[:, :N]

    rms = lambda x: np.sqrt(np.mean(x ** 2) + 1e-12)
    music *= 10 ** (-17 / 20) / rms(music)

    # ducking: até -7 dB quando há efeito tocando
    env = follower(np.abs(sfx).max(axis=0), attack=0.004, release=0.16)
    duck_db = -7.0 * np.clip(env / 0.18, 0, 1)
    duck = 10 ** (duck_db / 20)
    mix = music * duck + sfx
    mix = A.lp(mix, 18000)
    mix = A.limiter(mix * 10 ** (2.5 / 20), ceiling=10 ** (-2.3 / 20))

    pcm = (np.clip(mix.T, -1, 1) * 32767).astype("<i2")
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())

    # relatório: pico de cada família de efeito vs. nível da música (já com ducking) no mesmo instante
    print(f"audio ok: {out} ({N / SR:.2f}s, {len(events)} efeitos)")
    db = lambda v: 20 * np.log10(v + 1e-9)
    by = {}
    for ev in events:
        s = A.ns(ev["t"])
        e = min(N, s + A.ns(0.12))
        if e <= s:
            continue
        pk = np.abs(sfx[:, s:e]).max()
        mr = rms((music * duck)[:, s:e])
        mp = np.abs((music * duck)[:, s:e]).max()
        by.setdefault(ev["type"], []).append((db(pk) - db(mr), db(pk) - db(mp)))
    for k, v in sorted(by.items()):
        v = np.array(v)
        print(f"  {k:8s} pico do efeito vs música: {np.median(v[:, 0]):+5.1f} dB (RMS) | {np.median(v[:, 1]):+5.1f} dB (pico)  n={len(v)}")


if __name__ == "__main__":
    main(*sys.argv[1:5])
