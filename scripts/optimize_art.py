#!/usr/bin/env python3
"""Re-encode the art JPEGs at the size the gallery actually paints them.

The plates cap the picture at min(72svh, 720px) tall, and the tiles are smaller again, so the
files on disk need a long edge of about 1600px and nothing more. They already sit at 1600px but
were saved at desktop quality, which put 500-900KB behind a single plate: the first screen of
the gallery pulled 5.4MB. This rewrites them at quality 80, progressive, and only keeps the new
file when it is actually smaller.

Originals are recoverable from git history; re-run with --dry to measure without writing.
"""
import glob
import os
import sys

from PIL import Image, ImageOps

TARGETS = ["museum/art/*.jpg", "photos/art/performance/*.jpg"]
LONG_EDGE = 1600
QUALITY = 80
# below this the file is not worth re-encoding
FLOOR = 320 * 1024


def main(dry=False):
    before = after = 0
    changed = 0
    for pattern in TARGETS:
        for path in sorted(glob.glob(pattern)):
            size = os.path.getsize(path)
            before += size
            if size < FLOOR:
                after += size
                continue
            try:
                im = Image.open(path)
                im = ImageOps.exif_transpose(im).convert("RGB")
                im.thumbnail((LONG_EDGE, LONG_EDGE), Image.LANCZOS)
                tmp = path + ".tmp.jpg"
                im.save(tmp, "JPEG", quality=QUALITY, optimize=True, progressive=True)
                new = os.path.getsize(tmp)
                if new >= size * 0.92:
                    os.remove(tmp)
                    after += size
                    continue
                if dry:
                    os.remove(tmp)
                else:
                    os.replace(tmp, path)
                after += new
                changed += 1
                print("  %-46s %5dKB -> %5dKB" % (os.path.basename(path), size // 1024, new // 1024))
            except Exception as exc:                       # noqa: BLE001 - report, keep file
                print("  SKIP %s (%s)" % (path, exc))
                after += size
    print("re-encoded=%d  %.1fMB -> %.1fMB (%.0f%% smaller)"
          % (changed, before / 1e6, after / 1e6, 100 - 100 * after / max(before, 1)))


if __name__ == "__main__":
    main(dry="--dry" in sys.argv)
