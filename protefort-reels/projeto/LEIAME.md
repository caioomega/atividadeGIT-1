# Como renderizar de novo

```bash
cd build && npm install && cd ..
pip install scipy numpy
FPS=60 ./make.sh protefort_reels_60fps         # sem locução
# com locução (vo.wav) + palavras do Scribe (words.json):
python3 tools/align.py words.json build/cues.js     # reposiciona as cenas na voz
./make.sh protefort_reels_final vo.wav
```

O render usa Chromium headless (playwright-core). Ajuste o `EXE` em `build/render.js` para o caminho do seu Chrome.
