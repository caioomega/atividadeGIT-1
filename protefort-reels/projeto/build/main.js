/* Protefort – Reels 1080x1920 motion graphics. Deterministic: window.seek(t) renders time t. */
const INK = '#363435', OR = '#F58634', GR = '#858688', BG = '#F6F4F1', TILE = '#444244';
const c = window.CUES;
const $shake = document.getElementById('shake');
const $fx = document.getElementById('fx');
const $bg = document.getElementById('bg');
const SFX = [];
const S = (t, type, g = 1) => SFX.push({ t: +Math.max(0, t).toFixed(3), type, g });

let seed = 20251;
const rnd = () => { seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
const R = (a, b) => a + (b - a) * rnd();

function mk(tag, cls, parent, css, html) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (css) e.style.cssText = css;
  if (html != null) e.innerHTML = html;
  parent.appendChild(e);
  return e;
}
const svgFill = (s) => s.replace('<svg', '<svg width="100%" height="100%"');

function scene(z = 0) {
  const s = mk('div', 'scene', $shake, z ? `z-index:${z}` : '');
  const zl = mk('div', 'layer', s);
  return { s, z: zl };
}

function T(parent, text, { x = 540, y, size = 100, w = 800, color = INK, ls = 0, shadow = false, split = 'none', mask = false } = {}) {
  const wrap = mk('div', 'txt' + (shadow ? ' shadow' : '') + (mask ? ' mask' : ''), parent,
    `left:${x}px;top:${y}px;font-size:${size}px;font-weight:${w};color:${color};letter-spacing:${ls}px;`);
  const inner = mask ? mk('span', 'in', wrap) : wrap;
  const parts = [];
  if (split === 'chars') for (const ch of text) parts.push(mk('span', 'ch', inner, null, ch));
  else if (split === 'words') text.split(' ').forEach((wd, i, a) => { parts.push(mk('span', 'wd', inner, null, wd)); if (i < a.length - 1) inner.appendChild(document.createTextNode(' ')); });
  else inner.textContent = text;
  gsap.set(wrap, { xPercent: -50, yPercent: -50 });
  return { wrap, inner, parts };
}

function logoSVG(layer, fill) {
  const L = window.LOGO;
  return `<svg viewBox="0 0 ${L.W} ${L.W}" width="100%" height="100%"><path fill="${fill}" fill-rule="evenodd" d="${L[layer]}"/></svg>`;
}

const tl = gsap.timeline({ paused: true });

/* ---------- animation helpers ---------- */
const show = (s, t) => tl.set(s, { visibility: 'visible' }, Math.max(0, t));
const hide = (s, t) => tl.set(s, { visibility: 'hidden' }, t);

function maskUp(o, t, { dur = 0.55, stagger = 0 } = {}) {
  const tg = stagger && o.parts.length ? o.parts : o.inner;
  tl.fromTo(tg, { yPercent: 125 }, { yPercent: 0, duration: dur, ease: 'power4.out', stagger }, t);
}
function popParts(o, t, { stagger = 0.04, y = 70, dur = 0.5, rot = 0, ease = 'back.out(2.2)' } = {}) {
  tl.fromTo(o.parts, { y, opacity: 0, scale: 0.6, rotation: rot }, { y: 0, opacity: 1, scale: 1, rotation: 0, duration: dur, ease, stagger }, t);
}
function popIn(el, t, { dur = 0.5, from = 0, ease = 'back.out(2)', rot = 0 } = {}) {
  tl.fromTo(el, { scale: from, opacity: 0, rotation: rot }, { scale: 1, opacity: 1, rotation: 0, duration: dur, ease }, t);
}
function slam(el, t, { from = 3, dur = 0.22, blur = 16 } = {}) {
  // lands exactly at t
  tl.fromTo(el, { scale: from, opacity: 0, filter: `blur(${blur}px)` }, { scale: 1, opacity: 1, filter: 'blur(0px)', duration: dur, ease: 'power4.in' }, t - dur);
  tl.to(el, { keyframes: [{ scale: 0.92, duration: 0.06 }, { scale: 1.04, duration: 0.1 }, { scale: 1, duration: 0.18 }] }, t);
}
function shake(t, amp = 26, dur = 0.42) {
  const n = 9;
  for (let i = 0; i < n; i++) {
    const k = 1 - i / n;
    tl.to($shake, { x: R(-1, 1) * amp * k, y: R(-1, 1) * amp * k, rotation: R(-1, 1) * amp * 0.03 * k, duration: dur / n, ease: 'none' }, t + (i * dur) / n);
  }
  tl.to($shake, { x: 0, y: 0, rotation: 0, duration: 0.05 }, t + dur);
}
function ring(parent, t, x, y, { size = 180, color = OR, border = 10, scale = 4.5, dur = 0.75, sy = 1 } = {}) {
  const r = mk('div', 'ring', parent, `left:${x - size / 2}px;top:${y - size / 2}px;width:${size}px;height:${size}px;border-color:${color};border-width:${border}px;opacity:0`);
  tl.fromTo(r, { scaleX: 0.2, scaleY: 0.2 * sy, opacity: 1 }, { scaleX: scale, scaleY: scale * sy, opacity: 0, duration: dur, ease: 'power2.out', immediateRender: false }, t);
  return r;
}
function burst(parent, t, x, y, { n = 16, colors = [OR, INK, GR], dist = [120, 340], size = [10, 26], dur = 0.85, a0 = 0, a1 = 360, grav = 0 } = {}) {
  for (let i = 0; i < n; i++) {
    const s = R(size[0], size[1]);
    const sq = rnd() < 0.35;
    const p = mk('div', 'abs', parent, `left:${x - s / 2}px;top:${y - s / 2}px;width:${s}px;height:${s}px;border-radius:${sq ? 4 : s}px;background:${colors[i % colors.length]};opacity:0`);
    const a = ((a0 + (a1 - a0) * rnd()) * Math.PI) / 180, d = R(dist[0], dist[1]);
    tl.fromTo(p, { x: 0, y: 0, scale: 1, opacity: 1, rotation: 0 }, { x: Math.cos(a) * d, y: Math.sin(a) * d + grav, scale: 0, opacity: 1, rotation: R(-200, 200), duration: dur * R(0.7, 1.1), ease: 'power3.out', immediateRender: false }, t);
  }
}
function whip(t, outS, inS, { axis = 'x', sign = 1 } = {}) {
  const D = axis === 'x' ? 1080 : 1920;
  const f = axis === 'x' ? '#mbxb' : '#mbyb', fid = axis === 'x' ? 'url(#mbx)' : 'url(#mby)';
  const big = axis === 'x' ? '70 0' : '0 70';
  tl.set([outS, inS], { filter: fid }, t);
  tl.fromTo(f, { attr: { stdDeviation: '0 0' } }, { attr: { stdDeviation: big }, duration: 0.17, ease: 'power2.in', immediateRender: false }, t);
  tl.to(f, { attr: { stdDeviation: '0 0' }, duration: 0.28, ease: 'power2.out' }, t + 0.17);
  tl.to(outS, { [axis]: -D * sign, duration: 0.22, ease: 'power3.in' }, t);
  show(inS, t + 0.1);
  tl.fromTo(inS, { [axis]: D * sign }, { [axis]: 0, duration: 0.36, ease: 'power3.out' }, t + 0.1);
  hide(outS, t + 0.24);
  tl.set([outS, inS], { filter: 'none' }, t + 0.5);
  S(t, 'whoosh');
}
function sceneZoom(z, t0, t1, to = 1.04) { tl.fromTo(z, { scale: 1 }, { scale: to, duration: Math.max(0.1, t1 - t0), ease: 'none' }, t0); }

/* ---------- build ---------- */
function build() {
  const END = c.end;

  /* background life */
  const dots = $bg.querySelector('.dots');
  tl.fromTo(dots, { x: 0, y: 0 }, { x: -54, y: -108, duration: END, ease: 'none' }, 0);
  [[-200, 200, 900], [500, 1100, 1000], [-100, 1500, 700]].forEach(([x, y, s], i) => {
    const b = mk('div', 'blob', $bg, `left:${x}px;top:${y}px;width:${s}px;height:${s}px`);
    tl.to(b, { x: i % 2 ? -220 : 260, y: i % 2 ? 180 : -200, duration: 5 + i, repeat: Math.ceil(END / (5 + i)), yoyo: true, ease: 'sine.inOut' }, 0);
  });

  /* ===== S1 — hook ===== */
  const A = scene();
  const hz1 = mk('div', 'hazard', A.z, 'top:250px;transform:rotate(-4deg)');
  const hz2 = mk('div', 'hazard', A.z, 'top:1630px;transform:rotate(-4deg)');
  const t1a = T(A.z, 'SEU', { y: 690, size: 120, w: 800, color: GR, mask: true, ls: 4 });
  const t1b = T(A.z, 'TRABALHO', { y: 840, size: 158, w: 900, mask: true, split: 'chars', ls: -5 });
  const t1c = T(A.z, 'É', { y: 1000, size: 110, w: 800, color: GR });
  const t1d = T(A.z, 'PESADO?', { y: 1185, size: 192, w: 900, color: OR, shadow: true, ls: -7 });
  const wipe0 = mk('div', 'abs', $fx, `left:0;top:0;width:1080px;height:1920px;background:${OR}`);
  const wipeLogo = mk('div', 'abs', wipe0, 'left:290px;top:710px;width:500px;height:500px', logoSVG('orange', '#fff') .replace('<svg', '<svg style="position:absolute;inset:0"') + logoSVG('gray', 'rgba(255,255,255,.5)').replace('<svg', '<svg style="position:absolute;inset:0"') + logoSVG('dark', '#fff').replace('<svg', '<svg style="position:absolute;inset:0"'));
  show(A.s, 0);
  sceneZoom(A.z, 0, c.entao - 0.2, 1.05);
  tl.fromTo(wipeLogo, { scale: 1 }, { scale: 0.6, opacity: 0, duration: 0.25, ease: 'power2.in' }, 0);
  tl.fromTo(wipe0, { yPercent: 0 }, { yPercent: -100, duration: 0.42, ease: 'power3.inOut' }, 0.04);
  S(0.02, 'whoosh', 0.9);
  tl.fromTo([hz1, hz2], { xPercent: (i) => (i ? 30 : -30), opacity: 0 }, { xPercent: 0, opacity: 1, duration: 0.5, ease: 'power3.out' }, 0.2);
  tl.fromTo([hz1, hz2], { backgroundPosition: '0px 0px' }, { backgroundPosition: (i) => (i ? '905px 0px' : '-905px 0px'), duration: 6, ease: 'none' }, 0);
  maskUp(t1a, Math.max(0.12, c.seu - 0.12));
  maskUp(t1b, Math.max(0.2, c.seu + 0.05), { stagger: 0.03 });
  popIn(t1c.wrap, c.pesado - 0.36, { dur: 0.3 });
  tl.fromTo(t1d.wrap, { y: -1500, scaleY: 1.25, scaleX: 0.9 }, { y: 0, scaleY: 1, scaleX: 1, duration: 0.28, ease: 'power4.in' }, c.pesado - 0.28);
  tl.to(t1d.wrap, { keyframes: [{ scaleY: 0.76, scaleX: 1.14, duration: 0.07 }, { scaleY: 1.07, scaleX: 0.96, duration: 0.12 }, { scaleY: 1, scaleX: 1, duration: 0.22 }], transformOrigin: '50% 100%' }, c.pesado);
  tl.to([t1a.wrap, t1b.wrap, t1c.wrap], { y: 22, duration: 0.07, yoyo: true, repeat: 1, ease: 'power2.out' }, c.pesado);
  shake(c.pesado, 34);
  burst(A.z, c.pesado, 540, 1290, { n: 22, colors: [GR, '#b9b7b5', OR], dist: [160, 520], a0: 160, a1: 380, size: [10, 24] });
  ring(A.z, c.pesado, 540, 1300, { size: 260, sy: 0.22, scale: 5, border: 8 });
  S(c.pesado - 0.28, 'whoosh_down', 0.8); S(c.pesado, 'impact', 1.1);
  tl.to(t1d.wrap, { scale: 1.04, duration: 0.35, yoyo: true, repeat: 1, ease: 'sine.inOut' }, c.pesado + 0.42);

  /* ===== S2 — calçado FORTE ===== */
  const B = scene();
  const t2a = T(B.z, 'ENTÃO O SEU', { y: 390, size: 66, w: 700, color: GR, split: 'words', ls: 3 });
  const t2b = T(B.z, 'CALÇADO', { y: 505, size: 156, w: 900, mask: true, split: 'chars', ls: -5 });
  const t2c = T(B.z, 'TEM QUE SER', { y: 640, size: 66, w: 700, color: GR, split: 'words', ls: 3 });
  const glow2 = mk('div', 'blob', B.z, 'left:40px;top:780px;width:1000px;height:1000px;opacity:0');
  const t2d = T(B.z, 'FORTE!', { y: 830, size: 236, w: 900, color: OR, shadow: true, ls: -9 });
  const boot2 = mk('div', 'abs', B.z, 'left:160px;top:990px;width:760px;height:579px;transform-origin:50% 92%', svgFill(ICONS.botina));
  const tB = c.entao - 0.2;
  whip(tB, A.s, B.s);
  sceneZoom(B.z, tB, c.lama - 0.18, 1.04);
  popParts(t2a, c.entao, { stagger: 0.1, y: 40 });
  maskUp(t2b, c.calcado - 0.05, { stagger: 0.03 });
  popParts(t2c, Math.min(c.calcado + 0.42, c.forte - 0.5), { stagger: 0.08, y: 40 });
  tl.fromTo(boot2, { y: -1750, rotation: -16 }, { y: 0, rotation: 0, duration: 0.32, ease: 'power4.in' }, c.forte - 0.32);
  tl.to(boot2, { keyframes: [{ scaleY: 0.88, scaleX: 1.06, duration: 0.07 }, { scaleY: 1.04, scaleX: 0.98, duration: 0.12 }, { scaleY: 1, scaleX: 1, duration: 0.2 }] }, c.forte);
  slam(t2d.wrap, c.forte + 0.02, { from: 3.2 });
  shake(c.forte, 42, 0.5);
  ring(B.z, c.forte, 540, 1520, { size: 300, sy: 0.24, scale: 4.2, border: 9 });
  ring(B.z, c.forte + 0.1, 540, 1520, { size: 300, sy: 0.24, scale: 3, border: 6, color: GR });
  burst(B.z, c.forte, 540, 1515, { n: 26, colors: [GR, '#b9b7b5', OR, INK], dist: [200, 560], a0: 170, a1: 370 });
  tl.fromTo(glow2, { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1.25, duration: 0.45, ease: 'power2.out' }, c.forte);
  tl.to(glow2, { opacity: 0.35, duration: 0.6 }, c.forte + 0.45);
  S(c.forte - 0.32, 'whoosh_down', 0.9); S(c.forte, 'impact', 1.25);
  tl.to(boot2, { y: -14, duration: 0.5, yoyo: true, repeat: 1, ease: 'sine.inOut' }, c.forte + 0.45);

  /* ===== S3 — lama / impacto / horas ===== */
  const Cc = scene();
  const chipDef = [['lama', 'LAMA', c.lama], ['impacto', 'IMPACTO', c.impacto], ['relogio', 'HORAS EM PÉ', c.horas]];
  const chips = chipDef.map(([ic, lb, t], i) => {
    const ch = mk('div', 'chip', Cc.z, `left:110px;top:${620 + i * 270 - 100}px;width:860px`);
    const icw = mk('div', 'ic', ch);
    const i1 = mk('div', 'abs', icw, 'left:32px;top:32px;width:88px;height:88px;color:#fff', svgFill(ICONS[ic]));
    const i2 = mk('div', 'abs', icw, 'left:28px;top:28px;width:96px;height:96px;color:#fff;opacity:0', svgFill(ICONS.check));
    const l = mk('div', 'lb', ch, 'font-size:80px', lb);
    return { ch, icw, i1, i2, l, t };
  });
  const tC = c.lama - 0.18;
  tl.fromTo(B.s, { scale: 1, opacity: 1, filter: 'blur(0px)' }, { scale: 1.7, opacity: 0, filter: 'blur(14px)', duration: 0.26, ease: 'power3.in', immediateRender: false }, tC);
  hide(B.s, tC + 0.27);
  show(Cc.s, tC + 0.1);
  sceneZoom(Cc.z, tC, c.protefort1 + 0.1, 1.035);
  S(tC, 'whoosh', 0.7);
  chips.forEach(({ ch, icw, t }, i) => {
    tl.fromTo(ch, { scale: 0.2, opacity: 0, rotation: i % 2 ? 8 : -8, y: 90 }, { scale: 1, opacity: 1, rotation: 0, y: 0, duration: 0.55, ease: 'back.out(2)' }, t - 0.1);
    tl.fromTo(icw, { rotation: -140, scale: 0 }, { rotation: 0, scale: 1, duration: 0.55, ease: 'back.out(2.4)' }, t - 0.02);
    S(t - 0.08, 'pop');
  });
  const tChk = c.protefort1 - 0.22;
  chips.forEach(({ ch, icw, i1, i2, l }, i) => {
    const t = tChk + i * 0.07;
    tl.to(ch, { backgroundColor: OR, duration: 0.14 }, t);
    tl.to(l, { color: '#fff', duration: 0.14 }, t);
    tl.to(icw, { backgroundColor: '#fff', duration: 0.14 }, t);
    tl.to(i1, { scale: 0, opacity: 0, duration: 0.14 }, t);
    tl.fromTo(i2, { scale: 0, opacity: 0, color: OR }, { scale: 1, opacity: 1, duration: 0.35, ease: 'back.out(3)' }, t + 0.05);
    tl.to(ch, { keyframes: [{ scale: 1.07, duration: 0.08 }, { scale: 1, duration: 0.2 }] }, t);
    S(t, 'click', 0.9);
  });

  /* ===== S4 — Protefort aguenta tudo (orange) ===== */
  const D = scene();
  mk('div', 'abs', D.s, `left:0;top:0;width:1080px;height:1920px;background:${OR}`);
  D.s.insertBefore(D.s.lastChild, D.z);
  const decoRings = [0, 1, 2].map(() => mk('div', 'ring', D.z, 'left:340px;top:690px;width:400px;height:400px;border-color:rgba(255,255,255,.35);border-width:4px;opacity:0'));
  const mono = mk('div', 'abs', D.z, 'left:410px;top:300px;width:260px;height:260px');
  mk('div', 'abs', mono, 'inset:0;opacity:.45', logoSVG('gray', '#fff'));
  mk('div', 'abs', mono, 'inset:0', logoSVG('dark', '#fff'));
  mk('div', 'abs', mono, 'inset:0', logoSVG('orange', '#fff'));
  const t4a = T(D.z, 'A PROTEFORT', { y: 680, size: 84, w: 800, color: '#fff', mask: true, ls: 6 });
  const t4b = T(D.z, 'AGUENTA', { y: 860, size: 176, w: 900, color: '#fff', ls: -5 });
  const t4c = T(D.z, 'TUDO', { y: 1080, size: 300, w: 900, color: INK, ls: -10 });
  t4c.wrap.style.textShadow = '0.05em 0.05em 0 rgba(255,255,255,.45)';
  const t4d = T(D.z, 'ISSO COM VOCÊ', { y: 1290, size: 80, w: 700, color: '#fff', split: 'words', ls: 2 });
  const tD = c.protefort1 + 0.05;
  show(D.s, tD);
  tl.fromTo(D.s, { clipPath: 'circle(0px at 540px 890px)' }, { clipPath: 'circle(1300px at 540px 890px)', duration: 0.5, ease: 'power3.inOut' }, tD);
  hide(Cc.s, tD + 0.5);
  S(tD, 'swoosh');
  sceneZoom(D.z, tD, c.direto - 0.2, 1.05);
  popIn(mono, tD + 0.22, { dur: 0.55, rot: -90, ease: 'back.out(1.8)' });
  decoRings.forEach((r, i) => tl.fromTo(r, { scale: 0.3, opacity: 0.9 }, { scale: 3.4, opacity: 0, duration: 1.4, ease: 'power1.out', repeat: 1 }, tD + 0.3 + i * 0.45));
  maskUp(t4a, Math.max(tD + 0.18, c.protefort1 + 0.15));
  tl.fromTo(t4b.wrap, { x: -900, filter: 'blur(22px)', opacity: 0 }, { x: 0, filter: 'blur(0px)', opacity: 1, duration: 0.38, ease: 'power4.out' }, c.aguenta - 0.06);
  S(c.aguenta - 0.08, 'whoosh', 0.8);
  slam(t4c.wrap, c.tudo, { from: 2.8 });
  shake(c.tudo, 24, 0.35);
  S(c.tudo, 'impact', 0.85);
  popParts(t4d, c.comvoce, { stagger: 0.09, y: 50 });
  tl.to(t4c.wrap, { scale: 1.05, duration: 0.3, yoyo: true, repeat: 1, ease: 'sine.inOut' }, c.tudo + 0.4);

  /* ===== S5 — Mococa / 25 anos / Brasil ===== */
  const E = scene();
  const tE = c.direto - 0.22;
  tl.to(D.z, { scale: 0.25, opacity: 0, duration: 0.3, ease: 'power3.in' }, tE);
  tl.to(D.s, { clipPath: 'circle(78px at 540px 640px)', duration: 0.42, ease: 'power3.inOut' }, tE);
  S(tE, 'swoosh', 0.8);
  const gA = mk('div', 'layer', E.z);
  const gRings = [0, 1, 2].map(() => mk('div', 'ring', gA, 'left:440px;top:737px;width:200px;height:100px;border-width:6px;opacity:0'));
  const pin = mk('div', 'abs', gA, 'left:450px;top:553px;width:180px;height:240px;transform-origin:50% 100%', svgFill(ICONS.pin));
  const t5a = T(gA, 'DIRETO DE', { y: 960, size: 64, w: 700, color: GR, split: 'words', ls: 4 });
  const t5b = T(gA, 'MOCOCA', { y: 1110, size: 196, w: 900, split: 'chars', ls: -6, shadow: true });
  const t5c = T(gA, 'SÃO PAULO • BRASIL', { y: 1250, size: 50, w: 700, color: OR, mask: true, ls: 10 });
  show(E.s, tE + 0.36);
  hide(D.s, tE + 0.42);
  sceneZoom(E.z, tE + 0.36, c.botinas - 0.2, 1.035);
  tl.fromTo(pin, { scaleY: 0.55, scaleX: 1 }, { scaleY: 1, duration: 0.7, ease: 'elastic.out(1.1,0.45)' }, tE + 0.38);
  S(tE + 0.38, 'pop', 1);
  gRings.forEach((r, i) => tl.fromTo(r, { scale: 0.2, opacity: 1 }, { scale: 4, opacity: 0, duration: 1.1, ease: 'power2.out', repeat: 1 }, tE + 0.45 + i * 0.32));
  popParts(t5a, Math.max(tE + 0.4, c.direto), { stagger: 0.1, y: 40 });
  popParts(t5b, c.mococa - 0.05, { stagger: 0.045, y: 130, rot: 12, dur: 0.6 });
  maskUp(t5c, c.mococa + 0.35);
  S(c.mococa - 0.05, 'swoosh', 0.7);
  // 25 anos
  const tAn = c.anos - 0.22;
  tl.to(gA, { y: -260, opacity: 0, duration: 0.3, ease: 'power3.in' }, tAn);
  const gB = mk('div', 'layer', E.z);
  const RR = 300, CIRC = 2 * Math.PI * RR;
  const arcBox = mk('div', 'abs', gB, `left:${540 - 340}px;top:${880 - 340}px;width:680px;height:680px;transform:rotate(-90deg)`,
    `<svg viewBox="0 0 680 680" width="680" height="680"><circle cx="340" cy="340" r="${RR}" fill="none" stroke="#E4E1DD" stroke-width="26"/><circle id="arc" cx="340" cy="340" r="${RR}" fill="none" stroke="${OR}" stroke-width="26" stroke-linecap="round" stroke-dasharray="${CIRC}" stroke-dashoffset="${CIRC}"/></svg>`);
  const num = T(gB, '0', { y: 870, size: 330, w: 900, ls: -14 });
  const anos = T(gB, 'ANOS', { y: 1290, size: 112, w: 900, color: OR, ls: 20, shadow: true });
  tl.fromTo(gB, { scale: 0.4, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.42, ease: 'back.out(1.7)' }, tAn + 0.12);
  const cnt = { v: 0 };
  tl.fromTo(cnt, { v: 0 }, { v: 25, duration: 0.8, ease: 'power2.out', onUpdate: () => { num.wrap.textContent = Math.round(cnt.v); } }, tAn + 0.15);
  tl.fromTo('#arc', { attr: { 'stroke-dashoffset': CIRC } }, { attr: { 'stroke-dashoffset': 0 }, duration: 0.8, ease: 'power2.out' }, tAn + 0.15);
  for (let i = 0; i < 9; i++) S(tAn + 0.15 + 0.8 * (1 - Math.sqrt(1 - i / 9)), 'tick', 0.55);
  tl.to(num.wrap, { keyframes: [{ scale: 1.14, duration: 0.08 }, { scale: 1, duration: 0.25, ease: 'back.out(3)' }] }, tAn + 0.95);
  S(tAn + 0.95, 'ding', 0.8);
  slam(anos.wrap, Math.min(tAn + 0.75, c.protegendo - 0.4), { from: 2.4, blur: 10 });
  // protegendo quem faz o Brasil acontecer
  const tPr = c.protegendo - 0.18;
  tl.to(gB, { scale: 0.42, y: -380, duration: 0.45, ease: 'power3.inOut' }, tPr);
  const t5d = T(E.z, 'PROTEGENDO QUEM', { y: 880, size: 82, w: 800, mask: true, ls: -1 });
  const l2 = mk('div', 'txt mask', E.z, `left:540px;top:1010px;font-size:108px;font-weight:900;color:${INK};letter-spacing:-3px`);
  gsap.set(l2, { xPercent: -50, yPercent: -50 });
  const l2in = mk('span', 'in', l2);
  mk('span', null, l2in, null, 'FAZ O ');
  const hlw = mk('span', null, l2in, 'position:relative;display:inline-block;padding:0 18px');
  const hlbar = mk('div', 'abs', hlw, `left:0;top:8%;width:100%;height:90%;background:${OR};border-radius:16px;transform-origin:0 50%`);
  const hlt = mk('span', null, hlw, 'position:relative', 'BRASIL');
  const t5f = T(E.z, 'ACONTECER!', { y: 1160, size: 150, w: 900, color: OR, mask: true, ls: -5, shadow: true });
  maskUp(t5d, c.protegendo);
  tl.fromTo(l2in, { yPercent: 125 }, { yPercent: 0, duration: 0.55, ease: 'power4.out' }, Math.min(c.protegendo + 0.3, c.brasil - 0.3));
  tl.fromTo(hlbar, { scaleX: 0 }, { scaleX: 1, duration: 0.3, ease: 'power3.out' }, c.brasil - 0.06);
  tl.fromTo(hlt, { color: INK }, { color: '#fff', duration: 0.12 }, c.brasil);
  maskUp(t5f, c.brasil + 0.28);
  S(c.brasil - 0.06, 'swoosh', 0.7);

  /* ===== S6 — linha completa ===== */
  const F = scene();
  const tF = c.botinas - 0.22;
  whip(tF, E.s, F.s, { axis: 'y', sign: 1 });
  sceneZoom(F.z, tF, c.todos - 0.15, 1.03);
  const pill6 = mk('div', 'pill', F.z, `left:540px;top:370px;height:84px;padding:0 44px;background:${INK};color:#fff;font-weight:700;font-size:40px;letter-spacing:8px`, 'LINHA COMPLETA');
  gsap.set(pill6, { xPercent: -50, yPercent: -50 });
  const card = mk('div', 'card', F.z, 'left:110px;top:540px;width:860px;height:780px');
  mk('div', 'abs', card, `left:150px;top:110px;width:560px;height:560px;border-radius:50%;background:${OR}`);
  const prods = ['botina', 'coturno', 'tenis', 'sapato'].map((k) => mk('div', 'abs', card, 'left:60px;top:110px;width:740px;height:564px;opacity:0', svgFill(ICONS[k])));
  const nums = ['01', '02', '03', '04'].map((n) => mk('div', 'abs', card, `left:56px;top:44px;font-weight:800;font-size:44px;color:${INK};opacity:0`, `${n}<span style="color:${GR};font-weight:600">/04</span>`));
  const lab = mk('div', 'txt mask', F.z, 'left:540px;top:1450px;width:1000px;height:190px');
  gsap.set(lab, { xPercent: -50, yPercent: -50 });
  const labs = ['BOTINAS', 'COTURNOS', 'TÊNIS', 'SAPATOS'].map((w) => mk('div', 'abs', lab, `left:0;top:20px;width:1000px;text-align:center;font-weight:900;font-size:140px;letter-spacing:-4px;color:${INK}`, w));
  const segLab = mk('div', 'abs', lab, `left:0;top:30px;width:1000px;text-align:center`, `<span style="display:inline-block;background:${OR};color:#fff;font-weight:900;font-size:104px;letter-spacing:-2px;padding:6px 38px 2px;border-radius:24px">DE SEGURANÇA</span>`);
  tl.fromTo(pill6, { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 0.45, ease: 'back.out(2)' }, tF + 0.25);
  popIn(card, tF + 0.2, { from: 0.6, dur: 0.5, ease: 'back.out(1.6)' });
  const pt = [c.botinas, c.coturnos, c.tenis, c.sapatos];
  pt.forEach((t, i) => {
    if (i > 0) {
      tl.to(prods[i - 1], { x: -900, rotation: -14, opacity: 0, duration: 0.28, ease: 'power3.in' }, t - 0.1);
      tl.to(labs[i - 1], { yPercent: -130, duration: 0.3, ease: 'power3.in' }, t - 0.1);
      tl.set(nums[i - 1], { opacity: 0 }, t - 0.02);
    }
    tl.fromTo(prods[i], { x: 900, rotation: 14, opacity: 0 }, { x: 0, rotation: 0, opacity: 1, duration: 0.5, ease: 'back.out(1.5)' }, t - 0.06);
    tl.fromTo(labs[i], { yPercent: 170 }, { yPercent: 0, duration: 0.45, ease: 'power4.out' }, t - 0.04);
    tl.set(nums[i], { opacity: 1 }, t - 0.02);
    S(t - 0.08, 'whoosh', 0.55);
  });
  const tSeg = c.seguranca - 0.12;
  tl.to(card, { scale: 0.4, opacity: 0, duration: 0.25, ease: 'power3.in' }, tSeg);
  tl.to(labs[3], { yPercent: -130, duration: 0.28, ease: 'power3.in' }, tSeg);
  tl.fromTo(segLab, { yPercent: 220 }, { yPercent: 0, duration: 0.45, ease: 'power4.out' }, tSeg + 0.1);
  const grid = [[305, 800], [775, 800], [305, 1170], [775, 1170]].map(([x, y], i) => {
    const g = mk('div', 'card', F.z, `left:${x - 215}px;top:${y - 170}px;width:430px;height:340px;border-radius:44px;opacity:0`);
    mk('div', 'abs', g, `left:95px;top:50px;width:240px;height:240px;border-radius:50%;background:${OR}`);
    mk('div', 'abs', g, 'left:25px;top:25px;width:380px;height:290px', svgFill(ICONS[['botina', 'coturno', 'tenis', 'sapato'][i]]));
    tl.fromTo(g, { scale: 0, opacity: 0, rotation: i % 2 ? 10 : -10 }, { scale: 1, opacity: 1, rotation: 0, duration: 0.45, ease: 'back.out(1.8)' }, tSeg + 0.12 + i * 0.07);
    S(tSeg + 0.12 + i * 0.07, 'pop', 0.7);
    return g;
  });

  /* ===== S7 — C.A. / bidensidade / passo ===== */
  const G = scene();
  const tG = c.todos - 0.18;
  whip(tG, F.s, G.s);
  sceneZoom(G.z, tG, c.obra - 0.25, 1.03);
  const t7a = T(G.z, 'TODOS COM', { y: 420, size: 66, w: 700, color: GR, split: 'words', ls: 4 });
  const shield = mk('div', 'abs', G.z, 'left:350px;top:560px;width:380px;height:437px');
  shield.innerHTML = svgFill(ICONS.escudo);
  mk('div', 'abs', shield, 'left:0;top:150px;width:380px;text-align:center;font-weight:900;font-size:124px;color:#fff;letter-spacing:-2px;line-height:1', 'C.A.');
  const t7b = T(G.z, 'CERTIFICADO DE APROVAÇÃO', { y: 1090, size: 46, w: 700, color: INK, mask: true, ls: 3 });
  popParts(t7a, c.todos - 0.05, { stagger: 0.1, y: 40 });
  tl.fromTo(shield, { scale: 2.8, rotation: -18, opacity: 0 }, { scale: 1, rotation: 0, opacity: 1, duration: 0.24, ease: 'power4.in' }, c.ca - 0.24);
  tl.to(shield, { keyframes: [{ scale: 0.94, duration: 0.06 }, { scale: 1.03, duration: 0.1 }, { scale: 1, duration: 0.18 }] }, c.ca);
  shake(c.ca, 18, 0.3);
  ring(G.z, c.ca, 540, 780, { size: 380, scale: 2.4, border: 8 });
  burst(G.z, c.ca, 540, 780, { n: 14, colors: [OR, GR], dist: [250, 420], size: [10, 20] });
  S(c.ca, 'stamp', 1);
  maskUp(t7b, c.ca + 0.18);
  // bidensidade
  const tBi = c.bidensidade - 0.28;
  tl.to(shield, { scale: 0.4, y: -420, duration: 0.42, ease: 'power3.inOut' }, tBi);
  tl.to([t7a.wrap, t7b.wrap], { opacity: 0, y: -40, duration: 0.25 }, tBi);
  const gBi = mk('div', 'layer', G.z);
  const t7c = T(gBi, 'SOLADO', { y: 560, size: 60, w: 700, color: GR, mask: true, ls: 8 });
  const t7d = T(gBi, 'BIDENSIDADE', { y: 668, size: 112, w: 900, color: OR, mask: true, ls: -4, shadow: true });
  const top = mk('div', 'abs', gBi, 'left:150px;top:960px;width:780px;height:84px',
    `<svg viewBox="0 0 780 84" width="780" height="84"><path d="M40 4 H700 Q776 4 776 44 Q776 80 730 80 H40 Q4 80 4 42 Q4 4 40 4Z" fill="#E7E3DE" stroke="#CFCAC4" stroke-width="4"/><text x="390" y="54" text-anchor="middle" font-family="Poppins" font-weight="700" font-size="30" letter-spacing="8" fill="${GR}">AMORTECIMENTO</text></svg>`);
  const bot = mk('div', 'abs', gBi, 'left:150px;top:1044px;width:780px;height:96px',
    `<svg viewBox="0 0 780 96" width="780" height="96"><path d="M30 4 H736 Q776 4 776 40 Q776 78 730 78 H50 Q4 78 4 40 Q4 4 30 4Z" fill="${INK}"/>${[...Array(16)].map((_, i) => `<rect x="${44 + i * 44}" y="74" width="26" height="18" rx="4" fill="${INK}"/>`).join('')}<text x="390" y="52" text-anchor="middle" font-family="Poppins" font-weight="700" font-size="30" letter-spacing="8" fill="#fff">RESISTÊNCIA</text></svg>`);
  const pC = mk('div', 'pill', gBi, `left:540px;top:820px;height:92px;padding:0 44px;background:${OR};color:#fff;font-weight:800;font-size:52px`, '+ CONFORTO');
  const pF = mk('div', 'pill', gBi, `left:540px;top:1290px;height:92px;padding:0 44px;background:${INK};color:#fff;font-weight:800;font-size:52px`, '+ FIRMEZA');
  gsap.set([pC, pF], { xPercent: -50, yPercent: -50 });
  maskUp(t7c, c.bidensidade - 0.12);
  maskUp(t7d, c.bidensidade + 0.02);
  tl.fromTo(top, { x: -1100 }, { x: 0, duration: 0.45, ease: 'power4.out' }, c.bidensidade + 0.12);
  tl.fromTo(bot, { x: 1100 }, { x: 0, duration: 0.45, ease: 'power4.out' }, c.bidensidade + 0.2);
  S(c.bidensidade + 0.1, 'whoosh', 0.6); S(c.bidensidade + 0.2, 'whoosh', 0.5);
  tl.to(top, { y: -50, duration: 0.35, ease: 'power3.inOut' }, c.conforto - 0.3);
  tl.to(bot, { y: 50, duration: 0.35, ease: 'power3.inOut' }, c.conforto - 0.3);
  popIn(pC, c.conforto - 0.05, { dur: 0.45, ease: 'back.out(2.4)' });
  popIn(pF, c.firmeza - 0.05, { dur: 0.45, ease: 'back.out(2.4)' });
  S(c.conforto - 0.05, 'pop'); S(c.firmeza - 0.05, 'pop');
  // primeiro ao último passo
  const tPa = c.primeiro - 0.22;
  tl.to(gBi, { y: -220, opacity: 0, duration: 0.3, ease: 'power3.in' }, tPa);
  tl.to(shield, { opacity: 0, scale: 0.2, duration: 0.25 }, tPa);
  const t7e = T(G.z, 'DO PRIMEIRO', { y: 720, size: 92, w: 800, mask: true, ls: -2 });
  const t7f = T(G.z, 'AO ÚLTIMO', { y: 840, size: 92, w: 800, mask: true, ls: -2 });
  const t7g = T(G.z, 'PASSO', { y: 1030, size: 236, w: 900, color: OR, ls: -8, shadow: true });
  maskUp(t7e, c.primeiro);
  maskUp(t7f, Math.min(c.primeiro + 0.4, c.passo - 0.3));
  slam(t7g.wrap, c.passo, { from: 2.6 });
  S(c.passo, 'impact', 0.7);
  const nSteps = 6;
  for (let i = 0; i < nSteps; i++) {
    const x = 150 + i * 156, y = 1380 + (i % 2 ? 58 : -58);
    const fp = mk('div', 'abs', G.z, `left:${x - 45}px;top:${y - 105}px;width:90px;height:210px;color:${i === nSteps - 1 ? OR : INK};opacity:0`, svgFill(ICONS.pegada));
    const t = c.primeiro + i * Math.min(0.16, (c.obra - c.primeiro - 0.6) / nSteps);
    tl.fromTo(fp, { rotation: 90, scale: 0, opacity: 0 }, { rotation: 90, scale: 1, opacity: i === nSteps - 1 ? 1 : 0.85, duration: 0.25, ease: 'back.out(2.5)' }, t);
    if (i < nSteps - 1) tl.to(fp, { opacity: 0.18, duration: 0.6 }, t + 0.5);
    S(t, 'step', 0.6);
  }

  /* ===== S8 — setores (dark) ===== */
  const H = scene(5);
  const bgTop = mk('div', 'abs', H.s, `left:0;top:0;width:1080px;height:961px;background:${INK}`);
  const bgBot = mk('div', 'abs', H.s, `left:0;top:960px;width:1080px;height:960px;background:${INK}`);
  H.s.insertBefore(bgBot, H.z); H.s.insertBefore(bgTop, bgBot);
  const hdots = mk('div', 'abs', H.z, 'inset:-100px;background-image:radial-gradient(rgba(255,255,255,.07) 2.4px, transparent 2.6px);background-size:54px 54px');
  const t8a = T(H.z, 'EM QUALQUER SETOR', { y: 430, size: 46, w: 700, color: OR, mask: true, ls: 10 });
  const tiles = [['capacete', 'OBRA', c.obra], ['fabrica', 'INDÚSTRIA', c.industria], ['hospital', 'HOSPITAL', c.hospital], ['campo', 'CAMPO', c.campo]].map(([ic, lb, t], i) => {
    const [cx, cy] = [[305, 800], [775, 800], [305, 1270], [775, 1270]][i];
    const tile = mk('div', 'tile', H.z, `left:${cx - 205}px;top:${cy - 205}px`);
    const iw = mk('div', null, tile, `width:180px;height:180px;color:${OR}`, svgFill(ICONS[ic]));
    mk('div', 'lb', tile, null, lb);
    return { tile, iw, t };
  });
  const tH = c.obra - 0.3;
  const diag = mk('div', 'abs', $fx, `left:-700px;top:-400px;width:1500px;height:2720px;background:${OR};transform:rotate(14deg);opacity:0`);
  tl.fromTo(diag, { x: -1700, opacity: 1 }, { x: 2300, duration: 0.6, ease: 'power3.inOut' }, tH - 0.1);
  show(H.s, tH + 0.18);
  hide(G.s, tH + 0.2);
  S(tH - 0.1, 'whoosh', 0.9);
  sceneZoom(H.z, tH + 0.18, c.protecao - 0.2, 1.035);
  tl.fromTo(hdots, { y: 0 }, { y: -108, duration: 4, ease: 'none' }, tH);
  maskUp(t8a, tH + 0.3);
  tiles.forEach(({ tile, iw, t }, i) => {
    tl.fromTo(tile, { scale: 0, rotation: i % 2 ? 14 : -14 }, { scale: 1, rotation: 0, duration: 0.5, ease: 'back.out(1.8)' }, t - 0.1);
    tl.to(tile, { backgroundColor: OR, borderColor: OR, duration: 0.12 }, t);
    tl.to(iw, { color: '#fff', duration: 0.12 }, t);
    tl.fromTo(iw, { y: 0 }, { keyframes: [{ y: -26, duration: 0.14, ease: 'power2.out' }, { y: 0, duration: 0.3, ease: 'bounce.out' }] }, t);
    if (i > 0) {
      tl.to(tiles[i - 1].tile, { backgroundColor: TILE, borderColor: '#504e4f', duration: 0.2 }, t);
      tl.to(tiles[i - 1].iw, { color: OR, duration: 0.2 }, t);
    }
    S(t - 0.08, 'pop', 0.9);
  });

  /* ===== S9 — PROTEÇÃO + FORTE = PROTEFORT → logo → CTA ===== */
  const I = scene();
  const tI = c.protecao - 0.22;
  tiles.forEach(({ tile }, i) => tl.to(tile, { x: 540 - (i % 2 ? 775 : 305), y: 1035 - (i < 2 ? 800 : 1270), scale: 0, duration: 0.3, ease: 'power3.in' }, tI + i * 0.03));
  tl.to(t8a.wrap, { opacity: 0, duration: 0.2 }, tI);
  show(I.s, tI + 0.25);
  tl.to(bgTop, { y: -980, duration: 0.42, ease: 'power3.inOut' }, tI + 0.25);
  tl.to(bgBot, { y: 980, duration: 0.42, ease: 'power3.inOut' }, tI + 0.25);
  hide(H.s, tI + 0.7);
  S(tI + 0.25, 'swoosh', 0.8);
  const gM = mk('div', 'layer', I.z, 'transform-origin:540px 935px');
  const wP = T(gM, 'PROTEÇÃO', { y: 860, size: 136, w: 900, split: 'chars', ls: -4 });
  const wF = T(gM, 'FORTE', { y: 1010, size: 136, w: 900, color: OR, split: 'chars', ls: -4 });
  // measure merge targets
  const ref = T(I.z, 'PROTEFORT', { y: 935, size: 136, w: 900, split: 'chars', ls: -4 });
  const tr = ref.parts.map((p) => p.getBoundingClientRect());
  const pr = wP.parts.map((p) => p.getBoundingClientRect());
  const fr = wF.parts.map((p) => p.getBoundingClientRect());
  ref.wrap.remove();
  const keep = [[wP.parts[0], pr[0], tr[0]], [wP.parts[1], pr[1], tr[1]], [wP.parts[2], pr[2], tr[2]], [wP.parts[3], pr[3], tr[3]], [wP.parts[4], pr[4], tr[4]],
    [wF.parts[0], fr[0], tr[5]], [wF.parts[1], fr[1], tr[6]], [wF.parts[2], fr[2], tr[7]], [wF.parts[3], fr[3], tr[8]]];
  const drop = [wP.parts[5], wP.parts[6], wP.parts[7], wF.parts[4]];
  popParts(wP, c.protecao - 0.04, { stagger: 0.035, y: 110, dur: 0.5 });
  S(c.protecao - 0.04, 'swoosh', 0.7);
  slam(wF.wrap, c.forte2, { from: 2.6 });
  shake(c.forte2, 26, 0.35);
  ring(I.z, c.forte2, 540, 1010, { size: 300, scale: 3.2, border: 8, sy: 0.5 });
  S(c.forte2, 'impact', 1);
  const tm = Math.min(c.forte2 + 0.42, c.protefort - 0.4);
  drop.forEach((p, i) => tl.to(p, { y: 520, rotation: R(-70, 70), opacity: 0, duration: 0.45, ease: 'power2.in' }, tm + i * 0.03));
  S(tm, 'whoosh_down', 0.6);
  keep.forEach(([p, a, b]) => tl.to(p, { x: b.left - a.left, y: b.top - a.top, duration: 0.42, ease: 'power3.inOut' }, tm + 0.1));
  S(tm + 0.3, 'click', 0.8);
  tl.to(gM, { keyframes: [{ scale: 1.13, duration: 0.09 }, { scale: 1, duration: 0.3, ease: 'back.out(3)' }] }, c.protefort);
  const flash = mk('div', 'abs', $fx, 'inset:0;background:#fff;opacity:0');
  tl.fromTo(flash, { opacity: 0.85 }, { opacity: 0, duration: 0.35, ease: 'power2.out', immediateRender: false }, c.protefort);
  S(c.protefort, 'ding', 1);
  // logo reveal
  const tL = c.protefort + 0.4;
  tl.to(gM, { y: 30, scale: 0.8, duration: 0.5, ease: 'power3.inOut' }, tL);
  const logo = mk('div', 'abs', I.z, 'left:280px;top:330px;width:520px;height:520px');
  const L = window.LOGO, LC = 2 * Math.PI * 640;
  const lRing = mk('div', 'abs', logo, 'inset:0',
    `<svg viewBox="0 0 ${L.W} ${L.W}" width="100%" height="100%"><defs><mask id="rm"><circle id="rmc" cx="1120" cy="1110" r="640" fill="none" stroke="#fff" stroke-width="1300" stroke-dasharray="${LC}" stroke-dashoffset="${LC}" transform="rotate(200 1120 1110)"/></mask></defs><path fill="${OR}" fill-rule="evenodd" d="${L.orange}" mask="url(#rm)"/></svg>`);
  const lSh = mk('div', 'abs', logo, 'inset:0;opacity:0', logoSVG('gray', GR));
  const lP = mk('div', 'abs', logo, 'inset:0;opacity:0;transform-origin:50% 80%', logoSVG('dark', INK));
  tl.fromTo(lP, { y: -1000, rotation: -12, opacity: 1 }, { y: 0, rotation: 0, opacity: 1, duration: 0.4, ease: 'power4.in' }, tL + 0.05);
  tl.to(lP, { keyframes: [{ scaleY: 0.86, scaleX: 1.06, duration: 0.07 }, { scaleY: 1.04, scaleX: 0.98, duration: 0.12 }, { scaleY: 1, scaleX: 1, duration: 0.2 }] }, tL + 0.45);
  shake(tL + 0.45, 20, 0.3);
  S(tL + 0.05, 'whoosh_down', 0.7); S(tL + 0.45, 'impact', 0.9);
  tl.fromTo(lSh, { x: -36, y: -36, opacity: 0 }, { x: 0, y: 0, opacity: 1, duration: 0.35, ease: 'power3.out' }, tL + 0.5);
  tl.fromTo('#rmc', { attr: { 'stroke-dashoffset': LC } }, { attr: { 'stroke-dashoffset': 0 }, duration: 0.6, ease: 'power2.inOut' }, tL + 0.5);
  tl.fromTo(lRing, { rotation: -30, scale: 0.9 }, { rotation: 0, scale: 1, duration: 0.8, ease: 'back.out(1.6)' }, tL + 0.5);
  S(tL + 0.5, 'swoosh', 0.8);
  burst(I.z, tL + 0.48, 540, 600, { n: 22, colors: [OR, GR, INK], dist: [260, 520], size: [10, 22] });
  ring(I.z, tL + 0.46, 540, 600, { size: 400, scale: 2.6, border: 6 });
  const t9a = T(I.z, 'CALÇADOS PROFISSIONAIS', { y: 1048, size: 40, w: 700, color: GR, mask: true, ls: 8 });
  maskUp(t9a, Math.max(c.calcados, tL + 0.55));
  tl.to(lRing, { rotation: 5, duration: 1.6, yoyo: true, repeat: 3, ease: 'sine.inOut' }, tL + 1.3);
  // tagline
  const gT = mk('div', 'layer', I.z);
  const t9b = T(gT, 'PRA QUEM TRABALHA', { y: 1210, size: 70, w: 800, split: 'words', ls: -1 });
  const vb = mk('div', 'txt', gT, `left:540px;top:1340px;font-size:104px;font-weight:900;color:#fff;letter-spacing:-3px;padding:14px 40px 6px;`);
  gsap.set(vb, { xPercent: -50, yPercent: -50 });
  const vbBar = mk('div', 'abs', vb, `inset:0;background:${OR};border-radius:26px;transform-origin:0 50%`);
  const vbT = mk('span', null, vb, 'position:relative;display:inline-block', 'DE VERDADE!');
  popParts(t9b, Math.min(c.calcados + 0.75, c.verdade - 0.45), { stagger: 0.09, y: 40 });
  tl.fromTo(vbBar, { scaleX: 0 }, { scaleX: 1, duration: 0.3, ease: 'power3.out' }, c.verdade - 0.12);
  tl.fromTo(vbT, { scale: 0.3, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.4, ease: 'back.out(2.5)' }, c.verdade - 0.02);
  shake(c.verdade, 12, 0.25);
  S(c.verdade - 0.12, 'swoosh', 0.7); S(c.verdade, 'impact', 0.6);
  // CTA
  tl.to(gT, { y: -60, opacity: 0, duration: 0.3, ease: 'power3.in' }, c.cta - 0.1);
  const ctas = [['globo', 'protefortcalcados.com.br'], ['insta', '@protefortcalcados'], ['local', 'Mococa • SP']].map(([ic, txt], i) => {
    const p = mk('div', 'pill', I.z, `left:540px;top:${1215 + i * 122}px;height:100px;padding:0 44px 0 14px;background:#fff;box-shadow:0 18px 44px rgba(54,52,53,.12);gap:24px`);
    gsap.set(p, { xPercent: -50, yPercent: -50 });
    const icw = mk('div', null, p, `width:74px;height:74px;border-radius:50%;background:${OR};display:flex;align-items:center;justify-content:center`);
    mk('div', null, icw, 'width:42px;height:42px;color:#fff', svgFill(ICONS[ic]));
    mk('div', null, p, `font-weight:${i ? 700 : 800};font-size:44px;color:${INK}`, txt);
    tl.fromTo(p, { y: 80, opacity: 0, scale: 0.8 }, { y: 0, opacity: 1, scale: 1, duration: 0.5, ease: 'back.out(1.8)' }, c.cta + 0.1 + i * 0.13);
    S(c.cta + 0.1 + i * 0.13, 'pop', 0.7);
    return p;
  });
  tl.to(ctas[0], { scale: 1.05, duration: 0.4, yoyo: true, repeat: 3, ease: 'sine.inOut' }, c.cta + 1.0);
  tl.set({}, {}, END);
}

window.DURATION = c.end;
window.seek = (t) => { tl.seek(t, false); };
(async () => {
  await Promise.all([400, 600, 700, 800, 900].map((w) => document.fonts.load(`${w} 100px Poppins`)));
  await document.fonts.ready;
  build();
  window.SFX_EVENTS = SFX.sort((a, b) => a.t - b.t);
  tl.seek(0);
  window.READY = true;
})();
