import * as THREE from '../vendor/three.module.min.js';

const EYE = 1.62;
const RADIUS = 0.52;

/** First-person walker with AABB sliding collision against the gallery walls. */
export function makeWalker(camera, colliders) {
  const pos = new THREE.Vector3(0, EYE, 6);
  camera.position.copy(pos);

  const fwd = new THREE.Vector3();
  const right = new THREE.Vector3();
  const move = new THREE.Vector3();
  const joystick = { x: 0, y: 0 };

  function resolve(p) {
    for (const c of colliders) {
      const nx = Math.max(c.x0, Math.min(p.x, c.x1));
      const nz = Math.max(c.z0, Math.min(p.z, c.z1));
      const dx = p.x - nx;
      const dz = p.z - nz;
      const d2 = dx * dx + dz * dz;
      if (d2 < RADIUS * RADIUS) {
        if (d2 > 1e-6) {
          const d = Math.sqrt(d2);
          p.x = nx + (dx / d) * RADIUS;
          p.z = nz + (dz / d) * RADIUS;
        } else {
          // inside the box: push out along the smallest axis
          const l = p.x - c.x0, r = c.x1 - p.x, b = p.z - c.z0, f = c.z1 - p.z;
          const m = Math.min(l, r, b, f);
          if (m === l) p.x = c.x0 - RADIUS;
          else if (m === r) p.x = c.x1 + RADIUS;
          else if (m === b) p.z = c.z0 - RADIUS;
          else p.z = c.z1 + RADIUS;
        }
      }
    }
  }

  return {
    joystick,
    pos,
    teleport(x, z) { pos.x = x; pos.z = z; pos.y = EYE; camera.position.copy(pos); },
    get position() { return camera.position; },
    update(dt, keys, speedMul = 1, smooth = 0) {
      camera.getWorldDirection(fwd);
      fwd.y = 0;
      fwd.normalize();
      right.crossVectors(fwd, camera.up).normalize();

      move.set(0, 0, 0);
      if (keys.forward) move.add(fwd);
      if (keys.back) move.sub(fwd);
      if (keys.right) move.add(right);
      if (keys.left) move.sub(right);
      // analog joystick / drag-walk
      move.addScaledVector(fwd, -joystick.y);
      move.addScaledVector(right, joystick.x);

      if (move.lengthSq() > 0) {
        move.normalize().multiplyScalar(3.1 * speedMul * dt);
        pos.x += move.x;
        pos.z += move.z;
        resolve(pos);
      }
      // smooth vertical step toward eye height (no jumping, museum floor is flat)
      pos.y += (EYE - pos.y) * (1 - Math.exp(-dt * 6));
      camera.position.copy(pos);
    },
  };
}
