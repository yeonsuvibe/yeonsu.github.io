#!/usr/bin/env python3
"""Re-place the 28 photos whose venue the chat captures confirmed.

Blocks, decided from the chat screenshots + the photos themselves:
  #242-#247  프랑스_펫띠팔레   (painted cupola, marble statues, mosaic floor, selfie)
  #248-#254  프랑스_루브르박물관 (Winged Victory, Veronese, rainbow book tower)
  #255-#269  일본_오사카엑스포   (Grand Ring, PORTUGAL pavilion JP signage, PASONA)

#240 and #241 stay in _분류보류: they sit before the Petit Palais block and carry no
confirming evidence.
"""
import os
import shutil

ROOT = "Photos/musium"
SHEETS = "Photos/_sheets"

BLOCKS = [
    ("프랑스_펫띠팔레", range(242, 248)),
    ("프랑스_루브르박물관", range(248, 255)),
    ("일본_오사카엑스포", range(255, 270)),
]


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
    for folder, idxs in BLOCKS:
        for i in idxs:
            name = idx_to_name.get(i)
            if not name:
                print(f"NO-MANIFEST {i}")
                continue
            cur = where.get(name)
            if cur is None:
                print(f"NOT-FOUND #{i} {name}")
                continue
            dest_dir = os.path.join(ROOT, folder)
            dest = os.path.join(dest_dir, name)
            if os.path.normpath(cur) == os.path.normpath(dest):
                print(f"ALREADY #{i} {folder}")
                continue
            moves.append((i, cur, dest))

    for i, cur, dest in moves:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.move(cur, dest)
        print(f"#{i} {os.path.relpath(cur, ROOT)} -> {os.path.relpath(dest, ROOT)}")

    with open(os.path.join(SHEETS, "rollback_capture.sh"), "w", encoding="utf-8") as fh:
        fh.write('#!/bin/bash\nset -e\ncd "$(dirname "$0")/../musium"\n')
        for _, cur, dest in moves:
            fh.write(f'mv "{os.path.relpath(dest, ROOT)}" "{os.path.relpath(cur, ROOT)}"\n')
    os.chmod(os.path.join(SHEETS, "rollback_capture.sh"), 0o755)

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
