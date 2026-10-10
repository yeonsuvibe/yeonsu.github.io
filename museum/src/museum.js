import * as THREE from '../vendor/three.module.min.js';
import { makePanels, GALLERY, workZ, hallEnds } from './gallery.js';

/* ---------------------------------------------------------------
   Ahn Yeonsu — 3D Art Museum

   The building is drawn in black and white only: white walls, a white
   coffered roof with a raised glazed lantern, a grey stone floor with
   a black border, black skirting. No column, no pilaster, no ornament
   — nothing in grey competes with the works.

   The eleven works hang in black frames in one row along the art wall
   (+X), in date order. The row runs towards +Z, the visitor's right,
   so "next" slides the camera right along the wall. The camera rides
   parallel to the wall at eye height and never turns away from its
   normal, so the picture in hand is always dead centre.
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

function box(w, h, d, material, x, y, z) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), material);
  m.position.set(x, y, z);
  return m;
}

export async function initMuseum({ scene, data, hud }) {
  const W = MUSEUM.width;
  const H = MUSEUM.height;
  const xa = GALLERY.wallX;

  /* ---- the palette is monochrome, and only monochrome ---- */
  const mat = {
    floor: new THREE.MeshStandardMaterial({ color: 0xd6d6d6, roughness: 0.72, metalness: 0 }),
    border: new THREE.MeshStandardMaterial({ color: 0x1e1e1e, roughness: 0.6 }),
    wall: new THREE.MeshStandardMaterial({ color: 0xf4f4f4, roughness: 1 }),
    ceiling: new THREE.MeshStandardMaterial({ color: 0xfbfbfb, roughness: 1 }),
    trim: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.95 }),
    black: new THREE.MeshStandardMaterial({ color: 0x151515, roughness: 0.72 }),
    sky: new THREE.MeshBasicMaterial({ color: 0xffffff }),
    skyGlow: new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.55 }),
    lamp: new THREE.MeshBasicMaterial({ color: 0xffffff }),
  };

  const group = new THREE.Group();
  group.name = 'architecture';
  scene.add(group);

  /* span of the hall is fixed once the works are laid out */
  const panels0 = makePanels(data, mat, hud);
  const { zNear, zFar } = hallEnds(panels0.holders.length);
  const L = zFar - zNear;
  const zMid = (zNear + zFar) / 2;
  const xArt = xa + 0.16;         // inner face of the art wall
  const xOpp = -(W / 2);          // inner face of the opposite wall

  /* ---- floor: grey field, black border ---- */
  group.add(box(W + 0.8, 0.16, L + 0.8, mat.floor, 0, -0.08, zMid));
  const bw = 0.5;
  group.add(box(bw, 0.02, L + 0.8, mat.border, xArt - bw / 2, 0.011, zMid));
  group.add(box(bw, 0.02, L + 0.8, mat.border, xOpp + bw / 2, 0.011, zMid));
  group.add(box(W + 0.8, 0.02, bw, mat.border, 0, 0.011, zNear - 0.25));
  group.add(box(W + 0.8, 0.02, bw, mat.border, 0, 0.011, zFar + 0.25));

  /* ---- art wall (+X): plain white, with the service door at the far end ---- */
  const dh = DOOR.h;
  const leaves = [
    [0.20, H, zNear - 0.4, DOOR.z0],
    [0.20, H, DOOR.z1, zFar + 0.4],
    [0.20, dh, DOOR.z0, DOOR.z1],
    [0.20, H - dh - 0.3, DOOR.z0, DOOR.z1],
  ];
  for (const [t, h, z0, z1] of leaves) {
    group.add(box(t, h, Math.abs(z1 - z0), mat.wall, xArt + t / 2, h / 2, (z0 + z1) / 2));
  }
  // black door leaf, set into the wall like a flat panel
  group.add(box(0.06, dh - 0.06, DOOR.z1 - DOOR.z0 - 0.08, mat.black, xArt + 0.11, (dh - 0.06) / 2, (DOOR.z0 + DOOR.z1) / 2));

  /* ---- opposite wall and end walls ---- */
  group.add(box(MUSEUM.wallT, H, L + 1.6, mat.wall, xOpp - MUSEUM.wallT / 2, H / 2, zMid));
  group.add(box(W + 1.4, H, MUSEUM.wallT, mat.wall, 0, H / 2, zNear - 0.6));
  group.add(box(W + 1.4, H, MUSEUM.wallT, mat.wall, 0, H / 2, zFar + 0.6));

  /* ---- black skirting on every wall ---- */
  for (const [w, d, x, z] of [
    [0.06, L + 1.6, xArt, zMid], [0.06, L + 1.6, xOpp + 0.04, zMid],
    [W + 1.4, 0.06, 0, zNear - 0.26], [W + 1.4, 0.06, 0, zFar + 0.26],
  ]) {
    group.add(box(Math.max(w, 0.05), 0.16, Math.max(d, 0.05), mat.black, x, 0.08, z));
  }

  /* ---- coffered ceiling: a raised glazed lantern, with a black rib per bay ---- */
  const roofH = H + 0.9;
  const well = 3.9;
  const sideW = (W + 0.8 - well) / 2;
  group.add(box(sideW, 0.34, L + 0.8, mat.ceiling, xArt - sideW / 2, H - 0.17, zMid));
  group.add(box(sideW, 0.34, L + 0.8, mat.ceiling, xOpp + sideW / 2, H - 0.17, zMid));
  // the lantern above the well
  group.add(box(0.5, roofH - H, L + 0.8, mat.trim, well / 2 - 0.25, (roofH + H) / 2, zMid));
  group.add(box(0.5, roofH - H, L + 0.8, mat.trim, -well / 2 + 0.25, (roofH + H) / 2, zMid));
  group.add(box(well, 0.3, L + 0.8, mat.ceiling, 0, roofH + 0.15, zMid));
  group.add(box(well - 0.9, 0.06, L - 1.0, mat.sky, 0, H + 0.55, zMid));
  group.add(box(well - 1.6, 0.04, L - 1.4, mat.skyGlow, 0, H + 0.2, zMid));
  // bays: a thin black rib across the ceiling every 3.4 m
  for (let z = zNear + 1.7; z < zFar; z += 3.4) {
    group.add(box(W + 0.8, 0.2, 0.13, mat.black, 0, H - 0.1, z));
    group.add(box(well, 0.16, 0.12, mat.black, 0, H + 0.36, z));
  }

  /* ---- lighting: even, colourless daylight from the lantern ---- */
  scene.add(new THREE.HemisphereLight(0xffffff, 0xd8d8d8, 1.15));
  scene.add(new THREE.AmbientLight(0xffffff, 0.35));
  for (let z = zNear + 1; z < zFar; z += 4.5) {
    const l = new THREE.PointLight(0xffffff, 11, 24, 2);
    l.position.set(0, H + 0.2, z);
    scene.add(l);
  }
  // picture lights: a white bar off the wall above each frame
  for (const holder of panels0.holders) {
    const size = holder.userData.size;
    const yTop = GALLERY.workHeight + size.h / 2 + 0.4;
    const s = new THREE.SpotLight(0xffffff, 6, 7, 0.7, 0.85, 2);
    s.position.set(holder.position.x - 0.5, yTop, holder.position.z);
    s.target.position.set(holder.position.x, GALLERY.workHeight - 0.2, holder.position.z);
    group.add(s, s.target);
    // the fixture: a black housing on a bracket, with a white lit face below
    const arm = size.w * 0.36;
    const xw = holder.position.x + 0.16;                 // the wall face itself
    group.add(box(0.3, 0.05, 0.05, mat.black, xw - 0.15, yTop + 0.06, holder.position.z));   // bracket
    group.add(box(0.32, 0.1, arm, mat.black, xw - 0.16, yTop + 0.03, holder.position.z));    // housing
    group.add(box(0.26, 0.03, arm - 0.04, mat.lamp, xw - 0.16, yTop - 0.03, holder.position.z)); // lit face
  }

  scene.add(panels0.group);

  return { panels: panels0, zNear, zFar, door: DOOR };
}

export { GALLERY, workZ };
export const WALL_X = GALLERY.wallX;
