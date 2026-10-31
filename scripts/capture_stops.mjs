import { chromium } from '/Users/eungsikahn/Dev/VibeCAD360/node_modules/playwright/index.mjs';

// Capture every screenful so the tone audit can look at real pixels later.
const [file, tag] = process.argv.slice(2);
const noImg = process.argv.includes('--noimg');
const b = await chromium.launch({ channel: 'chrome' });
const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
await p.goto('file://' + file, { waitUntil: 'load', timeout: 60000 });
await p.waitForTimeout(2500);

// The photographs are warm by nature and would drown the palette signal. Hiding them
// leaves only what the CSS paints: paper, ink, frames.
if (noImg) {
  await p.evaluate(() => {
    document.querySelectorAll('img, canvas, video').forEach(el => { el.style.visibility = 'hidden'; });
  });
}

const height = await p.evaluate(() => document.documentElement.scrollHeight);
const stops = Math.min(12, Math.max(1, Math.ceil(height / 900)));
for (let i = 0; i < stops; i++) {
  await p.evaluate(y => window.scrollTo(0, y), i * 900);
  await p.waitForTimeout(900);
  await p.screenshot({ path: `/tmp/tone_${tag}_${i}.png` });
}
console.log(tag, 'stops', stops, 'height', height);
await b.close();
