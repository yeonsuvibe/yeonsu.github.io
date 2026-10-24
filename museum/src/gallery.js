import * as THREE from '../vendor/three.module.min.js';

/* ---------------------------------------------------------------
   The eleven works, hung in one row on the art wall (+X), in date
   order.  The row runs towards +Z, which is the visitor's right
   hand: pressing "next" slides the camera right along the wall.
   --------------------------------------------------------------- */

export const GALLERY = {
  workHeight: 1.45,     // centre of every work above the floor (= the viewing height)
  z0: 1.35,             // first work
  step: 1.7,            // nominal spacing along the wall
  maxW: 1.5,
  maxH: 1.15,
  minGap: 1.2,          // clear wall between neighbouring frames
  wallX: 2.6,           // the plane the works hang on
};

/* Z of every work, spaced from the real widths so nothing ever touches. */
let layout = [];
export function setLayout(sizes) {
  const z = [GALLERY.z0];
  for (let i = 1; i < sizes.length; i++) {
    const gap = Math.max(GALLERY.step, sizes[i - 1].w / 2 + sizes[i].w / 2 + GALLERY.minGap);
    z.push(z[i - 1] + gap);
  }
  layout = z;
}
/** Z of work i — follows the laid-out widths, or the nominal step before layout. */
export function workZ(i) {
  return layout[i] ?? (GALLERY.z0 + i * GALLERY.step);
}
export function hallEnds(count) {
  return { zNear: workZ(0) - 2.7, zFar: workZ(count - 1) + 2.7 };
}

export function makePanels(data, extra, hud) {
  const group = new THREE.Group();
  group.name = 'panels';
  const loader = new THREE.TextureLoader();
  const holders = [];

  const sizes = data.works.map((work) => measure(work.file));
  setLayout(sizes);          // must run before the holders are placed

  data.works.forEach((work, i) => {
    const t = loader.load(work.file);
    t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = 8;

    const size = sizes[i];
    const holder = new THREE.Group();
    holder.name = `work-${work.no}`;
    holder.position.set(GALLERY.wallX, GALLERY.workHeight, workZ(i));
    holder.rotation.y = -Math.PI / 2;           // face -X, into the room

    /* The moulding is four bars, not one slab: the artwork has to sit in
       a real opening, recessed a little behind the lip. That recess is
       the whole point — it lets the lip drop a shadow on the sheet and
       catch a highlight on its own edge, which a flat rectangle never
       can. Depth 0.075, 12 triangles a bar. */
    const fw = 0.1;          // width of the moulding face
    const fd = 0.075;        // how far the moulding stands off the wall
    const frameMat = new THREE.MeshStandardMaterial({
      color: 0x121212, roughness: 0.42, metalness: 0.08, envMapIntensity: 1.25,
    });

    const back = new THREE.Mesh(
      new THREE.BoxGeometry(size.w + fw * 2, size.h + fw * 2, 0.03), frameMat);
    back.position.z = 0.015;
    back.receiveShadow = true;

    const bar = (w, h, x, y) => {
      const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, fd), frameMat);
      m.position.set(x, y, fd / 2);
      m.castShadow = true;
      m.receiveShadow = true;
      return m;
    };
    const hw = size.w / 2, hh = size.h / 2;
    const bars = [
      bar(size.w + fw * 2, fw, 0, hh + fw / 2),      // top
      bar(size.w + fw * 2, fw, 0, -hh - fw / 2),     // bottom
      bar(fw, size.h, -hw - fw / 2, 0),              // left
      bar(fw, size.h, hw + fw / 2, 0),               // right
    ];

    // a hairline white liner, so the sheet sits on light not on black
    const liner = new THREE.Mesh(
      new THREE.PlaneGeometry(size.w + 0.02, size.h + 0.02),
      new THREE.MeshStandardMaterial({ color: 0xfbfbfb, roughness: 0.92, envMapIntensity: 0.8 }),
    );
    liner.position.z = 0.040;
    liner.receiveShadow = true;

    const art = new THREE.Mesh(
      new THREE.PlaneGeometry(size.w, size.h),
      /* Paper under glass: stays matte, and takes only a little of the
         environment so the work keeps its own colour. */
      new THREE.MeshStandardMaterial({
        map: t, roughness: 0.78, metalness: 0, envMapIntensity: 0.55,
        polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1,
      }),
    );
    art.position.z = 0.042;      // recessed 0.033 behind the moulding lip
    art.userData.work = work;
    art.receiveShadow = true;

    holder.add(back, ...bars, liner, art);
    holder.userData.work = work;
    holder.userData.isPanel = true;
    holder.userData.size = size;
    group.add(holder);
    holders.push(holder);
  });

  hud?.setTotal(holders.length);
  void extra; // (tex no longer used by the panels)
  return { group, holders };
}

/** Equal visual mass: same area, capped by the wall slot. */
function fit(iw, ih) {
  const aspect = iw / ih;
  let w = Math.min(GALLERY.maxW, Math.sqrt(1.5 * aspect));
  let h = w / aspect;
  if (h > GALLERY.maxH) { h = GALLERY.maxH; w = h * aspect; }
  return { w, h, aspect };
}

/** Size of a work from the aspect ratio recorded in art.json. */
function measure(file) {
  const entry = ASPECTS[file.split('/').pop()];
  const [iw, ih] = entry || [4, 3];
  return fit(iw, ih);
}

/* Aspect ratios of the web-sized copies in art/. Regenerate the web
   copies with tools/resize-art.sh whenever the originals change. */
const ASPECTS = {
  '04344F03-ED69-4122-B452-149E29714822.jpg': [1600, 1600],
  '20181208_164140.jpg': [1600, 1200],
  '1565617423567.jpg': [1600, 738],
  'IMG_0649.jpg': [1600, 1200],
  'IMG_0101.jpg': [1600, 1176],
  'IMG_1206.jpg': [1600, 1200],
  'IMG_4371.jpg': [1600, 1200],
  'IMG_5319.jpg': [1600, 739],
  'IMG_5885.jpg': [1600, 1200],
  'IMG_8140.jpg': [1600, 1200],
  'IMG_7061.jpg': [1600, 1200],
};
