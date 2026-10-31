import { chromium } from '/Users/eungsikahn/Dev/VibeCAD360/node_modules/playwright/index.mjs';

const b = await chromium.launch({ channel: 'chrome' });
for (const [w, h] of [[1440, 900], [1024, 768], [390, 844]]) {
  const p = await b.newPage({ viewport: { width: w, height: h } });
  const bad = [];
  p.on('response', r => { if (r.status() >= 400) bad.push(r.status() + ' ' + r.url().slice(-48)); });
  await p.goto('http://127.0.0.1:7799/gallery-v2.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(1000);
  const d = await p.evaluate(() => {
    const jr = document.querySelector('.jr');
    const r = jr.getBoundingClientRect();
    return {
      docW: document.documentElement.scrollWidth,
      winW: innerWidth,
      ko: /[\uac00-\ud7a3]/.test(document.body.textContent),
      stops: document.querySelectorAll('.jr').length,
      plates: document.querySelectorAll('.jr-plate img').length,
      firstLeft: Math.round(r.left),
    };
  });
  console.log(w, JSON.stringify(d), 'bad', bad.length);
  await p.close();
}
await b.close();
