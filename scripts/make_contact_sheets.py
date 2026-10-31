#!/usr/bin/env python3
"""Build indexed contact sheets for Photos/musium so each photo can be visually identified."""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

SRC = "Photos/musium"
OUT = "Photos/_sheets"
THUMB = 300          # long edge of each thumbnail
COLS, ROWS = 5, 4    # 20 per sheet
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
    os.makedirs(OUT, exist_ok=True)
    files = sorted(f for f in os.listdir(SRC) if f.lower().endswith((".jpeg", ".jpg", ".png")))
    font = load_font(20)
    cell_w, cell_h = THUMB, THUMB + LABEL_H
    sheet_w = COLS * (cell_w + PAD) + PAD
    sheet_h = ROWS * (cell_h + PAD) + PAD

    manifest = []
    per = COLS * ROWS
    for si in range(0, len(files), per):
        chunk = files[si:si + per]
        sheet = Image.new("RGB", (sheet_w, sheet_h), (24, 24, 28))
        draw = ImageDraw.Draw(sheet)
        for k, name in enumerate(chunk):
            idx = si + k + 1
            manifest.append((idx, name))
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
            # centre within cell
            ox = x + (cell_w - im.width) // 2
            oy = y + (cell_h - LABEL_H - im.height) // 2
            sheet.paste(im, (ox, oy))
            draw.rectangle([x, y, x + cell_w, y + cell_h], outline=(70, 70, 78))
            draw.text((x + 6, y + cell_h - LABEL_H + 3), f"#{idx}", fill=(255, 235, 90), font=font)
        out = os.path.join(OUT, f"sheet_{si // per + 1:02d}.jpg")
        sheet.save(out, quality=86)
        print(out, len(chunk))

    with open(os.path.join(OUT, "manifest.tsv"), "w", encoding="utf-8") as fh:
        for idx, name in manifest:
            fh.write(f"{idx}\t{name}\n")
    print("total", len(manifest))


if __name__ == "__main__":
    main()
