/**
 * Heads-up display: loader, intro, work counter, caption card, visit
 * ticks and the closing note of the wall tour.
 */
export function makeHud() {
  const el = (id) => document.getElementById(id);
  const hud = {
    intro: el('intro'),
    startBtn: el('startBtn'),
    hint: el('hint'),
    ticks: el('ticks'),
    counter: el('counter'),
    caption: el('caption'),
    captionNo: el('captionNo'),
    captionDate: el('captionDate'),
    captionText: el('captionText'),
    panelLight: el('panelLight'),
    endNote: el('endNote'),
    loader: el('loader'),
    loaderBar: el('loaderBar'),
    total: 0,
  };

  hud.setTotal = (n) => {
    hud.total = n;
    hud.ticks.innerHTML = '';
    for (let i = 0; i < n; i++) {
      const t = document.createElement('i');
      t.className = 'tick';
      hud.ticks.appendChild(t);
    }
    hud.counter.textContent = `01 / ${String(n).padStart(2, '0')}`;
  };

  /** Show the current work and mark every work up to it as seen. */
  hud.setIndex = (i, work) => {
    hud.counter.textContent = `${String(i + 1).padStart(2, '0')} / ${String(hud.total).padStart(2, '0')}`;
    if (work) {
      hud.captionNo.textContent = `No. ${work.no}`;
      hud.captionDate.textContent = work.date;
    }
    [...hud.ticks.children].forEach((t, k) => t.classList.toggle('on', k <= i));
    if (hud.panelLight) {
      const x = hud.total > 1 ? (i / (hud.total - 1)) : 0.5;
      const span = hud.panelLight.clientWidth - 26;
      hud.panelLight.style.setProperty('--px', `${x * span}px`);
    }
  };

  hud.setMoving = (moving) => hud.caption.classList.toggle('moving', !!moving);

  /** How much of the frame the work fills (0..1) — drives the caption weight. */
  hud.setFraming = (ratio) => {
    const r = Number.isFinite(ratio) ? ratio : 0.5;
    hud.caption.style.opacity = String(0.55 + 0.45 * Math.min(1, r));
  };

  hud.setEnd = (show) => hud.endNote.classList.toggle('show', !!show);

  hud.loading = (ratio) => {
    if (hud.loaderBar) hud.loaderBar.style.width = `${Math.round(ratio * 100)}%`;
  };
  hud.ready = () => hud.loader.classList.add('done');
  return hud;
}
