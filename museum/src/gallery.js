import * as THREE from '../vendor/three.module.min.js';

const PANEL_MAX_W = 2.4;
const PANEL_MAX_H = 2.0;

/** Frame profile used for every hung work: slim gilded chrome. */
export function makeChromeFrame() {
  return new THREE.MeshStandardMaterial({ color: 0xc8ab74, roughness: 0.42, metalness: 0.35 });
}

function fitSize(tex, maxW = PANEL_MAX_W, maxH = PANEL_MAX_H) {
  const iw = tex?.image?.width || 4;
  const ih = tex?.image?.height || 3;
  const aspect = iw / ih;
  let w = maxW;
  let h = w / aspect;
  if (h > maxH) { h = maxH; w = h * aspect; }
  return { w, h, aspect };
}

function makeSpotlight(x, y, z, tx, ty, tz, color = 0xfff0d4) {
  const spot = new THREE.SpotLight(color, 22, 11, 0.55, 0.75, 2);
  spot.position.set(x, y, z);
  spot.target.position.set(tx, ty, tz);
  const g = new THREE.Group();
  g.add(spot, spot.target);
  return g;
}

/**
 * Builds the framed, lit and captioned hanging works.
 * entries: [{ gallery, spots: [{ workIndex, pos, rotY }] }]
 */
export function makePanels(entries, data, textures, hud) {
  const group = new THREE.Group();
  group.name = 'panels';
  const loader = new THREE.TextureLoader();
  const panelMats = new Map();
  const hoverables = [];

  for (const { spots } of entries) {
    for (const spot of spots) {
      const work = data.works[spot.workIndex];
      if (!work) continue;
      const tex = loader.load(work.file);
      tex.colorSpace = THREE.SRGBColorSpace;
      tex.anisotropy = 8;
      const { w, h } = fitSize(tex);

      const holder = new THREE.Group();
      holder.position.copy(spot.pos);
      holder.rotation.y = spot.rotY;

      // canvas
      const art = new THREE.Mesh(
        new THREE.PlaneGeometry(w, h),
        new THREE.MeshStandardMaterial({ map: tex, roughness: 0.72, metalness: 0 }),
      );
      art.position.z = 0.075;
      art.userData.work = work;
      art.userData.panel = true;

      // frame
      const frameDepth = 0.09;
      const border = 0.085;
      const frameMat = makeChromeFrame();
      const parts = [
        [w + border * 2, border, 'h'], [w + border * 2, border, 'h'],
        [border, h, 'v'], [border, h, 'v'],
      ];
      parts.forEach(([pw, ph], i) => {
        const m = new THREE.Mesh(new THREE.BoxGeometry(pw, ph, frameDepth), frameMat);
        if (i < 2) m.position.set(0, (i === 0 ? 1 : -1) * (h / 2 + border / 2), 0.03);
        else m.position.set((i === 2 ? -1 : 1) * (w / 2 + border / 2), 0, 0.03);
        holder.add(m);
      });

      // mat / backing board
      const board = new THREE.Mesh(
        new THREE.BoxGeometry(w + border * 2, h + border * 2, 0.05),
        new THREE.MeshStandardMaterial({ color: 0xf4efe6, roughness: 0.9 }),
      );
      board.position.z = -0.02;
      holder.add(board, art);

      // wall label plaque
      const plaque = makePlaque(work, w, h);
      holder.add(plaque);

      // picture light
      const light = makeSpotlight(0, h / 2 + 1.0, 1.5, 0, 0, 0.1);
      holder.add(light);

      holder.userData.work = work;
      holder.userData.isPanel = true;
      group.add(holder);
      hoverables.push(art);
      panelMats.set(work.no, { mat: art.material, base: 0.72 });
    }
  }

  if (hud?.setTotal) hud.setTotal(data.works.length);
  return { group, hoverables, panelMats };
}

function makePlaque(work, w, h) {
  const canvas = document.createElement('canvas');
  canvas.width = 512; canvas.height = 160;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#efe9dd';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#c3a86f';
  ctx.fillRect(0, 0, canvas.width, 5);
  ctx.fillStyle = '#2a2724';
  ctx.font = '600 42px Inter, Helvetica, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText(`No. ${work.no}`, 26, 66);
  ctx.font = '300 40px Inter, Helvetica, sans-serif';
  ctx.fillStyle = '#5a544c';
  ctx.fillText(work.date, 26, 122);
  ctx.font = '300 30px Inter, Helvetica, sans-serif';
  ctx.textAlign = 'right';
  ctx.fillText('AHN YEONSU', canvas.width - 26, 96);

  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  const pw = Math.min(0.62, w * 0.34);
  const ph = pw * (canvas.height / canvas.width);
  const plaque = new THREE.Mesh(
    new THREE.PlaneGeometry(pw, ph),
    new THREE.MeshStandardMaterial({ map: tex, roughness: 0.8 }),
  );
  plaque.position.set(w / 2 + 0.25 + pw / 2, -h / 2 - 0.22 - ph / 2, 0.06);
  return plaque;
}

/** Floating room-name sign (canvas sprite). */
export function makeLabel(text, hud) {
  const canvas = document.createElement('canvas');
  canvas.width = 1024; canvas.height = 128;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.font = '600 56px Inter, Helvetica, sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillStyle = 'rgba(12,10,9,0.55)';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#e8dcc0';
  ctx.fillText(text, canvas.width / 2, canvas.height / 2 + 2);
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  const mesh = new THREE.Mesh(
    new THREE.PlaneGeometry(5.2, 0.65),
    new THREE.MeshBasicMaterial({ map: tex, transparent: true }),
  );
  return mesh;
}
