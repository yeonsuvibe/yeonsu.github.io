#!/usr/bin/env python3
"""Round-2 contact sheets for the photos still loose in Photos/musium.

Keeps the ORIGINAL index from Photos/_sheets/manifest.tsv as the on-sheet label,
so a label read off the sheet maps straight back to the first-round numbering.
Writes round-2 files as Photos/_sheets/r2_sheet_NN.jpg and r2_manifest.tsv.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

SRC = "Photos/musium"
OUT = "Photos/_sheets"
MANIFEST = os.path.join(OUT, "manifest.tsv")
THUMB = 300
COLS, ROWS = 5, 4
PAD = 6
LABEL_H = 26


def load_font(size):
    for p in (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def main():
    idx_of = {}
    with open(MANIFEST, encoding="utf-8") as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) == 2 and parts[0].isdigit():
                idx_of[parts[1]] = int(parts[0])

    loose = sorted(f for f in os.listdir(SRC) if f.lower().endswith((".jpeg", ".jpg", ".png")))
    items = []
    unknown = []
    for name in loose:
        if name in idx_of:
            items.append((idx_of[name], name))
        else:
            unknown.append(name)
    items.sort()

    font = load_font(20)
    cell_w, cell_h = THUMB, THUMB + LABEL_H
    sheet_w = COLS * (cell_w + PAD) + PAD
    sheet_h = ROWS * (cell_h + PAD) + PAD

    per = COLS * ROWS
    written = 0
    manifest_rows = []
    for si in range(0, len(items), per):
        chunk = items[si:si + per]
        sheet = Image.new("RGB", (sheet_w, sheet_h), (24, 24, 28))
        draw = ImageDraw.Draw(sheet)
        for k, (idx, name) in enumerate(chunk):
            manifest_rows.append((idx, name))
            try:
                im = Image.open(os.path.join(SRC, name))
                im.draft("RGB", (THUMB * 2, THUMB * 2))
                im = im.convert("RGB")
                im.thumbnail((THUMB, THUMB))
            except Exception as e:
                print("ERR", name, e, file=sys.stderr)
                continue
            col, row = k % COLS, k // COLS
            x = PAD + col * (cell_w + PAD)
            y = PAD + row * (cell_h + PAD)
            ox = x + (cell_w - im.width) // 2
            oy = y + (cell_h - LABEL_H - im.height) // 2
            sheet.paste(im, (ox, oy))
            draw.rectangle([x, y, x + cell_w, y + cell_h], outline=(70, 70, 78))
            draw.text((x + 6, y + cell_h - LABEL_H + 3), f"#{idx}", fill=(255, 235, 90), font=font)
        out = os.path.join(OUT, f"r2_sheet_{si // per + 1:02d}.jpg")
        sheet.save(out, quality=86)
        written += 1
        print(out, len(chunk))

    with open(os.path.join(OUT, "r2_manifest.tsv"), "w", encoding="utf-8") as fh:
        for idx, name in manifest_rows:
            fh.write(f"{idx}\t{name}\n")

    print("sheets", written, "photos", len(manifest_rows), "unknown", len(unknown))
    if unknown:
        print("UNKNOWN:", unknown[:5])


if __name__ == "__main__":
    main()
