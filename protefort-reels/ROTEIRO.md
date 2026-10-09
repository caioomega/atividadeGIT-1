# Protefort Calçados: Reels em motion graphics

**Formato:** 1080×1920 (9:16), **60 fps**, 35,5 s. H.264 High + AAC 256k, mixado em -14 LUFS.
**Paleta (tirada do logo):** laranja `#F58634`, grafite `#363435`, cinza `#858688`, fundo off-white `#F6F4F1`.
**Fonte:** Poppins (400–900).
**Estilo:** baseado no vídeo de referência. Fundo claro, tipografia cinética, ícones e cards que "pulam", telas cheias na cor da marca, câmera com tremor nos impactos, logo animado no final.

## Arquivos

| Arquivo | O que é |
|---|---|
| `protefort_reels_60fps.mp4` | Vídeo completo em 60 fps com trilha + desenho de som (sem locução) |
| `protefort_reels_60fps_so_efeitos.mp4` | Só os efeitos sonoros, para colocar uma música do próprio Instagram |
| `projeto/` | Código-fonte da animação (HTML/GSAP), da trilha e do pipeline de render |

## Locução (ElevenLabs v4)

**Voz escolhida:** *Nassif – Persuasive Sales & Ads* (`zhza6dIY7yb1xz5MKTvQ`), locutor brasileiro de anúncios, rápido e enérgico.
**Modelo:** `eleven_v4`.

> **Pendente:** a conta do ElevenLabs está sem créditos. Restam 61 dos 10.000 do plano, e um take da locução custa cerca de 519. As gerações falharam e nenhum crédito foi cobrado. Com créditos disponíveis, a locução é gerada, as cenas se reposicionam sozinhas pelos tempos das palavras (transcrição Scribe → `tools/align.py`) e o vídeo é renderizado de novo com a trilha abaixando por baixo da voz.

Texto enviado ao v4 (as tags entre colchetes controlam a interpretação):

```
[excited] Seu trabalho é pesado? Então o seu calçado tem que ser FORTE!
Lama… impacto… horas e horas em pé…
[confident] A Protefort aguenta tudo isso com você.
Direto de Mococa, são 25 anos protegendo quem faz o Brasil acontecer!
Botinas, coturnos, tênis e sapatos de segurança.
Todos com C.A. e solado bidensidade: mais conforto, mais firmeza, do primeiro ao último passo.
Na obra, na indústria, no hospital ou no campo…
[excited] Proteção… FORTE! Isso é Protefort.
Calçados profissionais pra quem trabalha de verdade!
```

## Storyboard

| Tempo | Locução | Na tela |
|---|---|---|
| 0–1,8 s | Seu trabalho é pesado? | Wipe laranja com o logo → "SEU TRABALHO É **PESADO?**" cai do topo com tremor, poeira e faixas zebradas de obra |
| 1,8–4 s | Então o seu calçado tem que ser FORTE! | Whip pan → "CALÇADO / TEM QUE SER / **FORTE!**" + botina despencando e pisando forte (ondas de choque) |
| 4–7,4 s | Lama… impacto… horas em pé… | Três cards com ícones (gota, raio, relógio) surgindo no ritmo |
| 7,4–9,6 s | A Protefort aguenta tudo isso com você | Os cards viram ✓ laranja → círculo laranja toma a tela: "A PROTEFORT **AGUENTA TUDO** ISSO COM VOCÊ" |
| 9,6–14 s | Direto de Mococa, 25 anos… Brasil acontecer | O círculo encolhe e vira pin de mapa: "**MOCOCA** – SÃO PAULO • BRASIL" → contador 0→25 com arco → "PROTEGENDO QUEM FAZ O **BRASIL** ACONTECER!" |
| 14–17,7 s | Botinas, coturnos, tênis e sapatos de segurança | Carrossel de produtos (01/04…04/04) → grade 2×2 "**DE SEGURANÇA**" |
| 17,7–23,3 s | Todos com C.A. e solado bidensidade… passo | Selo **C.A.** carimbando → corte do solado separando as camadas (amortecimento / resistência) com "+ CONFORTO" e "+ FIRMEZA" → pegadas atravessando a tela: "DO PRIMEIRO AO ÚLTIMO **PASSO**" |
| 23,3–26,4 s | Na obra, na indústria, no hospital ou no campo | Tela grafite com quatro blocos (capacete, fábrica, hospital, trator) acendendo em laranja |
| 26,4–29,6 s | Proteção… FORTE! Isso é Protefort. | "PROTEÇÃO" + "FORTE" → as letras "ÇÃO" e "E" caem e o resto se junta em **PROTEFORT** → o logo se monta (P cai, sombra desliza, anel laranja se desenha) |
| 29,6–35,5 s | Calçados profissionais pra quem trabalha de verdade! | "CALÇADOS PROFISSIONAIS / PRA QUEM TRABALHA **DE VERDADE!**" → CTA: protefortcalcados.com.br · @protefortcalcados · Mococa • SP |

## Informações usadas (pesquisa)

- **Protefort Calçados Profissionais Ltda.**, Mococa/SP. Fabrica calçados ocupacionais e de segurança.
- "25 anos protegendo quem faz o Brasil acontecer" (site oficial; o Instagram diz que atua desde 2001).
- Todos os calçados têm C.A. (Certificado de Aprovação) do Ministério do Trabalho e Emprego, e o solado é bidensidade.
- Linhas: botinas, coturnos, tênis, sapatos, Urban, Branca, Agro, Metatarso, Bi Comfort, Comfort Mono.
- Setores: construção civil, industrial, hospitalar, agronegócio e alimentício.
- Contato: Rua Luiz Spinelli, 160 – Mococa/SP · (19) 3665-7743 · WhatsApp (19) 3666-7670 *(telefones e endereço não entraram no vídeo)*.

Fontes: [site oficial](https://www.protefortcalcados.com.br/) · [setor agronegócio](https://www.protefortcalcados.com.br/setores/agronegocio) · [contato](https://www.protefortcalcados.com.br/contato/) · [Instagram](https://www.instagram.com/protefortcalcados/) · [LinkedIn](https://br.linkedin.com/company/protefort-cal%C3%A7ados-profissionais-ltda) · [Facebook](https://www.facebook.com/protefortcalcados/) · [CNPJ 12.133.295/0001-53](https://cnpj.biz/12133295000153)

**Para conferir com o cliente:** os "25 anos" (o CNPJ é de 2010; o perfil no LinkedIn diz fundação em 2003; o Instagram, 2001) e o @ do Instagram no CTA.

## Desenho de som

São 184 efeitos sincronizados com os movimentos, cada um com pequenas variações de tom e posição no estéreo. Todos foram calibrados para um volume equilibrado, e a trilha abaixa sozinha nos impactos.

| Efeito | Onde entra |
|---|---|
| **Whip** (whoosh grande) | Transições de cena (whip pans, wipe diagonal) |
| **Dash** (whoosh curto) | Cards, produtos, faixas e blocos deslizando |
| **Swish** | Textos que sobem por máscara |
| **Tap** | Cada palavra/letra que pula (efeito de digitação) |
| **Click** (mouse) | Cards virando ✓, troca de produto, blocos dos setores, CTA |
| **Pop / Boop** | Ícones e botões aparecendo (com tom subindo em sequência) |
| **Check** | Sino de confirmação nos 3 cards (dó–mi–sol) |
| **Tick** | Contador 0→25 (tom subindo) |
| **Marker** | Marca-texto passando em "BRASIL" e "DE VERDADE!" |
| **Sonar** | Pings do pin de Mococa |
| **Zip / Whomp** | Círculos laranja abrindo/fechando, junção do PROTEFORT |
| **Suck + Hit / Impact + Debris** | "PESADO?", botina, "TUDO", "PASSO", "FORTE", logo |
| **Stamp** | Selo C.A. |
| **Passos** | Pegadas atravessando a tela |
| **Riser + Shimmer + Ding** | Montagem do logo, contador e CTA |

## Observações

- **Trilha e efeitos:** o conector do ElevenLabs disponível não gera música, e os efeitos de lá custam 200 créditos por geração (a conta tem 61). Por isso a batida (124 BPM, com "drop" no logo) e todos os efeitos foram sintetizados no código. Dá para trocar a música por uma licenciada ou usar a versão "só efeitos" com um áudio do Instagram.
- **Produtos:** o site da Protefort estava bloqueado pela rede do ambiente, então os calçados são ilustrações vetoriais na paleta da marca, não fotos reais. Com fotos/PNGs dos produtos, dá para trocar no carrossel.
- **Áreas seguras do Reels:** textos importantes ficam entre y≈250 e y≈1510, fora da área da legenda e dos botões.
