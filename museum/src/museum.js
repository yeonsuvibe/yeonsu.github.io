import * as THREE from '../vendor/three.module.min.js';
import { makePanels, GALLERY, workZ, hallEnds } from './gallery.js';

/* ---------------------------------------------------------------
   Ahn Yeonsu — 3D Art Museum

   A single gallery hall with the weight of a real museum building:
   a stone dado along the floor, deep coffered bays overhead, a raised
   central skylight, and picture lights on every work. Walls are tiled
   with the art — one row along the long wall, and a few on the opposite
   wall to open the room. The visitor reads them by sliding along the
   wall to the right.

   The camera rides a rail parallel to the art wall at a child's eye
   height; it never turns away from the wall normal, so the picture in
   hand is always dead centre.
   --------------------------------------------------------------- */

export const MUSEUM = {
  width: 9.4,          // wall to wall
  height: 5.0,         // floor to the underside of the coffered roof
  endZ: 2.4,           // hall overhang past the first/last bay
  wallT: 0.4,
};

/** Service door in the art wall, local Z (the work in hand must clear it). */
export const DOOR = { z0: -6.3, z1: -1.7, h: 1.62 };

/* ------------------------------------------------------------------ */

function loadTextures() {
  const loader = new THREE.TextureLoader();
  const load = (url, repeat, filter) =>
    new Promise((resolve) => {
      loader.load(url, (t) => {
        t.wrapS = t.wrapT = THREE.RepeatWrapping;
        t.repeat.set(repeat[0], repeat[1]);
        t.colorSpace = THREE.SRGBColorSpace;
        t.anisotropy = 8;
        if (filter) { t.magFilter = filter; }
        resolve(t);
      }, undefined, () => resolve(null));
    });
  return Promise.all([
    load('textures/floor.png', [3, 18]),
    load('textures/plaster.png', [18, 1.6]),
  ]).then(([floor, plaster]) => ({ floor, plaster }));
}

function box(w, h, d, material, x, y, z) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), material);
  m.position.set(x, y, z);
  return m;
}

export async function initMuseum({ scene, data, hud }) {
  const tex = await loadTextures();
  const W = MUSEUM.width;
  const H = MUSEUM.height;
  const xa = GALLERY.wallX;

  const mat = {
    floor: new THREE.MeshStandardMaterial({ color: 0xd2cabd, map: tex.floor, roughness: 0.7, metalness: 0.02 }),
    artWall: new THREE.MeshStandardMaterial({ color: 0xf7f4ee, map: tex.plaster, roughness: 0.98 }),
    plainWall: new THREE.MeshStandardMaterial({ color: 0xefeae2, roughness: 0.99 }),
    ceiling: new THREE.MeshStandardMaterial({ color: 0xf1ece4, roughness: 1 }),
    coving: new THREE.MeshStandardMaterial({ color: 0xded6c9, roughness: 0.97 }),
    dado: new THREE.MeshStandardMaterial({ color: 0xcbc1b1, roughness: 0.86 }),
    stone: new THREE.MeshStandardMaterial({ color: 0xdcd5ca, roughness: 0.88 }),
    sky: new THREE.MeshBasicMaterial({ color: 0xfffbf1 }),
    skyGlow: new THREE.MeshBasicMaterial({ color: 0xfff8ea, transparent: true, opacity: 0.5 }),
    lamp: new THREE.MeshBasicMaterial({ color: 0xfff4e2 }),
  };

  const group = new THREE.Group();
  group.name = 'architecture';
  scene.add(group);

  /* span of the hall is fixed once the works are laid out */
  const panels0 = makePanels(data, tex, hud);
  const { zNear, zFar } = hallEnds(panels0.holders.length);
  const L = zFar - zNear;
  const zMid = (zNear + zFar) / 2;
  const xArt = xa + 0.16;         // inner face of the art wall
  const xOpp = -(W / 2);          // inner face of the opposite wall

  /* ---- floor: stone field with a darker border, like a real gallery ---- */
  group.add(box(W + 0.8, 0.16, L + 0.8, mat.floor, 0, -0.08, zMid));
  const bw = 0.42;
  group.add(box(bw, 0.03, L + 0.8, mat.stone, xArt - bw / 2, 0.015, zMid));
  group.add(box(bw, 0.03, L + 0.8, mat.stone, xOpp + bw / 2, 0.015, zMid));
  group.add(box(W + 0.8, 0.03, bw, mat.stone, 0, 0.015, zNear - 0.2));
  group.add(box(W + 0.8, 0.03, bw, mat.stone, 0, 0.015, zFar + 0.2));

  /* ---- art wall (+X): plaster panels around the service door ---- */
  const dh = DOOR.h;
  const leaves = [
    [0.20, H, zNear - 0.4, DOOR.z0],
    [0.20, H, DOOR.z1, zFar + 0.4],
    [0.20, dh, DOOR.z0, DOOR.z1],
    [0.20, H - dh - 0.34, DOOR.z0, DOOR.z1],
  ];
  for (const [t, h, z0, z1] of leaves) {
    group.add(box(t, h, Math.abs(z1 - z0), mat.artWall, xArt + t / 2, h / 2, (z0 + z1) / 2));
  }
  // door reveal + stepped architrave
  for (const z of [DOOR.z0, DOOR.z1]) {
    group.add(box(0.85, dh, 0.14, mat.plainWall, xArt + 0.5, dh / 2, z));
    group.add(box(0.10, dh + 0.14, 0.26, mat.stone, xArt + 0.03, (dh + 0.14) / 2, z + (z === DOOR.z0 ? -0.11 : 0.11)));
  }
  group.add(box(0.10, 0.2, DOOR.z1 - DOOR.z0 + 0.5, mat.stone, xArt + 0.03, dh + 0.16, (DOOR.z0 + DOOR.z1) / 2));

  /* ---- opposite wall, ends, and a stone dado on every wall ---- */
  group.add(box(MUSEUM.wallT, H, L + 1.6, mat.plainWall, xOpp - MUSEUM.wallT / 2, H / 2, zMid));
  group.add(box(W + 1.4, H, MUSEUM.wallT, mat.plainWall, 0, H / 2, zNear - 0.6));
  group.add(box(W + 1.4, H, MUSEUM.wallT, mat.plainWall, 0, H / 2, zFar + 0.6));
  for (const [w, d, x, z] of [
    [0.07, L + 1.6, xArt, zMid], [0.07, L + 1.6, xOpp + 0.05, zMid],
    [W + 1.4, 0.07, 0, zNear - 0.28], [W + 1.4, 0.07, 0, zFar + 0.28],
  ]) {
    group.add(box(Math.max(w, 0.06), 0.14, Math.max(d, 0.06), mat.dado, x, 0.07, z));
  }

  /* ---- coffered ceiling: a raised glazed strip and deep bays ---- */
  const roofH = H + 0.9;
  // outer ceiling, dropped, leaving the central well
  const well = 3.9;
  const sideW = (W + 0.8 - well) / 2;
  group.add(box(sideW, 0.34, L + 0.8, mat.ceiling, xArt - sideW / 2, H - 0.17, zMid));
  group.add(box(sideW, 0.34, L + 0.8, mat.ceiling, xOpp + sideW / 2, H - 0.17, zMid));
  // the lantern above the well
  group.add(box(0.5, roofH - H, L + 0.8, mat.coving, well / 2 - 0.25, (roofH + H) / 2, zMid));
  group.add(box(0.5, roofH - H, L + 0.8, mat.coving, -well / 2 + 0.25, (roofH + H) / 2, zMid));
  group.add(box(well, 0.3, L + 0.8, mat.ceiling, 0, roofH + 0.15, zMid));
  group.add(box(well - 0.9, 0.06, L - 1.0, mat.sky, 0, H + 0.55, zMid));
  group.add(box(well - 1.6, 0.04, L - 1.4, mat.skyGlow, 0, H + 0.2, zMid));
  // bays: a transverse rib every 3.4 m across the ceiling
  for (let z = zNear + 1.7; z < zFar; z += 3.4) {
    group.add(box(W + 0.8, 0.26, 0.36, mat.coving, 0, H - 0.13, z));
    group.add(box(well, 0.22, 0.3, mat.coving, 0, H + 0.34, z));
  }

  /* ---- pilasters on the art wall: a bay around every work ---- */
  const bays = [];
  for (const holder of panels0.holders) {
    const z = holder.position.z;
    const hw = holder.userData.size.w / 2;
    bays.push(z - hw - 0.5, z + hw + 0.5);
  }
  for (const z of bays) {
    group.add(box(0.34, H, 0.44, mat.artWall, xArt - 0.17, H / 2, z));
    group.add(box(0.42, 0.46, 0.54, mat.dado, xArt - 0.19, 0.23, z));
    group.add(box(0.4, 0.14, 0.5, mat.stone, xArt - 0.18, H - 0.44, z));
  }

  /* ---- pilasters opposite the works: they give the hall its depth ---- */
  for (let z = zNear + 1.2; z < zFar; z += 3.4) {
    group.add(box(0.55, H - 0.3, 0.52, mat.coving, xOpp + 0.3, (H - 0.3) / 2, z));
    group.add(box(0.72, 0.34, 0.68, mat.dado, xOpp + 0.36, 0.17, z));
    group.add(box(0.72, 0.16, 0.68, mat.stone, xOpp + 0.36, 0.42, z));
    group.add(box(0.72, 0.2, 0.68, mat.stone, xOpp + 0.36, H - 0.34, z));
  }

  /* ---- lighting: even, colourless daylight from the lantern ---- */
  scene.add(new THREE.HemisphereLight(0xffffff, 0xcdc6ba, 1.05));
  scene.add(new THREE.AmbientLight(0xffffff, 0.3));
  for (let z = zNear + 1; z < zFar; z += 4.5) {
    const l = new THREE.PointLight(0xfff8ec, 12, 22, 2);
    l.position.set(0, H + 0.2, z);
    scene.add(l);
  }
  // picture lights: a slim hood above each frame, aimed at the work
  const spots = [];
  for (const holder of panels0.holders) {
    const size = holder.userData.size;
    const yTop = GALLERY.workHeight + size.h / 2 + 0.34;
    const s = new THREE.SpotLight(0xfff0d6, 7, 6, 0.7, 0.85, 2);
    s.position.set(holder.position.x - 0.42, yTop, holder.position.z);
    s.target.position.set(holder.position.x, GALLERY.workHeight - 0.2, holder.position.z);
    group.add(s, s.target);
    // the fixture itself: a thin bar just off the wall, above the sheet
    group.add(box(0.2, 0.055, size.w * 0.5, mat.lamp, holder.position.x - 0.34, yTop, holder.position.z));
    spots.push(s);
  }

  scene.add(panels0.group);

  return { panels: panels0, zNear, zFar, door: DOOR };
}

export { GALLERY, workZ };
export const WALL_X = GALLERY.wallX;
