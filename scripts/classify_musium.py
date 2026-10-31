#!/usr/bin/env python3
"""Move only the photos whose venue is visually confirmed into 국가_장소 folders.

Reads Photos/_sheets/manifest.tsv (idx -> filename). Anything not listed as
confirmed stays untouched. Every move is recorded for 1:1 rollback.
"""
import os
import shutil
import sys

ROOT = "Photos/musium"
MANIFEST = "Photos/_sheets/manifest.tsv"
LOG = "Photos/_sheets/move_log.tsv"

# venue -> [indices]  (only indices whose venue is visually confirmed)
CONFIRMED = {
    "프랑스_오르세미술관": [2, 3, 4, 7, 8, 9, 10, 11, 12],
    "프랑스_루브르박물관": [5, 6, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 24, 25, 32],
    "프랑스_오랑주리미술관": [213, 214, 215, 216],
    "프랑스_베르사유궁": [30],
    "이탈리아_판테온": [61, 62, 63],
    "이탈리아_베네치아비엔날레": [41, 42, 43, 44, 45, 46, 47, 64, 65, 66, 67, 68, 69, 70,
                          71, 73, 74, 98, 99, 108, 112, 113, 114, 115, 116, 117, 118, 119],
    "이탈리아_보르게세미술관": [75, 80, 81],
    "바티칸_바티칸박물관": [82, 83, 84],
    "이탈리아_우피치미술관": [91, 92, 95],
    "이탈리아_베네치아": [93, 128],
    "이탈리아_피사": [268],
}


def main():
    idx_to_name = {}
    with open(MANIFEST, encoding="utf-8") as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) == 2 and parts[0].isdigit():
                idx_to_name[int(parts[0])] = parts[1]

    moves = []
    missing = []
    for venue, idxs in CONFIRMED.items():
        dest_dir = os.path.join(ROOT, venue)
        for i in idxs:
            name = idx_to_name.get(i)
            if not name:
                missing.append((i, "no-manifest"))
                continue
            src = os.path.join(ROOT, name)
            if not os.path.exists(src):
                missing.append((i, "already-moved-or-absent"))
                continue
            os.makedirs(dest_dir, exist_ok=True)
            dest = os.path.join(dest_dir, name)
            if os.path.exists(dest):
                missing.append((i, "dest-exists"))
                continue
            moves.append((src, dest))

    for src, dest in moves:
        shutil.move(src, dest)

    with open(LOG, "w", encoding="utf-8") as fh:
        fh.write("#src\tdest\n")
        for src, dest in moves:
            fh.write(f"{src}\t{dest}\n")

    with open("Photos/_sheets/rollback.sh", "w", encoding="utf-8") as fh:
        fh.write("#!/bin/bash\n# undo classify_musium.py\nset -e\ncd \"$(dirname \"$0\")/../musium\"\n")
        for src, dest in moves:
            rel_src = os.path.relpath(src, ROOT)
            rel_dest = os.path.relpath(dest, ROOT)
            fh.write(f'mv "{rel_dest}" "{rel_src}"\n')
    os.chmod("Photos/_sheets/rollback.sh", 0o755)

    print(f"moved {len(moves)}")
    for venue in CONFIRMED:
        d = os.path.join(ROOT, venue)
        n = len(os.listdir(d)) - (1 if os.path.exists(os.path.join(d, ".DS_Store")) else 0) if os.path.isdir(d) else 0
        print(f"  {venue}: {n}")
    if missing:
        print("skipped:", missing)
    left = [f for f in os.listdir(ROOT) if f.lower().endswith(".jpeg")]
    print(f"remaining loose photos: {len(left)}")


if __name__ == "__main__":
    main()
