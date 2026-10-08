# AD Inter — Indústria (20 s, motion graphics)

Anúncio de 20 s, 1080×1080 e 30 fps, no estilo do vídeo de referência: palavras com blur,
degradê vivo, barra de busca, card com anel 3D de ícones, botão de status, nuvens e endcard
com glitch. Tudo foi feito em código: a animação é HTML/CSS renderizado quadro a quadro no
Chromium, e o som é sintetizado em Python, sem samples.

**Arquivo final:** `inter_industria_ad_20s.mp4`

## Roteiro

| Tempo | Cena | Efeitos sonoros |
|---|---|---|
| 0,0–2,0 | Fundo branco. A engrenagem entra girando e aparece "Pronto pra acelerar" palavra por palavra | whoosh, clique, pops, riser |
| 2,0–3,8 | O degradê laranja entra varrendo a tela e aparece "sua indústria?". O texto vira uma pílula de vidro | impacto + whoosh (drop), pops, clique, dash |
| 3,8–6,5 | Barra de busca com "Inter Empresas" sendo digitado. Ela sobe e vira um card (Conta PJ, Pix e boletos, Capital de giro, Câmbio) | digitação tecla a tecla, whoosh, pop, ticks |
| 6,9–9,9 | Anel 3D com 14 ícones industriais e bancários. Depois gira rápido e sai | whoosh grande, ticks, dash giratório |
| 9,9–12,6 | "Pague, receba e invista. Tudo em um só app." Botão "Enviando Pix…" → "Pix enviado!" | pops, ticks de processamento, riser, ding + brilho |
| 12,6–16,0 | Nuvens e fábricas sobem. "Acelere sua indústria." CTA "Abra sua conta PJ" e o cursor clica | whoosh de ar, pops, dash, clique de mouse, reverse |
| 16,0–20,0 | Endcard escuro. Os raios do símbolo abrem em leque, o "inter" monta letra por letra, as barras entram com glitch e aparece a URL inter.co/empresas | impacto, dash, ticks melódicos, pops, glitch, digitação, brilho |

Trilha: house/pop a 120 BPM em Ré maior. O drop sincroniza com a entrada do degradê. Em
10–12 s há um respiro enquanto o Pix "processa" e a batida volta no "Pix enviado!". O fim
resolve em IV→I no endcard. A trilha abaixa automaticamente (ducking) quando os efeitos tocam.

## Estrutura

- `ad.html`: a animação inteira. `render(t)` é uma função pura do tempo, e o mesmo
  cronograma `T` gera a lista de efeitos sonoros (`window.SFX`), então imagem e som
  ficam sempre sincronizados. Para mudar textos ou tempos, edite `T`, `ROWS`,
  `HEAD_LINES` etc.
- `assets/logo.js`: o logo Inter vetorizado a partir das imagens enviadas, com a geometria dos raios do símbolo.
- `tools/vectorize.py` e `tools/make_logo_js.py`: vetorização do logo (potrace).
- `tools/clouds.py`: texturas de nuvem e vapor.
- `tools/render.mjs`: render no Chromium (Playwright) com motion blur e processos em paralelo.
- `tools/audio.py`: síntese dos efeitos e da trilha, mixagem, ducking e limitador.
- `build.sh`: gera tudo de ponta a ponta.

## Gerar de novo

```bash
pip install numpy scipy pillow potracer
./build.sh            # FPS=30 SUB=2 JOBS=4 por padrão
```

Para ver um instante específico: abra `ad.html?t=12.2` no navegador, ou rode
`node tools/render.mjs frames out/ 12.2`.

> Os textos e afirmações do anúncio (por exemplo "Conta PJ digital", "Pix e boletos" e a URL)
> são de exemplo. Confirme com a marca antes de publicar.
