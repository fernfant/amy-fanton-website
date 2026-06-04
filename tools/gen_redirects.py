#!/usr/bin/env python3
"""Generate redirect stubs for old WordPress URLs that 404 on the new site.

Old site used root-level /<slug>/ permalinks + /category/<x>/ pages; the new
static site uses /blog/<slug>.html. Google still has the old URLs indexed, so
they 404 and waste their ranking equity. This writes a tiny meta-refresh +
canonical stub at each old path pointing to the right new page, so Google
consolidates the old URL into the new one.

Re-run after adding/renaming posts:  python3 tools/gen_redirects.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://www.fantonphotography.com"

# old slug -> new page, for posts that were renamed
RENAMES = {
    "santorini-elopement": "/blog/santorini-elopement-photos.html",
    "elegant-old-word-argentina-bridal-shoot": "/blog/tigre-argentina-wedding-photography.html",
    "hermione-harbutt-2015-collection-london-wedding-photography-at-westonbirt-2": "/blog/westonbirt-wedding-photography.html",
}

# old non-post pages -> best new destination
SECTIONS = {
    "contact": "/enquire.html",
    "inquiries": "/enquire.html",
    "pricing": "/about.html",
    "prices-2": "/about.html",
    "investment": "/about.html",
    "experience": "/about.html",
    "family-photography-pricin": "/about.html",
    "portrait-photography-experienc": "/about.html",
    "portfolio": "/blog/index.html",
    "portfolio-2": "/blog/index.html",
    "gallery": "/blog/index.html",
    "wedding-blog": "/blog/index.html",
    "london-family-photographer-blog": "/blog/index.html",
    "portrait-photography": "/blog/index.html",
    "fashion-photography-in-london": "/blog/index.html",
    "londonweddingphotographer": "/",
    "london-family-photographer": "/blog/index.html#family",
    "wedding-photography": "/",
    "wedding-engagements": "/blog/index.html#wedding",
    "lifestyle-pregnancy-photography-london": "/blog/index.html#newborn",
    "boudoir-maternity-photography-in-london": "/blog/index.html#newborn",
    "boudoir-maternity-session-london": "/blog/index.html#newborn",
    "hyde-park-maternity-photography-london-pregnancy-photographer": "/blog/hyde-park-maternity-shoot.html",
}

# old /category/<x>/ -> portfolio section
CATEGORIES = {
    "wedding": "#wedding", "couples": "#wedding", "featured-work": "#wedding",
    "family": "#family", "children": "#family",
    "newborn": "#newborn", "maternity": "#newborn",
    "recent-sessions": "", "specials": "", "uncategorized": "",
}

STUB = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Redirecting — Amy Fanton Photography</title>
  <link rel="canonical" href="{canon}" />
  <meta http-equiv="refresh" content="0; url={target}" />
  <script>location.replace("{target}");</script>
</head>
<body><p>Redirecting to <a href="{target}">Amy Fanton Photography</a>…</p></body>
</html>
"""

# real top-level names we must never shadow with a redirect dir
RESERVED = {"blog", "images", "fonts", "about", "press", "enquire", "index",
            "wedding-photography", "wedding-engagements", "favicon", "robots"}

def canon_url(target):
    t = target.split("#")[0]
    return BASE + ("/" if t == "/" else t)

def write_stub(path_dir, target):
    out = ROOT / path_dir
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(STUB.format(target=BASE + target if target.startswith("/") else target,
                                                 canon=canon_url(target)))

def main():
    new_slugs = sorted(f.stem for f in (ROOT / "blog").glob("*.html") if f.stem != "index")
    n = 0
    # 1) every new post gets a root-level /<slug>/ redirect (covers all matching old URLs)
    for s in new_slugs:
        if s in RESERVED:
            continue
        write_stub(s, f"/blog/{s}.html"); n += 1
    # 2) renamed posts
    for old, target in RENAMES.items():
        write_stub(old, target); n += 1
    # 3) old section/landing pages
    for old, target in SECTIONS.items():
        if old in RESERVED and old not in ("wedding-photography", "wedding-engagements"):
            continue
        write_stub(old, target); n += 1
    # 4) old category pages
    for cat, frag in CATEGORIES.items():
        write_stub(f"category/{cat}", f"/blog/index.html{frag}"); n += 1

    print(f"wrote {n} redirect stubs ({len(new_slugs)} posts + {len(RENAMES)} renames "
          f"+ {len(SECTIONS)} sections + {len(CATEGORIES)} categories)")

if __name__ == "__main__":
    main()
