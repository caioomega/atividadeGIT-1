#!/usr/bin/env bash
# Gera o AD completo: texturas → vídeo (Chromium) → áudio (síntese) → mp4 final.
# Requisitos: node + playwright (Chromium), python3 (numpy, scipy, pillow, potracer), ffmpeg.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build

FPS=${FPS:-30}      # quadros por segundo
SUB=${SUB:-2}       # subquadros por quadro (motion blur)
JOBS=${JOBS:-4}     # processos de render em paralelo

python3 tools/clouds.py assets
node tools/render.mjs sfx build/sfx.json
node tools/render.mjs video build/video_noaudio.mp4 "$FPS" "$SUB" "$JOBS"
python3 tools/audio.py build/sfx.json build/audio.wav

# leve granulação para evitar banding nos degradês + áudio AAC
ffmpeg -y -v error -i build/video_noaudio.mp4 -i build/audio.wav \
  -vf "noise=alls=3:allf=u,format=yuv420p" \
  -c:v libx264 -preset slow -crf 17 -profile:v high -movflags +faststart \
  -c:a aac -b:a 256k -ar 48000 -shortest \
  inter_industria_ad_20s.mp4
echo "pronto: inter_industria_ad_20s.mp4"
