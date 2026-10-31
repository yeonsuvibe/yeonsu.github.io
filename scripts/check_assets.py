#!/usr/bin/env python3
"""Which images does gallery-v2.html reference that origin/main does not have?

The page works locally because the files sit on this disk. The published site only
has what git carries, so a referenced-but-uncommitted file becomes a 404 for every
visitor. This lists the gap instead of guessing from the browser's request log.
"""
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "gallery-v2.html")

tracked = set(subprocess.run(
    ["git", "ls-tree", "-r", "--name-only", "origin/main"],
    cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines())

html = open(PAGE, encoding="utf-8").read()
refs = sorted(set(re.findall(r'(?:src|href)="((?:photos|museum)/[^"]+)"', html)))
refs += sorted(set(re.findall(r"url\('((?:photos|museum)/[^']+)'\)", html)))

missing_tracked = [r for r in refs if r not in tracked]
missing_disk = [r for r in refs if not os.path.exists(os.path.join(ROOT, r))]
missing_remote = [r for r in missing_tracked if os.path.exists(os.path.join(ROOT, r))]

print("referenced      :", len(refs))
print("not in origin   :", len(missing_tracked))
print("  ...of which the file IS on this disk (commit gap):", len(missing_remote))
print("  ...and absent on disk too (broken reference):", len(missing_disk))
for r in missing_disk[:10]:
    print("   BROKEN", r)
for r in missing_remote[:10]:
    print("   UNCOMMITTED", r)
