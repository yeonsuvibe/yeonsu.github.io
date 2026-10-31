#!/usr/bin/env python3
"""Place the Palais de Tokyo block.

Evidence: the chair supplied a 20-photo chat capture and said it is the Palais de Tokyo
exhibition in Paris. The capture matches our contact sheet photo-for-photo, and the
filename suffixes run 001..020 without a break across index #187..#206, so that is one
send batch = the block.

  187 striped-stripe canvas wall     188 pale abstract canvas
  189 canvas over photo, moon        190 four teal canvases
  191 shelf of plants and cakes      192 bathtub with grey cat
  193 48 small drawings grid         194 magnets on dark board
  195 Eiffel Tower through window    196 selfie (two women)
  197 black teardrops on white       198 stones and bottles on floor
  199 silver shard floor patch       200 hand over silver shard
  201 red-and-blue dots wall         202 "Visitors Poll" iPad  <- was wrongly Venice
  203 periodic-table light wall      204 white creature in glass box
  205 red-and-white papers on tables 206 anatomy drawing + comic panel
                                      <- 202/205 were wrongly Venice, 187 too

#207 onward starts a NEW batch (08:40:35 001) and is not in the capture, so it stays
in _분류보류 rather than being guessed into this block.
"""
import os
import shutil

ROOT = "Photos/musium"
SHEETS = "Photos/_sheets"
FOLDER = "프랑스_팔레드도쿄"
IDXS = range(187, 207)


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

    with open(os.path.join(SHEETS, "rollback_palais.sh"), "w", encoding="utf-8") as fh:
        fh.write('#!/bin/bash\nset -e\ncd "$(dirname "$0")/../musium"\n')
        for _, cur, dest in moves:
            fh.write(f'mv "{os.path.relpath(dest, ROOT)}" "{os.path.relpath(cur, ROOT)}"\n')
    os.chmod(os.path.join(SHEETS, "rollback_palais.sh"), 0o755)

    with open(os.path.join(SHEETS, "corrections.tsv"), "a", encoding="utf-8") as fh:
        for i, cur, dest in moves:
            fh.write(f"{i}\t{os.path.dirname(cur)[len(ROOT) + 1:]}\t{FOLDER}\t"
                     f"캡처 대조: 팔레드도쿄 전시 20장 배치\n")

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
