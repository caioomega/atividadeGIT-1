# Café Santa Luzia: Reels 30 s (motion graphics rústico)

Vídeo vertical (1080×1920, 30 fps, 30 s) para o @cafe.santa.luzia, de Mococa-SP. Segue a
identidade da marca: preto, dourado gravado, sépia, verde da folha e vermelho do café-cereja.
As fontes têm o mesmo espírito do logo: **Rye** (letreiro do "SANTA LUZIA"), **Cinzel** (versaletes
do "TRADIÇÃO E QUALIDADE") e **IM Fell English** (itálico antigo). Todas são licença OFL.

**Arquivo:** `cafe_santa_luzia_30s_sem_locucao.mp4`. Quando a locução for gerada, a versão
final sai como `cafe_santa_luzia_30s.mp4`.

## Roteiro

| Tempo | Cena | Locução (ElevenLabs v4, voz "Francis – Minas Gerais") | Efeitos |
|---|---|---|---|
| 0–6,1 | Amanhecer na roça: sol nascendo, morros gravados com fileiras de café, casa da fazenda, passarinhos. Aparece "MOCOCA · SP" | "Lá em Mococa, interior de São Paulo… o dia começa cedo na roça." | vento, passarinhos (com bem-te-vi), grilos, galo ao longe, brilho |
| 6,1–10,9 | A tinta se espalha e revela os colhedores do logo numa moldura dourada; a câmera vai do mais velho ao mais novo | "Cada pé de café é cuidado com o carinho de quem aprendeu com os mais velhos." | papel, swish, batida de madeira |
| 10,9–15,0 | "100% ARÁBICA" carimbado; um galho de café cresce e as cerejas brotam; fita "Variedade Arara" | "Café 100% arábica… variedade Arara." | carimbo de madeira, batidinhas afinadas a cada cereja, fita desenrolando |
| 15,0–19,1 | Casa da fazenda desenhada à mão; um caminho pontilhado leva os grãos até a xícara, que se enche e solta vapor | "Da nossa fazenda… direto pra sua xícara." | grãos rolando, xícara no pires, café sendo servido, colherzinha |
| 19,1–23,2 | O pacote preto com o rótulo cai na mesa; grãos espalhados; brilho dourado; fita "Tradição e Qualidade" | "Café Santa Luzia. Tradição e qualidade." | pacote pousando, grãos, brilho |
| 23,2–30 | Logo completo com moldura de arabescos; "Peça pelo WhatsApp", @cafe.santa.luzia | "Peça já o seu pelo WhatsApp." | carimbo, acorde final da viola, passarinhos |

**Trilha "roça":** toada caipira a 88 BPM em Mi maior, sintetizada (sem samples):

- viola caipira com cordas duplas fazendo a melodia em terças, o dueto típico da moda de viola;
- violão de nylon com baixo e acorde no ritmo de toada;
- sanfona com palhetas levemente desafinadas (musette), ganzá e bumbo leve.

Os cortes de cena caem na batida da trilha. Com a locução, a trilha abaixa 9 dB sob a voz.

**Visual rústico:** papel envelhecido, hachuras de gravura, transições de "tinta se espalhando",
granulação de película, poeira e riscos, oscilação leve de luz e vazamento de luz quente.

## Locução (ElevenLabs)

O roteiro já está pronto no flow "Café Santa Luzia – Reels 30s" do ElevenLabs (modelo
`eleven_v4`, voz Francis). A geração falhou por falta de créditos: a conta tinha 61 de 10.000,
e cada take custa ~335. Com créditos disponíveis:

```bash
VO=caminho/da/locucao.mp3 ./build.sh
```

O `tools/align_vo.py` acha as 6 frases pelas pausas e encaixa a voz entre 1 s e ~26,8 s. Se
ela passar disso, acelera no máximo 12%, sem mudar o tom. Os cortes de cena e os textos se
reposicionam sozinhos, sempre caindo na batida.

## Estrutura

- `video.html`: a animação inteira (`render(t)`). Os tempos vêm das frases da locução (`VO`).
- `tools/textures.py`: papéis, máscaras de tinta e recortes do logo.
- `tools/render.mjs`: render no Chromium com motion blur e 4 processos em paralelo.
- `tools/audio.py`: trilha caipira (Karplus-Strong, sanfona aditiva), efeitos, ducking e limitador.
- `tools/align_vo.py`: encaixe da locução.
- `build.sh`: gera tudo de ponta a ponta.

> Textos de exemplo, baseados na bio da marca: 100% Arábica, Variedade Arara, Mococa-SP,
> "Da fazenda para sua xícara" e pedidos pelo WhatsApp. Confirme com o cliente antes de publicar.
