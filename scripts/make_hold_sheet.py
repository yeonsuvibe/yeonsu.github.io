#!/usr/bin/env python3
"""Rebuild contact sheets containing ONLY the 108 still-unclassified photos,
labelled with their original manifest index, so chat captures can be matched
photo-for-photo in one pass."""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = "Photos/musium"
HELD = os.path.join(ROOT, "_분류보류")
OUT = os.path.join(OUT_DIR := "Photos/_sheets", "hold")
os.makedirs(OUT, exist_ok=True)
THUMB = 260
COLS, ROWS = 5, 4
PAD, LABEL_H = 6, 24


def load_font(size):
    for p in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf",
              "/System/Library/Fonts/Helvetica.ttc"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


name_to_idx = {}
with open(os.path.join("Photos/_sheets", "manifest.tsv"), encoding="utf-8") as fh:
    for line in fh:
        p = line.rstrip("\n").split("\t")
        if len(p) == 2 and p[0].isdigit():
            name_to_idx[p[1]] = int(p[0])

files = sorted(
    (f for f in os.listdir(HELD) if f.lower().endswith((".jpeg", ".jpg", ".png"))),
    key=lambda f: name_to_idx.get(f, 10**9),
)
print("held:", len(files))

font = load_font(18)
cell_w, cell_h = THUMB, THUMB + LABEL_H
w = COLS * (cell_w + PAD) + PAD
h = ROWS * (cell_h + PAD) + PAD
per = COLS * ROWS

for si in range(0, len(files), per):
    chunk = files[si:si + per]
    sheet = Image.new("RGB", (w, h), (20, 20, 24))
    draw = ImageDraw.Draw(sheet)
    for k, name in enumerate(chunk):
        try:
            im = Image.open(os.path.join(HELD, name))
            im.draft("RGB", (THUMB * 2, THUMB * 2))
            im = im.convert("RGB")
            im.thumbnail((THUMB, THUMB))
        except Exception as e:
            print("ERR", name, e)
            continue
        col, row = k % COLS, k // COLS
        x = PAD + col * (cell_w + PAD)
        y = PAD + row * (cell_h + PAD)
        sheet.paste(im, (x + (cell_w - im.width) // 2,
                         y + (cell_h - LABEL_H - im.height) // 2))
        draw.rectangle([x, y, x + cell_w, y + cell_h], outline=(70, 70, 80))
        draw.text((x + 6, y + cell_h - LABEL_H + 2),
                  f"#{name_to_idx.get(name, '?')}", fill=(255, 235, 90), font=font)
    out = os.path.join(OUT, f"hold_{si // per + 1:02d}.jpg")
    sheet.save(out, quality=88)
    print(out, len(chunk))
