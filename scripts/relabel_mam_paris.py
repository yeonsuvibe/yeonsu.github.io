#!/usr/bin/env python3
"""Place the Musée d'Art Moderne de Paris block.

Decisive evidence, each seen in the photo itself:
  #207  window over the Seine toward Passerelle Debilly  (the 1937 east wing)
  #209  Raoul Dufy "La Fée Électricité" room, curved wall   (MAM Paris, permanent)
  #212  Modigliani, white wall + grey floor
  #217  Picasso nude, signed "Picasso" on the canvas
  #218  André Derain, ballerina, signed "a. Derain"
  #225  Suzanne Valadon "La Chambre bleue"                  (MAM Paris, permanent)

Both batches are contiguous sends (08:40:35-48 and 08:41:06-15), and every frame in them
shows the same white walls, gold carved frames and plank floor, so the batch is judged
as one room set rather than per-photo.

#213-#216 already sit in 프랑스_오랑주리미술관 and are NOT touched here. #213 was checked
directly and shows a Monet Water Lilies room, so that placement stands.
"""
import os
import shutil

ROOT = "Photos/musium"
SHEETS = "Photos/_sheets"
FOLDER = "프랑스_파리시립현대미술관"
IDXS = list(range(207, 213)) + list(range(217, 226))


def main():
    idx_to_name = {}
    with open(os.path.join(SHEETS, "manifest.tsv"), encoding="utf-8") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) == 2 and p[0].isdigit():
                idx_to_name[int(p[0])] = p[1]

    where = {}
    for dp, _, fs in os.walk(ROOT):
        for f in fs:
            if f.lower().endswith((".jpeg", ".jpg", ".png")):
                where[f] = os.path.join(dp, f)

    moves = []
    for i in IDXS:
        name = idx_to_name.get(i)
        if not name:
            print(f"NO-MANIFEST #{i}")
            continue
        cur = where.get(name)
        if cur is None:
            print(f"NOT-FOUND #{i} {name}")
            continue
        dest = os.path.join(ROOT, FOLDER, name)
        if os.path.normpath(cur) == os.path.normpath(dest):
            print(f"ALREADY #{i}")
            continue
        moves.append((i, cur, dest))

    for i, cur, dest in moves:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.move(cur, dest)
        print(f"#{i} {os.path.relpath(cur, ROOT)} -> {FOLDER}")

    with open(os.path.join(SHEETS, "rollback_mam.sh"), "w", encoding="utf-8") as fh:
        fh.write('#!/bin/bash\nset -e\ncd "$(dirname "$0")/../musium"\n')
        for _, cur, dest in moves:
            fh.write(f'mv "{os.path.relpath(dest, ROOT)}" "{os.path.relpath(cur, ROOT)}"\n')
    os.chmod(os.path.join(SHEETS, "rollback_mam.sh"), 0o755)

    print(f"\nmoved {len(moves)}")
    total = 0
    for d in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, d)
        if not os.path.isdir(p):
            continue
        n = len([f for f in os.listdir(p) if not f.startswith(".")])
        total += n
        print(f"  {d}: {n}")
    print(f"TOTAL={total}")


if __name__ == "__main__":
    main()
