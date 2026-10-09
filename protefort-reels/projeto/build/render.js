// node render.js stills <outdir> t1,t2,...      -> PNG stills
// node render.js frames <outdir> <fps> <workers> -> JPEG frame sequence + sfx.json
const { chromium } = require('./node_modules/playwright-core');
const fs = require('fs');
const path = require('path');
const EXE = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const URL = 'file://' + path.resolve(__dirname, 'index.html');

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => console.error('PAGEERROR', e.message));
  page.on('console', (m) => { if (m.type() === 'error') console.error('CONSOLE', m.text()); });
  await page.goto(URL);
  await page.waitForFunction(() => window.READY === true, null, { timeout: 30000 });
  return page;
}
const seek = (page, t) => page.evaluate((t) => { window.seek(Math.max(t, 0.0005)); }, t);

(async () => {
  const [mode, outdir, a, b] = process.argv.slice(2);
  fs.mkdirSync(outdir, { recursive: true });
  const browser = await chromium.launch({ executablePath: EXE, args: ['--disable-gpu-vsync', '--force-color-profile=srgb'] });
  if (mode === 'stills') {
    const page = await openPage(browser);
    for (const t of a.split(',').map(Number)) {
      await seek(page, t);
      await page.screenshot({ path: path.join(outdir, `t_${t.toFixed(2).padStart(6, '0')}.png`) });
    }
  } else {
    const fps = +a, workers = +b;
    const page0 = await openPage(browser);
    const dur = await page0.evaluate(() => window.DURATION);
    const sfx = await page0.evaluate(() => window.SFX_EVENTS);
    fs.writeFileSync(path.join(outdir, '..', 'sfx.json'), JSON.stringify({ duration: dur, events: sfx }, null, 1));
    await page0.close();
    const N = Math.ceil(dur * fps);
    const per = Math.ceil(N / workers);
    let done = 0;
    const t0 = Date.now();
    await Promise.all([...Array(workers)].map(async (_, w) => {
      const page = await openPage(browser);
      for (let i = w * per; i < Math.min(N, (w + 1) * per); i++) {
        await seek(page, i / fps);
        await page.screenshot({ path: path.join(outdir, `f_${String(i).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 93 });
        if (++done % 100 === 0) console.log(`${done}/${N} frames, ${((Date.now() - t0) / 1000).toFixed(0)}s`);
      }
    }));
    console.log('frames', N, 'duration', dur);
  }
  await browser.close();
})();
