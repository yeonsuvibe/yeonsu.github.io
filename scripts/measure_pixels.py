#!/usr/bin/env python3
"""Measure the temperature of what actually rendered.

A declared colour can be cool while the page still reads warm — a gradient stop, a text
halo, or an overlay can carry it. So this reads the screenshots: r-b per pixel, averaged
over a grid. Negative means cool, positive means the page still has cream in it.
"""
import glob
import sys

from PIL import Image

tag = sys.argv[1]
files = sorted(glob.glob("/tmp/tone_%s_*.png" % tag),
               key=lambda f: int(f.rsplit("_", 1)[1].split(".")[0]))

tot = 0.0
worst = -999
cool = 0
for f in files:
    im = Image.open(f).convert("RGB")
    w, h = im.size
    px = im.load()
    s = 0
    n = 0
    mx = -999
    step = 13
    for y in range(12, h - 12, step):
        for x in range(12, w - 12, step):
            r, g, b = px[x, y]
            d = r - b
            s += d
            n += 1
            if d > mx:
                mx = d
    mean = s / n
    tot += mean
    worst = max(worst, mx)
    if mean <= 0:
        cool += 1
    print("%s stop%-2d mean r-b %6.1f   max %4d" % (tag, files.index(f), mean, mx))

print("%s SUMMARY mean %6.2f  worst-max %d  cool-stops %d/%d"
      % (tag, tot / len(files), worst, cool, len(files)))
