import * as THREE from '../vendor/three.module.min.js';
import { PointerLockControls } from './PointerLockControls.js';
import { makePanels, makeChromeFrame, makeLabel } from './gallery.js';
import { makeHud } from './hud.js';

/* ---------------------------------------------------------------
   Ahn Yeonsu — 3D Art Museum
   Layout: an entry gallery (1) plus two wings (2, 3) holding the
   eleven captioned works of the Art Portfolio, in date order.
   --------------------------------------------------------------- */

export const MUSEUM = {
  galleryW: 14,      // inner width  (x)
  galleryH: 7.2,     // wall height  (y)
  corridorW: 6,      // inner width of connecting corridor
  gap: 12,           // corridor length (z) between galleries
};

export const GALLERIES = [
  { id: 0, z0: 0, depth: 22 },
  { id: 1, z0: 34, depth: 22 },
  { id: 2, z0: 68, depth: 22 },
];

/** Works are split into the rooms in date order, as evenly as possible. */
export function splitWorks(works, rooms = GALLERIES.length) {
  const per = Math.ceil(works.length / rooms);
  const out = [];
  for (let i = 0; i < works.length; i += per) out.push(works.slice(i, i + per));
  while (out.length < rooms) out.push([]);
  return out;
}

const FLOOR_Y = 0;

async function loadTextures() {
  const loader = new THREE.TextureLoader();
  const load = (url, repeat) =>
    new Promise((resolve) => {
      loader.load(
        url,
        (t) => {
          t.wrapS = t.wrapT = THREE.RepeatWrapping;
          t.repeat.set(repeat[0], repeat[1]);
          t.colorSpace = THREE.SRGBColorSpace;
          t.anisotropy = 8;
          resolve(t);
        },
        undefined,
        () => resolve(null),
      );
    });
  const [floor, wall] = await Promise.all([
    load('textures/floor.png', [6, 30]),
    load('textures/wall.png', [4, 2]),
  ]);
  return { floor, wall };
}

function boxMesh(w, h, d, material) {
  return new THREE.Mesh(new THREE.BoxGeometry(w, h, d), material);
}

function buildArchitecture(scene, materials) {
  const { galleryW, galleryH, corridorW, gap } = MUSEUM;
  const collide = [];

  const wallMat = materials.wall;
  const trimMat = materials.trim;
  const floorMat = materials.floor;

  for (const g of GALLERIES) {
    const z = -(g.z0 + g.depth / 2);
    const half = g.depth / 2;
    const wallT = 0.4, floorT = 0.1;

    // floor
    const floor = boxMesh(galleryW + 0.8, floorT, g.depth + 0.8, floorMat);
    floor.position.set(0, FLOOR_Y - floorT / 2, z);
    scene.add(floor);

    // ceiling
    const ceil = boxMesh(galleryW + 0.8, 0.2, g.depth + 0.8, materials.ceiling);
    ceil.position.set(0, galleryH, z);
    scene.add(ceil);

    // side walls
    for (const sx of [-1, 1]) {
      const w = boxMesh(wallT, galleryH, g.depth + 0.8, wallMat);
      w.position.set(sx * (galleryW / 2 + wallT / 2), galleryH / 2, z);
      scene.add(w);
      collide.push({ x0: w.position.x - wallT / 2, x1: w.position.x + wallT / 2, z0: z - half - 0.4, z1: z + half + 0.4 });
    }

    // end walls, with a door opening toward the next gallery
    const hasDoor = g.id < GALLERIES.length - 1;
    for (const [side, zz] of [['front', z + half], ['back', z - half]]) {
      const door = hasDoor && side === 'back';
      if (door) {
        const sideW = (galleryW - corridorW) / 2 + 0.4;
        for (const sx of [-1, 1]) {
          const w = boxMesh(sideW, galleryH, wallT, wallMat);
          w.position.set(sx * (galleryW / 2 - sideW / 2 + 0.4), galleryH / 2, zz);
          scene.add(w);
          collide.push({ x0: w.position.x - sideW / 2, x1: w.position.x + sideW / 2, z0: zz - wallT / 2, z1: zz + wallT / 2 });
        }
        const lintel = boxMesh(corridorW + 0.8, galleryH - 3.4, wallT, wallMat);
        lintel.position.set(0, 3.4 + (galleryH - 3.4) / 2, zz);
        scene.add(lintel);
      } else {
        const w = boxMesh(galleryW + 0.8, galleryH, wallT, wallMat);
        w.position.set(0, galleryH / 2, zz);
        scene.add(w);
        if (side !== 'front') collide.push({ x0: -(galleryW / 2 + 0.4), x1: galleryW / 2 + 0.4, z0: zz - wallT / 2, z1: zz + wallT / 2 });
      }
    }

    // ceiling light coves
    for (const sx of [-1, 0, 1]) {
      const cove = boxMesh(2.4, 0.12, g.depth * 0.8, materials.light);
      cove.position.set(sx * 3.6, galleryH - 0.14, z);
      scene.add(cove);
    }

    // baseboard trim
    for (const sx of [-1, 1]) {
      const t = boxMesh(0.08, 0.14, g.depth + 0.8, trimMat);
      t.position.set(sx * (galleryW / 2), 0.07, z);
      scene.add(t);
    }
  }

  // corridors between galleries
  for (let i = 0; i < GALLERIES.length - 1; i++) {
    const z0 = GALLERIES[i].z0 + GALLERIES[i].depth;
    const zc = -(z0 + gap / 2);
    const floor = boxMesh(corridorW + 0.8, 0.1, gap + 0.4, floorMat);
    floor.position.set(0, FLOOR_Y - 0.05, zc);
    scene.add(floor);
    const ceil = boxMesh(corridorW + 0.8, 0.2, gap + 0.4, materials.ceiling);
    ceil.position.set(0, 3.5, zc);
    scene.add(ceil);
    for (const sx of [-1, 1]) {
      const w = boxMesh(0.4, 3.5, gap + 0.4, wallMat);
      w.position.set(sx * (corridorW / 2 + 0.2), 1.75, zc);
      scene.add(w);
      collide.push({ x0: w.position.x - 0.2, x1: w.position.x + 0.2, z0: zc - gap / 2, z1: zc + gap / 2 });
    }
    const light = boxMesh(1.6, 0.1, gap * 0.6, materials.light);
    light.position.set(0, 3.4, zc);
    scene.add(light);
  }

  return collide;
}

function addLighting(scene) {
  scene.add(new THREE.HemisphereLight(0xfff6e8, 0x2a2118, 0.55));

  for (const g of GALLERIES) {
    const z = -(g.z0 + g.depth / 2);
    for (const sx of [-1, 0, 1]) {
      const p = new THREE.PointLight(0xffe9c9, 26, 16, 2);
      p.position.set(sx * 3.6, MUSEUM.galleryH - 0.5, z);
      scene.add(p);
    }
    // accent light on each wall
  }
  for (let i = 0; i < GALLERIES.length - 1; i++) {
    const z0 = GALLERIES[i].z0 + GALLERIES[i].depth;
    const zc = -(z0 + MUSEUM.gap / 2);
    const p = new THREE.PointLight(0xffe9c9, 14, 12, 2);
    p.position.set(0, 3.0, zc);
    scene.add(p);
  }
}

export async function initMuseum({ renderer, scene, camera, data, hud }) {
  const textures = await loadTextures();
  const materials = {
    wall: new THREE.MeshStandardMaterial({
      color: textures.wall ? 0xffffff : 0xded6c8,
      map: textures.wall,
      roughness: 0.95,
      metalness: 0,
    }),
    ceiling: new THREE.MeshStandardMaterial({ color: 0xe8e2d6, roughness: 1 }),
    trim: new THREE.MeshStandardMaterial({ color: 0x2b2724, roughness: 0.6, metalness: 0.2 }),
    floor: new THREE.MeshStandardMaterial({
      color: textures.floor ? 0xffffff : 0x8a6440,
      map: textures.floor,
      roughness: 0.55,
      metalness: 0.05,
    }),
    light: new THREE.MeshStandardMaterial({ color: 0xfff6e3, emissive: 0xfff0d0, emissiveIntensity: 1.4 }),
    frame: makeChromeFrame(),
  };

  const colliders = buildArchitecture(scene, materials);
  addLighting(scene);

  // assign each work a wall spot inside its gallery (walls alternate, date order kept)
  const rooms = splitWorks(data.works);
  const entries = [];
  GALLERIES.forEach((g, roomIndex) => {
    const list = rooms[roomIndex] || [];
    if (!list.length) return;
    const z = -(g.z0 + g.depth / 2);
    const span = g.depth - 7;
    const walls = [[], []];            // [left wall, right wall]
    list.forEach((work, i) => walls[i % 2].push(work));
    const spots = [];
    walls.forEach((wallWorks, w) => {
      const side = w === 0 ? -1 : 1;
      const gap = wallWorks.length > 1 ? Math.min(5.4, span / (wallWorks.length - 1)) : 0;
      wallWorks.forEach((work, i) => {
        const along = (i - (wallWorks.length - 1) / 2) * gap;
        spots.push({
          workIndex: data.works.indexOf(work),
          pos: new THREE.Vector3(side * MUSEUM.galleryW / 2, 2.5, z + along),
          rotY: side < 0 ? Math.PI / 2 : -Math.PI / 2,
        });
      });
    });
    entries.push({ gallery: g, spots });
  });

  const panels = makePanels(entries, data, textures, hud);
  panels.group.traverse((o) => { o.userData.panel = true; });
  scene.add(panels.group);

  // gallery title labels over each doorway
  for (const g of GALLERIES) {
    const z = -(g.z0 + 0.35);
    const label = makeLabel(`${data.title} · Room ${g.id + 1}`, hud);
    label.position.set(0, MUSEUM.galleryH - 0.55, z);
    label.rotation.y = Math.PI;
    scene.add(label);
  }

  return { colliders, panels };
}
