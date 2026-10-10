import * as THREE from './vendor/three.module.min.js';
import { PointerLockControls } from './src/PointerLockControls.js';
import { initMuseum, GALLERIES } from './src/museum.js';
import { makeHud } from './src/hud.js';
import { makeWalker } from './src/walker.js';

const canvas = document.querySelector('canvas.webgl');
const hud = makeHud();

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0b0a09);
scene.fog = new THREE.Fog(0x0b0a09, 18, 52);

const camera = new THREE.PerspectiveCamera(72, innerWidth / innerHeight, 0.05, 200);

const data = await fetch('art.json').then((r) => r.json());

hud.loading(0.25);
const { colliders, panels } = await initMuseum({ renderer, scene, camera, data, hud });
// plaques and lamps must not block the crosshair ray
panels.group.traverse((o) => { if (o.userData && o.userData.isPanel) o.layers.set(1); });
hud.setTotal(data.works.length);
hud.loading(1);
// hide the loader once the first frame is on screen
requestAnimationFrame(() => requestAnimationFrame(() => hud.ready()));

const controls = new PointerLockControls(camera, canvas);
controls.minPolarAngle = 0.15;
controls.maxPolarAngle = Math.PI - 0.15;
const walker = makeWalker(camera, colliders);

/* ---------------- interaction ---------------- */

const keys = { forward: false, back: false, left: false, right: false };
const raycaster = new THREE.Raycaster();
raycaster.far = 12;
const screenCenter = new THREE.Vector2(0, 0);
let hovered = null;

addEventListener('keydown', (e) => {
  switch (e.code) {
    case 'KeyW': case 'ArrowUp': keys.forward = true; break;
    case 'KeyS': case 'ArrowDown': keys.back = true; break;
    case 'KeyA': case 'ArrowLeft': keys.left = true; break;
    case 'KeyD': case 'ArrowRight': keys.right = true; break;
    case 'Equal': case 'NumpadAdd': controls._pointerSpeed = Math.min(2.5, controls._pointerSpeed + 0.15); break;
    case 'Minus': case 'NumpadSubtract': controls._pointerSpeed = Math.max(0.3, controls._pointerSpeed - 0.15); break;
    default: return;
  }
});
addEventListener('keyup', (e) => {
  switch (e.code) {
    case 'KeyW': case 'ArrowUp': keys.forward = false; break;
    case 'KeyS': case 'ArrowDown': keys.back = false; break;
    case 'KeyA': case 'ArrowLeft': keys.left = false; break;
    case 'KeyD': case 'ArrowRight': keys.right = false; break;
  }
});

// drag / touch look + walk pad
const drag = { active: false, x: 0, y: 0, moved: false, touch: false };
canvas.addEventListener('pointerdown', (e) => {
  if (controls.isLocked) return;
  drag.active = true;
  drag.touch = e.pointerType === 'touch';
  drag.moved = false;
  drag.x = e.clientX;
  drag.y = e.clientY;
  canvas.setPointerCapture(e.pointerId);
});
canvas.addEventListener('pointermove', (e) => {
  if (!drag.active) return;
  const dx = e.clientX - drag.x;
  const dy = e.clientY - drag.y;
  drag.x = e.clientX;
  drag.y = e.clientY;
  if (Math.abs(dx) + Math.abs(dy) > 1) drag.moved = true;
  const euler = new THREE.Euler(0, 0, 0, 'YXZ');
  euler.setFromQuaternion(camera.quaternion);
  euler.y -= dx * 0.0032;
  euler.x -= dy * 0.0032;
  euler.x = Math.max(-Math.PI / 2 + 0.15, Math.min(Math.PI / 2 - 0.15, euler.x));
  camera.quaternion.setFromEuler(euler);
  if (drag.touch && Math.abs(dy) > 0) walker.joystick.y = Math.max(-1, Math.min(1, -dy / 40));
});
addEventListener('pointerup', () => {
  drag.active = false;
  walker.joystick.y = 0;
  walker.joystick.x = 0;
});

// clicking the canvas locks the pointer (desktop)
canvas.addEventListener('click', () => { if (!controls.isLocked) controls.lock(); });
document.getElementById('startBtn').addEventListener('click', (e) => {
  e.stopPropagation();
  hud.intro.classList.add('gone');
  if (matchMedia('(pointer: fine)').matches) controls.lock();
});

/* ---------------- loop ---------------- */

const clock = new THREE.Clock();
let uiTick = 0;

function animate() {
  const dt = Math.min(0.05, clock.getDelta());
  walker.update(dt, keys);

  raycaster.setFromCamera(screenCenter, camera);
  raycaster.layers.set(0);
  const hit = raycaster.intersectObjects(panels.hoverables, false)[0];
  const next = hit ? hit.object.userData.work : null;
  if (next !== hovered) {
    hovered = next;
    hud.setFocus(hovered);
    if (hovered) hud.markSeen(hovered);
  }

  // end-of-run notice when the visitor reaches the last gallery
  uiTick += dt;
  if (uiTick > 0.25) {
    uiTick = 0;
    const z = camera.position.z;
    const lastZ = -(GALLERIES[GALLERIES.length - 1].z0 + GALLERIES[GALLERIES.length - 1].depth);
    hud.endNote.classList.toggle('show', z < lastZ + 6);
  }

  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
animate();

// debug handle (used by the headless verification spike)
window.__museum = { camera, scene, walker, controls, panels, data, hud };

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

addEventListener('pointerlockchange', () => {
  hud.hint.classList.toggle('hide', controls.isLocked || !!hovered);
});
