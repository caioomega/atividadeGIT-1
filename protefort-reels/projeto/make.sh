#!/bin/bash
# Full pipeline. usage: ./make.sh <out_name> [vo.wav]
set -e
D=$(cd "$(dirname "$0")" && pwd); B=$D/build; O=$D/out
NAME=$1; VO=$2
rm -rf $O/frames
node $B/render.js frames $O/frames 30 4 | tail -1
python3 -I $D/tools/audio.py $O/sfx.json $B/cues.js $O
ENC="-c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -profile:v high -r 30 -movflags +faststart -c:a aac -b:a 192k -ar 48000"
LIM="alimiter=limit=0.95:level=false,loudnorm=I=-14:TP=-1.5:LRA=11"
if [ -n "$VO" ]; then
  ffmpeg -v error -y -framerate 30 -i $O/frames/f_%05d.jpg -i $O/music.wav -i $O/sfx.wav -i "$VO" -filter_complex \
   "[3:a]aresample=48000,pan=stereo|c0=c0|c1=c0,apad,asplit[v1][v2];[1:a]volume=0.55[m];[m][v1]sidechaincompress=threshold=0.03:ratio=9:attack=15:release=380:makeup=1[md];[2:a]volume=0.7[s];[md][s][v2]amix=inputs=3:normalize=0:duration=first,$LIM[a]" \
   -map 0:v -map "[a]" $ENC -shortest "$D/$NAME.mp4"
else
  ffmpeg -v error -y -framerate 30 -i $O/frames/f_%05d.jpg -i $O/music.wav -i $O/sfx.wav -filter_complex \
   "[1:a]volume=0.62[m];[2:a]volume=0.9[s];[m][s]amix=inputs=2:normalize=0,$LIM[a]" -map 0:v -map "[a]" $ENC -shortest "$D/$NAME.mp4"
  ffmpeg -v error -y -framerate 30 -i $O/frames/f_%05d.jpg -i $O/sfx.wav -filter_complex "[1:a]$LIM[a]" -map 0:v -map "[a]" $ENC -shortest "$D/${NAME}_so_efeitos.mp4"
fi
echo done
