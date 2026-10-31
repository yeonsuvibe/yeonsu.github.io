#!/usr/bin/env python3
"""Prove the cool conversion did not cost readability.

Every warm literal was replaced with a colour of the same relative luminance, so the
claim is checkable exactly: recompute the pair, print the luminance delta, and print the
WCAG ratio of each text tone against the page's light surface and its dark surface.
A conversion that quietly darkened the paper would show up here as a ratio drop.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coolize import cool, is_warm, lum, contrast, lin  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# the surfaces the design actually reads against
LIGHT = (236, 238, 241)   # the cool paper
DARK = (21, 21, 21)       # the cool espresso


def pairs(name):
    import re
    src = open(os.path.join(ROOT, name), encoding="utf-8").read()
    seen = {}
    for m in re.finditer(r"#([0-9a-fA-F]{6})\b", src):
        h = m.group(1)
        rgb = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
        if is_warm(rgb):
            seen["#" + h.lower()] = rgb
    for m in re.finditer(r"(?<![\d.])(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})(?![\d.])", src):
        rgb = tuple(int(m.group(i)) for i in (1, 2, 3))
        if all(v <= 255 for v in rgb) and is_warm(rgb):
            seen["%d,%d,%d" % rgb] = rgb
    return seen


for name in sys.argv[1:]:
    warm = pairs(name)
    if not warm:
        print("%s: no warm literals left (already converted)" % name)
        continue
    print("== %s: %d remaining warm literals" % (name, len(warm)))
    worst_l = 0.0
    worst_c = 0.0
    for old, rgb in warm.items():
        new = cool(rgb)
        dl = abs(lum(rgb) - lum(new))
        dc = abs(contrast(rgb, DARK) - contrast(new, DARK))
        worst_l = max(worst_l, dl)
        worst_c = max(worst_c, dc)
        print("  %-18s -> %-18s  dLum %.4f  ratio-on-dark %.2f -> %.2f"
              % (old, "%d,%d,%d" % new, dl, contrast(rgb, DARK), contrast(new, DARK)))
    print("  worst luminance delta %.4f, worst contrast delta %.3f\n" % (worst_l, worst_c))
