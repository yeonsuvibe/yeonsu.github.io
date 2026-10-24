import * as THREE from '../vendor/three.module.min.js';

/* ---------------------------------------------------------------
   Light, as a real white hall has it.

   Everything here exists for one reason: a surface must be able to
   tell where it is in the room. Three things do that, in order of
   how much of the realism they carry:

     1. an environment map  — the room's own brightness arriving from
        every direction. This is what makes a white wall read as white
        instead of flat, because the top of the wall sees the bright
        lantern and the bottom sees the darker floor.
     2. baked falloff       — a gradient multiplied into the wall and
        floor colour, so the floor darkens towards the skirting and
        the wall darkens towards the floor. Free: no extra shader.
     3. real shadows        — one directional light casts them; the
        point lights stay shadowless so the cost stays flat.

   Nothing here is per-frame work: the env map and the baked textures
   are built once at load and then just sampled.
   --------------------------------------------------------------- */

/** Vertical gradient of the room's light, wrapped as an equirect. */
function hallEquirect() {
  const c = document.createElement('canvas');
  c.width = 256; c.height = 128;
  const g = c.getContext('2d');

  // zenith → horizon → floor. The lantern well over the middle of the
  // hall is the brightest thing we have, so the top is nearly white.
  const grad = g.createLinearGradient(0, 0, 0, 128);
  grad.addColorStop(0.00, '#ffffff');
  grad.addColorStop(0.22, '#fbfbfa');
  grad.addColorStop(0.50, '#e4e4e2');
  grad.addColorStop(0.74, '#b6b4b0');
  grad.addColorStop(1.00, '#8d8b87');
  g.fillStyle = grad;
  g.fillRect(0, 0, 256, 128);

  // the glazed well: a soft bright band across the top, centre-weighted
  const well = g.createRadialGradient(128, 8, 2, 128, 8, 96);
  well.addColorStop(0, 'rgba(255,255,255,1)');
  well.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = well;
  g.fillRect(0, 0, 256, 60);

  const t = new THREE.CanvasTexture(c);
  t.mapping = THREE.EquirectangularReflectionMapping;
  t.colorSpace = THREE.SRGBColorSpace;
  t.needsUpdate = true;
  return t;
}

/** Build the PMREM environment once and hang it on the scene. */
export function installEnvironment(renderer, scene, intensity = 1) {
  const pmrem = new THREE.PMREMGenerator(renderer);
  pmrem.compileEquirectangularShader();
  const equirect = hallEquirect();
  const env = pmrem.fromEquirectangular(equirect).texture;
  scene.environment = env;
  scene.environmentIntensity = intensity;
  equirect.dispose();
  pmrem.dispose();
  return env;
}

/** Wall: a whisper of falloff towards the floor, plus a hair of grain. */
export function wallFalloffTexture() {
  const c = document.createElement('canvas');
  c.width = 16; c.height = 256;
  const g = c.getContext('2d');
  const grad = g.createLinearGradient(0, 0, 0, 256);
  grad.addColorStop(0.00, '#ffffff');   // at the ceiling
  grad.addColorStop(0.45, '#fbfbfb');
  grad.addColorStop(0.82, '#efefee');
  grad.addColorStop(1.00, '#e2e2e0');   // at the skirting
  g.fillStyle = grad;
  g.fillRect(0, 0, 16, 256);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
  return t;
}

/** Floor stone: fine, deterministic mottling that tiles, so a 24 m
    plate keeps its grain instead of being smeared across one box UV. */
export function floorStoneTexture() {
  const S = 512;
  const c = document.createElement('canvas');
  c.width = S; c.height = S;
  const g = c.getContext('2d');
  g.fillStyle = '#f2f2f1';
  g.fillRect(0, 0, S, S);

  let seed = 1337;
  const rnd = () => (seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296;
  for (let i = 0; i < 2600; i++) {
    const x = rnd() * S, y = rnd() * S, r = 0.7 + rnd() * 3.1;
    const v = 226 + Math.floor(rnd() * 24);
    g.fillStyle = `rgba(${v},${v},${v - 2},${0.05 + rnd() * 0.17})`;
    g.beginPath();
    g.arc(x, y, r, 0, Math.PI * 2);
    g.fill();
  }
  // a few hairline veins, the way a honed stone reads up close
  g.strokeStyle = 'rgba(196,195,192,0.22)';
  g.lineWidth = 1;
  for (let i = 0; i < 26; i++) {
    g.beginPath();
    const x = rnd() * S, y = rnd() * S;
    g.moveTo(x, y);
    g.lineTo(x + (rnd() - 0.5) * 150, y + (rnd() - 0.5) * 150);
    g.stroke();
  }

  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.anisotropy = 8;
  return t;
}

/** Where the floor meets a wall it goes quiet. One overlay plane does it. */
export function floorEdgeTexture() {
  const S = 256;
  const c = document.createElement('canvas');
  c.width = S; c.height = S;
  const g = c.getContext('2d');
  g.clearRect(0, 0, S, S);

  const edge = 34;
  const bands = [
    [0, 0, edge, S, true], [S - edge, 0, edge, S, true],
    [0, 0, S, edge, false], [0, S - edge, S, edge, false],
  ];
  for (const [x, y, w, h, vert] of bands) {
    const from = vert ? (x === 0 ? x : x + w) : (y === 0 ? y : y + h);
    const to = vert ? (x === 0 ? x + w : x) : (y === 0 ? y + h : y);
    const lg = vert
      ? g.createLinearGradient(from, y, to, y)
      : g.createLinearGradient(x, from, x, to);
    lg.addColorStop(0, 'rgba(96,95,92,0.42)');
    lg.addColorStop(0.5, 'rgba(140,139,136,0.14)');
    lg.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = lg;
    g.fillRect(x, y, w, h);
  }

  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
  return t;
}

/**
 * Stand-in for a doorway's light. Not a lamp object: a single cheap
 * directional light that carries the only shadow map in the scene.
 */
export function installLights(scene, { zNear, zFar, height }) {
  const group = new THREE.Group();
  group.name = 'lighting';

  // the lantern well: the one light that defines the room, and the only
  // one allowed to cast. Straight down, so shadows sit under the frames.
  const key = new THREE.DirectionalLight(0xffffff, 1.55);
  key.position.set(0, height + 3.2, (zNear + zFar) / 2);
  key.target.position.set(0, 0, (zNear + zFar) / 2);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  key.shadow.radius = 3;
  key.shadow.bias = -0.0006;
  key.shadow.normalBias = 0.018;

  const s = key.shadow.camera;
  const halfL = (zFar - zNear) / 2 + 2.5;
  s.left = -6; s.right = 6;
  s.top = halfL; s.bottom = -halfL;
  s.near = 0.5; s.far = 16;
  s.updateProjectionMatrix();

  group.add(key, key.target);

  /* Soft fill down the length of the hall. Intensity is low on purpose:
     the environment already carries most of the brightness, and these
     are here only to keep the far end from going dead. */
  for (let z = zNear + 1.4; z < zFar; z += 6.2) {
    const l = new THREE.PointLight(0xffffff, 3.4, 22, 2);
    l.position.set(0, height - 0.5, z);
    group.add(l);
  }

  scene.add(group);
  return group;
}
