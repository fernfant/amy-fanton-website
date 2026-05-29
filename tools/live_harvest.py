import subprocess, re, collections, pathlib, sys

FEAT = pathlib.Path("/tmp/feat_imgs")

def get(u, t=60):
    return subprocess.run(["curl","-sSL","--max-time",str(t),"-A","Mozilla/5.0",u],capture_output=True).stdout
def txt(u, t=60): return get(u,t).decode("utf8","ignore")
def is_jpeg(b): return b[:3]==b"\xff\xd8\xff"

JOBS = {
 "maria-keith":   "https://www.rockmywedding.co.uk/maria-keith/",
 "elizabeth-jacob":"https://www.rockmywedding.co.uk/elizabeth-jacob/",
 "neon-pimlico":  "https://www.rockmywedding.co.uk/modern-neon-bright-no-11-pimlico-road/",
 "blush-pink-beach":"https://blovedblog.com/weddings/as-the-sea-glistens-blush-pink-beach-wedding-inspiration/",
}

def harvest_rmw(slug, url, maxn=30):
    h = txt(url)
    # gallery imgs live at rockmywedding.co.uk/<WxH>/images/article/<id>/<file>.jpg
    arts = re.findall(r'/images/article/(\d+)/([^"\'?\s]+\.jpe?g)', h, re.I)
    byid = collections.Counter(i for i,_ in arts)
    # the real gallery = the article id with the most distinct files (nav/related share an id but few files each)
    bycount = {}
    for i,f in arts: bycount.setdefault(i,set()).add(f)
    ranked = sorted(bycount.items(), key=lambda kv:-len(kv[1]))
    print(f"[{slug}] article-id files:", [(i,len(s)) for i,s in ranked[:6]])
    top, files = ranked[0]
    files = sorted(files)
    d = FEAT/slug; d.mkdir(parents=True, exist_ok=True)
    for f in d.iterdir():
        if f.is_file(): f.unlink()
    i=0
    for fn in files:
        if i>=maxn: break
        # request a large size
        for size in ("1200x1800","1000x1500","900x1350","1200x800","1800x1200"):
            data = get(f"https://rockmywedding.co.uk/{size}/images/article/{top}/{fn}")
            if is_jpeg(data) and len(data)>30000:
                (d/f"{i:02d}.jpg").write_bytes(data); i+=1; break
    print(f"[{slug}] saved {i} from article {top}")
    return i

def harvest_bloved(slug, url, maxn=30):
    h = txt(url)
    # try inline + lazy attrs, keep amy-fanton originals (full-size, not the -WxH thumbs)
    urls = re.findall(r'(?:src|data-src|data-lazy-src|href)="([^"]+wp-content/uploads/[^"]+\.jpe?g)"', h, re.I)
    fanton=[u for u in urls if re.search(r'fanton|amy', u, re.I)]
    print(f"[{slug}] total upload jpgs={len(set(urls))} fanton={len(set(fanton))}")
    cand = fanton if fanton else urls
    # strip -WxH size suffix to get originals, dedupe
    norm=[]
    for u in cand:
        u=re.sub(r'-\d{2,4}x\d{2,4}(\.\w+)$', r'\1', u)
        norm.append(u)
    norm=list(dict.fromkeys(norm))
    d = FEAT/slug; d.mkdir(parents=True, exist_ok=True)
    for f in d.iterdir():
        if f.is_file(): f.unlink()
    i=0
    for u in norm:
        if i>=maxn: break
        data=get(u)
        if is_jpeg(data) and len(data)>30000:
            (d/f"{i:02d}.jpg").write_bytes(data); i+=1
    print(f"[{slug}] saved {i}")
    return i

if __name__=="__main__":
    only=sys.argv[1:]
    for slug,url in JOBS.items():
        if only and slug not in only: continue
        try:
            if "blovedblog" in url: harvest_bloved(slug,url)
            else: harvest_rmw(slug,url)
        except Exception as e:
            print(f"[{slug}] ERR {e}")
    print("LIVE HARVEST DONE")
