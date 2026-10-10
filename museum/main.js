import * as THREE from './vendor/three.module.min.js';
import { initMuseum } from './src/museum.js';
import { makeHud } from './src/hud.js';
import { TourGuide, collectTargets } from './src/guide.js';

/* ---------------------------------------------------------------
   Ahn Yeonsu — 3D Art Museum
   Guided tour: the visitor always stands in front of the current
   work; ← → (or A/D) move the view from piece to piece, work first.
   --------------------------------------------------------------- */

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
scene.fog = new THREE.Fog(0x0b0a09, 20, 58);

const camera = new THREE.PerspectiveCamera(72, innerWidth / innerHeight, 0.05, 200);

const data = await fetch('art.json').then((r) => r.json());

hud.loading(0.25);
const { panels } = await initMuseum({ renderer, scene, camera, data, hud });
hud.setTotal(data.works.length);
hud.loading(1);

const targets = collectTargets(panels.group, data.works);
const guide = new TourGuide({ camera, targets, hud });
guide.onMoveStart = () => { hud.captionText.textContent = 'walking to the next piece…'; };
guide.onArrive = (i, work) => { hud.captionText.textContent = work ? 'original work, Art Portfolio 2018–2026' : ''; };

guide.goTo(0, { instant: true });

/* ---------------- input ---------------- */

let dragging = false;
let last = { x: 0, y: 0 };
let moved = 0;

canvas.addEventListener('pointerdown', (e) => {
  dragging = true; moved = 0;
  last = { x: e.clientX, y: e.clientY };
  canvas.setPointerCapture(e.pointerId);
  canvas.classList.add('grabbing');
});
canvas.addEventListener('pointermove', (e) => {
  if (!dragging) return;
  const dx = e.clientX - last.x;
  const dy = e.clientY - last.y;
  last = { x: e.clientX, y: e.clientY };
  moved += Math.abs(dx) + Math.abs(dy);
  if (moved > 6) guide.look(dx, dy);
});
const endDrag = () => { dragging = false; canvas.classList.remove('grabbing'); };
canvas.addEventListener('pointerup', endDrag);
canvas.addEventListener('pointercancel', endDrag);

// click the canvas: advance, or look again after a look-away offset
canvas.addEventListener('click', () => {
  if (moved > 6) return;
  if (guide.offset.yaw || guide.offset.pitch) guide.goTo(guide.index, { instant: true });
  else guide.next();
});

addEventListener('keydown', (e) => {
  switch (e.code) {
    case 'ArrowRight': case 'KeyD': case 'PageDown': case 'Space': guide.next(); break;
    case 'ArrowLeft': case 'KeyA': case 'PageUp': guide.prev(); break;
    case 'Home': guide.goTo(0); break;
    case 'End': guide.goTo(targets.length - 1); break;
    default: return;
  }
  e.preventDefault();
});

document.getElementById('prevBtn').addEventListener('click', (e) => { e.stopPropagation(); guide.prev(); });
document.getElementById('nextBtn').addEventListener('click', (e) => { e.stopPropagation(); guide.next(); });
hud.caption.addEventListener('click', (e) => {
  e.stopPropagation();
  hud.caption.classList.toggle('open');
});
document.getElementById('startBtn').addEventListener('click', (e) => {
  e.stopPropagation();
  hud.intro.classList.add('gone');
});

/* ---------------- loop ---------------- */

const clock = new THREE.Clock();
function animate() {
  const dt = Math.min(0.05, clock.getDelta());
  guide.update(dt);
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
animate();

requestAnimationFrame(() => requestAnimationFrame(() => hud.ready()));

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

// handle used by the headless verification spike
window.__museum = { camera, scene, guide, panels, data, hud };
