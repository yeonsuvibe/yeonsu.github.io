import * as THREE from '../vendor/three.module.min.js';
import { makePanels, GALLERY, workZ } from './gallery.js';

/* ---------------------------------------------------------------
   Ahn Yeonsu — 3D Art Museum

   One continuous hall. The camera rides a horizontal rail at a fixed
   height about 2.6 m out from the art wall, and the view axis stays
   perpendicular to the wall: moving to the next work slides the
   camera along the wall to the right, it never turns to approach.
   The camera height never changes, so the works are always seen at
   eye level and never read as hung high on the wall.
   --------------------------------------------------------------- */

export const MUSEUM = {
  width: 6.0,          // wall to wall across the hall
  margin: 2.4,         // extra hall length beyond the first/last work
  height: 3.55,
  wallT: 0.35,
};

/** Walk distance to each work; the rail sits on the -X side. */
export const RAIL_X = 0.8;                 // where the visitor stands
export const DOOR = { zA: 4.6, zB: -3.6, h: 1.56 };   // service door in the art wall

export function museumFloorY() { return 0; }

/* ------------------------------------------------------------------ */

function loadTextures() {
  const loader = new THREE.TextureLoader();
  const load = (url, repeat) =>
    new Promise((resolve) => {
      loader.load(url, (t) => {
        t.wrapS = t.wrapT = THREE.RepeatWrapping;
        t.repeat.set(repeat[0], repeat[1]);
        t.colorSpace = THREE.SRGBColorSpace;
        t.anisotropy = 8;
        resolve(t);
      }, undefined, () => resolve(null));
    });
  return Promise.all([
    load('textures/floor.png', [3, 22]),
    load('textures/plaster.png', [16, 1.1]),
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
  const zFront = MUSEUM.margin;                 // +Z end
  const zBack = workZ(data.works.length - 1) - MUSEUM.margin;
  const L = zFront - zBack;
  const zMid = (zFront + zBack) / 2;
  const xa = GALLERY.wallX;

  const mat = {
    floor: new THREE.MeshStandardMaterial({ color: 0xf0ece3, map: tex.floor, roughness: 0.72, metalness: 0 }),
    artWall: new THREE.MeshStandardMaterial({ color: 0xfbf8f2, map: tex.plaster, roughness: 0.99 }),
    plainWall: new THREE.MeshStandardMaterial({ color: 0xf3efe7, roughness: 0.99 }),
    ceiling: new THREE.MeshStandardMaterial({ color: 0xf8f5ef, roughness: 1 }),
    soffit: new THREE.MeshStandardMaterial({ color: 0xe9e4da, roughness: 1 }),
    sky: new THREE.MeshBasicMaterial({ color: 0xfffbf2 }),
    stone: new THREE.MeshStandardMaterial({ color: 0xe8e3d9, roughness: 0.92 }),
  };

  const group = new THREE.Group();
  group.name = 'architecture';
  scene.add(group);

  /* floor */
  group.add(box(W + 0.8, 0.12, L + 0.8, mat.floor, 0, -0.06, zMid));

  /* art wall (+X), built around the service door */
  const xw = xa + 0.15;
  const doorHeight = DOOR.h;
  const leaves = [
    [0.18, H, zFront + 0.4, DOOR.zA],                       // front of the door
    [0.18, H, DOOR.zB, zBack - 0.4],                        // behind the door
    [0.18, doorHeight, DOOR.zA, DOOR.zB],                   // below
    [0.18, H - doorHeight - 0.28, DOOR.zA, DOOR.zB],        // lintel
  ];
  for (const [t, h, z0, z1] of leaves) {
    group.add(box(t, h, Math.abs(z1 - z0), mat.artWall, xw, h / 2, (z0 + z1) / 2));
  }
  // reveal, so the opening reads as a real door
  group.add(box(0.9, DOOR.h, 0.16, mat.plainWall, xa + 0.5, DOOR.h / 2, DOOR.zA));
  group.add(box(0.9, DOOR.h, 0.16, mat.plainWall, xa + 0.5, DOOR.h / 2, DOOR.zB));
  group.add(box(0.7, 0.06, DOOR.zA - DOOR.zB, mat.stone, xa + 0.4, 0.03, (DOOR.zA + DOOR.zB) / 2));

  /* opposite wall (-X) */
  group.add(box(MUSEUM.wallT, H, L + 0.8, mat.plainWall, -(W / 2 - MUSEUM.wallT / 2), H / 2, zMid));

  /* end walls */
  group.add(box(W + 1, H, MUSEUM.wallT, mat.plainWall, 0, H / 2, zFront + 0.4));
  group.add(box(W + 1, H, MUSEUM.wallT, mat.plainWall, 0, H / 2, zBack - 0.4));

  /* ceiling: a flat pale slab with one long skylight strip centred on the hall */
  group.add(box(W + 0.8, 0.28, L + 0.8, mat.ceiling, 0, H + 0.14, zMid));
  group.add(box(2.4, 0.24, L + 0.8, mat.soffit, 0.4, H - 0.12, zMid));
  group.add(box(1.9, 0.05, L - 1.4, mat.sky, 0.4, H - 0.26, zMid));

  /* a suspension slot along the art wall, reading as the lighting track */
  group.add(box(0.34, 0.1, L - 1.2, mat.stone, xa - 0.45, H - 0.16, zMid));

  const panels = makePanels(data, tex, hud);
  group.add(panels.group);

  /* lighting: even, colourless daylight — the works hold the only colour */
  scene.add(new THREE.HemisphereLight(0xffffff, 0xdcd6cb, 1.25));
  scene.add(new THREE.AmbientLight(0xffffff, 0.42));
  for (let z = zFront - 3; z > zBack + 2; z -= 7.5) {
    const l = new THREE.PointLight(0xfff8ee, 8, 18, 2);
    l.position.set(0, H - 0.7, z);
    scene.add(l);
  }
  // a soft wash on the works themselves, from above and behind the rail
  for (let z = zFront - 2; z > zBack + 1; z -= 3.4) {
    const l = new THREE.PointLight(0xffffff, 4, 6.5, 2);
    l.position.set(RAIL_X + 0.9, H - 0.4, z);
    scene.add(l);
  }

  return { panels, zFront, zBack };
}

export { workZ, GALLERY };
export const WALL_X = GALLERY.wallX;
