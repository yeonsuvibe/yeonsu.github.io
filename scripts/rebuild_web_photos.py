#!/usr/bin/env python3
"""Rebuild the web photo set from photos/museum and re-point gallery.html at it.

The web set under photos/journeys was built from an older classification: it still
carries venues that no longer exist in the museum folders (Borghese, San Luigi dei
Francesi, Palais Garnier, MAM Paris) and is missing the newer ones (Ponte, MAXXI).
This generator reads photos/museum, writes one folder per venue in the trip order,
and rewrites the journeys section of gallery.html to match.

Spec, taken from the existing set so nothing shifts visually: long edge 1500px,
JPEG quality 82, orientation applied from EXIF then EXIF dropped (the originals
carry GPS and the web set should not), ordered by EXIF capture time rather than the
Kakao transfer filenames.
"""
import os
import re
import shutil
from datetime import datetime

from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "photos", "museum")
WEB = os.path.join(ROOT, "photos", "journeys")
GALLERY = os.path.join(ROOT, "gallery.html")
LONG_EDGE = 1500
QUALITY = 82

# folder -> url slug. Trip order, same as journeys.html.
VENUES = [
    ("프랑스_오르세미술관", "orsay", "Musée d'Orsay, Paris"),
    ("프랑스_루브르박물관", "louvre", "Louvre Museum, Paris"),
    ("프랑스_오랑주리미술관", "orangerie", "Musée de l'Orangerie, Paris"),
    ("프랑스_자크뮈르미술관", "jacquemart-andre", "Musée Jacquemart-André, Paris"),
    ("프랑스_팔레드도쿄", "palais-de-tokyo", "Palais de Tokyo, Paris"),
    ("프랑스_파리부르스드코메르스", "bourse-de-commerce", "Bourse de Commerce, Paris"),
    ("프랑스_펫띠팔레", "petit-palais", "Petit Palais, Paris"),
    ("프랑스_베르사유궁", "versailles", "Palace of Versailles"),
    ("바티칸_바티칸박물관", "vatican", "Vatican Museums, Vatican City"),
    ("이탈리아_판테온", "pantheon", "Pantheon, Rome"),
    ("이탈리아_로마국립현대미술관", "gnam", "Galleria Nazionale d'Arte Moderna, Rome"),
    ("이탈리아_MAXXI현대미술관", "maxxi", "MAXXI, Rome"),
    ("이탈리아_폰테미술관", "ponte", "Ponte, Rome"),
    ("이탈리아_피렌체첸트로스토리카", "centro-storico", "Van Gogh Immersive, Florence"),
    ("이탈리아_우피치미술관", "uffizi", "Uffizi Gallery, Florence"),
    ("이탈리아_밀라노오페라하우스", "scala", "Teatro alla Scala, Milan"),
    ("이탈리아_베네치아비엔날레", "venice-biennale", "Venice Biennale"),
    ("독일_슈타델미술관", "staedel", "Städel Museum, Frankfurt"),
    ("스위스_취리히미술관", "kunsthaus-zurich", "Kunsthaus Zürich"),
    ("日本_오사카엑스포", "expo-osaka", "Expo 2025, Osaka"),
]


def shot_time(path):
    """EXIF capture time. Kakao filenames are transfer times, never shot times."""
    try:
        ex = Image.open(path).getexif()
        raw = ex.get(36867) or ex.get(306)
        if raw:
            return datetime.strptime(raw, "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    return datetime.fromtimestamp(os.path.getmtime(path))


def photos_in(folder):
    d = os.path.join(SRC, folder)
    names = [n for n in os.listdir(d) if n.lower().endswith((".jpg", ".jpeg", ".png"))]
    if not names:
        return []
    return sorted((os.path.join(d, n) for n in names), key=shot_time)


def emit(folder, slug):
    files = photos_in(folder)
    out = os.path.join(WEB, slug)
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out, exist_ok=True)
    dims = []
    for i, f in enumerate(files, 1):
        im = Image.open(f)
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((LONG_EDGE, LONG_EDGE), Image.LANCZOS)
        dest = os.path.join(out, "%03d.jpg" % i)
        im.save(dest, "JPEG", quality=QUALITY, optimize=True, progressive=True)
        dims.append(im.size)
    return dims


def plate(src, w, h):
    return ('    <figure class="jr-plate" role="listitem"><img src="%s" width="%d" '
            'height="%d" alt="" loading="lazy" decoding="async"></figure>' % (src, w, h))


def main():
    articles = []
    total = 0
    for folder, slug, name in VENUES:
        if not os.path.isdir(os.path.join(SRC, folder)):
            raise SystemExit("missing museum folder: %s" % folder)
        dims = emit(folder, slug)
        total += len(dims)
        body = "\n".join(
            plate("photos/journeys/%s/%03d.jpg" % (slug, i + 1), w, h)
            for i, (w, h) in enumerate(dims))
        articles.append('<article class="jr" data-reveal>\n'
                        '  <h3 class="jr-name">%s</h3>\n'
                        '  <div class="jr-rail" role="list">\n%s\n  </div>\n</article>'
                        % (name, body))

    # drop folders from the old classification
    keep = {slug for _, slug, _ in VENUES}
    removed = []
    for d in sorted(os.listdir(WEB)):
        p = os.path.join(WEB, d)
        if os.path.isdir(p) and d not in keep:
            shutil.rmtree(p)
            removed.append(d)

    with open(GALLERY, encoding="utf-8") as fh:
        html = fh.read()
    start = html.index('<div class="jrs">')
    end = html.index('</section>', start)
    block_end = html.rindex('</div>', start, end)
    html = html[:start] + '<div class="jrs">\n' + "\n".join(articles) + "\n" + html[block_end:]

    words = {20: "Twenty", 21: "Twenty-one", 22: "Twenty-two", 23: "Twenty-three",
             24: "Twenty-four", 25: "Twenty-five"}
    html = re.sub(r'<h2>Twenty[^<]*places, 2023&mdash;2026\.</h2>',
                  '<h2>%s places, 2023&mdash;2026.</h2>' % words.get(len(VENUES), str(len(VENUES))),
                  html)
    with open(GALLERY, "w", encoding="utf-8") as fh:
        fh.write(html)

    print("venues=%d photos=%d removed_stale=%d" % (len(VENUES), total, len(removed)))
    if removed:
        print("stale:", ", ".join(removed))


if __name__ == "__main__":
    main()
