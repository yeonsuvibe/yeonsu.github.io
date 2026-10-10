import * as THREE from '../vendor/three.module.min.js';
import { GALLERIES } from './museum.js';

const EYE = 1.75;
const VFOV = (72 * Math.PI) / 180;
const SPEED = 4.2;                 // metres per second along the tour path
const MIN_T = 0.85;
const MAX_T = 2.8;

/** Holders of the hanging works, ordered like data.works (date order). */
export function collectTargets(panelGroup, works) {
  const holders = [];
  panelGroup.traverse((o) => {
    if (o.userData && o.userData.isPanel && o.userData.work) holders.push(o);
  });
  const byNo = new Map(holders.map((h) => [h.userData.work.no, h]));
  return works.map((w) => byNo.get(w.no)).filter(Boolean);
}

/** Which gallery a world z belongs to (-1 for a corridor). */
function roomAtZ(z) {
  const world = -z;
  for (let i = 0; i < GALLERIES.length; i++) {
    const g = GALLERIES[i];
    if (world >= g.z0 && world <= g.z0 + g.depth) return i;
  }
  return -1;
}

function corridorZ(i) {
  const g = GALLERIES[i];
  return -(g.z0 + g.depth + (GALLERIES[i + 1].z0 - (g.z0 + g.depth)) / 2);
}

const easeInOut = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

/**
 * Camera-on-rails tour: stands each work in front of the visitor, in date
 * order, and moves between them along a safe path (through room centres).
 */
export class TourGuide {
  constructor({ camera, targets, hud }) {
    this.camera = camera;
    this.targets = targets;
    this.hud = hud;
    this.index = -1;
    this.mode = 'tour';
    this.moving = null;
    this.offset = { yaw: 0, pitch: 0 };   // free look applied on top of the pose
    this.aim = new THREE.Vector3();        // the point the camera looks at
    this._look = new THREE.Vector3();
    this._q = new THREE.Quaternion();
    this._m = new THREE.Matrix4();
    this._up = new THREE.Vector3(0, 1, 0);
    this.onArrive = null;
  }

  /** Where the visitor stands to see holder h. */
  poseFor(holder) {
    const size = holder.userData.size || { w: 2.4, h: 2.0 };
    const fit = (Math.max(size.w, size.h) / 2) / Math.tan(VFOV / 2);
    const dist = THREE.MathUtils.clamp(fit * 1.45 + 0.35, 2.0, 4.2);
    const n = new THREE.Vector3(Math.sin(holder.rotation.y), 0, Math.cos(holder.rotation.y));
    const pos = holder.position.clone().addScaledVector(n, dist);
    pos.y = EYE;
    const look = holder.position.clone();
    look.y -= 0.35;
    return { pos, look, normal: n, dist };
  }

  /** Waypoints that never cross a wall. */
  pathTo(from, to) {
    const a = from.pos, b = to.pos;
    const ra = roomAtZ(a.z);
    const rb = roomAtZ(b.z);
    const pts = [a.clone()];
    if (ra !== rb) {
      pts.push(new THREE.Vector3(0, EYE, a.z));
      const lo = Math.min(ra, rb);
      const hi = Math.max(ra, rb);
      for (let i = lo; i < hi; i++) pts.push(new THREE.Vector3(0, EYE, corridorZ(i)));
      pts.push(new THREE.Vector3(0, EYE, b.z));
    } else if (Math.abs(a.x - b.x) > 0.5) {
      pts.push(new THREE.Vector3(0, EYE, (a.z + b.z) / 2));
    }
    pts.push(b.clone());
    return pts;
  }

  goTo(index, { instant = false } = {}) {
    const i = Math.max(0, Math.min(this.targets.length - 1, index));
    if (i === this.index && !instant) return;
    const target = this.poseFor(this.targets[i]);
    if (this.index < 0 || instant) {
      this.index = i;
      this.offset.yaw = 0;
      this.offset.pitch = 0;
      this.camera.position.copy(target.pos);
      this.aim.copy(target.look);
      this.arrive(i);
      return;
    }
    const path = this.pathTo(this.poseFor(this.targets[this.index]), target);
    let len = 0;
    for (let k = 1; k < path.length; k++) len += path[k].distanceTo(path[k - 1]);
    this.moving = {
      path,
      len,
      total: THREE.MathUtils.clamp(len / SPEED, MIN_T, MAX_T),
      t: 0,
      index: i,
      look: target.look.clone(),
    };
    this.onMoveStart?.(i);
  }

  next() { this.goTo(this.index + 1); }
  prev() { this.goTo(this.index - 1); }

  arrive(i) {
    this.index = i;
    this.offset.yaw = 0;
    this.offset.pitch = 0;
    this.hud?.setIndex(i, this.targets[i]?.userData.work);
    if (i === this.targets.length - 1) this.hud?.setEnd(true);
    this.onArrive?.(i, this.targets[i]?.userData.work);
  }

  /** Drag-to-look, clamped, reset on the next move. */
  look(dx, dy) {
    this.offset.yaw = THREE.MathUtils.clamp(this.offset.yaw - dx * 0.0032, -0.55, 0.55);
    this.offset.pitch = THREE.MathUtils.clamp(this.offset.pitch - dy * 0.0032, -0.36, 0.36);
  }

  update(dt) {
    if (this.moving) {
      const m = this.moving;
      m.t = Math.min(1, m.t + dt / m.total);
      const e = easeInOut(m.t);
      const d = e * m.len;
      let acc = 0;
      let p = m.path[m.path.length - 1];
      for (let k = 1; k < m.path.length; k++) {
        const seg = m.path[k].distanceTo(m.path[k - 1]);
        if (d <= acc + seg) {
          const f = seg > 0 ? (d - acc) / seg : 0;
          p = m.path[k - 1].clone().lerp(m.path[k], f);
          break;
        }
        acc += seg;
      }
      this.camera.position.copy(p);
      this.aim.copy(m.look);
      if (m.t >= 1) {
        this.arrive(m.index);
        this.moving = null;
      }
    }
    // aim smoothly at the work, plus the visitor's look offset
    this._m.lookAt(this.camera.position, this.aim, this._up);
    this._q.setFromRotationMatrix(this._m);
    if (this.offset.yaw || this.offset.pitch) {
      const off = new THREE.Quaternion().setFromEuler(new THREE.Euler(this.offset.pitch, this.offset.yaw, 0, 'YXZ'));
      this._q.multiply(off);
    }
    const k = 1 - Math.exp(-dt * 5.5);
    this.camera.quaternion.slerp(this._q, this.moving ? k * 0.7 : k);

    if (!this.moving && this.targets[this.index]) {
      const want = this.poseFor(this.targets[this.index]).pos;
      this.camera.position.lerp(want, 1 - Math.exp(-dt * 3));
    }
  }
}
