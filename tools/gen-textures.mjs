// One-off generator for museum textures (wood floor / plaster wall).
// Pure JS PNG writer — no dependencies. Run: node tools/gen-textures.mjs
import fs from 'node:fs';
import zlib from 'node:zlib';
import path from 'node:path';

const OUT = path.join(import.meta.dirname ?? '.', '..', 'museum', 'textures');

function crc32(buf) {
  let c, table = [];
  for (let n = 0; n < 256; n++) {
    c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    table[n] = c >>> 0;
  }
  let crc = 0xffffffff;
  for (const b of buf) crc = table[(crc ^ b) & 0xff] ^ (crc >>> 8);
  return (crc ^ 0xffffffff) >>> 0;
}

function chunk(type, data) {
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length);
  const t = Buffer.from(type, 'ascii');
  const body = Buffer.concat([t, data]);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(body));
  return Buffer.concat([len, body, crc]);
}

function writePNG(file, w, h, rgb) {
  const raw = Buffer.alloc((w * 3 + 1) * h);
  for (let y = 0; y < h; y++) {
    raw[y * (w * 3 + 1)] = 0;
    rgb.copy(raw, y * (w * 3 + 1) + 1, y * w * 3, (y + 1) * w * 3);
  }
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0);
  ihdr.writeUInt32BE(h, 4);
  ihdr[8] = 8; ihdr[9] = 2; ihdr[10] = 0; ihdr[11] = 0; ihdr[12] = 0;
  const png = Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    chunk('IHDR', ihdr),
    chunk('IDAT', zlib.deflateSync(raw, { level: 9 })),
    chunk('IEND', Buffer.alloc(0)),
  ]);
  fs.writeFileSync(file, png);
  return png.length;
}

// deterministic hash noise
function noise(x, y, seed) {
  let h = x * 374761393 + y * 668265263 + seed * 2246822519;
  h = (h ^ (h >>> 13)) * 1274126177;
  return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
}

function woodFloor(size = 512) {
  const rgb = Buffer.alloc(size * size * 3);
  const plankH = size / 4, plankW = size;
  for (let y = 0; y < size; y++) {
    const row = Math.floor(y / plankH);
    const off = (row % 2) * (plankW / 3);
    for (let x = 0; x < size; x++) {
      const px = (x + off) % plankW;
      const n = 0.62 + 0.38 * noise(x, y, 7);
      const grain = 0.92 + 0.08 * Math.sin(px * 0.05 + row * 2.1) * Math.sin(px * 0.013);
      const edge = Math.min(px, plankW - px) < 2 ? 0.55 : 1;
      const rowEdge = Math.min(y % plankH, plankH - 1 - (y % plankH)) < 2 ? 0.5 : 1;
      const k = n * grain * edge * rowEdge;
      const r = Math.min(255, Math.round(120 * k + 34));
      const g = Math.min(255, Math.round(86 * k + 22));
      const b = Math.min(255, Math.round(62 * k + 15));
      const i = (y * size + x) * 3;
      rgb[i] = r; rgb[i + 1] = g; rgb[i + 2] = b;
    }
  }
  return { rgb, size };
}

function plasterWall(size = 512) {
  const rgb = Buffer.alloc(size * size * 3);
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const n = noise(x, y, 3) * 0.6 + noise(x >> 2, y >> 2, 11) * 0.4;
      const v = 214 + (n - 0.5) * 22;
      const i = (y * size + x) * 3;
      rgb[i] = Math.round(v); rgb[i + 1] = Math.round(v - 3); rgb[i + 2] = Math.round(v - 9);
    }
  }
  return { rgb, size };
}

fs.mkdirSync(OUT, { recursive: true });
const a = woodFloor(512);
console.log('floor.png', writePNG(path.join(OUT, 'floor.png'), a.size, a.size, a.rgb));
const b = plasterWall(512);
console.log('wall.png', writePNG(path.join(OUT, 'wall.png'), b.size, b.size, b.rgb));
