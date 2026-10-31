#!/usr/bin/env python3
"""Rebuild journeys.html from the reclassified photos/museum folders.

Source of truth: one subfolder of photos/museum per venue, Korean folder name.
The folder name never reaches the page; VENUE maps it to the English name the
US-admissions audience reads, plus a one- or two-line introduction.

Chair rules still enforced here:
  - no Korean in any visible string
  - no per-photo dates or counts of anything but photos
  - every served image is a derivation under photos/thumb/<folder>/<stem>.jpg
"""
import os
import re
from datetime import datetime
from PIL import Image, ImageOps

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "photos", "museum")
THUMB = os.path.join(ROOT, "photos", "thumb")
OUT = os.path.join(ROOT, "journeys.html")
THUMB_MAX = 720

# folder -> (English name shown as the chapter heading, introduction kept under two lines)
VENUE = {
    "프랑스_오르세미술관": (
        "Musée d'Orsay, Paris",
        "Impressionist masterpieces in a Beaux-Arts railway station on the Left Bank."),
    "프랑스_루브르박물관": (
        "Musée du Louvre, Paris",
        "The world's largest art museum, from the Mona Lisa to the Winged Victory."),
    "프랑스_오랑주리미술관": (
        "Musée de l'Orangerie, Paris",
        "Monet's Water Lilies in the two elliptical rooms he designed himself."),
    "프랑스_자크뮈르미술관": (
        "Musée Jacquemart-André, Paris",
        "A banker's private mansion, still hung the way its collectors left it."),
    "프랑스_팔레드도쿄": (
        "Palais de Tokyo, Paris",
        "Raw concrete and no permanent collection — Paris at its most experimental."),
    "프랑스_파리부르스드코메르스": (
        "Bourse de Commerce, Paris",
        "Tadao Ando's concrete cylinder inside the old grain exchange, now Pinault's collection."),
    "프랑스_펫띠팔레": (
        "Petit Palais, Paris",
        "A Beaux-Arts palace built for the 1900 World's Fair, with a gilded courtyard garden."),
    "프랑스_베르사유궁": (
        "Palace of Versailles",
        "The Sun King's court: the Hall of Mirrors, royal apartments and formal gardens."),
    "바티칸_바티칸박물관": (
        "Vatican Museums, Rome",
        "Papal collections along the Belvedere, ending at the Sistine Chapel ceiling."),
    "이탈리아_판테온": (
        "Pantheon, Rome",
        "A second-century temple whose open oculus still lights the original marble floor."),
    "이탈리아_로마국립현대미술관": (
        "Galleria Nazionale d'Arte Moderna, Rome",
        "Italy's national modern collection, from the Macchiaioli to the twentieth century."),
    "이탈리아_MAXXI현대미술관": (
        "MAXXI, Rome",
        "Zaha Hadid's concrete-and-steel museum for twenty-first-century art, in Flaminio."),
    "이탈리아_폰테미술관": (
        "Ponte, Rome",
        "Walk-through rooms of neon, projected crystal and hand-painted lines on the walls."),
    "이탈리아_피렌체첸트로스토리카": (
        "Van Gogh Immersive, Florence",
        "Starry Night and the sunflowers thrown across the stone of an old Florentine interior."),
    "이탈리아_우피치미술관": (
        "Galleria degli Uffizi, Florence",
        "Botticelli's Venus and the Medici's unmatched Renaissance collection."),
    "이탈리아_밀라노오페라하우스": (
        "Teatro alla Scala, Milan",
        "The 1778 opera house where Verdi and Tosca premiered — gilded boxes and red velvet."),
    "이탈리아_베네치아비엔날레": (
        "La Biennale di Venezia",
        "The Giardini and Arsenale pavilions, where each country stages its own answer."),
    "독일_슈타델미술관": (
        "Städel Museum, Frankfurt",
        "Seven centuries under one roof, from Cranach to the German Romantics and on to Baselitz."),
    "스위스_취리히미술관": (
        "Kunsthaus Zürich",
        "Switzerland's largest art museum: Monet and Munch through to Warhol on the Limmat."),
    "日本_오사카엑스포": (
        "Expo 2025, Osaka",
        "The Yumeshima island expo: national pavilions, mass timber and the Grand Ring."),
}

# itinerary order, not alphabetical: the page reads as the trip happened
CITIES = [
    ("Paris, France", ["프랑스_오르세미술관", "프랑스_루브르박물관", "프랑스_오랑주리미술관",
                       "프랑스_자크뮈르미술관", "프랑스_팔레드도쿄", "프랑스_파리부르스드코메르스",
                       "프랑스_펫띠팔레"]),
    ("Versailles, France", ["프랑스_베르사유궁"]),
    ("Vatican City", ["바티칸_바티칸박물관"]),
    ("Rome, Italy", ["이탈리아_판테온", "이탈리아_로마국립현대미술관",
                     "이탈리아_MAXXI현대미술관", "이탈리아_폰테미술관"]),
    ("Florence, Italy", ["이탈리아_피렌체첸트로스토리카", "이탈리아_우피치미술관"]),
    ("Milan, Italy", ["이탈리아_밀라노오페라하우스"]),
    ("Venice, Italy", ["이탈리아_베네치아비엔날레"]),
    ("Frankfurt, Germany", ["독일_슈타델미술관"]),
    ("Zurich, Switzerland", ["스위스_취리히미술관"]),
    ("Osaka, Japan", ["日本_오사카엑스포"]),
]

CITY_HEAD = ('<div class="city-header" style="text-align:center;margin:64px 0 28px;'
             'padding-bottom:14px;border-bottom:1px solid var(--paper-deep);'
             "font-family:'Cormorant Garamond',serif;font-size:2.1rem;letter-spacing:.3em;"
             'text-transform:uppercase;color:var(--ink)">{city} '
             '<span style="font-size:1.1rem;letter-spacing:.15em;color:var(--ink-faint)">'
             '&middot; {n} photos</span></div>')


def shot_time(path):
    """EXIF capture time. Kakao filenames are transfer times, never shot times."""
    try:
        ex = Image.open(path).getexif()
    except Exception:
        return None
    raw = ex.get(36867) or ex.get(306)
    if not raw:
        return None
    try:
        return datetime.strptime(raw[:19], "%Y:%m:%d %H:%M:%S")
    except ValueError:
        return None


def make_thumb(folder, name):
    d = os.path.join(THUMB, folder)
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, os.path.splitext(name)[0] + ".jpg")
    src = os.path.join(SRC, folder, name)
    if not (os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src)):
        im = ImageOps.exif_transpose(Image.open(src))
        im.thumbnail((THUMB_MAX, THUMB_MAX))
        if im.mode != "RGB":
            im = im.convert("RGB")
        im.save(dst, "JPEG", quality=80)
    return os.path.relpath(dst, ROOT).replace(os.sep, "/")


def collect(folder):
    d = os.path.join(SRC, folder)
    if not os.path.isdir(d):
        return []
    out = []
    for name in sorted(os.listdir(d)):
        if not name.lower().endswith((".jpeg", ".jpg", ".png")):
            continue
        out.append({"name": name, "dt": shot_time(os.path.join(d, name))})
    out.sort(key=lambda it: (it["dt"] or datetime(1900, 1, 1), it["name"]))
    return out


def build():
    blocks, total, unknown = [], 0, []
    for city, folders in CITIES:
        present = [(f, collect(f)) for f in folders]
        present = [(f, its) for f, its in present if its]
        if not present:
            continue
        blocks.append(CITY_HEAD.format(city=city, n=sum(len(i) for _, i in present)))
        for folder, its in present:
            if folder not in VENUE:
                unknown.append(folder)
                continue
            title, story = VENUE[folder]
            blocks.append('<div class="timeline-chapter">')
            blocks.append("<h3>%s</h3>" % title)
            blocks.append('<p class="chapter-desc">Photos: %d</p>'
                          '<p class="museum-story">%s</p>' % (len(its), story))
            blocks.append("</div>")
            for it in its:
                thumb = make_thumb(folder, it["name"])
                blocks.append('<div class="timeline-item" data-animate="">')
                blocks.append('<div class="timeline-content">')
                blocks.append('<img alt="%s" loading="lazy" src="%s"/>'
                              % (title.replace('"', "&quot;"), thumb))
                blocks.append("</div>")
                blocks.append("</div>")
            total += len(its)
    return "\n".join(blocks), total, unknown


def main():
    body, total, unknown = build()
    if unknown:
        raise SystemExit("ABORT: folder without an English name: %s" % unknown)

    page = open(OUT, encoding="utf-8").read()
    head, rest = page.split('<div class="timeline">', 1)
    tail = "</div>\n</div></section>" + rest.split("</div>\n</div></section>", 1)[1]
    html = head + '<div class="timeline">\n' + body + "\n" + tail

    visible = re.sub(r"<[^>]+>", " ", html.split("</nav>", 1)[1].split("<script>", 1)[0])
    hangul = re.findall(r"[\uAC00-\uD7A3]+", visible)
    if hangul:
        raise SystemExit("ABORT: Hangul in visible text: %s" % set(hangul))

    srcs = re.findall(r'src="(photos/thumb/[^"]+)"', html)
    missing = [s for s in srcs if not os.path.exists(os.path.join(ROOT, s))]

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("photos=%d img=%d missing_files=%d chapters=%d"
          % (total, len(srcs), len(missing), html.count("timeline-chapter")))
    for m in missing[:5]:
        print("  MISSING", m)
    if missing:
        raise SystemExit("ABORT: %d referenced thumbs do not exist" % len(missing))


if __name__ == "__main__":
    main()
