#!/usr/bin/env python3
"""Move the paper and the ink from warm cream/espresso to a cool gallery grey.

The gold was already taken out, which left the page in two temperatures: silver frames
on cream paper. This closes that gap without touching a single photograph.

Rule, same as the silver: keep relative luminance identical so every contrast ratio the
design was tuned to survives. The cool cast scales with brightness so shadows stay
neutral and only the lit surfaces pick up the faint blue of a plaster wall.

Untouched on purpose:
  * the accent red (--accent / --crimson) is the page's only warm note, not metal
  * pure black/white and the already-cool greys
  * anything inside an image path or a <script> block is never a colour literal
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(rgb):
    r, g, b = (lin(max(0.0, min(255.0, v))) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def shaped(v):
    """A cool grey, not a blue one: the red-to-blue spread tops out at 5 of 255.

    The first attempt let the spread reach 20 at paper brightness and turned the page
    powder-blue (blue pinned at 255). Cool grey plaster measures r-b of about 5; that is
    the whole difference between #ebedf0 and cream.
    """
    lead = max(0.0, min(5.0, v * 0.021))
    return (v - lead * 0.4, v, v + lead * 0.6)


def cool(rgb):
    """solve the grey whose luminance equals rgb, with a brightness-scaled cool cast."""
    target = lum(rgb)
    lo, hi = 0.0, 255.0
    for _ in range(50):
        v = (lo + hi) / 2
        if lum(shaped(v)) < target:
            lo = v
        else:
            hi = v
    v = (lo + hi) / 2
    return tuple(max(0, min(255, int(round(c)))) for c in shaped(v))


def hue_sat(rgb):
    r, g, b = rgb
    mx, mn = max(rgb), min(rgb)
    if mx == mn:
        return 0.0, 0.0
    d = mx - mn
    if mx == r:
        h = (60 * ((g - b) / d)) % 360
    elif mx == g:
        h = 60 * ((b - r) / d) + 120
    else:
        h = 60 * ((r - g) / d) + 240
    return h, d / mx


def is_warm(rgb):
    r, g, b = rgb
    if max(rgb) - min(rgb) < 6:  # neutral
        return False
    # warm means the green sits between red and blue.
    if not (r > g > b):
        return False
    # and it must be a tan/cream, not the crimson accent: #a8351f is r>g>b too, but it
    # sits at hue 10 and 82% saturation, while every cream here sits at hue 30-51.
    h, s = hue_sat(rgb)
    if h < 24 and s > 0.5:
        return False
    return True


HEX = re.compile(r"#([0-9a-fA-F]{6})\b")
TRIPLE = re.compile(r"(?<![\d.])(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})(?![\d.])")


def scan(name):
    src = open(os.path.join(ROOT, name), encoding="utf-8").read()
    table = {}
    for m in HEX.finditer(src):
        h = m.group(1)
        rgb = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
        if is_warm(rgb):
            table["#" + h.lower()] = (rgb, "#%02x%02x%02x" % cool(rgb))
    for m in TRIPLE.finditer(src):
        rgb = tuple(int(m.group(i)) for i in (1, 2, 3))
        if all(v <= 255 for v in rgb) and is_warm(rgb):
            key = "%d,%d,%d" % rgb
            table[key] = (rgb, "%d,%d,%d" % cool(rgb))
    return src, table


def report(name, apply=False):
    src, table = scan(name)
    out = src
    print("== %s : %d warm literals" % (name, len(table)))
    rows = []
    for old, (rgb, new) in table.items():
        n = src.count(old)
        rows.append((n, old, "%02x%02x%02x" % rgb, new))
        out = out.replace(old, new)
    rows.sort(reverse=True)
    for n, old, o, new in rows:
        print("  x%-3d %-18s -> %-18s" % (n, old, new))
    if apply and out != src:
        open(os.path.join(ROOT, name), "w", encoding="utf-8").write(out)
        print("  APPLIED, %d bytes delta" % (len(out) - len(src)))
    return table


if __name__ == "__main__":
    files = [a for a in sys.argv[1:] if not a.startswith("-")]
    apply = "--apply" in sys.argv
    for f in files:
        report(f, apply)
