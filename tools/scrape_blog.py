import subprocess, re, html, json, sys
from pathlib import Path

CAND = [
 # destination / weddings (match portfolio shoots)
 "santorini-elopement-photos","venice-wedding-photography",
 "surrey-wedding-photography-mayfield-lavender-wedding-inspiration",
 "westonbirt-wedding-photography","preston-court-wedding-photography",
 "christmas-hengrave-hall-wedding-photography","tigre-argentina-wedding-photography",
 "louise-roe-dorney-court-wedding","london-wedding-photographer-in-los-angeles",
 "elegant-old-word-argentina-bridal-shoot","coastal-bridal-shoot",
 "london-wedding-photographer-in-buenos-aires-wedding-at-the-lowlands",
 "ritz-london-wedding-photographer","london-wedding-photography-at-the-mortons-club",
 "london-wedding-photographer-turks-caicos-london-wedding-photography",
 "european-destination-wedding-photography-in-greece",
 # engagements / proposals
 "chelsea-engagement-photos","flower-field-engagement-session-london-engagement-photography",
 "best-proposal-photography-ideas","regents-park-engagement-photography-session",
 "london-bridge-engagement","kensington-engagement-session-london-engagement-photography",
 # family / newborn / maternity
 "newborn-photography-in-london","kensington-newborn-photography",
 "london-autumn-maternity-shoot","hyde-park-maternity-shoot",
 "richmond-park-family-shoot","iconic-london-family-photography",
]

def curl(url, out=None, t=45):
    args=["curl","-sSL","--max-time",str(t),url]
    if out: args+=["-o",out]
    r=subprocess.run(args,capture_output=True)
    return r.stdout if not out else (r.returncode==0)

def cdx(url, extra=""):
    u=f"https://web.archive.org/cdx/search/cdx?url={url}&output=text&fl=timestamp,statuscode,mimetype,length{extra}"
    return curl(u).decode("utf-8","ignore").strip().splitlines()

def best_html_ts(slug):
    rows=cdx(f"fantonphotography.com/{slug}/","&filter=statuscode:200&filter=mimetype:text/html")
    # prefer 2016-2018 captures, largest length
    cands=[]
    for r in rows:
        p=r.split()
        if len(p)>=4:
            ts,length=p[0],int(p[3] or 0)
            yr=ts[:4]
            score=length + (500000 if yr in ("2016","2017","2018") else 0)
            cands.append((score,ts,length))
    if not cands: return None
    cands.sort(reverse=True)
    return cands[0][1]

def best_img_ts(imgurl):
    rows=cdx(imgurl,"&filter=statuscode:200&filter=mimetype:image/jpeg")
    best=None
    for r in rows:
        p=r.split()
        if len(p)>=4:
            ln=int(p[3] or 0)
            if best is None or ln>best[1]: best=(p[0],ln)
    return best

def clean(t): return html.unescape(re.sub(r'<[^>]+>','',t)).strip()

results=[]
for slug in CAND:
    ts=best_html_ts(slug)
    if not ts:
        print(f"SKIP {slug}: no html capture"); continue
    raw=curl(f"https://web.archive.org/web/{ts}id_/http://www.fantonphotography.com/{slug}/").decode("utf-8","ignore")
    title=""
    m=re.search(r'og:title"\s+content="([^"]*)"',raw) or re.search(r'<title>([^<]*)</title>',raw)
    if m:
        title=clean(m.group(1))
        title=re.split(r"\s+[-|\u2013]\s+",title)[0].strip()
    date=""
    m=re.search(r'entry-date[^>]*datetime="([^"]*)"',raw) or re.search(r'article:published_time"\s+content="([^"]*)"',raw) or re.search(r'datetime="(20[0-9-]{8})',raw)
    if m: date=m.group(1)[:10]
    # body
    m=re.search(r'(class="entry-content".*?)(?=<footer|</article|class="(?:entry-footer|sharedaddy|nav-links|comments))',raw,re.S)
    body=m.group(1) if m else raw
    paras=[clean(p) for p in re.findall(r'<p[^>]*>(.*?)</p>',body,re.S)]
    paras=[p for p in paras if len(p)>50 and "wp-content" not in p]
    # og image
    mi=re.search(r'og:image"\s+content="([^"]*)"',raw)
    imgurl=""
    cover_ok=False
    if mi:
        imgurl=re.sub(r'^https?://web\.archive\.org/web/[0-9]+[a-z_]*/','',mi.group(1))
        bi=best_img_ts(imgurl.replace("http://",""))
        if bi:
            ok=curl(f"https://web.archive.org/web/{bi[0]}id_/{imgurl}", out=f"/Users/fernando/Projects/amy-fanton-website/images/blog/{slug}.jpg")
            cover_ok=ok
    rec={"slug":slug,"title":title,"date":date,"paras":paras,"npara":len(paras),
         "wordcount":sum(len(p.split()) for p in paras),"cover_ok":bool(cover_ok)}
    results.append(rec)
    print(f"OK {slug} | {date} | cover={'Y' if cover_ok else 'N'} | paras={len(paras)} words={rec['wordcount']} | {title[:50]}")

json.dump(results,open("/tmp/blog_data/posts.json","w"),indent=1)
print(f"\n=== {len(results)} processed, covers: {sum(r['cover_ok'] for r in results)} ===")
