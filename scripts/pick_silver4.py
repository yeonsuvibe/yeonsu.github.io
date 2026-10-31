#!/usr/bin/env python3
"""Final silver ramp: luminance matched to the gold, cool cast only where light lands.

A constant blue lead turned the dark moulding into navy (#0b111d). Real silver keeps
its shadows neutral and only picks up sky in the highlights, so the blue lead scales
with the value: ~1 at black, ~16 at white. Luminance is still solved so the WCAG
contrast of every text step is unchanged from the gold it replaces.
"""


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
    """blue lead grows with brightness; red sits a third of that below the green."""
    lead = round(max(1.0, min(16.0, v * 0.072)))
    return (v - round(lead / 2.4), v, v + lead)


def solve(gold):
    target = lum(gold)
    lo, hi = 0.0, 255.0
    for _ in range(60):
        v = (lo + hi) / 2
        if lum(shaped(v)) < target:
            lo = v
        else:
            hi = v
    v = int(round((lo + hi) / 2))
    return tuple(max(0, min(255, int(round(c)))) for c in shaped(v))


CREAM = (242, 238, 228)
WALL = (232, 224, 209)
DARK = (29, 25, 22)

ROWS = [
    ("#c9a97f  accent/.tn/.pl-kick/f-note a", (201, 169, 127)),
    ("#d9c9ae  hero em", (217, 201, 174)),
    ("#e8d5b6  tile hover border", (232, 213, 182)),
    ("#cdc4b3  rail mat / plate bg", (205, 196, 179)),
    ("rgba(201,169,127) ring 1px", (201, 169, 127)),
    ("rgba(206,174,132) ring 2px", (206, 174, 132)),
    ("rgba(214,180,136) fillet", (214, 180, 136)),
    ("rgba(255,236,203) specular", (255, 236, 203)),
    ("rgba(90,74,54) scrollbar", (90, 74, 54)),
    ("#332a1f  moulding hi", (51, 42, 31)),
    ("#1d1710  moulding mid", (29, 23, 16)),
    ("#13100b  moulding lo", (19, 16, 11)),
    ("#3b3022  plate hi", (59, 48, 34)),
    ("#241c13  plate mid", (36, 28, 19)),
    ("#14110c  plate lo", (20, 17, 12)),
    ("#1d1916  tile bg", (29, 25, 22)),
    ("#1b1510  ring solid", (27, 21, 16)),
]

print("%-38s %-8s %-8s %s" % ("role", "gold", "silver", "cream wall dark  (gold)"))
worst = 0.0
for role, g in ROWS:
    s = solve(g)
    d = contrast(g, CREAM) - contrast(s, CREAM)
    worst = max(worst, abs(d))
    print("%-38s #%02x%02x%02x  #%02x%02x%02x  %4.2f %4.2f %5.2f  (%4.2f %4.2f %5.2f)"
          % (role, *g, *s,
             contrast(s, CREAM), contrast(s, WALL), contrast(s, DARK),
             contrast(g, CREAM), contrast(g, WALL), contrast(g, DARK)))
print("\nmax contrast drift on cream: %.3f" % worst)
