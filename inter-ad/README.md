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

## Versão 2: com a música "DARK AURA FUNK (Slowed) – elude"

**Arquivo:** `inter_industria_ad_funk_20s.mp4`

É o mesmo roteiro, com a mesma intenção, mas sincronizado com a música enviada:

- Uso o trecho de 6,93 s a 26,93 s da faixa. São 1,85 s de intro, e então o drop (o 808) entra
  junto com o degradê laranja. O vídeo termina exatamente onde a seção pesada da música acaba.
- Todas as entradas de texto, trocas de cena, cliques e o endcard caem na batida
  (112,26 BPM, uma batida a cada 0,5345 s). O cronograma está em `T_FUNK`, dentro do `ad.html`.
- O visual é mais limpo: sem glitch e sem faíscas.
- Os SFX são menos numerosos e mais destacados. Usei agudos e transientes claros, que passam
  por cima do 808. A música abaixa até 7 dB a cada efeito (ducking), então os picos dos
  efeitos ficam de 4 a 10 dB acima da música.
- Os SFX com nota (ticks dos raios do logo, "ding" do Pix) estão afinados em Si, Mi e Fá#,
  notas do tom da música (Si menor).

A música não vai para o repositório: `music/` está no `.gitignore`. Para gerar de novo,
coloque o mp3 em `music/dark_aura_funk_elude.mp3` e rode `VARIANT=funk ./build.sh`.

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
- `tools/mix_music.py`: mixa uma música enviada com os efeitos (versão funk).
- `build.sh`: gera tudo de ponta a ponta.

## Gerar de novo

```bash
pip install numpy scipy pillow potracer
./build.sh                 # versão 1 (FPS=30 SUB=2 JOBS=4 por padrão)
VARIANT=funk ./build.sh    # versão com a música
```

Para ver um instante específico: abra `ad.html?t=12.2` (ou `ad.html?v=funk&t=12.2`) no navegador,
ou rode `node tools/render.mjs frames out/ 12.2` (com `AD_VARIANT=funk` para a versão 2).

> Os textos e afirmações do anúncio (por exemplo "Conta PJ digital", "Pix e boletos" e a URL)
> são de exemplo. Confirme com a marca antes de publicar.
