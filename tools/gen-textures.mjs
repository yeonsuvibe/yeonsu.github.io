import fs from 'node:fs';
import zlib from 'node:zlib';
import path from 'node:path';

/* ------------------------------------------------------------------
   One-off generator for the museum textures. Pure JS PNG writer, no
   dependencies. Run: node tools/gen-textures.mjs
   Swap the TREATMENT switch to try another material for the art wall.
   ------------------------------------------------------------------ */

const OUT = path.join(import.meta.dirname ?? '.', '..', 'museum', 'textures');
const TREATMENT = 'plaster';   // 'plaster' | 'woven'

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
  const body = Buffer.concat([Buffer.from(type, 'ascii'), data]);
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
const smooth = (t) => t * t * (3 - 2 * t);
function valueNoise(x, y, seed) {
  const xi = Math.floor(x), yi = Math.floor(y);
  const xf = smooth(x - xi), yf = smooth(y - yi);
  const a = noise(xi, yi, seed), b = noise(xi + 1, yi, seed);
  const c = noise(xi, yi + 1, seed), d = noise(xi + 1, yi + 1, seed);
  return (a * (1 - xf) + b * xf) * (1 - yf) + (c * (1 - xf) + d * xf) * yf;
}

/** A quiet, pale floor: matte oak stone, low contrast — never competes with the works. */
function floor(size = 512) {
  const rgb = Buffer.alloc(size * size * 3);
  const plankH = size / 4;
  for (let y = 0; y < size; y++) {
    const row = Math.floor(y / plankH);
    const off = (row % 2) * (size / 3);
    for (let x = 0; x < size; x++) {
      const px = (x + off) % size;
      const grain = valueNoise(px * 0.06, row * 40 + px * 0.01, 5);
      const n = valueNoise(x * 0.09, y * 0.09, 7) * 0.5 + valueNoise(x * 0.4, y * 0.4, 9) * 0.5;
      const seam = Math.min(px, size - px) < 1.6 ? 0.86 : 1;
      const joint = Math.min(y % plankH, plankH - 1 - (y % plankH)) < 1.6 ? 0.88 : 1;
      const v = (196 + (n - 0.5) * 16 + (grain - 0.5) * 18) * seam * joint;
      const i = (y * size + x) * 3;
      rgb[i] = Math.min(255, Math.round(v + 6));
      rgb[i + 1] = Math.min(255, Math.round(v + 1));
      rgb[i + 2] = Math.min(255, Math.round(v - 8));
    }
  }
  return { rgb, size };
}

/** Bare plaster. Soft, colourless, evenly lit. */
function plasterWall(size = 512) {
  const rgb = Buffer.alloc(size * size * 3);
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const n = valueNoise(x * 0.02, y * 0.02, 3) * 0.65 + valueNoise(x * 0.09, y * 0.09, 11) * 0.35;
      const v = 240 + (n - 0.5) * 10;
      const i = (y * size + x) * 3;
      rgb[i] = Math.round(v);
      rgb[i + 1] = Math.round(v - 1);
      rgb[i + 2] = Math.round(v - 4);
    }
  }
  return { rgb, size };
}

/** Alternative art-wall treatment: fine woven linen weave. */
function wovenWall(size = 512) {
  const rgb = Buffer.alloc(size * size * 3);
  const period = 4;
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const warp = Math.sin((x / period) * Math.PI) ** 2;
      const weft = Math.sin((y / period) * Math.PI) ** 2;
      const n = valueNoise(x * 1.4, y * 1.4, 13);
      const v = 232 + (warp * 0.5 + weft * 0.5 - 0.5) * 9 + (n - 0.5) * 6;
      const i = (y * size + x) * 3;
      rgb[i] = Math.round(v);
      rgb[i + 1] = Math.round(v - 2);
      rgb[i + 2] = Math.round(v - 8);
    }
  }
  return { rgb, size };
}

fs.mkdirSync(OUT, { recursive: true });
const f = floor(512);
console.log('floor.png', writePNG(path.join(OUT, 'floor.png'), f.size, f.size, f.rgb));
const art = TREATMENT === 'woven' ? wovenWall(512) : plasterWall(512);
console.log(`plaster.png (${TREATMENT})`, writePNG(path.join(OUT, 'plaster.png'), art.size, art.size, art.rgb));
