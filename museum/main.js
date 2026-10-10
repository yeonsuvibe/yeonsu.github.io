import * as THREE from './vendor/three.module.min.js';
import { initMuseum, GALLERY } from './src/museum.js';
import { makeHud } from './src/hud.js';
import { WallTour } from './src/guide.js';

/* ---------------------------------------------------------------
   Ahn Yeonsu — 3D Art Museum
   One continuous hall. The camera rides a rail parallel to the art
   wall; ← → slide it along the wall, so the view never turns away
   from a work. The wheel fades the distance slightly.
   --------------------------------------------------------------- */

const canvas = document.querySelector('canvas.webgl');
const hud = makeHud();

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.NoToneMapping;      // keep the works true to their own colour

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xefeae1);
scene.fog = new THREE.Fog(0xefeae1, 30, 62);

const camera = new THREE.PerspectiveCamera(56, innerWidth / innerHeight, 0.05, 200);

const data = await fetch('art.json').then((r) => r.json());

hud.loading(0.25);
const { panels } = await initMuseum({ scene, data, hud });
hud.loading(1);

const tour = new WallTour({ camera, targets: panels.holders, hud });
tour.onMoveStart = () => hud.setMoving(true);
tour.onArrive = (i, work) => {
  hud.setMoving(false);
  hud.setFraming(tour.framing(panels.holders[i]));
  hud.captionText.textContent = work ? 'original work · Art Portfolio 2018–2026' : '';
};
tour.goTo(0, { instant: true });

/* ---------------- input ---------------- */

addEventListener('keydown', (e) => {
  switch (e.code) {
    case 'ArrowRight': case 'KeyD': case 'Space': case 'PageDown': tour.next(); break;
    case 'ArrowLeft': case 'KeyA': case 'PageUp': tour.prev(); break;
    case 'Equal': case 'NumpadAdd': tour.zoomBy(-100); break;
    case 'Minus': case 'NumpadSubtract': tour.zoomBy(100); break;
    case 'Home': tour.goTo(0); break;
    case 'End': tour.goTo(panels.holders.length - 1); break;
    default: return;
  }
  e.preventDefault();
});

canvas.addEventListener('wheel', (e) => {
  e.preventDefault();
  tour.zoomBy(e.deltaY);
}, { passive: false });

// touch: swipe left/right to change work, pinch is left to the browser
let touchStart = null;
canvas.addEventListener('touchstart', (e) => {
  if (e.touches.length === 1) touchStart = { x: e.touches[0].clientX, y: e.touches[0].clientY };
});
canvas.addEventListener('touchend', (e) => {
  if (!touchStart || !e.changedTouches.length) return;
  const dx = e.changedTouches[0].clientX - touchStart.x;
  const dy = e.changedTouches[0].clientY - touchStart.y;
  if (Math.abs(dx) > 44 && Math.abs(dx) > Math.abs(dy)) (dx < 0 ? tour.next() : tour.prev());
  touchStart = null;
});

document.getElementById('prevBtn').addEventListener('click', (e) => { e.stopPropagation(); tour.prev(); });
document.getElementById('nextBtn').addEventListener('click', (e) => { e.stopPropagation(); tour.next(); });
document.getElementById('startBtn').addEventListener('click', (e) => {
  e.stopPropagation();
  hud.intro.classList.add('gone');
});

/* ---------------- loop ---------------- */

const clock = new THREE.Clock();
function animate() {
  const dt = Math.min(0.05, clock.getDelta());
  tour.update(dt);
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
window.__museum = { camera, scene, tour, panels, data, hud, GALLERY, THREE, raycaster: new THREE.Raycaster() };
