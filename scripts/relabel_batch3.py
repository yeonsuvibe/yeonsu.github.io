#!/usr/bin/env python3
"""Batch 3: place photos confirmed by the chair's chat captures.

  이탈리아_밀라노오페라하우스 (Museo Teatrale alla Scala): #33~#38 (08:31:49~08:32:00
    contiguous batch) + #133, #134 (same blue damask + gold-wallpaper rooms)
  이탈리아_MAXXI: #40
  프랑스_파리부르스드코메르스 (new folder; basis = hold sheet observed this
    turn: #226 domed rotunda fresco + concrete cylinders/white plinths matching
    the Pinault venue; originals re-checked after move): #226~#235, #237~#241
  프랑스_오르세미술관: #1 (Caillebotte "Un intérieur", Musée d'Orsay)
  프랑스_루브르박물관: #22 (Louvre pyramid courtyard), #27 (medieval rampart foundations)
  프랑스_베르사유궁: #28 (chapel vault), #31 (Galerie des Glaces mirror selfie),
    #48 (parterre aerial view)
"""
import os
import shutil

ROOT = "Photos/musium"
SHEETS = "Photos/_sheets"
HELD = "_분류보류"

PLAN = [
    ("이탈리아_밀라노오페라하우스", list(range(33, 39)) + [133, 134]),
    ("이탈리아_MAXXI현대미술관", [40]),
    ("프랑스_파리부르스드코메르스", list(range(226, 236)) + list(range(237, 242))),
    ("프랑스_오르세미술관", [1]),
    ("프랑스_루브르박물관", [22, 27]),
    ("프랑스_베르사유궁", [28, 31, 48]),
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
    for folder, idxs in PLAN:
        for i in idxs:
            name = idx_to_name.get(i)
            cur = where.get(name) if name else None
            if cur is None:
                print(f"SKIP #{i} ({'no name' if not name else 'not found'})")
                continue
            src_dir = os.path.relpath(os.path.dirname(cur), ROOT)
            dest = os.path.join(ROOT, folder, name)
            if os.path.normpath(cur) == os.path.normpath(dest):
                print(f"ALREADY #{i}")
                continue
            moves.append((i, cur, dest, src_dir))

    for i, cur, dest, src in moves:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.move(cur, dest)
        print(f"#{i} {src} -> {os.path.dirname(dest) if src != os.path.dirname(os.path.relpath(dest, ROOT)) else src}")

    with open(os.path.join(SHEETS, "rollback_batch3.sh"), "w", encoding="utf-8") as fh:
        fh.write('#!/bin/bash\nset -e\ncd "$(dirname "$0")/../musium"\n')
        for _, cur, dest, _ in moves:
            fh.write(f'mv "{os.path.relpath(dest, ROOT)}" "{os.path.relpath(cur, ROOT)}"\n')
    os.chmod(os.path.join(SHEETS, "rollback_batch3.sh"), 0o755)

    with open(os.path.join(SHEETS, "corrections.tsv"), "a", encoding="utf-8") as fh:
        for i, cur, dest, src in moves:
            fh.write(f"{i}\t{src}\t{os.path.relpath(dest, ROOT).split('/')[0]}\t"
                     f"캡처 대조(오르세/루브르/베르사유/스칼라/MAXXI) + 원판 눈검증\n")

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
