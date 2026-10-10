import * as THREE from '../vendor/three.module.min.js';
import { GALLERY, workZ } from './museum.js';

const FOCAL = (48 * Math.PI) / 180;    // the nominal lens of the tour camera
const EYE = 1.45;                      // fixed viewing height (= work centre height)
const ZOOM_MIN = 0.88;                 // a little closer than the framed view
const ZOOM_MAX = 1.45;                 // a little further back
const MIN_T = 0.65;
const MAX_T = 2.1;
const SPEED = 3.6;                     // metres per second along the wall

/**
 * Camera on a rail parallel to the art wall.
 *
 *  - position: (wallX - dist, EYE, workZ(i)). The view axis is always the
 *    wall normal, so the work in hand sits dead centre.
 *  - next/prev: the camera slides along +Z / -Z only. +Z is the visitor's
 *    right, so "next" always reads as moving right along the wall.
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

  sizeOf(holder) {
    return holder?.userData?.size || { w: 1.5, h: 1.1 };
  }

  /**
   * Distance at which the work in hand is framed. The height always fits;
   * on narrow screens the width may crop a little rather than walking the
   * camera through the opposite wall.
   */
  get fitDist() {
    const s = this.sizeOf(this.targets[this.index]);
    const tanV = Math.tan(FOCAL / 2);
    const tanH = Math.max(tanV * this.camera.aspect, tanV * 0.62);
    const dH = (s.h / 2 + 0.62) / tanV;   // leave the hall visible around the work
    const dW = (s.w / 2 + 0.42) / tanH;
    return Math.max(dH, dW);
  }

  /** Live distance to the art plane: the wheel moves this only. */
  get dist() {
    const d = Math.max(0.9, this.fitDist * this.zoom);
    return Math.min(d, GALLERY.wallX + 2.0);   // never through the far wall
  }

  /** 0..1 — how much of the frame the work fills (weights the caption). */
  framing(holder) {
    const s = this.sizeOf(holder);
    return Math.min(1, s.h / (2 * this.dist * Math.tan(FOCAL / 2)));
  }

  goTo(i, { instant = false } = {}) {
    const idx = Math.max(0, Math.min(this.targets.length - 1, i));
    if (idx === this.index) return;
    if (this.index < 0 || instant) {
      this.index = idx;
      this.camera.position.set(GALLERY.wallX - this.dist, EYE, workZ(idx));
      this.camera.rotation.set(0, -Math.PI / 2, 0);
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
      const k = 1 - Math.exp(-dt * 9);
      this.camera.position.x += (want - this.camera.position.x) * k;
      this.camera.position.y += (EYE - this.camera.position.y) * k;
      this.camera.position.z = workZ(this.index);
    }
    // the view axis never leaves the wall normal
    this.camera.rotation.set(0, -Math.PI / 2, 0);
    this.camera.updateMatrixWorld();
  }
}
