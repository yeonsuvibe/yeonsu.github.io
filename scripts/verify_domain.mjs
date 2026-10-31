import { chromium } from '/Users/eungsikahn/Dev/VibeCAD360/node_modules/playwright/index.mjs';

// Moving from /yeonsu.github.io/ to the domain root changes the base path, so a link that
// worked before can silently 404 now. Crawl the live chain from the new origin and watch
// for failed requests, then capture the first screen.
const BASE = process.argv[2] || 'https://yeonsu.ahnvibe.kr/';
const b = await chromium.launch({ channel: 'chrome' });
const p = await b.newPage({ viewport: { width: 1440, height: 900 } });

const failed = [];
p.on('response', r => {
  const u = r.url();
  if (r.status() >= 400) failed.push(r.status() + ' ' + u);
  else if (/\.(html|css|js|json|png|jpg|jpeg|webp|svg)$/i.test(u) && !r.ok()) failed.push(r.status() + ' ' + u);
});
p.on('requestfailed', r => failed.push('NETFAIL ' + r.url()));

await p.goto(BASE, { waitUntil: 'load', timeout: 60000 });
await p.waitForTimeout(3500);

const state = await p.evaluate(() => {
  const ifr = document.querySelector('iframe');
  const fr = ifr && ifr.contentDocument;
  return {
    url: location.href,
    title: document.title,
    iframeSrc: ifr ? ifr.getAttribute('src') : null,
    iframeLoaded: !!fr,
    tiles: fr ? fr.querySelectorAll('.tile, .plate, figure').length : 0,
    sand: fr ? getComputedStyle(fr.documentElement).getPropertyValue('--sand').trim() : null,
  };
});
await p.screenshot({ path: '/tmp/domain_home.png' });

for (const path of ['gallery.html', 'gallery-v2.html', 'articles.html', 'refs.html']) {
  const r = await p.goto(BASE + path, { waitUntil: 'domcontentloaded', timeout: 45000 }).catch(e => null);
  console.log(path.padEnd(18), r ? r.status() : 'ERR');
}

console.log(JSON.stringify(state, null, 1));
console.log('failed requests:', failed.length);
failed.slice(0, 12).forEach(f => console.log('  ', f));
await b.close();
