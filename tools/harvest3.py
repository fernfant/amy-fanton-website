import re, subprocess, pathlib, sys
FEAT = pathlib.Path("/tmp/feat_imgs")

def get(url, t=60):
    r = subprocess.run(["curl","-sSL","--max-time",str(t),"-A","Mozilla/5.0",url],capture_output=True)
    return r.stdout
def txt(url, t=40):
    return get(url,t).decode("utf8","ignore")
def is_jpeg(b): return b[:3]==b"\xff\xd8\xff"
def cdx_img(url, n=6):
    r=subprocess.run(["curl","-sSL","--max-time","30",
      f"https://web.archive.org/cdx/search/cdx?url={url}&output=text&fl=timestamp&filter=statuscode:200&filter=mimetype:image/jpeg&collapse=digest&limit={n}"],
      capture_output=True,text=True)
    return [l.strip() for l in r.stdout.splitlines() if l.strip()]
def cdx_html(slug):
    r=subprocess.run(["curl","-sSL","--max-time","30",
      f"https://web.archive.org/cdx/search/cdx?url=rockmywedding.co.uk/{slug}&output=text&fl=timestamp,length&filter=statuscode:200&collapse=digest&limit=20"],
      capture_output=True,text=True)
    rows=[l.split() for l in r.stdout.splitlines() if l.strip()]
    rows=[(ts,int(ln)) for ts,ln in rows]
    rows.sort(key=lambda x:-x[1])  # biggest = real article
    return [ts for ts,_ in rows]

def harvest_rmw(slug, outdir, maxn=24):
    out = FEAT/outdir; out.mkdir(parents=True, exist_ok=True)
    html=""
    for ts in cdx_html(slug)[:5]:
        html = txt(f"https://web.archive.org/web/{ts}id_/http://www.rockmywedding.co.uk/{slug}/")
        if "wp-content/gallery" in html or "wp-content/uploads" in html:
            break
    urls = re.findall(r'(?:src|data-src|href)="([^"]*wp-content/(?:gallery|uploads)/[^"]+\.jpe?g)"', html, re.I)
    norm=[]
    for u in urls:
        u=re.sub(r'^https?://web\.archive\.org/web/[0-9a-z_]+/','',u)
        if u.startswith("//"): u="http:"+u
        if not u.startswith("http"): continue
        if re.search(r'logo|avatar|gravatar|-150x|-100x|-300x|icon|feed|thumb',u,re.I): continue
        norm.append(u)
    norm=list(dict.fromkeys(norm))
    print(f"[{slug}] html={len(html)}B candidate imgs={len(norm)}")
    i=0
    for u in norm:
        if i>=maxn: break
        for ts in cdx_img(u)[:3]:
            data=get(f"https://web.archive.org/web/{ts}im_/{u}")
            if is_jpeg(data) and len(data)>30000:
                (out/f"{i:02d}.jpg").write_bytes(data); i+=1
                break
    print(f"[{slug}] saved {i} -> {outdir}")
    return i

if __name__=="__main__":
    jobs=[("liff-klaus","liff-klaus"),
          ("ethereal-lovers-venice","ethereal-venice"),
          ("romantic-lavender-fields","lavender-fields2")]
    for slug,od in jobs:
        try: harvest_rmw(slug,od)
        except Exception as e: print(f"[{slug}] ERR {e}")
    print("HARVEST3 DONE")
