import json, re, shutil, pathlib, html
from PIL import Image

_dim_cache = {}
def dims(rel):
    if rel not in _dim_cache:
        try:
            with Image.open(ROOT/rel) as im: _dim_cache[rel] = f' width="{im.size[0]}" height="{im.size[1]}"'
        except Exception: _dim_cache[rel] = ""
    return _dim_cache[rel]

ROOT = pathlib.Path("/Users/fernando/Projects/amy-fanton-website")
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
}
GAL.mkdir(parents=True, exist_ok=True)
BLOGDIR.mkdir(exist_ok=True)

def esc(s): return html.escape(s, quote=True)

CUR = [
 ("santorini-elopement-photos","text","Weddings","santorini",None,None,"A Santorini Elopement",None),
 ("louise-roe-dorney-court-wedding","text","Weddings",None,None,None,None,None),
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
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Allura&family=Open+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Theano+Didot&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="../styles.css" />
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
    page = HEAD.format(title=esc(b["title"]+" — Amy Fanton Photography"),
                       desc=esc(b["title"]+" — wedding and portrait photography by Amy Fanton."), nav=NAV)
    page += f'''
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
                  desc="Stories from weddings, elopements and portrait sessions photographed by Amy Fanton in London and around the world.", nav=NAV)
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

pending=[b for b in built if b.get("pending")]
print(f"Built {len(built)} posts ({new_built} new from Wayback text; {len(pending)} awaiting photos)")
for b in built:
    print(f"  {('YEAR' if b['is_year'] else 'DATE')} {b['date_iso']:11} {b['cat']:18} cover={'Y' if b['cover'] else 'N'} gal={len(b['gallery']):2}  {b['title']}")
