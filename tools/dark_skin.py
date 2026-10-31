#!/usr/bin/env python3
"""Inject a dark skin into the black-box set's journeys/articles pages.

Why: set 02 is the dark gallery. Its east/back walls load journeys.html and
articles.html in an iframe. Those pages carry their own light palette, so the
wall shows up as a white sheet inside a near-black room (measured mean_lum 237
against the room's 64).

How: both pages colour everything through :root tokens in index.css plus a few
literal paper-tinted overlays. So we (1) append a token override block at the
end of the set's index.css, and (2) neutralise the light literals that are not
tokenised. No structural change, so the root files stay untouched.
"""
import os
import re

SET = '/Users/eungsikahn/Dev/yeonsu_profile/sets/02-black-box'

DARK_CSS = """

/* ============================================================
   Dark skin — this set IS the black box gallery.
   The room runs at ~#0d0c0a; the document wall must sit in that
   range instead of flashing a white sheet (was mean_lum 237 vs 64).
   Contrast on #12110e: ink 16.0:1, ink-soft 8.4:1, gilt 8.4:1.
   ============================================================ */
:root {
    --paper: #12110e;
    --paper-deep: #171612;
    --ink: #f0ece2;
    --ink-soft: #b3ac9e;
    --ink-faint: #7d776b;
    --rule: rgba(240, 236, 226, 0.20);
    --gilt: #c9a86a;
    color-scheme: dark;
}

html, body { background: var(--paper); color: var(--ink); }

/* The noise overlay draws with the browser default (black) — fine on dark. */

nav {
    background: transparent;
    border-bottom: 1px solid var(--rule);
}
nav a, nav li a { color: var(--ink); }
nav a:hover { color: var(--gilt); }
.logo a { color: var(--ink); }

::selection { background: var(--gilt); color: #12110e; }

/* Paper-tinted surfaces that would otherwise glow white */
.section,
.section.light,
.section.dark { background: transparent; }

blockquote {
    background: rgba(240, 236, 226, 0.045);
    border-left: 2px solid var(--gilt);
}

.timeline-overlay { background: rgba(18, 17, 14, 0.94); }

footer {
    background: transparent;
    border-top: 1px solid var(--rule);
    color: var(--ink-faint);
}
footer a { color: var(--ink-soft); }

figure, .card, .label, .pl { background: transparent; }

a { color: inherit; }
a:hover { color: var(--gilt); }

/* Museum labels keep the brass tone but must read on dark */
.museum-label, .caption, .meta, figcaption { color: var(--ink-soft); }

/* Anything that hard-codes the light paper tone */
[style*="background:#f4f1ea"],
[style*="background: #f4f1ea"] { background: var(--paper) !important; }
"""

# literals in the pages that bypass the tokens
REPLACEMENTS = [
    ('rgba(246,245,241,.9)', 'rgba(18,17,14,.9)'),
    ('rgba(246,245,241,.94)', 'rgba(18,17,14,.94)'),
    ('rgba(246,245,241,.95)', 'rgba(18,17,14,.95)'),
    ('rgba(244, 241, 234, 0.94)', 'rgba(18, 17, 14, 0.94)'),
    ('rgba(244, 241, 234, 0.9)', 'rgba(18, 17, 14, 0.9)'),
    ('#f4f1ea', '#12110e'),
    ('#f4f3ef', '#12110e'),
    ('#16150f', '#f0ece2'),
    ('#1a1815', '#f0ece2'),
    ('#14120f', '#f0ece2'),
    ('#8a857a', '#7d776b'),
]


def skin_css():
    path = os.path.join(SET, 'index.css')
    with open(path) as fh:
        css = fh.read()
    if '/* Dark skin — this set IS the black box gallery.' in css:
        print('  index.css: dark skin already present, skipped')
        return
    with open(path, 'a') as fh:
        fh.write(DARK_CSS)
    print(f'  index.css: appended dark skin (+{len(DARK_CSS)}B)')


def skin_pages():
    for name in ('journeys.html', 'articles.html'):
        path = os.path.join(SET, name)
        with open(path) as fh:
            text = fh.read()
        before = text
        n = 0
        for old, new in REPLACEMENTS:
            c = text.count(old)
            if c:
                text = text.replace(old, new)
                n += c
        if text != before:
            with open(path, 'w') as fh:
                fh.write(text)
        print(f'  {name}: {n} literal replacements')


def verify():
    for name in ('journeys.html', 'articles.html'):
        with open(os.path.join(SET, name)) as fh:
            t = fh.read()
        light = [x for x in ('#f4f1ea', '#f4f3ef', '#16150f', 'rgba(246,245,241') if x in t]
        print(f'  {name}: residual light literals -> {light or "NONE"}')
    with open(os.path.join(SET, 'index.css')) as fh:
        css = fh.read()
    print(f'  index.css: --paper override present -> {"--paper: #12110e" in css}')


if __name__ == '__main__':
    skin_css()
    skin_pages()
    print('--- verify ---')
    verify()
