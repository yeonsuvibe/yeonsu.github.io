#!/bin/sh
# Regenerate the web-sized copies of the original artworks in museum/art/.
# The originals in photos/art/ are kept untouched.
#
#   sh tools/resize-art.sh
#
# After running, update the ASPECTS table in museum/src/gallery.js if any
# image's proportions changed — the hall layout is spaced from those sizes.
set -e
cd "$(dirname "$0")/.."
mkdir -p museum/art
for f in photos/art/*; do
  b=$(basename "$f")
  out="museum/art/${b%.*}.jpg"
  sips -Z 1600 -s format jpeg -s formatOptions 80 "$f" --out "$out" >/dev/null
  printf '%-46s %s\n' "${b%.*}.jpg" "$(sips -g pixelWidth -g pixelHeight "$out" | awk '/pixelWidth/{w=$2}/pixelHeight/{h=$2}END{print w"x"h}')"
done
du -sh museum/art
