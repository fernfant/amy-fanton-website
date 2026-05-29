import re, subprocess, pathlib, json
OUT = pathlib.Path("/tmp/feat_imgs")
BLOG = pathlib.Path("/Users/fernando/Projects/amy-fanton-website/images/blog")

def curl(url, dest, mn=4000):
    subprocess.run(["curl","-sSL","--max-time","60","-A","Mozilla/5.0",url,"-o",str(dest)], capture_output=True)
    return dest.exists() and dest.stat().st_size > mn

def cdx_best(url):
    r = subprocess.run(["curl","-sSL","--max-time","30",
        f"https://web.archive.org/cdx/search/cdx?url={url}&output=text&fl=timestamp,length&filter=statuscode:200&collapse=digest&limit=15"],
        capture_output=True,text=True)
    rows=[l.split() for l in r.stdout.splitlines() if l.strip()]
    rows=[(t,int(ln)) for t,ln in rows]
    # prefer 2015-2017 captures, largest
    early=[x for x in rows if x[0][:4] in ("2015","2016","2017")]
    pool=early or rows
    return max(pool,key=lambda x:x[1])[0] if pool else None

# 1) fix galleries: lavender (http), sassi (lmd live), blush (bloved wayback)
gal = {
 "lavender-fields": ("/tmp/feat_rmw_lav.html","20170707061302",
    r'(https?://www\.rockmywedding\.co\.uk/+wp-content/gallery/lavender-fields-shoot/[^"]+\.jpg)'),
 "sassi-holford-northumberland": ("/tmp/feat_lmd.html",None,
    r'(https://www\.lovemydress\.net/wp-content/uploads/2016/10/wpid\d+-sassi-holford[^"\' ]+\.jpg)'),
 "blush-pink-beach": ("/tmp/feat_bloved.html",None,
    r'(https://blovedblog\.com/wp-content/uploads/2016/09/bloved-wedding-blog-amy-fanton-photography[^"\' ]+\.jpg)'),
}
def strip_dim(u): return re.sub(r"-\d{2,4}x\d{2,4}(\.\w+)$", r"\1", u)
for slug,(hf,ts,rx) in gal.items():
    raw=open(hf,errors="ignore").read()
    seen=set(); urls=[]
    for u in re.findall(rx,raw):
        fu=strip_dim(u); k=fu.rsplit("/",1)[-1]
        if k in seen: continue
        seen.add(k); urls.append(fu)
    d=OUT/slug; d.mkdir(parents=True,exist_ok=True)
    ok=0
    for i,u in enumerate(urls[:18]):
        dl=f"https://web.archive.org/web/{ts}id_/{u}" if ts else u
        dest=d/f"{i:02d}_{u.rsplit('/',1)[-1]}"
        if curl(dl,dest): ok+=1
        else: dest.unlink(missing_ok=True)
    print(f"GAL {slug}: {ok}/{min(len(urls),18)}")

# 2) recover covers for uncovered posts -> first real content image
covers = {
 "elegant-old-word-argentina-bridal-shoot":"elegant-old-word-argentina-bridal-shoot",
 "ritz-london-wedding-photographer":"ritz-london-wedding-photographer",
 "london-wedding-photography-at-the-mortons-club":"london-wedding-photography-at-the-mortons-club",
 "european-destination-wedding-photography-in-greece":"european-destination-wedding-photography-in-greece",
 "flower-field-engagement-session-london-engagement-photography":"flower-field-engagement-session-london-engagement-photography",
 "kensington-newborn-photography":"kensington-newborn-photography",
 "hyde-park-maternity-shoot":"hyde-park-maternity-shoot",
}
for slug in covers:
    ts=cdx_best(f"fantonphotography.com/{slug}/")
    if not ts:
        print(f"COVER {slug}: no capture"); continue
    r=subprocess.run(["curl","-sSL","--max-time","50",
        f"https://web.archive.org/web/{ts}id_/http://www.fantonphotography.com/{slug}/"],
        capture_output=True,text=True)
    html=r.stdout
    # find content images (wp-content/uploads), skip logos/avatars/tiny thumbs
    imgs=re.findall(r'(?:src|data-src)="([^"]*wp-content/uploads/[^"]+\.jpe?g)"',html,re.I)
    imgs=[i for i in imgs if not re.search(r'logo|avatar|gravatar|-150x|-100x|icon',i,re.I)]
    got=False
    for u in imgs[:6]:
        if u.startswith("//"): u="https:"+u
        if u.startswith("/"): u="https://web.archive.org"+u
        if not u.startswith("http"): continue
        dl=u if "web.archive.org" in u else f"https://web.archive.org/web/{ts}id_/{u}"
        dest=BLOG/f"{slug}.jpg"
        if curl(dl,dest,mn=15000):
            print(f"COVER {slug}: OK ({dest.stat().st_size//1024}KB) ts={ts}")
            got=True; break
        else:
            dest.unlink(missing_ok=True)
    if not got: print(f"COVER {slug}: FAILED ({len(imgs)} candidates) ts={ts}")
print("FIXDONE")
