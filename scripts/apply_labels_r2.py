#!/usr/bin/env python3
"""Apply round-2 labels: move every remaining loose photo into its judged folder.

Fails closed: if the label set does not exactly cover the manifest set, nothing moves.
"""
import os
import shutil
import sys

ROOT = "Photos/musium"
SHEETS = "Photos/_sheets"
MANIFEST = os.path.join(SHEETS, "r2_manifest.tsv")
LABELS = os.path.join(SHEETS, "labels_r2.tsv")


def read_manifest():
    idx_to_name = {}
    with open(MANIFEST, encoding="utf-8") as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2 and parts[0].isdigit():
                idx_to_name[int(parts[0])] = parts[1]
    return idx_to_name


def read_labels():
    labels = {}
    with open(LABELS, encoding="utf-8") as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if not parts or not parts[0].isdigit():
                continue
            idx = int(parts[0])
            labels[idx] = (parts[1], parts[2] if len(parts) > 2 else "low")
    return labels


def main():
    idx_to_name = read_manifest()
    labels = read_labels()

    missing = sorted(set(idx_to_name) - set(labels))
    extra = sorted(set(labels) - set(idx_to_name))
    if missing or extra:
        print(f"ABORT missing={missing} extra={extra}", file=sys.stderr)
        return 1

    moves, skipped = [], []
    for idx, (folder, conf) in sorted(labels.items()):
        name = idx_to_name[idx]
        src = os.path.join(ROOT, name)
        if not os.path.exists(src):
            skipped.append((idx, "absent"))
            continue
        dest_dir = os.path.join(ROOT, folder)
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, name)
        if os.path.exists(dest):
            skipped.append((idx, "dest-exists"))
            continue
        moves.append((idx, src, dest))

    for _, src, dest in moves:
        shutil.move(src, dest)

    with open(os.path.join(SHEETS, "move_log_r2.tsv"), "w", encoding="utf-8") as fh:
        fh.write("#idx\tsrc\tdest\n")
        for idx, src, dest in moves:
            fh.write(f"{idx}\t{src}\t{dest}\n")

    with open(os.path.join(SHEETS, "rollback_r2.sh"), "w", encoding="utf-8") as fh:
        fh.write('#!/bin/bash\nset -e\ncd "$(dirname "$0")/../musium"\n')
        for _, src, dest in moves:
            fh.write(f'mv "{os.path.relpath(dest, ROOT)}" "{os.path.relpath(src, ROOT)}"\n')
    os.chmod(os.path.join(SHEETS, "rollback_r2.sh"), 0o755)

    print(f"moved {len(moves)}  skipped {len(skipped)}")
    if skipped:
        print("skipped:", skipped)

    dirs = sorted(d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d)))
    total = 0
    for d in dirs:
        n = len([f for f in os.listdir(os.path.join(ROOT, d)) if not f.startswith(".")])
        total += n
        print(f"  {d}: {n}")
    loose = len([f for f in os.listdir(ROOT) if f.lower().endswith((".jpeg", ".jpg", ".png"))])
    print(f"loose leftover: {loose}")
    print(f"TOTAL in museum tree: {total + loose}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
