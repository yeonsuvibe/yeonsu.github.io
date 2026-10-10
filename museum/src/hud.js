/**
 * Heads-up display: intro overlay, crosshair + work name, visit ticks,
 * and the holding-pattern note that appears at the end of the run.
 */
export function makeHud() {
  const el = (id) => document.getElementById(id);
  const hud = {
    intro: el('intro'),
    startBtn: el('startBtn'),
    hint: el('hint'),
    crosshair: el('crosshair'),
    focus: el('focus'),
    ticks: el('ticks'),
    endNote: el('endNote'),
    loader: el('loader'),
    loaderBar: el('loaderBar'),
    total: 0,
    seen: new Set(),
  };

  hud.setTotal = (n) => {
    hud.total = n;
    hud.ticks.innerHTML = '';
    for (let i = 0; i < n; i++) {
      const d = document.createElement('i');
      d.className = 'tick';
      hud.ticks.appendChild(d);
    }
  };

  hud.markSeen = (work) => {
    if (!work || hud.seen.has(work.no)) return;
    hud.seen.add(work.no);
    const idx = [...hud.ticks.children].find((c, i) => {
      return !c.classList.contains('on') && [...hud.ticks.children].filter((x) => x.classList.contains('on')).length === hud.seen.size - 1;
    });
    const tick = hud.ticks.children[[...hud.seen].length - 1];
    if (tick) tick.classList.add('on');
    if (hud.seen.size === hud.total && hud.endNote) hud.endNote.classList.add('show');
    void idx;
  };

  hud.setFocus = (work, progress) => {
    if (!work) {
      hud.focus.classList.remove('show');
      hud.ticks.classList.remove('show');
      hud.hint.classList.remove('hide');
      return;
    }
    hud.focus.classList.add('show');
    hud.hint.classList.add('hide');
    hud.focus.innerHTML = `<b>No. ${work.no}</b><span>${work.date}</span>`;
  };

  hud.loading = (ratio) => {
    if (hud.loaderBar) hud.loaderBar.style.width = `${Math.round(ratio * 100)}%`;
  };
  hud.ready = () => hud.loader.classList.add('done');
  return hud;
}
