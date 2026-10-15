#!/usr/bin/env bash
# Gera o Reels do Café Santa Luzia (30 s, 1080x1920).
# Requisitos: node + playwright (Chromium), python3 (numpy, scipy, pillow), ffmpeg.
#
#   ./build.sh                          → versão sem locução (trilha + efeitos + textos)
#   VO=locucao.mp3 ./build.sh           → com a locução do ElevenLabs encaixada automaticamente
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build

FPS=${FPS:-30}; SUB=${SUB:-2}; JOBS=${JOBS:-4}
VOARG=""
OUT=cafe_santa_luzia_30s_sem_locucao.mp4

python3 tools/textures.py assets
if [ -n "${VO:-}" ]; then
  python3 tools/align_vo.py "$VO" build/vo_aligned.wav build/vo_times.json
  export VO_TIMES=build/vo_times.json
  VOARG=build/vo_aligned.wav
  OUT=cafe_santa_luzia_30s.mp4
fi
node tools/render.mjs sfx build/sfx.json
node tools/render.mjs video build/video_noaudio.mp4 "$FPS" "$SUB" "$JOBS"
python3 tools/audio.py build/sfx.json build/audio.wav $VOARG

ffmpeg -y -v error -i build/video_noaudio.mp4 -i build/audio.wav \
  -vf "format=yuv420p" -c:v libx264 -preset slow -crf 18 -profile:v high -movflags +faststart \
  -c:a aac -b:a 256k -ar 48000 -shortest "$OUT"
echo "pronto: $OUT"
