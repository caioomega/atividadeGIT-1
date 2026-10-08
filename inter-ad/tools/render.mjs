// Renderiza ad.html quadro a quadro com Chromium (Playwright) e envia para o ffmpeg.
// Uso:
//   node tools/render.mjs frames <outDir> t1 t2 ...          -> PNGs de instantes específicos
//   node tools/render.mjs video <out.mp4> [fps] [sub] [jobs] -> vídeo sem áudio
//        sub  = subquadros por quadro (motion blur, obturador de 180°)
//        jobs = processos em paralelo (cada um renderiza um trecho)
//   node tools/render.mjs sfx <out.json>                     -> exporta a lista de efeitos sonoros
// Variável AD_VARIANT=funk renderiza a versão com a música (ad.html?v=funk).
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync, rmSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const self = fileURLToPath(import.meta.url);
// AD_VARIANT=funk seleciona a variante sincronizada com a música (ad.html?v=funk)
const pageUrl = 'file://' + path.resolve(here, '..', 'ad.html') + (process.env.AD_VARIANT ? `?v=${process.env.AD_VARIANT}` : '');
const [mode, out, ...rest] = process.argv.slice(2);

const run = (cmd, args) => new Promise((res, rej) => {
  const p = spawn(cmd, args, { stdio: ['ignore', 'inherit', 'inherit'] });
  p.on('close', c => c === 0 ? res() : rej(new Error(`${cmd} saiu com ${c}`)));
});

async function openPage() {
  const browser = await chromium.launch({ args: ['--font-render-hinting=none', '--disable-lcd-text'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1080 }, deviceScaleFactor: 1 });
  await page.goto(pageUrl);
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => Promise.all([...document.images].map(i => i.decode())));
  return { browser, page };
}

if (mode === 'sfx') {
  const { browser, page } = await openPage();
  const data = await page.evaluate(() => ({ sfx: window.SFX, T: window.T, dur: window.DUR }));
  writeFileSync(out, JSON.stringify(data, null, 1));
  console.log('sfx events:', data.sfx.length);
  await browser.close();
} else if (mode === 'frames') {
  const { browser, page } = await openPage();
  mkdirSync(out, { recursive: true });
  for (const t of rest.map(Number)) {
    await page.evaluate(t => window.render(t), t);
    await page.screenshot({ path: path.join(out, `t_${t.toFixed(2).padStart(5, '0')}.png`) });
  }
  console.log('frames ok');
  await browser.close();
} else if (mode === 'chunk') {
  // trecho [a, b) de quadros → segmento quase sem perdas
  const [fps, sub, a, b] = rest.map(Number);
  const { browser, page } = await openPage();
  const vf = sub > 1 ? ['-vf', `tmix=frames=${sub},select='eq(mod(n\\,${sub})\\,${sub - 1})',setpts=N/${fps}/TB`] : [];
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps * sub), '-i', '-', ...vf,
    '-r', String(fps), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '8', '-pix_fmt', 'yuv444p', out],
    { stdio: ['pipe', 'inherit', 'inherit'] });
  const shutter = 0.5 / fps; // 180°
  for (let i = a; i < b; i++) {
    for (let k = 0; k < sub; k++) {
      const off = sub > 1 ? (k / (sub - 1) - .5) * shutter : 0;
      await page.evaluate(t => window.render(t), Math.max(0, i / fps + off));
      const buf = await page.screenshot({ type: 'png' });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    }
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
} else if (mode === 'video') {
  const fps = Number(rest[0] || 30), sub = Number(rest[1] || 1), jobs = Number(rest[2] || 4);
  const { browser, page } = await openPage();
  const dur = await page.evaluate(() => window.DUR);
  await browser.close();
  const n = Math.round(dur * fps), per = Math.ceil(n / jobs);
  const tmp = out + '.parts';
  rmSync(tmp, { recursive: true, force: true });
  mkdirSync(tmp, { recursive: true });
  const t0 = Date.now();
  const parts = [];
  for (let j = 0; j < jobs; j++) {
    const a = j * per, b = Math.min(n, a + per);
    if (a >= b) break;
    const f = path.join(tmp, `part${j}.mp4`);
    parts.push(f);
    console.log(`job ${j}: quadros ${a}–${b - 1}`);
  }
  await Promise.all(parts.map((f, j) => run('node', [self, 'chunk', f, fps, sub, j * per, Math.min(n, (j + 1) * per)])));
  writeFileSync(path.join(tmp, 'list.txt'), parts.map(p => `file '${path.resolve(p)}'`).join('\n'));
  await run('ffmpeg', ['-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', path.join(tmp, 'list.txt'), '-c', 'copy', out]);
  console.log(`video ok: ${n} quadros em ${((Date.now() - t0) / 1000).toFixed(0)}s`);
}
