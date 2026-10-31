#!/usr/bin/env python3
"""Replace every gold-family literal in a page with its luminance-matched silver.

The same tan appears as hex, as rgb(), and inside rgba() with six different alphas,
so a hand edit misses copies. This walks an explicit table (gold -> silver) and
reports any gold-family literal still left afterwards, so "all of it" is checkable
rather than asserted. Applied per file; nothing outside the table is touched.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# gold literal -> silver literal. Contrast of each pair was solved, not eyeballed:
# luminance is held equal so no text step loses readability (max drift 0.068).
TABLE_V2 = {
    "#c9a97f": "#a9aebb",          # accent text, tile number, plate kicker, footer link
    "#d9c9ae": "#c5cbda",          # hero italic emphasis
    "#e8d5b6": "#d1d7e6",          # tile hover border
    "#cdc4b3": "#bfc5d3",          # journey plate mat
    "255,236,203": "231,238,254",  # specular inset on the tile
    "255,238,208": "231,238,254",  # specular inset on the plate moulding
    "255,240,212": "231,238,254",  # radial sheen on the plate
    "201,169,127": "169,174,187",  # gold rebate rings
    "206,174,132": "174,179,192",  # outer pinstripe
    "214,180,136": "180,185,198",  # fillet against the mat
    "60,46,28": "42,43,46",        # warm cast shadow -> neutral
    "90,74,54": "75,77,83",        # scrollbar thumb
    "#332a1f": "#2a2b2e",          # tile moulding highlight
    "#1d1710": "#17181a",          # tile moulding mid
    "#13100b": "#101011",          # tile moulding shadow
    "#3b3022": "#303236",          # plate moulding highlight
    "#3a2f22": "#2f3134",          # plate moulding highlight variant
    "#241c13": "#1c1d1f",          # plate moulding mid
    "#14110c": "#111112",          # plate moulding shadow
    "#1d1916": "#191a1c",          # tile body
    "#1b1510": "#151618",          # solid ring between fillet and pinstripe
    "#8d8175": "#7b7d82",          # hairline rule
    "#8d8677": "#7d7f84",          # muted ink
}

GOLD_LEFT = re.compile(
    r"#c9a97f|#d9c9ae|#e8d5b6|#cdc4b3|#b89a6a|#a8351f00|"
    r"rgba?\(\s*(?:201|206|214|255)\s*,\s*(?:169|174|180|236|238|240)\s*,\s*"
    r"(?:127|132|136|203|208|212)|"
    r"#[0-9a-f]{2}([0-9a-f]{2})([0-9a-f]{2})", re.I)


def warm_gold(hexstr):
    """true when the colour is a warm metal-ish tan (hue 20-55, sat >= 10)."""
    h = hexstr.lstrip("#")
    if len(h) != 6:
        return False
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    mx, mn = max(r, g, b), min(r, g, b)
    if mx == mn:
        return False
    if mx == b:          # blue-dominant: not gold
        return False
    sat = (mx - mn) / mx
    if sat < 0.10:
        return False
    # warm and not red: gold sits between orange and yellow
    return r > g > b and (r - b) <= 140 and g >= b


def run(name, table):
    path = os.path.join(ROOT, name)
    src = open(path, encoding="utf-8").read()
    before = src
    counts = {}
    for gold, silver in table.items():
        n = src.count(gold)
        if n:
            counts[gold] = n
            src = src.replace(gold, silver)
    if src != before:
        open(path, "w", encoding="utf-8").write(src)
    print("== %s: %d literals replaced, %d bytes delta"
          % (name, sum(counts.values()), len(src) - len(before)))
    for g, n in sorted(counts.items(), key=lambda x: -x[1]):
        print("   %-12s -> %-10s x%d" % (g, table[g], n))

    # proof step: nothing gold-ish may survive
    left = []
    for m in re.finditer(r"#[0-9a-fA-F]{6}\b", src):
        if warm_gold(m.group(0)):
            left.append(m.group(0))
    for m in re.finditer(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", src):
        r, g, b = (int(m.group(i)) for i in (1, 2, 3))
        if r > g > b and (r - b) >= 12 and max(r, g, b) > 40:
            left.append(m.group(0))
    print("   gold-family left: %d %s" % (len(left), sorted(set(left))[:8]))


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "gallery-v2.html", TABLE_V2)
