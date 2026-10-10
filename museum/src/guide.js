import * as THREE from '../vendor/three.module.min.js';
import { GALLERY, workZ } from './museum.js';

const FOCAL = (48 * Math.PI) / 180;    // the nominal lens of the tour camera
const EYE = 1.45;                      // the camera never changes height (work centre height)
const ZOOM_MIN = 0.86;   // a little closer than the framed view
const ZOOM_MAX = 1.5;    // a little further back
const MIN_T = 0.7;
const MAX_T = 2.4;
const SPEED = 4.0;                     // metres per second along the wall

/**
 * Camera-on-rails along the art wall.
 *
 *  - position: (x, EYE, workZ(i)) — the view axis is always the -X wall
 *    normal, so every work is seen dead centre.
 *  - next/prev: the camera only slides along ±Z, along the wall. No turn.
 *  - wheel: fades the distance to the wall between ZOOM_MIN..ZOOM_MAX.
 */
export class WallTour {
  constructor({ camera, targets, hud }) {
    this.camera = camera;
    this.targets = targets;
    this.hud = hud;
    this.index = -1;
    this.zoom = 1;
    this.moving = null;
    this.onMoveStart = null;
    this.onArrive = null;
  }

  /** Horizontal or vertical half-angle tangent, whichever is tighter. */
  get effTan() {
    const aspect = this.camera.aspect || 1.6;
    return Math.tan(FOCAL / 2) * Math.min(1, aspect);
  }

  /**
   * Distance at which the current work is framed. The height always
   * fits; on narrow screens the width may crop a little rather than
   * pushing the camera through the opposite wall.
   */
  get fitDist() {
    const s = this.sizeOf(this.targets[this.index]) || { w: 1.5, h: 1.1 };
    const tanV = Math.tan(FOCAL / 2);
    const tanH = Math.max(tanV * (this.camera.aspect || 1.6), tanV * 0.62);
    const dH = (s.h / 2 + 0.18) / tanV;
    const dW = (s.w / 2 + 0.18) / tanH;
    return Math.min(3.0, Math.max(dH, dW));
  }

  /** Live distance to the art plane: the wheel moves this only. */
  get dist() {
    const d = Math.max(0.9, this.fitDist * this.zoom);
    // never cross the opposite wall (the hall stays readable)
    return Math.min(d, GALLERY.wallX + 2.2);
  }

  /** 0..1 — how much of the frame the work fills (used to weight the caption). */
  framing(holder) {
    const s = this.sizeOf(holder);
    return Math.min(1, s.h / (2 * this.dist * this.effTan));
  }

  sizeOf(holder) {
    return holder?.userData?.size || { w: 1.5, h: 1.1 };
  }

  goTo(i, { instant = false } = {}) {
    const idx = Math.max(0, Math.min(this.targets.length - 1, i));
    if (idx === this.index) return;
    if (this.index < 0 || instant) {
      this.index = idx;
      if (typeof idx === 'number' && this.targets[idx]) {
        this.camera.position.set(GALLERY.wallX - this.dist, EYE, workZ(idx));
        this.camera.rotation.set(0, -Math.PI / 2, 0);
      }
      this.arrive(idx);
      return;
    }
    const z0 = workZ(this.index);
    const z1 = workZ(idx);
    this.moving = {
      z0, z1, t: 0,
      total: THREE.MathUtils.clamp(Math.abs(z1 - z0) / SPEED, MIN_T, MAX_T),
      index: idx,
    };
    this.onMoveStart?.(idx);
  }

  next() { this.goTo(this.index + 1); }
  prev() { this.goTo(this.index - 1); }

  arrive(i) {
    this.index = i;
    const work = this.targets[i]?.userData?.work;
    this.hud?.setIndex(i, work);
    this.hud?.setEnd(i === this.targets.length - 1);
    this.onArrive?.(i, work);
  }

  /** Wheel zoom: only the distance to the wall changes. */
  zoomBy(delta) {
    const step = Math.sign(delta) * 0.045;
    this.zoom = THREE.MathUtils.clamp(this.zoom + step, ZOOM_MIN, ZOOM_MAX);
  }

  update(dt) {
    if (this.moving) {
      const m = this.moving;
      m.t = Math.min(1, m.t + dt / m.total);
      const e = m.t < 0.5 ? 4 * m.t * m.t * m.t : 1 - Math.pow(-2 * m.t + 2, 3) / 2;
      const z = m.z0 + (m.z1 - m.z0) * e;
      this.camera.position.set(GALLERY.wallX - this.dist, EYE, z);
      if (m.t >= 1) {
        this.arrive(m.index);
        this.moving = null;
      }
    } else if (this.index >= 0) {
      const want = GALLERY.wallX - this.dist;
      this.camera.position.x += (want - this.camera.position.x) * (1 - Math.exp(-dt * 9));
      this.camera.position.y += (EYE - this.camera.position.y) * (1 - Math.exp(-dt * 9));
      this.camera.position.z = workZ(this.index);
    }
    // the view axis never leaves the wall normal
    this.camera.rotation.set(0, -Math.PI / 2, 0);
    this.camera.updateMatrixWorld();
  }
}
