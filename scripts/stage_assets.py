#!/usr/bin/env python3
"""git add every asset gallery-v2.html references that origin/main lacks.

Same rule as check_assets.py, but acting: the page must not ship with tiles that
only load on the machine that built it.
"""
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tracked = set(subprocess.run(
    ["git", "ls-tree", "-r", "--name-only", "origin/main"],
    cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines())

html = open(os.path.join(ROOT, "gallery-v2.html"), encoding="utf-8").read()
refs = sorted(set(re.findall(r'(?:src|href)="((?:photos|museum)/[^"]+)"', html)))

missing = [r for r in refs if r not in tracked and os.path.exists(os.path.join(ROOT, r))]
if missing:
    subprocess.run(["git", "add", "--"] + missing, cwd=ROOT, check=True)
print("staged", len(missing))
for m in missing:
    print(" +", m)
