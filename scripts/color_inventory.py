#!/usr/bin/env python3
"""List every colour literal in gallery-v2.html and classify it warm vs neutral.

Replacing "gold" by eye misses copies: the same tan is written six ways here
(hex, rgb, rgba with four different alphas, and gradient stops). This dumps the
true inventory with hue and saturation so the sweep is complete, not sampled.
"""
import colorsys
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = sys.argv[1] if len(sys.argv) > 1 else "gallery-v2.html"
src = open(os.path.join(ROOT, NAME), encoding="utf-8").read()

HEX = re.compile(r"#([0-9a-fA-F]{3,8})\b")
RGB = re.compile(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)")


def hls(r, g, b):
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return h * 360, l * 100, s * 100


def bucket(hue, sat, lum):
    if sat < 8:
        return "neutral"
    if 20 <= hue <= 55:
        return "GOLD"
    if hue < 20 or hue > 330:
        return "red"
    if 55 < hue <= 90:
        return "olive"
    return "cool"


rows = {}
for m in HEX.finditer(src):
    v = m.group(1)
    if len(v) in (3, 4):
        v = "".join(c * 2 for c in v[:3])
    elif len(v) >= 6:
        v = v[:6]
    else:
        continue
    r, g, b = int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)
    rows.setdefault(("#" + v.lower(), "hex"), [0, r, g, b])[0] += 1

for m in RGB.finditer(src):
    r, g, b = (int(m.group(i)) for i in (1, 2, 3))
    key = ("rgb(%d,%d,%d)" % (r, g, b), "rgb")
    rows.setdefault(key, [0, r, g, b])[0] += 1

groups = {}
for (lit, kind), (n, r, g, b) in rows.items():
    h, l, s = hls(r, g, b)
    k = bucket(h, s, l)
    groups.setdefault(k, []).append((n, lit, h, s, l))

for k in ("GOLD", "olive", "red", "neutral", "cool"):
    if k not in groups:
        continue
    items = sorted(groups[k], key=lambda x: -x[0])
    print("== %s (%d distinct, %d occurrences)" % (k, len(items), sum(i[0] for i in items)))
    for n, lit, h, s, l in items:
        print("   %-20s x%-3d hue=%5.1f sat=%5.1f lum=%5.1f" % (lit, n, h, s, l))
