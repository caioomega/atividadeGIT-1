#!/bin/bash
# Full pipeline. usage: [FPS=60] [SKIP_RENDER=1] ./make.sh <out_name> [vo.wav]
set -e
D=$(cd "$(dirname "$0")" && pwd); B=$D/build; O=$D/out
NAME=$1; VO=$2; FPS=${FPS:-60}
if [ -z "$SKIP_RENDER" ]; then rm -rf $O/frames; node $B/render.js frames $O/frames $FPS 4 | tail -1; fi
python3 -I $D/tools/audio.py $O/sfx.json $B/cues.js $O
ENC="-c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -profile:v high -level 4.2 -r $FPS -g $((FPS/2)) -movflags +faststart -c:a aac -b:a 256k -ar 48000"
LIM="alimiter=limit=0.95:level=false,loudnorm=I=-14:TP=-1.5:LRA=11"
# music is ducked by the sound design (and by the voice when present) so every hit punches through
if [ -n "$VO" ]; then
  ffmpeg -v error -y -framerate $FPS -i $O/frames/f_%05d.jpg -i $O/music.wav -i $O/sfx.wav -i "$VO" -filter_complex \
   "[3:a]aresample=48000,pan=stereo|c0=c0|c1=c0,apad,asplit[v1][v2];[2:a]volume=0.6,asplit[s1][s2];[1:a]volume=0.45[m];[m][v1]sidechaincompress=threshold=0.03:ratio=9:attack=15:release=380[m2];[m2][s1]sidechaincompress=threshold=0.06:ratio=3:attack=5:release=180[md];[md][s2][v2]amix=inputs=3:normalize=0:duration=first,$LIM[a]" \
   -map 0:v -map "[a]" $ENC -shortest "$D/$NAME.mp4"
else
  ffmpeg -v error -y -framerate $FPS -i $O/frames/f_%05d.jpg -i $O/music.wav -i $O/sfx.wav -filter_complex \
   "[2:a]volume=0.95,asplit[s1][s2];[1:a]volume=0.55[m];[m][s1]sidechaincompress=threshold=0.06:ratio=3:attack=5:release=180[md];[md][s2]amix=inputs=2:normalize=0,$LIM[a]" \
   -map 0:v -map "[a]" $ENC -shortest "$D/$NAME.mp4"
  ffmpeg -v error -y -framerate $FPS -i $O/frames/f_%05d.jpg -i $O/sfx.wav -filter_complex "[1:a]$LIM[a]" -map 0:v -map "[a]" $ENC -shortest "$D/${NAME}_so_efeitos.mp4"
fi
echo done
