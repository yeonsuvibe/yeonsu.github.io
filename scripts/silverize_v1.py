#!/usr/bin/env python3
"""V1's gold -> silver, same rule as V2: luminance matched, cool cast in the lights.

V1 keeps its own palette (a 3D gallery on WARM PAVILION), so only the metals move:
--gilt and its hover step, the bronze moulding, and the warm shadow casts. The warm
paper, ink, and the crimson accent are left alone — they are not metal.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TABLE = {
    "#9a7b46": "#8e939c",   # --gilt, the one gold the design actually paints
    "#a8894f": "#9a9fa8",   # --gilt hover step (theme block)
    "#b89a6a": "#a6abb4",   # any lighter gilt
    "#7d5820": "#6f737b",   # hp-kick, the AA-corrected gold text
    "42,35,28": "36,37,40",   # warm line/shadow casts -> neutral
    "44,33,20": "38,39,42",   # bronze moulding shadow
    "44,32,18": "38,39,42",   # bronze moulding shadow variant
    "30,24,18": "26,27,29",
    "#241e18": "#1f2124",   # dates / name (warm near-black)
    "#3c3830": "#383a3e",
    "#7a6a55": "#74777c",   # --soft warm grey
    "#1a1815": "#191a1c",
    "#14120f": "#131416",
}

NAMES = sys.argv[1:] or ["gallery.html"]
for name in NAMES:
    path = os.path.join(ROOT, name)
    src = open(path, encoding="utf-8").read()
    before = len(src)
    total = 0
    for gold, silver in TABLE.items():
        n = src.count(gold)
        if n:
            total += n
            src = src.replace(gold, silver)
            print("%-10s %-12s -> %-10s x%d" % (name, gold, silver, n))
    open(path, "w", encoding="utf-8").write(src)
    print("%-10s %d literals, %d bytes delta" % (name, total, len(src) - before))
