import re, subprocess, pathlib
BLOG = pathlib.Path("/Users/fernando/Projects/amy-fanton-website/images/blog")
slugs = [
 "elegant-old-word-argentina-bridal-shoot",
 "ritz-london-wedding-photographer",
 "london-wedding-photography-at-the-mortons-club",
 "european-destination-wedding-photography-in-greece",
 "flower-field-engagement-session-london-engagement-photography",
]
def get(url, timeout=50):
    r=subprocess.run(["curl","-sSL","--max-time",str(timeout),"-A","Mozilla/5.0",url],capture_output=True)
    return r.stdout
def is_jpeg(b): return b[:3]==b"\xff\xd8\xff"
def cdx(url):
    r=subprocess.run(["curl","-sSL","--max-time","30",
      f"https://web.archive.org/cdx/search/cdx?url={url}&output=text&fl=timestamp&filter=statuscode:200&filter=mimetype:image/jpeg&collapse=digest&limit=10"],
      capture_output=True,text=True)
    return [l.strip() for l in r.stdout.splitlines() if l.strip()]
for slug in slugs:
    # get article html (try a few captures), pull og:image and content imgs
    html=""
    for ts in ("20160601000000","20151201000000","20170101000000"):
        html=get(f"https://web.archive.org/web/{ts}id_/http://www.fantonphotography.com/{slug}/").decode("utf8","ignore")
        if "wp-content/uploads" in html: break
    cands=[]
    m=re.search(r'og:image"\s+content="([^"]+)"',html) or re.search(r'og:image" content="([^"]+)"',html)
    if m: cands.append(m.group(1))
    cands += re.findall(r'(?:src|data-src)="([^"]*wp-content/uploads/[^"]+\.jpe?g)"',html,re.I)
    # normalize: strip wayback prefix to original url
    norm=[]
    for u in cands:
        u=re.sub(r'^https?://web\.archive\.org/web/[0-9a-z_]+/','',u)
        if u.startswith("//"): u="http:"+u
        if not u.startswith("http"): continue
        if re.search(r'logo|avatar|gravatar|-150x|-100x|icon|feed',u,re.I): continue
        norm.append(u)
    got=False
    for u in dict.fromkeys(norm):
        for ts in cdx(u)[:3]:
            data=get(f"https://web.archive.org/web/{ts}im_/{u}")
            if is_jpeg(data) and len(data)>20000:
                (BLOG/f"{slug}.jpg").write_bytes(data)
                print(f"{slug}: OK {len(data)//1024}KB {u.rsplit('/',1)[-1]}")
                got=True; break
        if got: break
    if not got: print(f"{slug}: FAIL ({len(norm)} cands)")
print("DONE2")
