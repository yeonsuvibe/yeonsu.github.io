import * as THREE from '../vendor/three.module.min.js';

/**
 * Minimal pointer-lock FPS controls (three.js PointerLockControls pattern),
 * with an added step-based move API used by the museum walker.
 */
export class PointerLockControls extends THREE.EventDispatcher {
  constructor(camera, domElement) {
    super();
    this.camera = camera;
    this.domElement = domElement;
    this.isLocked = false;
    this.minPolarAngle = 0;
    this.maxPolarAngle = Math.PI;

    this._euler = new THREE.Euler(0, 0, 0, 'YXZ');
    this._PI_2 = Math.PI / 2;
    this._pointerSpeed = 1.0;
    this._onMouseMove = this._onMouseMove.bind(this);
    this._onPointerlockChange = this._onPointerlockChange.bind(this);
    this._onPointerlockError = this._onPointerlockError.bind(this);

    this.domElement.ownerDocument.addEventListener('mousemove', this._onMouseMove);
    this.domElement.ownerDocument.addEventListener('pointerlockchange', this._onPointerlockChange);
    this.domElement.ownerDocument.addEventListener('pointerlockerror', this._onPointerlockError);
  }

  _onMouseMove(event) {
    if (!this.isLocked) return;
    const movementX = event.movementX || 0;
    const movementY = event.movementY || 0;
    this._euler.setFromQuaternion(this.camera.quaternion);
    this._euler.y -= movementX * 0.002 * this._pointerSpeed;
    this._euler.x -= movementY * 0.002 * this._pointerSpeed;
    this._euler.x = Math.max(this._PI_2 - this.maxPolarAngle, Math.min(this._PI_2 - this.minPolarAngle, this._euler.x));
    this.camera.quaternion.setFromEuler(this._euler);
    this.dispatchEvent({ type: 'change' });
  }

  _onPointerlockChange() {
    const locked = this.domElement.ownerDocument.pointerLockElement === this.domElement;
    if (this.isLocked && !locked) this.dispatchEvent({ type: 'unlock' });
    else if (!this.isLocked && locked) this.dispatchEvent({ type: 'lock' });
    this.isLocked = locked;
  }

  _onPointerlockError() {
    this.dispatchEvent({ type: 'error' });
  }

  lock() { this.domElement.requestPointerLock(); }
  unlock() { this.domElement.ownerDocument.exitPointerLock(); }

  dispose() {
    this.domElement.ownerDocument.removeEventListener('mousemove', this._onMouseMove);
    this.domElement.ownerDocument.removeEventListener('pointerlockchange', this._onPointerlockChange);
    this.domElement.ownerDocument.removeEventListener('pointerlockerror', this._onPointerlockError);
  }
}
