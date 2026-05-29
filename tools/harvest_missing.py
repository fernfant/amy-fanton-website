import subprocess, re, html, json, sys, pathlib

ROOT = pathlib.Path("/Users/fernando/Projects/amy-fanton-website")
IMG  = ROOT/"images/blog"
AUTO = pathlib.Path("/tmp/feat_imgs/auto")
AUTO.mkdir(parents=True, exist_ok=True)

NEW = [
 "american-family-photographer-in-london","argentina-trip",
 "best-tips-for-beautiful-engagement-photos","connecticut-travel-sessions",
 "family-photography-in-greece",
 "hyde-park-london-engagement-photo-session-london-engagement-photographer",
 "june-20-2013","kensington-anniversary-photo-session","little-miss-biz-waterford-ct",
 "london-anniversary-photo-session","london-anniversary-photography",
 "london-autumn-childrens-portrait","london-baptism-photography",
 "london-birthday-party-photography","london-birthday-photography",
 "london-childrens-portraits-toddler-ballerina","london-couples-photography",
 "london-engagement-photos","london-lavender-photo-sessions",
 "london-maternity-photography","london-newborn-photo-session",
 "london-phone-booth-photo-session","london-surprise-proposal-engagment-photo-session",
 "london-wedding-editorial","london-wedding-inspiration-shoot-london-wedding-photography",
 "mr-charming-june-21-2013","newborn-photo-session-london-newborn-photography",
 "outdoor-newborn-photography-london-newborn-photographer",
 "party-of-six-in-stonington-ct-june-22-2013",
 "pregnancy-photo-session-little-venice-london-maternity-photography",
 "pregnancy-photography-session-hampstead-heath-london",
 "three-is-the-magic-number-wilcox-park-ri","wedding-photography-thames-river",
 # variants the old scraper skipped (genuinely distinct posts):
 "london-wedding-photographer-turks-caicos-london-wedding-photography",
 "kensington-engagement-session-london-engagement-photography",
]

def curl(url, out=None, t=45):
    args=["curl","-sSL","--max-time",str(t),"-A","Mozilla/5.0",url]
    if out: args+=["-o",out]
    r=subprocess.run(args,capture_output=True)
    return r.stdout if not out else (r.returncode==0)

def cdx(url, extra=""):
    u=f"https://web.archive.org/cdx/search/cdx?url={url}&output=text&fl=timestamp,statuscode,mimetype,length{extra}"
    return curl(u,t=40).decode("utf-8","ignore").strip().splitlines()

def best_html_ts(slug):
    rows=cdx(f"fantonphotography.com/{slug}/","&filter=statuscode:200&filter=mimetype:text/html")
    cands=[]
    for r in rows:
        p=r.split()
        if len(p)>=4:
            ts,length=p[0],int(p[3] or 0)
            yr=ts[:4]
            score=length + (500000 if yr in ("2015","2016","2017","2018") else 0)
            cands.append((score,ts))
    cands.sort(reverse=True)
    return [ts for _,ts in cands]

def is_jpeg(b): return b[:3]==b"\xff\xd8\xff"
def clean(t): return html.unescape(re.sub(r'<[^>]+>','',t)).strip()
def strip_size(u): return re.sub(r'-\d{2,4}x\d{2,4}(\.\w+)$', r'\1', u)

def img_ts(imgurl):
    rows=cdx(imgurl,"&filter=statuscode:200&filter=mimetype:image/jpeg&collapse=digest")
    out=[]
    for r in rows:
        p=r.split()
        if len(p)>=4: out.append((int(p[3] or 0),p[0]))
    out.sort(reverse=True)
    return [ts for _,ts in out]

CATMAP=[
 (r"wedding|editorial|elopement|bridal|thames", "Weddings"),
 (r"engag|proposal|couple|anniversary|phone-booth", "Engagements"),
 (r"inspiration", "Inspiration"),
 (r"newborn|maternity|pregnan", "Newborn & Maternity"),
 (r"family|child|baby|baptism|birthday|ballerina|portrait|little-miss|magic-number|party-of-six|mr-charming|june-20|june-21|biz|travel|greece|lavender|trip", "Family"),
]
def catof(slug):
    for rx,c in CATMAP:
        if re.search(rx,slug,re.I): return c
    return "Family"

def harvest(slug):
    cat=catof(slug)
    raw=""
    for ts in best_html_ts(slug)[:4]:
        raw=curl(f"https://web.archive.org/web/{ts}id_/http://www.fantonphotography.com/{slug}/").decode("utf-8","ignore")
        if "entry-content" in raw or "wp-content/uploads" in raw: break
    if not raw:
        return None
    title=""
    m=re.search(r'og:title"\s+content="([^"]*)"',raw) or re.search(r'<title>([^<]*)</title>',raw)
    if m:
        title=clean(m.group(1)); title=re.split(r"\s+[-|–—]\s+",title)[0].strip()
    date=""
    m=re.search(r'entry-date[^>]*datetime="([^"]*)"',raw) or re.search(r'article:published_time"\s+content="([^"]*)"',raw) or re.search(r'datetime="(20[0-9-]{8})',raw)
    if m: date=m.group(1)[:10]
    m=re.search(r'(class="entry-content".*?)(?=<footer|</article|class="(?:entry-footer|sharedaddy|nav-links|comments))',raw,re.S)
    body=m.group(1) if m else raw
    paras=[clean(p) for p in re.findall(r'<p[^>]*>(.*?)</p>',body,re.S)]
    paras=[p for p in paras if len(p)>50 and "wp-content" not in p]
    # gallery image urls from body (full-size hrefs preferred)
    raws=re.findall(r'(?:href|src)="([^"]*wp-content/uploads/[^"]+\.jpe?g)"', body, re.I)
    norm=[]
    for u in raws:
        u=re.sub(r'^https?://web\.archive\.org/web/[0-9a-z_]+/','',u)
        if u.startswith("//"): u="http:"+u
        if not u.startswith("http"): continue
        if re.search(r'logo|avatar|gravatar|icon|badge|-150x|-100x|-300x|thumb',u,re.I): continue
        norm.append(strip_size(u))
    norm=list(dict.fromkeys(norm))
    # download cover (og:image) + gallery
    d=AUTO/slug; d.mkdir(parents=True,exist_ok=True)
    for f in d.iterdir():
        if f.is_file(): f.unlink()
    i=0; saved_urls=[]
    for u in norm:
        if i>=24: break
        got=False
        for ts in img_ts(u.replace("http://","").replace("https://",""))[:4]:
            data=curl(f"https://web.archive.org/web/{ts}im_/{u}")
            if is_jpeg(data) and len(data)>30000:
                (d/f"{i:02d}.jpg").write_bytes(data); i+=1; got=True; saved_urls.append(u); break
    cover_ok=False
    if i>0:
        # cover = og:image if it matches a saved one, else first gallery
        (IMG/f"{slug}.jpg").write_bytes((d/"00.jpg").read_bytes()); cover_ok=True
    rec={"slug":slug,"title":title,"date":date,"paras":paras,"npara":len(paras),
         "wordcount":sum(len(p.split()) for p in paras),"cover_ok":cover_ok,
         "cat":cat,"gal":i}
    print(f"{'OK ' if cover_ok else 'NOIMG'} {slug[:48]:48} {date or '????-??-??'} {cat[:18]:18} paras={len(paras):2} gal={i}")
    return rec

if __name__=="__main__":
    only=sys.argv[1:]
    todo=[s for s in NEW if (not only or s in only)]
    out=[]
    for s in todo:
        try: out.append(harvest(s))
        except Exception as e: print(f"ERR {s}: {e}")
    out=[r for r in out if r]
    json.dump(out, open("/tmp/blog_data/new_posts.json","w"), indent=1)
    print(f"\n=== harvested {len(out)}/{len(todo)} -> /tmp/blog_data/new_posts.json ===")
