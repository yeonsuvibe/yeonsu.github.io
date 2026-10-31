#!/usr/bin/env python3
"""Report whether the web photo sets still match photos/museum.

journeys.html reads photos/thumb/<folder>, gallery.html reads photos/journeys/<slug>.
Both were built from earlier classifications at different times, so this checks three
things: every referenced image exists, every thumb folder still has a museum folder,
and no photo in photos/museum is missing from the thumb set.
"""
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUSEUM = os.path.join(ROOT, "photos", "museum")
THUMB = os.path.join(ROOT, "photos", "thumb")
WEB = os.path.join(ROOT, "photos", "journeys")
EXTS = (".jpg", ".jpeg", ".png")


def refs(page, prefix):
    with open(os.path.join(ROOT, page), encoding="utf-8") as fh:
        return re.findall(r'src="(%s/[^"]+)"' % prefix, fh.read())


def main():
    for page, prefix in (("journeys.html", "photos/thumb"), ("gallery.html", "photos/journeys")):
        r = refs(page, prefix)
        missing = [x for x in r if not os.path.exists(os.path.join(ROOT, x))]
        print("%-14s refs=%-4d unique=%-4d missing=%d" % (page, len(r), len(set(r)), len(missing)))
        for m in missing[:10]:
            print("   MISS %s" % m)

    museum_dirs = sorted(d for d in os.listdir(MUSEUM) if os.path.isdir(os.path.join(MUSEUM, d)))
    thumb_dirs = sorted(d for d in os.listdir(THUMB) if os.path.isdir(os.path.join(THUMB, d)))
    stale = [d for d in thumb_dirs if d not in museum_dirs]
    absent = [d for d in museum_dirs if d not in thumb_dirs]
    print("thumb folders=%d museum folders=%d stale=%d absent=%d"
          % (len(thumb_dirs), len(museum_dirs), len(stale), len(absent)))
    for d in stale:
        n = len(glob.glob(os.path.join(THUMB, d, "*")))
        print("   STALE thumb/%s (%d files)" % (d, n))
    for d in absent:
        print("   ABSENT thumb/%s" % d)

    # every museum photo needs a thumb beside it
    need = 0
    for d in museum_dirs:
        src = os.path.join(MUSEUM, d)
        if not os.path.isdir(src):
            continue
        for n in os.listdir(src):
            if n.lower().endswith(EXTS):
                stem = os.path.splitext(n)[0]
                if not os.path.exists(os.path.join(THUMB, d, stem + ".jpg")):
                    need += 1
    print("museum photos lacking a thumb:", need)

    loose = [f for f in glob.glob(os.path.join(THUMB, "*")) if os.path.isfile(f)]
    used = set(refs("journeys.html", "photos/thumb"))
    unused = [os.path.basename(f) for f in loose if "photos/thumb/" + os.path.basename(f) not in used]
    print("loose files at thumb root=%d unreferenced=%d" % (len(loose), len(unused)))

    web_dirs = sorted(d for d in os.listdir(WEB) if os.path.isdir(os.path.join(WEB, d)))
    print("web set folders=%d files=%d"
          % (len(web_dirs), len(glob.glob(os.path.join(WEB, "*", "*")))))


if __name__ == "__main__":
    main()
