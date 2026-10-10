/**
 * Heads-up display: intro overlay, loader, work counter, caption card,
 * visit ticks and the closing note of the guided tour.
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

  /** Show the current work and mark every work up to it as visited. */
  hud.setIndex = (i, work) => {
    hud.counter.textContent = `${String(i + 1).padStart(2, '0')} / ${String(hud.total).padStart(2, '0')}`;
    if (work) {
      hud.captionNo.textContent = `No. ${work.no}`;
      hud.captionDate.textContent = work.date;
    }
    [...hud.ticks.children].forEach((t, k) => t.classList.toggle('on', k <= i));
  };

  hud.setEnd = (show) => hud.endNote.classList.toggle('show', !!show);

  hud.loading = (ratio) => {
    if (hud.loaderBar) hud.loaderBar.style.width = `${Math.round(ratio * 100)}%`;
  };
  hud.ready = () => hud.loader.classList.add('done');
  return hud;
}
