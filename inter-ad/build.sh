#!/usr/bin/env bash
# Gera o AD completo: texturas → vídeo (Chromium) → áudio → mp4 final.
# Requisitos: node + playwright (Chromium), python3 (numpy, scipy, pillow, potracer), ffmpeg.
#
#   ./build.sh                 → versão 1 (trilha sintetizada)        → inter_industria_ad_20s.mp4
#   VARIANT=funk ./build.sh    → versão com a música DARK AURA FUNK   → inter_industria_ad_funk_20s.mp4
#                                (coloque o mp3 em music/dark_aura_funk_elude.mp3 ou passe MUSIC=...)
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build

FPS=${FPS:-30}      # quadros por segundo
SUB=${SUB:-2}       # subquadros por quadro (motion blur)
JOBS=${JOBS:-4}     # processos de render em paralelo
VARIANT=${VARIANT:-v1}

python3 tools/clouds.py assets

if [ "$VARIANT" = "funk" ]; then
  MUSIC=${MUSIC:-music/dark_aura_funk_elude.mp3}
  START=${START:-6.935}   # trecho da música: o drop (808) cai em 1,85 s do AD
  export AD_VARIANT=funk
  node tools/render.mjs sfx build/sfx_funk.json
  node tools/render.mjs video build/video_funk_noaudio.mp4 "$FPS" "$SUB" "$JOBS"
  python3 tools/mix_music.py build/sfx_funk.json "$MUSIC" "$START" build/audio_funk.wav
  VIDEO=build/video_funk_noaudio.mp4; AUDIO=build/audio_funk.wav; OUT=inter_industria_ad_funk_20s.mp4
else
  node tools/render.mjs sfx build/sfx.json
  node tools/render.mjs video build/video_noaudio.mp4 "$FPS" "$SUB" "$JOBS"
  python3 tools/audio.py build/sfx.json build/audio.wav
  VIDEO=build/video_noaudio.mp4; AUDIO=build/audio.wav; OUT=inter_industria_ad_20s.mp4
fi

# granulação estática leve (evita banding nos degradês) + áudio AAC
ffmpeg -y -v error -i "$VIDEO" -i "$AUDIO" \
  -vf "noise=alls=3:allf=u,format=yuv420p" \
  -c:v libx264 -preset slow -crf 17 -profile:v high -movflags +faststart \
  -c:a aac -b:a 256k -ar 48000 -shortest \
  "$OUT"
echo "pronto: $OUT"
