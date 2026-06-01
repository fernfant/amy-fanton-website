"""
Audit every Journal post's hero/cover image so mismatches are easy to eyeball.

For each blog/<slug>.html (excluding index.html) it extracts the category
(eyebrow), title (h1) and hero <img> src, resolves the file on disk, and:
  1. prints a text table (slug | category | hero filename | flags)
  2. builds labeled contact sheets at /tmp/<out>_NN.png — each cell shows the
     hero photo with "NN slug [category]" so you can scan for wrong subjects
     (e.g. a bride on a newborn post), the studio logo, or missing heroes.

Heuristic text flags (NOT a substitute for looking — they just pre-sort):
  NO-HERO   post has no <div class="post-hero">
  LOGO?     hero filename/look suggests the studio logo (amylogo / 'logo')
  TINY      hero image < 600px on its long edge (often a placeholder/logo)

Run:  /tmp/pilenv/bin/python3 .claude/skills/audit_post_heroes/audit_covers.py
      [--out /tmp/cover_audit] [--per 12] [--cols 4]
"""
import re, sys, html, pathlib
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[3]
BLOG = ROOT / "blog"

def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default

OUT = arg("--out", "/tmp/cover_audit")
PER = int(arg("--per", "12"))
COLS = int(arg("--cols", "4"))

def field(pat, t):
    m = re.search(pat, t, re.S)
    return html.unescape(re.sub(r"\s+", " ", m.group(1)).strip()) if m else ""

posts = []
for p in sorted(BLOG.glob("*.html")):
    if p.name == "index.html":
        continue
    t = p.read_text(errors="ignore")
    cat = field(r'<p class="eyebrow">(.*?)</p>', t)
    title = field(r'<h1 class="post-title">(.*?)</h1>', t)
    m = re.search(r'<div class="post-hero"><img src="([^"]+)"', t)
    hero = m.group(1) if m else None
    flags = []
    fp = None
    if not hero:
        flags.append("NO-HERO")
    else:
        fp = (p.parent / hero).resolve()
        name = fp.name.lower()
        if "logo" in name or "amylogo" in name:
            flags.append("LOGO?")
        try:
            with Image.open(fp) as im:
                if max(im.size) < 600:
                    flags.append("TINY")
        except Exception:
            flags.append("MISSING-FILE")
    posts.append(dict(slug=p.stem, cat=cat, title=title, hero=hero, fp=fp, flags=flags))

# text table
w = max(len(x["slug"]) for x in posts)
print(f"\n{len(posts)} posts\n" + "-" * 80)
for i, x in enumerate(posts):
    fn = x["fp"].name if x["fp"] else "—"
    fl = (" ⚑ " + ",".join(x["flags"])) if x["flags"] else ""
    print(f'{i:2} {x["slug"]:<{w}}  [{x["cat"]:<20}] {fn}{fl}')
flagged = [x for x in posts if x["flags"]]
print("-" * 80)
print(f'{len(flagged)} auto-flagged: ' + ", ".join(x["slug"] for x in flagged) if flagged else "no auto-flags")

# contact sheets
THUMB, PAD, LABEL = 360, 12, 30
def load(fp):
    try:
        im = Image.open(fp).convert("RGB"); im.thumbnail((THUMB, THUMB)); return im
    except Exception:
        im = Image.new("RGB", (THUMB, THUMB // 2), (220, 210, 210))
        ImageDraw.Draw(im).text((10, 10), "missing", fill=(120, 0, 0)); return im

sheets = [posts[i:i + PER] for i in range(0, len(posts), PER)]
for s, group in enumerate(sheets, 1):
    rows = (len(group) + COLS - 1) // COLS
    cw, ch = THUMB + PAD, THUMB + LABEL + PAD
    canvas = Image.new("RGB", (COLS * cw + PAD, rows * ch + PAD), (250, 249, 247))
    dr = ImageDraw.Draw(canvas)
    for j, x in enumerate(group):
        idx = (s - 1) * PER + j
        r, c = divmod(j, COLS)
        ox, oy = PAD + c * cw, PAD + r * ch
        thumb = load(x["fp"]) if x["fp"] else Image.new("RGB", (THUMB, 80), (235, 230, 225))
        canvas.paste(thumb, (ox, oy + LABEL))
        lab = f'{idx} {x["slug"]}'[:42]
        sub = f'[{x["cat"]}]' + (" ⚑" + ",".join(x["flags"]) if x["flags"] else "")
        dr.text((ox + 2, oy + 2), lab, fill=(20, 20, 20))
        dr.text((ox + 2, oy + 15), sub[:46], fill=(150, 30, 30) if x["flags"] else (110, 110, 110))
    f = f"{OUT}_{s:02d}.png"
    canvas.save(f)
    print("wrote", f)
