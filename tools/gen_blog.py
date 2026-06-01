import json, re, shutil, pathlib, html, urllib.parse
from PIL import Image

_dim_cache = {}
def dims(rel):
    if rel not in _dim_cache:
        try:
            with Image.open(ROOT/rel) as im: _dim_cache[rel] = f' width="{im.size[0]}" height="{im.size[1]}"'
        except Exception: _dim_cache[rel] = ""
    return _dim_cache[rel]

def og_image(src_rel, out_rel, W=1200, H=630):
    """Center-crop src image to a 1200x630 landscape share card. Returns out_rel or None."""
    try:
        src = ROOT/src_rel
        if not src.exists(): return None
        out = ROOT/out_rel; out.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(src) as im:
            im = im.convert("RGB")
            w, h = im.size
            scale = max(W/w, H/h)
            nw, nh = int(w*scale+0.5), int(h*scale+0.5)
            im = im.resize((nw, nh), Image.LANCZOS)
            l = (nw-W)//2
            t = int((nh-H)*0.18)  # bias toward top so faces survive on full-length portraits
            im.crop((l, t, l+W, t+H)).save(out, "JPEG", quality=85)
        return out_rel
    except Exception:
        return None

ROOT = pathlib.Path("/Users/fernando/Projects/amy-fanton-website")
BASE = "https://www.fantonphotography.com/"

def page_title(b):
    """SEO title ≤ ~60 chars: keep the studio suffix only if it fits."""
    base = b["title"].strip()
    for suffix in (" — Amy Fanton Photography", " · Amy Fanton", ""):
        if len(base + suffix) <= 60:
            return base + suffix
    return base  # base itself is long; use as-is (give it a TITLE_OVERRIDE to shorten)

def meta_desc(b):
    """Unique meta description = the post's first real sentence (~155 chars)."""
    for kind, txt in b.get("paras", []):
        t = re.sub(r"\s+", " ", txt).strip()
        if len(t) >= 50:
            if len(t) > 155:
                t = t[:152].rsplit(" ", 1)[0] + "…"
            return t
    return b["title"] + " — wedding and portrait photography by Amy Fanton."

def post_schema(b, url, ogimg, desc):
    """Article + BreadcrumbList JSON-LD for a Journal post."""
    pub = {"@type": "Organization", "name": "Amy Fanton Photography",
           "logo": {"@type": "ImageObject", "url": BASE + "icon-512.png"}}
    article = {"@context": "https://schema.org", "@type": "Article",
               "headline": b["title"], "image": ogimg, "description": desc,
               "author": pub, "publisher": pub, "mainEntityOfPage": url}
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", b.get("date_iso", "") or ""):
        article["datePublished"] = b["date_iso"]
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList",
              "itemListElement": [
                  {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE},
                  {"@type": "ListItem", "position": 2, "name": "Journal", "item": BASE + "blog/index.html"},
                  {"@type": "ListItem", "position": 3, "name": b["title"], "item": url}]}
    return ('<script type="application/ld+json">' + json.dumps(article) + "</script>\n    "
            '<script type="application/ld+json">' + json.dumps(crumbs) + "</script>")
IMG  = ROOT/"images/blog"
GAL  = IMG/"gallery"
BLOGDIR = ROOT/"blog"
FEAT = pathlib.Path("/tmp/feat_imgs")
NEW_SRC = ROOT/"Vault/Wayback-Recovered"
POSTS = {p["slug"]: p for p in json.load(open("/tmp/blog_data/posts.json"))}
try:
    NEWTEXT = json.load(open("/tmp/blog_data/new_text.json"))
except FileNotFoundError:
    NEWTEXT = {}

# clean up a few harvested titles
TITLE_OVERRIDE = {
 "american-family-photographer-in-london": "An American Family in London",
 "june-20-2013": "Little Ladies at Harkness",
 "mr-charming-june-21-2013": "Mr. Charming",
 "party-of-six-in-stonington-ct-june-22-2013": "Party of Six in Stonington",
 "three-is-the-magic-number-wilcox-park-ri": "Three is the Magic Number",
 "pregnancy-photography-session-hampstead-heath-london": "A Hampstead Heath Maternity Shoot",
}
GAL.mkdir(parents=True, exist_ok=True)
BLOGDIR.mkdir(exist_ok=True)

def esc(s): return html.escape(s, quote=True)

CUR = [
 ("santorini-elopement-photos","text","Weddings","santorini",None,None,"A Santorini Elopement",None),
 ("louise-roe-dorney-court-wedding","text","Weddings","louiseroe",None,None,None,None),
 ("chelsea-engagement-photos","text","Engagements",None,None,None,None,None),
 ("venice-wedding-photography","text","Weddings",None,
   "Eeek — waking up to another feature on Rock My Wedding, where they called this one of their favourite shoots they’ve ever shown! Still pinching myself.",None,None,None),
 ("coastal-bridal-shoot","text","Inspiration",None,
   "A bit longer in CT than expected and my camera was calling my name — a sneak peek of yesterday’s dreamy sunset bridal session, m’dears!",None,None,None),
 ("christmas-hengrave-hall-wedding-photography","text","Weddings",None,None,None,None,None),
 ("surrey-wedding-photography-mayfield-lavender-wedding-inspiration","text","Inspiration","lavender-fields",
   "Is anyone else dreaming of spring? Counting down the days until these gorgeous fields are in bloom again — in case you missed my Mayfield Lavender shoot on Rock My Wedding!",None,None,None),
 ("london-wedding-photographer-in-los-angeles","text","Weddings","losangeles",None,None,None,None),
 ("westonbirt-wedding-photography","text","Inspiration","hermione-lmd",
   "So beyond thrilled to see some of my work featured on Love My Dress today — the gorgeous Hermione Harbutt 2015 collection of nature-inspired headpieces and hair vines!",None,
   "Hermione Harbutt 2015 Collection",None),
 ("european-destination-wedding-photography-in-greece","text","Weddings",None,None,None,None,None),
 ("flower-field-engagement-session-london-engagement-photography","text","Engagements","flowerfield",None,None,None,None),
 ("iconic-london-family-photography","text","Family",None,
   "How picture perfect is this family?! More from this iconic London mini session — walking across Westminster Bridge with Big Ben behind them.",None,"Westminster London Family Photography",None),
 ("kensington-newborn-photography","text","Newborn & Maternity",None,None,None,None,None),
 ("hyde-park-maternity-shoot","text","Family",None,None,None,None,None),
 ("elegant-old-word-argentina-bridal-shoot","text","Weddings","argentina-elopement",
   "I’ve done my own little blog post on the elegant Argentinian bridal shoot — pop over and take a look at some of my favourites from this dreamy day!",None,
   "An Elegant Argentinian Bridal Shoot",None),
 ("richmond-park-family-shoot","text","Family",None,None,None,None,None),
 ("london-autumn-maternity-shoot","text","Newborn & Maternity",None,None,None,None,None),
 ("newborn-photography-in-london","text","Newborn & Maternity",None,None,None,None,None),
 ("london-wedding-photographer-in-buenos-aires-wedding-at-the-lowlands","text","Weddings","ba",None,None,None,None),
 ("ritz-london-wedding-photographer","text","Weddings","ritz",None,None,None,None),
 ("london-wedding-photography-at-the-mortons-club","text","Weddings",None,None,None,None,None),
 ("best-proposal-photography-ideas","text","Engagements","proposal",None,None,None,None),
 ("maria-and-keith","gallery","Weddings","maria-keith",None,"2017",
   "Maria & Keith",
   "Maria and Keith’s elegant celebration, full of warmth and easy romance. Featured on Rock My Wedding."),
 ("northumberland-country-garden-wedding","gallery","Weddings","sassi-holford-northumberland",None,"2016",
   "An English Country Garden Wedding",
   "A pastel-hued English country garden wedding in Northumberland, the bride in Sassi Holford. Featured on Love My Dress."),
 ("neon-bright-pimlico-road","gallery","Inspiration","neon-pimlico",None,"2017",
   "Neon Bright at No. 11 Pimlico Road",
   "A modern, colour-drenched editorial shoot at No. 11 Pimlico Road — bold neon brights against classic London elegance. Featured on Rock My Wedding."),
 ("blush-pink-beach-inspiration","gallery","Inspiration","blush-pink-beach",None,"2016",
   "Blush Pink Beach Inspiration",
   "Soft blush tones and sea breeze — a romantic beachside bridal inspiration shoot. Featured on B.Loved."),
 ("lake-annecy-wedding-in-talloires","gallery","Weddings","lakeannecy",
   "A spring wedding on the shores of Lake Annecy, beneath the snow-capped peaks of the French Alps.",
   "2018-12-11","A Lake Annecy Wedding in Talloires",
   "The couple married at the historic L'Abbaye de Talloires, the bride in a delicate long-sleeved lace gown by Suzanne Neville. Their celebration wove together English and Kenyan family traditions, framed by the still water and mountains of Haute-Savoie. Featured on Style Me Pretty."),
 ("modern-french-chateau-wedding-courcelles-le-roy","gallery","Weddings","chateau",
   "A modern celebration at Château Courcelles Le Roy in the French countryside.",
   "2018-11-21","A Modern French Château Wedding",
   "Golden-hour portraits across the château grounds — the groom in a sharp blue suit, the bride in lace — with soft peach and gold woven through the flowers, stationery and styling. Featured on Style Me Pretty."),
 ("elegant-argentinian-inspiration-shoot","gallery","Inspiration","argentina-inspiration",
   "A bright, contemporary Argentinian inspiration shoot in the airy interiors of Buenos Aires.",
   "2015-05-06","An Elegant Argentinian Inspiration Shoot",
   "Soft beaded gowns against hand-painted majolica tiles, with greenery, succulents and clean, modern tablescapes — a fresh, light-filled counterpoint to old-world romance. Featured on Style Me Pretty."),
 ("nature-inspired-bridal-hair-accessories","gallery","Inspiration","hermione",
   "A fine-art editorial of nature-inspired bridal hair vines and headpieces, shot for Hermione Harbutt.",
   "2015-09-16","Nature-Inspired Bridal Hair Accessories",
   "Delicate floral hair vines, jewelled headpieces and pins styled with soft lace gowns across an English manor and its gardens — a romantic study in bridal detail. Featured on Love My Dress."),
]

def clean_para(t): return re.sub(r"\s+"," ",t).strip()

def clean_title(t):
    t = re.split(r'\s*[-–—|]{1,2}\s*', t)[0]
    t = re.split(r'\s+by\s+', t, flags=re.I)[0]
    return re.sub(r'\s+', ' ', t).strip()

def split_paras(t, target=300, hard=520):
    # Break a long single blob into readable paragraphs at sentence boundaries.
    if len(t) <= hard: return [t]
    sents = re.split(r'(?<=[.!?”’])\s+', t)
    out, cur = [], ""
    for s in sents:
        if cur and len(cur) + 1 + len(s) > hard:
            out.append(cur); cur = ""
        cur = (cur + " " + s).strip() if cur else s
        if len(cur) >= target:
            out.append(cur); cur = ""
    if cur:
        if out and len(cur) < 120: out[-1] += " " + cur
        else: out.append(cur)
    return out

def valid_jpeg(p):
    try:
        with open(p,"rb") as f: return f.read(3)==b"\xff\xd8\xff"
    except Exception: return False

def copy_gallery(slug, src):
    src = pathlib.Path(src)
    if not src.exists(): return []
    out = GAL/slug; out.mkdir(parents=True, exist_ok=True)
    files = sorted([f for f in src.iterdir() if f.suffix.lower() in (".jpg",".jpeg",".png")])
    res=[]
    i=0
    for f in files:
        if not valid_jpeg(f): continue
        dest = out/f"{i:02d}.jpg"; shutil.copy(f, dest); i+=1
        res.append(f"images/blog/gallery/{slug}/{dest.name}")
    return res

MONTHS=["","January","February","March","April","May","June","July","August","September","October","November","December"]
def disp_date(iso):
    m=re.match(r"(\d{4})-(\d{2})-(\d{2})",iso or "")
    if not m: return iso or ""
    y,mo,d=m.groups(); return f"{int(d)} {MONTHS[int(mo)]} {y}"

NAV = '''<header class="site-header" id="top">
    <nav class="nav">
      <a href="../index.html#portfolio" class="nav-link">Portfolio</a>
      <a href="index.html" class="nav-link">Journal</a>
      <a href="../index.html#about" class="nav-link">About</a>
      <a href="../index.html#press" class="nav-link">Press</a>
      <a href="../index.html#contact" class="nav-link">Contact</a>
      <a href="https://www.instagram.com/amyfanton/" target="_blank" rel="noopener" class="nav-link">Instagram</a>
    </nav>
  </header>'''
FOOTER = '''<footer class="site-footer">
    <p class="footer-brand">Amy Fanton Photography</p>
    <p class="footer-note">Fine Art Wedding &amp; Portrait Photography &middot; London &amp; Worldwide</p>
    <p class="footer-copy">&copy; <span id="year"></span> Amy Fanton Photography. All rights reserved.</p>
  </footer>'''
HEAD = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <link rel="canonical" href="{canonical}" />
  <meta name="theme-color" content="#2b2724" />
  <link rel="icon" href="/favicon.ico" sizes="any" />
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png" />
  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
  <link rel="manifest" href="/site.webmanifest" />
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="Amy Fanton Photography" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:image" content="{ogimage}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{title}" />
  <meta name="twitter:image" content="{ogimage}" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Allura&family=Open+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Theano+Didot&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="../styles.css?v=131" />
</head>
<body>
  {nav}
'''

built=[]
for slug,kind,cat,gdir,fb,dov,tov,iov in CUR:
    p = POSTS.get(slug, {})
    title = tov or p.get("title") or slug.replace("-"," ").title()
    date_iso = dov or p.get("date") or ""
    is_year = bool(re.fullmatch(r"\d{4}", date_iso or ""))
    gallery = copy_gallery(slug, FEAT/gdir) if gdir else []
    cover_fs = IMG/f"{slug}.jpg"
    cover = f"images/blog/{slug}.jpg" if valid_jpeg(cover_fs) else (gallery[0] if gallery else None)
    if not cover:
        print(f"  SKIP (no valid cover): {slug}")
        continue
    paras=[]
    if fb: paras.append(("fb", clean_para(fb)))
    if kind=="text":
        for para in p.get("paras",[]):
            cp=clean_para(para)
            if len(cp)<=40: continue
            if re.search(r"(please contact me|if you'?d like to discuss|get in touch).{0,80}(@|\d{6,})", cp, re.I): continue
            for sp in split_paras(cp): paras.append(("p",sp))
    elif iov:
        paras.append(("p", clean_para(iov)))
    built.append(dict(slug=slug,title=title,cat=cat,date_iso=date_iso,is_year=is_year,
                      cover=cover,gallery=gallery,paras=paras))

built_slugs = {b["slug"] for b in built}
new_built = 0
for slug, rec in NEWTEXT.items():
    if slug in built_slugs: continue
    title = TITLE_OVERRIDE.get(slug) or clean_title(rec.get("title") or "") or slug.replace("-"," ").title()
    date_iso = rec.get("date") or ""
    gallery = copy_gallery(slug, NEW_SRC/slug)
    cover_fs = IMG/f"{slug}.jpg"
    cover = f"images/blog/{slug}.jpg" if valid_jpeg(cover_fs) else (gallery[0] if gallery else None)
    paras=[]
    for para in rec.get("paras",[]):
        cp=clean_para(para)
        if len(cp)<=40: continue
        if re.search(r"(please contact me|if you'?d like to discuss|get in touch).{0,80}(@|\d{6,})", cp, re.I): continue
        for sp in split_paras(cp): paras.append(("p",sp))
    built.append(dict(slug=slug,title=title,cat=rec.get("cat","Family"),date_iso=date_iso,
                      is_year=False,cover=cover,gallery=gallery,paras=paras,pending=(cover is None)))
    new_built += 1

def sortkey(b):
    d=b["date_iso"]
    return (d+"-06-30") if re.fullmatch(r"\d{4}",d) else (d or "0000-00-00")
built.sort(key=sortkey, reverse=True)

for b in built:
    body=[]
    for kind,txt in b["paras"]:
        body.append(f'<p class="post-lead">{esc(txt)}</p>' if kind=="fb" else f"<p>{esc(txt)}</p>")
    body_html="\n        ".join(body)
    gal_html=""
    if b["gallery"]:
        items="\n        ".join(
            f'<div class="gallery-item"><img src="../{esc(u)}"{dims(u)} alt="{esc(b["title"])} — photograph by Amy Fanton" loading="lazy" /></div>'
            for u in b["gallery"])
        gal_html=f'\n      <div class="post-gallery gallery">\n        {items}\n      </div>'
    datedisp = b["date_iso"] if b["is_year"] else disp_date(b["date_iso"])
    hero = f'<div class="post-hero"><img src="../{esc(b["cover"])}"{dims(b["cover"])} alt="{esc(b["title"])}" /></div>' if b["cover"] else ""
    _og = og_image(b["cover"], f"images/og/{b['slug']}.jpg") if b.get("cover") else None
    _ogimg = f"{BASE}{_og}" if _og else f"{BASE}images/og/home.jpg"
    _url = f"{BASE}blog/{b['slug']}.html"
    _qu = urllib.parse.quote(_url, safe=""); _qt = urllib.parse.quote(b["title"], safe="")
    _qi = urllib.parse.quote(f"{BASE}{_og}" if _og else f"{BASE}images/og/home.jpg", safe="")
    _ICON = {
      "pin":'<path d="M12 2C6.48 2 2 6.48 2 12c0 4.24 2.64 7.86 6.36 9.32-.09-.79-.17-2.01.03-2.88.18-.78 1.17-4.97 1.17-4.97s-.3-.6-.3-1.48c0-1.39.81-2.43 1.81-2.43.85 0 1.27.64 1.27 1.41 0 .86-.55 2.14-.83 3.33-.24 1 .5 1.81 1.48 1.81 1.78 0 3.14-1.88 3.14-4.58 0-2.39-1.72-4.07-4.18-4.07-2.85 0-4.52 2.13-4.52 4.34 0 .86.33 1.78.74 2.28.08.1.09.19.07.29-.08.32-.25 1-.28 1.14-.04.18-.15.22-.34.13-1.25-.58-2.03-2.4-2.03-3.87 0-3.15 2.29-6.04 6.6-6.04 3.46 0 6.16 2.47 6.16 5.77 0 3.44-2.17 6.21-5.18 6.21-1.01 0-1.97-.53-2.29-1.15l-.62 2.37c-.23.86-.83 1.95-1.24 2.61.93.29 1.92.44 2.95.44 5.52 0 10-4.48 10-10S17.52 2 12 2z"/>',
      "fb":'<path d="M22 12.06C22 6.5 17.52 2 12 2S2 6.5 2 12.06c0 5 3.66 9.15 8.44 9.94v-7.03H7.9v-2.9h2.54V9.85c0-2.5 1.49-3.89 3.78-3.89 1.09 0 2.23.2 2.23.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56v1.87h2.78l-.44 2.9h-2.34V22c4.78-.79 8.44-4.94 8.44-9.94z"/>',
      "wa":'<path d="M.057 24l1.687-6.163a11.87 11.87 0 0 1-1.587-5.946C.16 5.335 5.495 0 12.05 0a11.82 11.82 0 0 1 8.413 3.488 11.82 11.82 0 0 1 3.48 8.414c-.003 6.557-5.338 11.892-11.893 11.892a11.9 11.9 0 0 1-5.688-1.448L.057 24zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884a9.86 9.86 0 0 0 1.51 5.26l-.999 3.648 3.629-.95zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414z"/>',
      "mail":'<path d="M3 5h18a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zm9 6.2 8-5.2H4l8 5.2zM4 8.1V18h16V8.1l-8 5.2-8-5.2z"/>',
      "link":'<path d="M3.9 12a3.1 3.1 0 0 1 3.1-3.1h4V7H7a5 5 0 0 0 0 10h4v-1.9H7A3.1 3.1 0 0 1 3.9 12zM9 13h6v-2H9v2zm8-6h-4v1.9h4a3.1 3.1 0 0 1 0 6.2h-4V17h4a5 5 0 0 0 0-10z"/>',
    }
    def _ic(k): return f'<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">{_ICON[k]}</svg>'
    share = (f'<div class="post-share"><span class="post-share-label">Share this story</span><div class="share-row">'
      f'<a class="share-btn" href="https://pinterest.com/pin/create/button/?url={_qu}&media={_qi}&description={_qt}" target="_blank" rel="noopener" aria-label="Pin on Pinterest">{_ic("pin")}</a>'
      f'<a class="share-btn" href="https://www.facebook.com/sharer/sharer.php?u={_qu}" target="_blank" rel="noopener" aria-label="Share on Facebook">{_ic("fb")}</a>'
      f'<a class="share-btn" href="https://wa.me/?text={_qt}%20{_qu}" target="_blank" rel="noopener" aria-label="Share on WhatsApp">{_ic("wa")}</a>'
      f'<a class="share-btn" href="mailto:?subject={_qt}&body={_qu}" aria-label="Share by email">{_ic("mail")}</a>'
      f'<button class="share-btn share-copy" type="button" data-url="{_url}" aria-label="Copy link">{_ic("link")}</button>'
      f'</div></div>')
    _desc = meta_desc(b)
    _schema = post_schema(b, _url, _ogimg, _desc)
    page = HEAD.format(title=esc(page_title(b)),
                       desc=esc(_desc), nav=NAV, canonical=_url, ogimage=_ogimg)
    page += f'''
  {_schema}
  <article class="post">
    <header class="post-head">
      <p class="eyebrow">{esc(b["cat"])}</p>
      <h1 class="post-title">{esc(b["title"])}</h1>
      <p class="post-date">{esc(datedisp)}</p>
    </header>
    {hero}
    <div class="post-body">
        {body_html}
    </div>{gal_html}
    {share}
    <p class="post-back"><a href="index.html">&larr; Back to the Journal</a></p>
  </article>

  {FOOTER}
  <div class="lightbox" id="lightbox" aria-hidden="true">
    <button class="lb-close" id="lbClose" aria-label="Close">&times;</button>
    <button class="lb-nav lb-prev" id="lbPrev" aria-label="Previous">&#8249;</button>
    <img class="lb-img" id="lbImg" src="" alt="" />
    <button class="lb-nav lb-next" id="lbNext" aria-label="Next">&#8250;</button>
  </div>
  <script src="../blog.js"></script>
</body>
</html>
'''
    (BLOGDIR/f"{b['slug']}.html").write_text(page)

cards=[]
for b in built:
    datedisp = b["date_iso"] if b["is_year"] else disp_date(b["date_iso"])
    yr = b["date_iso"][:4]
    if b["cover"]:
        thumb = f'<div class="journal-thumb"><img src="../{esc(b["cover"])}"{dims(b["cover"])} alt="{esc(b["title"])}" loading="lazy" /></div>'
    else:
        thumb = f'<div class="journal-thumb journal-thumb--empty"><span class="thumb-mono">AF</span><span class="thumb-cat">{esc(b["cat"])}</span></div>'
    cards.append(f'''        <a class="journal-card{' is-pending' if b.get('pending') else ''}" href="{esc(b['slug'])}.html" data-cat="{esc(b['cat'])}" data-year="{esc(yr)}">
          {thumb}
          <div class="journal-meta">
            <p class="journal-cat">{esc(b['cat'])}</p>
            <h2 class="journal-title">{esc(b['title'])}</h2>
            <p class="journal-date">{esc(datedisp)}</p>
          </div>
        </a>''')

from collections import Counter
CAT_ORDER=["Weddings","Engagements","Family","Newborn & Maternity","Inspiration"]
cat_counts=Counter(b["cat"] for b in built)
cats=[c for c in CAT_ORDER if c in cat_counts]+[c for c in cat_counts if c not in CAT_ORDER]
years=sorted({b["date_iso"][:4] for b in built}, reverse=True)
cat_btns=[f'<button class="filter-btn is-active" data-type="cat" data-val="all">All Stories <span class="filter-count">{len(built)}</span></button>']
for c in cats:
    cat_btns.append(f'<button class="filter-btn" data-type="cat" data-val="{esc(c)}">{esc(c)} <span class="filter-count">{cat_counts[c]}</span></button>')
year_btns=['<button class="filter-btn is-active" data-type="year" data-val="all">All Years</button>']
for y in years:
    year_btns.append(f'<button class="filter-btn" data-type="year" data-val="{esc(y)}">{esc(y)}</button>')
ind='\n          '
sidebar=f'''<aside class="journal-sidebar">
        <div class="filter-group" data-group="cat">
          <p class="filter-head">Browse</p>
          {ind.join(cat_btns)}
        </div>
        <div class="filter-group filter-group-years" data-group="year">
          <p class="filter-head">By Year</p>
          <div class="filter-years">{ind.join(year_btns)}</div>
        </div>
      </aside>'''
FILTER_JS='''(function(){
  var state={cat:"all",year:"all"};
  var cards=[].slice.call(document.querySelectorAll(".journal-card"));
  var btns=[].slice.call(document.querySelectorAll(".filter-btn"));
  var empty=document.getElementById("journalEmpty");
  function apply(){
    var shown=0;
    cards.forEach(function(c){
      var ok=(state.cat==="all"||c.dataset.cat===state.cat)&&(state.year==="all"||c.dataset.year===state.year);
      c.hidden=!ok; if(ok)shown++;
    });
    if(empty)empty.hidden=shown>0;
  }
  btns.forEach(function(b){
    b.addEventListener("click",function(){
      var t=b.dataset.type; state[t]=b.dataset.val;
      btns.forEach(function(o){ if(o.dataset.type===t) o.classList.toggle("is-active",o===b); });
      apply();
    });
  });
})();'''
idx = HEAD.format(title="Journal &mdash; Amy Fanton Photography",
                  desc="Stories from weddings, elopements and portrait sessions photographed by Amy Fanton in London and around the world.", nav=NAV,
                  canonical=f"{BASE}blog/index.html",
                  ogimage=f"{BASE}images/og/home.jpg")
og_image("images/originals/photo-17.jpg", "images/og/home.jpg")
idx += f'''
  <section class="section journal-intro">
    <header class="section-head">
      <p class="eyebrow">The Journal</p>
      <h1 class="section-title">Stories &amp; Sessions</h1>
      <p class="contact-lead">Weddings, elopements and portrait sessions from London and far beyond &mdash; in my own words.</p>
    </header>
    <div class="journal-layout">
      {sidebar}
      <div class="journal-main">
        <div class="journal-grid">
{chr(10).join(cards)}
        </div>
        <p class="journal-empty" id="journalEmpty" hidden>No stories in this view yet.</p>
      </div>
    </div>
  </section>

  {FOOTER}
  <script src="../script.js"></script>
  <script>{FILTER_JS}</script>
</body>
</html>
'''
(BLOGDIR/"index.html").write_text(idx)

# sitemap.xml — home + journal index + every post (studio page excluded on purpose)
urls=[BASE, BASE+"blog/index.html"] + [f"{BASE}blog/{b['slug']}.html" for b in built]
sm=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in urls:
    sm.append(f'  <url><loc>{u}</loc></url>')
sm.append('</urlset>')
(ROOT/"sitemap.xml").write_text("\n".join(sm)+"\n")
print(f"Wrote sitemap.xml ({len(urls)} urls)")

pending=[b for b in built if b.get("pending")]
print(f"Built {len(built)} posts ({new_built} new from Wayback text; {len(pending)} awaiting photos)")
for b in built:
    print(f"  {('YEAR' if b['is_year'] else 'DATE')} {b['date_iso']:11} {b['cat']:18} cover={'Y' if b['cover'] else 'N'} gal={len(b['gallery']):2}  {b['title']}")
