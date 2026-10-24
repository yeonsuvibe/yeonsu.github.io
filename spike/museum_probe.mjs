import pw from '/Users/eungsikahn/Dev/VibeHarness/node_modules/playwright-core/index.js';
const { chromium } = pw;

const URL = process.env.MURL || 'http://127.0.0.1:7789/museum/index.html';
const TAG = process.env.TAG || 'base';

const b = await chromium.launch({
  channel: 'chrome',
  headless: false,
  args: ['--window-position=-3000,-3000', '--window-size=1400,1000', '--enable-gpu-rasterization', '--ignore-gpu-blocklist'],
});
const p = await b.newPage({ viewport: { width: 1367, height: 1009 }, deviceScaleFactor: 1 });
const errs = [];
p.on('pageerror', (e) => errs.push(String(e)));
p.on('console', (m) => { if (m.type() === 'error' && !/favicon/.test(m.text())) errs.push(m.text()); });

await p.goto(URL, { waitUntil: 'networkidle' });
await p.waitForTimeout(2500);

// enter the hall
await p.evaluate(() => { document.getElementById('startBtn')?.click(); });
await p.waitForTimeout(600);

const ready = await p.evaluate(() => !!window.__museum);
if (!ready) {
  await p.screenshot({ path: `/tmp/museum-${TAG}-fail.png` });
  console.log(JSON.stringify({ tag: TAG, bootFailed: true, errs: errs.slice(0, 8) }));
  await b.close();
  process.exit(0);
}

const measure = await p.evaluate(async () => {
  const M = window.__museum;
  const r = M.scene.userData.__renderer || null;
  // find the renderer off the canvas (three keeps it on the element it drew)
  const renderer = window.__museum.renderer;
  const times = [];
  await new Promise((res) => {
    let last = performance.now();
    let n = 0;
    function tick() {
      const now = performance.now();
      times.push(now - last);
      last = now;
      if (++n < 160) requestAnimationFrame(tick); else res();
    }
    requestAnimationFrame(tick);
  });
  const s = times.slice(30).sort((a, b) => a - b);
  const info = renderer ? renderer.info.render : null;
  return {
    rendererFound: !!renderer,
    medianFrameMs: +s[Math.floor(s.length / 2)].toFixed(2),
    p95FrameMs: +s[Math.floor(s.length * 0.95)].toFixed(2),
    calls: info?.calls ?? null,
    triangles: info?.triangles ?? null,
    programs: renderer?.info.programs?.length ?? null,
    textures: renderer?.info.memory?.textures ?? null,
    geometrics: renderer?.info.memory?.geometries ?? null,
    toneMapping: renderer?.toneMapping ?? null,
    shadowEnabled: renderer?.shadowMap?.enabled ?? null,
    pixelRatio: renderer?.getPixelRatio?.() ?? null,
    lights: (() => { let n = 0; M.scene.traverse((o) => { if (o.isLight) n++; }); return n; })(),
    envMap: !!M.scene.environment,
  };
});

await p.screenshot({ path: `/tmp/museum-${TAG}.png` });
console.log(JSON.stringify({ tag: TAG, ...measure, errs: errs.slice(0, 5) }));
await b.close();
