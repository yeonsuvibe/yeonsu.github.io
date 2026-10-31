#!/usr/bin/env python3
"""Verify the four sets are self-contained.

For every HTML/CSS file in each set, collect local references (src=, href=, url(...))
and confirm the target exists inside that same set directory.
Reports any reference that escapes the set or is missing on disk.
"""
import os
import re
import sys

P = '/Users/eungsikahn/Dev/yeonsu_profile'
S = os.path.join(P, 'sets')

REF_RX = re.compile(r'''(?:src|href)\s*=\s*["']([^"'#]+)|url\(\s*["']?([^"')]+)["']?\s*\)''')
SKIP_PREFIX = ('data:', 'http://', 'https://', 'mailto:', '#', 'javascript:')


def local_refs(path):
    with open(path, 'r', errors='replace') as fh:
        text = fh.read()
    out = []
    for m in REF_RX.finditer(text):
        ref = m.group(1) or m.group(2)
        if not ref or ref.startswith(SKIP_PREFIX):
            continue
        ref = ref.split('?')[0].split('#')[0].strip()
        # skip percent-encoded fragment refs inside inline SVG data URIs (e.g. %23noiseFilter)
        if ref.startswith('%23') or ref.startswith('#'):
            continue
        if ref:
            out.append(ref)
    return out


def main():
    total_files = 0
    total_refs = 0
    missing = []
    escaped = []

    for d in sorted(os.listdir(S)):
        D = os.path.join(S, d)
        if not os.path.isdir(D):
            continue
        nfiles = 0
        nrefs = 0
        for f in sorted(os.listdir(D)):
            if not f.endswith(('.html', '.css')):
                continue
            p = os.path.join(D, f)
            nfiles += 1
            for ref in local_refs(p):
                nrefs += 1
                target = os.path.normpath(os.path.join(D, ref))
                # escape check
                if not target.startswith(D + os.sep) and target != D:
                    escaped.append((d, f, ref))
                    continue
                if not os.path.exists(target):
                    missing.append((d, f, ref))
        total_files += nfiles
        total_refs += nrefs
        print(f'  {d:20s} {nfiles} files, {nrefs} local refs')

    print()
    print(f'total: {total_files} files, {total_refs} local refs')
    print(f'missing targets : {len(missing)}')
    for row in missing[:20]:
        print('   MISSING', row)
    print(f'escaped sets    : {len(escaped)}')
    for row in escaped[:20]:
        print('   ESCAPED', row)

    return 1 if (missing or escaped) else 0


if __name__ == '__main__':
    sys.exit(main())
