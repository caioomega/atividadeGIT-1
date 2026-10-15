"""Encaixa a locução do ElevenLabs no vídeo.

Uso: python3 tools/align_vo.py locucao.mp3 build/vo_aligned.wav build/vo_times.json [inicio=1.0] [fim_max=26.8]

1. Acha as 6 frases do roteiro pelas 5 maiores pausas da fala (as tags [pause] do roteiro).
2. Remonta a voz: frase 1 começa em `inicio`, respiros iguais entre frases (0,4–1,0 s),
   e, se ainda passar de `fim_max`, acelera levemente (no máximo 12%, sem mudar o tom).
3. Grava o áudio alinhado (48 kHz) e os tempos de cada frase — o video.html usa esses tempos
   para posicionar cortes e textos (VO_TIMES=build/vo_times.json no render).
"""
import json
import subprocess
import sys
import wave

import numpy as np

SR = 48000
N_PHRASES = 6


def load(path, tempo=1.0):
    af = ["-af", f"atempo={tempo:.4f}"] if abs(tempo - 1) > 1e-3 else []
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, *af, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def phrases(x):
    hop = SR // 100
    n = len(x) // hop
    rms = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(axis=1))
    db = 20 * np.log10(rms + 1e-9)
    thr = max(-45.0, db.max() - 32)
    voiced = db > thr
    segs, i = [], 0
    while i < n:
        if voiced[i]:
            j = i
            while j < n and voiced[j]:
                j += 1
            segs.append([i, j])
            i = j
        else:
            i += 1
    # junta picos muito curtos/colados (respiração, sílabas)
    merged = []
    for s in segs:
        if merged and s[0] - merged[-1][1] < 8:   # < 80 ms
            merged[-1][1] = s[1]
        else:
            merged.append(s)
    merged = [s for s in merged if s[1] - s[0] >= 6]
    if len(merged) < N_PHRASES:
        raise SystemExit(f"achei só {len(merged)} trechos de fala; esperava {N_PHRASES}")
    gaps = sorted(range(len(merged) - 1), key=lambda k: merged[k + 1][0] - merged[k][1], reverse=True)[: N_PHRASES - 1]
    cuts = sorted(gaps)
    out, a = [], 0
    for c in cuts + [len(merged) - 1]:
        out.append((merged[a][0] * hop, merged[c][1] * hop))
        a = c + 1
    return out


def main(src, dst, times_json, start=1.0, end_max=26.8):
    start, end_max = float(start), float(end_max)
    tempo = 1.0
    for _ in range(3):
        x = load(src, tempo)
        ph = phrases(x)
        pre, post = int(0.06 * SR), int(0.12 * SR)
        chunks = [x[max(0, a - pre): min(len(x), b + post)] for a, b in ph]
        speech = sum(len(c) for c in chunks) / SR
        gap = np.clip((end_max - start - speech) / (N_PHRASES - 1), 0.4, 1.0)
        total = start + speech + gap * (N_PHRASES - 1)
        if total <= end_max + 1e-3 or tempo >= 1.12:
            break
        tempo = min(1.12, tempo * (total - start) / (end_max - start))
    out = np.zeros(int((total + 1.0) * SR))
    times, t = [], start
    for c in chunks:
        s = int(t * SR)
        fade = int(0.01 * SR)
        c = c.copy()
        c[:fade] *= np.linspace(0, 1, fade)
        c[-fade:] *= np.linspace(1, 0, fade)
        out[s: s + len(c)] += c
        times.append([round(t + 0.06, 3), round(t + len(c) / SR - 0.12, 3)])
        t += len(c) / SR + gap
    pcm = (np.clip(np.vstack([out, out]).T, -1, 1) * 32767).astype("<i2")
    with wave.open(dst, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    json.dump({"phrases": times, "tempo": round(tempo, 4), "gap": round(float(gap), 3)}, open(times_json, "w"), indent=1)
    print(f"locução alinhada: {len(times)} frases, respiro {gap:.2f}s, andamento x{tempo:.3f}, termina em {times[-1][1]:.2f}s")
    for k, (a, b) in enumerate(times, 1):
        print(f"  frase {k}: {a:6.2f} → {b:6.2f}")


if __name__ == "__main__":
    main(*sys.argv[1:6])
