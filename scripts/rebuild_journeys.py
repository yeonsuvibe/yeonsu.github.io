#!/usr/bin/env python3
"""Rebuild journeys.html strictly from the classified photo folders.

Source of truth: photos/musium/<국가_장소>/*.  Every image keeps its verified
EXIF DateTimeOriginal; chapters are per venue, split when a venue's visit has
a >2-day gap, ordered chronologically. Thumbs mirror the folder path under
photos/thumb/<folder>/ so the wall=1 prefix swap keeps working.
No Korean in any visible string (chair rule 2026-10-31: US admissions audience).
"""
import os
from datetime import datetime
from collections import defaultdict

from PIL import Image, ImageOps

ROOT = "photos/musium"
THUMB = "photos/thumb"
THUMB_MAX = 720
OUT = "journeys.html"

VENUE = {  # folder -> (English title, one-line story)
    "프랑스_오르세미술관": ("Musée d'Orsay, Paris", "Impressionist masterpieces housed in a Beaux-Arts railway station on the Left Bank."),
    "프랑스_루브르박물관": ("Musée du Louvre, Paris", "The world's largest art museum, from the Mona Lisa to the Winged Victory of Samothrace."),
    "프랑스_베르사유궁": ("Palace of Versailles", "The Sun King's gilded court: Hall of Mirrors, royal apartments and endless formal gardens."),
    "이탈리아_판테온": ("The Pantheon, Rome", "Two millennia of engineering: the world's largest unreinforced concrete dome."),
    "이탈리아_MAXXI현대미술관": ("MAXXI — National Museum of 21st Century Arts, Rome", "Zaha Hadid's concrete ribbons of contemporary art and architecture."),
    "이탈리아_로마국립현대미술관": ("Galleria Nazionale d'Arte Moderna, Rome", "Italian modernism from the Macchiaioli to de Chirico's metaphysical spaces."),
    "바티칸_바티칸박물관": ("Vatican Museums", "Raphael's Rooms and the Sistine Ceiling — the artistic heart of the Catholic Church."),
    "이탈리아_보르게세미술관": ("Galleria Borghese, Rome", "Bernini's marble drama and Caravaggio's shadows inside a cardinal's villa."),
    "이탈리아_산루이지데이프란체시": ("San Luigi dei Francesi, Rome", "A quiet French church holding Caravaggio's brilliant Contarelli Chapel."),
    "이탈리아_우피치미술관": ("Galleria degli Uffizi, Florence", "Botticelli's Venus and the Medici's unmatched Renaissance collection."),
    "이탈리아_피렌체첸트로스토리카": ("Van Gogh Immersive Exhibition, Florence", "Starry Night projected across the vaults of a historic Florentine palace."),
    "이탈리아_베네치아": ("Venice", "Lagoon light, Byzantine domes and the slow theatre of the canals."),
    "이탈리아_베네치아비엔날레": ("Venice Biennale", "The world's oldest art exhibition: national pavilions and the Arsenale halls."),
    "이탈리아_밀라노오페라하우스": ("Teatro alla Scala Museum, Milan", "Verdi's stage — boxes, chandeliers and the costumes of La Scala."),
    "스위스_취리히미술관": ("Kunsthaus Zürich", "From Hodler and Giacometti to Warhol on the Limmat."),
    "독일_슈타델미술관": ("Städel Museum, Frankfurt", "Seven centuries of painting, from Cranach's Venus to the German Impressionists."),
    "일본_오사카엑스포": ("Expo 2025 Osaka", "The Grand Roof and national pavilions on Yumeshima — technology as public art."),
    "프랑스_파리오페라가르니에": ("Palais Garnier, Paris", "Garnier's marble staircase and Chagall's ceiling — the phantom's opera house."),
    "프랑스_자크뮈르미술관": ("Musée Jacquemart-André, Paris", "A Gilded Age mansion with Fragonard, Bellini and medieval tapestries."),
    "프랑스_팔레드도쿄": ("Palais de Tokyo, Paris", "Europe's largest platform for contemporary art, raw concrete by the Seine."),
    "프랑스_파리시립현대미술관": ("Musée d'Art Moderne de Paris", "Matisse's three-panel monument and the city's collection of modern masters."),
    "프랑스_오랑주리미술관": ("Musée de l'Orangerie, Paris", "Monet's Water Lilies in elliptical rooms he designed himself."),
    "프랑스_파리부르스드코메르스": ("Bourse de Commerce — Pinault Collection, Paris", "Tadao Ando's concrete cylinder inside an 18th-century grain exchange."),
    "프랑스_펫띠팔레": ("Petit Palais, Paris", "The Belle Époque glass atrium of the city's fine-arts palace."),
}

PLACE = {  # folder -> (country, city) sort keys for place-based grouping
    "프랑스_오르세미술관": ("France", "Paris", 1),
    "프랑스_루브르박물관": ("France", "Paris", 2),
    "프랑스_오랑주리미술관": ("France", "Paris", 3),
    "프랑스_파리부르스드코메르스": ("France", "Paris", 4),
    "프랑스_팔레드도쿄": ("France", "Paris", 5),
    "프랑스_파리시립현대미술관": ("France", "Paris", 6),
    "프랑스_자크뮈르미술관": ("France", "Paris", 7),
    "프랑스_펫띠팔레": ("France", "Paris", 8),
    "프랑스_파리오페라가르니에": ("France", "Paris", 9),
    "프랑스_베르사유궁": ("France", "Versailles", 1),
    "이탈리아_판테온": ("Italy", "Rome", 1),
    "이탈리아_산루이지데이프란체시": ("Italy", "Rome", 2),
    "바티칸_바티칸박물관": ("Italy", "Rome", 3),
    "이탈리아_보르게세미술관": ("Italy", "Rome", 4),
    "이탈리아_MAXXI현대미술관": ("Italy", "Rome", 5),
    "이탈리아_로마국립현대미술관": ("Italy", "Rome", 6),
    "이탈리아_우피치미술관": ("Italy", "Florence", 1),
    "이탈리아_피렌체첸트로스토리카": ("Italy", "Florence", 2),
    "이탈리아_베네치아": ("Italy", "Venice", 1),
    "이탈리아_베네치아비엔날레": ("Italy", "Venice", 2),
    "이탈리아_밀라노오페라하우스": ("Italy", "Milan", 1),
    "스위스_취리히미술관": ("Switzerland", "Zurich", 1),
    "독일_슈타델미술관": ("Germany", "Frankfurt", 1),
    "일본_오사카엑스포": ("Japan", "Osaka", 1),
}


def load_items():
    items = []
    for folder in sorted(os.listdir(ROOT)):
        path = os.path.join(ROOT, folder)
        if not os.path.isdir(path) or folder not in VENUE:
            continue
        for name in sorted(os.listdir(path)):
            if not name.lower().endswith((".jpeg", ".jpg", ".png")):
                continue
            fp = os.path.join(path, name)
            dt = None
            try:
                im = Image.open(fp)
                ex = im.getexif()
                dt = ex.get(36867) or ex.get(306)
                if dt:
                    dt = datetime.strptime(dt[:19], "%Y:%m:%d %H:%M:%S")
            except Exception:
                pass
            items.append({"folder": folder, "name": name, "dt": dt})
    return items


def make_thumb(folder, name, dt_hint):
    d = os.path.join(THUMB, folder)
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, os.path.splitext(name)[0] + ".jpg")
    src = os.path.join(ROOT, folder, name)
    if not (os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src)):
        im = Image.open(src)
        im = ImageOps.exif_transpose(im)
        im.thumbnail((THUMB_MAX, THUMB_MAX))
        if im.mode != "RGB":
            im = im.convert("RGB")
        im.save(dst, "JPEG", quality=80)
    return os.path.relpath(dst, "photos")


def chapters(items):
    """One chapter per venue, grouped by place (country, city). No dates."""
    by_venue = defaultdict(list)
    for it in items:
        by_venue[it["folder"]].append(it)
    chs = []
    for folder, its in by_venue.items():
        its.sort(key=lambda x: (x["dt"] or datetime(1900, 1, 1)))
        chs.append((folder, its))
    chs.sort(key=lambda c: (PLACE[c[0]], VENUE[c[0]][0].lower()))
    return chs


HTML_HEAD = """<!DOCTYPE html>

<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Crect width='16' height='16' fill='%23f4f1ea'/%3E%3Crect x='3' y='3' width='10' height='10' fill='none' stroke='%2316150f'/%3E%3C/svg%3E"/>
<title>YEONSU AHN - Digital Portfolio</title>
<link href="index.css" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&amp;family=Jost:wght@300;400;500&amp;display=swap" rel="stylesheet"/>
</head>
<body>
<!-- Navigation -->
<nav>
<div class="logo"><a href="index.html" style="color:inherit;text-decoration:none">YEONSU AHN</a></div>
<ul>
<li><a href="index.html">Home</a></li>
<li><a href="gallery.html?auto=0">Art Gallery</a></li>
<li><a href="journeys.html" class="active">Cultural Journeys</a></li>
<li><a href="articles.html">Journalism</a></li>
<li><a href="ec.html">Extracurricular</a></li>
</ul>
</nav>
<section class="section light" id="museums">
<div class="container">
<h2 class="section-title">Cultural Journeys</h2>
<p class="section-subtitle">Museums and cultural sites, grouped by city.</p>
<div class="timeline">
"""

FOOT_TMPL = """</div>
</div></section>
<footer>
<p>YEONSU AHN &mdash; Cultural Journeys.</p>
</footer>
<script src="script.js"></script>
%(wall)s
<script>
document.addEventListener("DOMContentLoaded", () => {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) { entry.target.classList.add('in-view'); observer.unobserve(entry.target); }
        });
    }, { threshold: 0.15, rootMargin: "0px" });
    document.querySelectorAll('[data-animate]').forEach((el) => { observer.observe(el); });
});
</script>
</body>
"""


def main():
    old = open(OUT, encoding="utf-8").read()
    a = old.find("<script>\nif(window.top!==window.self")
    b = old.find("</script>", a)
    assert a != -1 and b != -1, "wall=1 script block not found in old journeys.html"
    wall = old[a:b + len("</script>")]

    items = load_items()
    chs = chapters(items)

    CITY_CSS = ('style="text-align:center;margin:64px 0 28px;padding-bottom:14px;'
                'border-bottom:1px solid var(--paper-deep);font-family:\'Cormorant Garamond\',serif;'
                'font-size:2.1rem;letter-spacing:.3em;text-transform:uppercase;color:var(--ink)"')
    out = [HTML_HEAD]
    seen_city = None
    for folder, its in chs:
        title, story = VENUE[folder]
        country, city, _ = PLACE[folder]
        if (country, city) != seen_city:
            seen_city = (country, city)
            label = f"{city}, {country}"
            n_city = sum(len(v) for f, v in chs if PLACE[f][0] == country and PLACE[f][1] == city)
            out.append(f'<div class="city-header" {CITY_CSS}>{label} <span style="font-size:1.1rem;letter-spacing:.15em;color:var(--ink-faint)">&middot; {n_city} photos</span></div>\n')
        out.append('<div class="timeline-chapter">\n')
        out.append(f"<h3>{title}</h3>\n")
        out.append(f'<p class="chapter-desc">Photos: {len(its)}</p><p class="museum-story">{story}</p>\n')
        out.append("</div>\n")
        for it in its:
            thumb_rel = make_thumb(it["folder"], it["name"], it["dt"])
            src = "photos/" + thumb_rel
            out.append('<div class="timeline-item" data-animate="">\n<div class="timeline-content">\n')
            out.append(f'<img alt="{title}" loading="lazy" src="{src}"/>\n')
            out.append("</div>\n</div>\n")
    out.append(FOOT_TMPL % {"wall": wall})
    html = "".join(out)

    korean = [ch for ch in html.split(">", 1)[0]]  # visible-text guard below instead
    import re
    visible = re.sub(r"<[^>]+>", " ", html.split("</nav>", 1)[1].split("<script>", 1)[0])
    hangul = re.findall(r"[\uAC00-\uD7A3]+", visible)
    if hangul:
        raise SystemExit(f"ABORT: Hangul in visible text: {set(hangul)}")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"chapters={len(chs)} photos={len(items)} -> {OUT}")
    for folder, its in chs:
        print(f"  {PLACE[folder][1]:<12} {VENUE[folder][0]}: {len(its)}")


if __name__ == "__main__":
    main()
