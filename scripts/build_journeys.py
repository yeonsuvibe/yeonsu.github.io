#!/usr/bin/env python3
"""Rebuild the Cultural Journeys section from photos/musium.

Each subfolder of photos/musium is one place. The folder name is Korean, so this
table is the only place a Korean name is translated; everything downstream works
on ASCII slugs. Rules from the chair, enforced here:
  - place name and photographs only; no captions, no counts, no dates
  - originals are 3024x4032 (842 MB total), so every served file is a derivation
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "photos", "musium")
OUT = os.path.join(ROOT, "photos", "journeys")
MAX_EDGE = 1500          # long edge of the served file
QUALITY = "72"           # sips q; keeps ~250 KB per plate at this edge
PER_PAGE_MARK = "    "

# itinerary order: Paris, then Versailles, Rome, Florence, Milan, Venice, then
# Frankfurt, Zurich, Osaka. Folder name -> (display name, slug)
PLACES = [
    ("프랑스_루브르박물관",          "Louvre Museum, Paris",              "louvre"),
    ("프랑스_오르세미술관",          "Musée d'Orsay, Paris",              "orsay"),
    ("프랑스_오랑주리미술관",        "Musée de l'Orangerie, Paris",       "orangerie"),
    ("프랑스_펫띠팔레",              "Petit Palais, Paris",               "petit-palais"),
    ("프랑스_파리시립현대미술관",    "Musée d'Art Moderne de Paris",      "mam-paris"),
    ("프랑스_팔레드도쿄",            "Palais de Tokyo, Paris",            "palais-de-tokyo"),
    ("프랑스_파리부르스드코메르스",  "Bourse de Commerce, Paris",         "bourse-de-commerce"),
    ("프랑스_자크뮈르미술관",        "Musée Jacquemart-André, Paris",     "jacquemart-andre"),
    ("프랑스_파리오페라가르니에",    "Palais Garnier, Paris",             "palais-garnier"),
    ("프랑스_베르사유궁",            "Palace of Versailles",              "versailles"),
    ("이탈리아_보르게세미술관",      "Galleria Borghese, Rome",           "borghese"),
    ("이탈리아_로마국립현대미술관",  "Galleria Nazionale d'Arte Moderna, Rome", "gnam"),
    ("이탈리아_MAXXI현대미술관",     "MAXXI, Rome",                       "maxxi"),
    ("이탈리아_판테온",              "Pantheon, Rome",                    "pantheon"),
    ("이탈리아_산루이지데이프란체시", "San Luigi dei Francesi, Rome",      "san-luigi"),
    ("바티칸_바티칸박물관",          "Vatican Museums, Vatican City",     "vatican"),
    ("이탈리아_우피치미술관",        "Uffizi Gallery, Florence",          "uffizi"),
    ("이탈리아_피렌체첸트로스토리카", "Centro Storico, Florence",          "centro-storico"),
    ("이탈리아_밀라노오페라하우스",  "Teatro alla Scala, Milan",          "scala"),
    ("이탈리아_베네치아",            "Venice",                            "venice"),
    ("이탈리아_베네치아비엔날레",    "Venice Biennale",                   "venice-biennale"),
    ("독일_슈타델미술관",            "Städel Museum, Frankfurt",          "staedel"),
    ("스위스_취리히미술관",          "Kunsthaus Zürich",                  "kunsthaus-zurich"),
    ("일본_오사카엑스포",            "Expo 2025, Osaka",                  "expo-osaka"),
]

EXTS = (".jpeg", ".jpg", ".png", ".JPG", ".JPEG")


def dims(path):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", path],
                         capture_output=True, text=True).stdout
    w = int(re.search(r"pixelWidth:\s*(\d+)", out).group(1))
    h = int(re.search(r"pixelHeight:\s*(\d+)", out).group(1))
    return w, h


def build():
    if not os.path.isdir(SRC):
        sys.exit("missing source: " + SRC)
    os.makedirs(OUT, exist_ok=True)
    known = {p[0] for p in PLACES}
    actual = {d for d in os.listdir(SRC) if os.path.isdir(os.path.join(SRC, d))}
    unmapped = sorted(actual - known)
    if unmapped:
        sys.exit("unmapped folders (add them to PLACES): " + ", ".join(unmapped))
    missing = sorted(known - actual)
    if missing:
        print("note: listed but absent: " + ", ".join(missing), file=sys.stderr)

    places = []
    for folder, display, slug in PLACES:
        src_dir = os.path.join(SRC, folder)
        if not os.path.isdir(src_dir):
            continue
        files = sorted(f for f in os.listdir(src_dir) if f.endswith(EXTS))
        if not files:
            continue
        dst_dir = os.path.join(OUT, slug)
        os.makedirs(dst_dir, exist_ok=True)
        plates = []
        for i, name in enumerate(files, 1):
            src = os.path.join(src_dir, name)
            dst = os.path.join(dst_dir, "%03d.jpg" % i)
            # resize only when stale: reruns must not re-encode 250 files
            if not (os.path.exists(dst) and
                    os.path.getmtime(dst) >= os.path.getmtime(src)):
                subprocess.run(["sips", "-Z", str(MAX_EDGE), "-s", "format", "jpeg",
                                "-s", "formatOptions", QUALITY, src, "--out", dst],
                               capture_output=True, check=True)
            w, h = dims(dst)
            plates.append({"src": "photos/journeys/%s/%03d.jpg" % (slug, i),
                           "w": w, "h": h})
        places.append({"name": display, "slug": slug, "plates": plates})
        print("%-38s %3d plates" % (display, len(plates)), file=sys.stderr)
    return places


def markup(places):
    L = []
    L.append('<div class="jrs">')
    for p in places:
        L.append('<article class="jr" data-reveal>')
        L.append('  <h3 class="jr-name">%s</h3>' % p["name"])
        L.append('  <div class="jr-rail" role="list">')
        for pl in p["plates"]:
            L.append('    <figure class="jr-plate" role="listitem">'
                     '<img src="%s" width="%d" height="%d" alt="" '
                     'loading="lazy" decoding="async"></figure>'
                     % (pl["src"], pl["w"], pl["h"]))
        L.append('  </div>')
        L.append('</article>')
    L.append('</div>')
    return "\n".join(L)


if __name__ == "__main__":
    data = build()
    with open(os.path.join(ROOT, "scripts", "journeys.json"), "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, "scripts", "journeys.html"), "w") as f:
        f.write(markup(data))
    total = sum(len(p["plates"]) for p in data)
    print("places=%d plates=%d" % (len(data), total), file=sys.stderr)
