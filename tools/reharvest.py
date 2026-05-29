import re, subprocess, pathlib
OUT = pathlib.Path("/tmp/feat_imgs")

JOBS = {
 "maria-keith": ("/tmp/feat_rmw_mk.html",
    r'(https?://www\.rockmywedding\.co\.uk/+wp-content/gallery/[^"\']+\.jpe?g)'),
 "elizabeth-jacob": ("/tmp/feat_rmw_ej.html",
    r'(https?://www\.rockmywedding\.co\.uk/+wp-content/gallery/[^"\']+\.jpe?g)'),
 "neon-pimlico": ("/tmp/feat_rmw_neon.html",
    r'(https?://www\.rockmywedding\.co\.uk/+wp-content/gallery/[^"\']+\.jpe?g)'),
 "lavender-fields": ("/tmp/feat_rmw_lav.html",
    r'(https?://www\.rockmywedding\.co\.uk/+wp-content/gallery/[^"\']+\.jpe?g)'),
 "blush-pink-beach": ("/tmp/feat_bloved.html",
    r'(https?://blovedblog\.com/wp-content/uploads/[^"\']+amy-fanton-photography[^"\']+\.jpe?g)'),
}

def get(url, t=60):
    return subprocess.run(["curl","-sSL","--max-time",str(t),"-A","Mozilla/5.0",url],capture_output=True).stdout
def is_jpeg(b): return b[:3]==b"\xff\xd8\xff"
def cdx(url, n=6):
    r=subprocess.run(["curl","-sSL","--max-time","30",
      f"https://web.archive.org/cdx/search/cdx?url={url}&output=text&fl=timestamp&filter=statuscode:200&filter=mimetype:image/jpeg&collapse=digest&limit={n}"],
      capture_output=True,text=True)
    return [l.strip() for l in r.stdout.splitlines() if l.strip()]

for slug,(hf,rx) in JOBS.items():
    raw = open(hf, errors="ignore").read()
    urls = re.findall(rx, raw, re.I)
    # normalize: collapse // and strip wayback prefix
    norm=[]
    for u in urls:
        u=re.sub(r'^https?://web\.archive\.org/web/[0-9a-z_]+/','',u)
        u=re.sub(r'(co\.uk)//+wp-content',r'\1/wp-content',u)
        u=re.sub(r'(\.com)//+wp-content',r'\1/wp-content',u)
        norm.append(u)
    norm=list(dict.fromkeys(norm))
    d=OUT/slug; d.mkdir(parents=True, exist_ok=True)
    # clear old broken files
    for f in d.iterdir():
        if f.is_file(): f.unlink()
    i=0
    for u in norm:
        if i>=24: break
        saved=False
        for ts in cdx(u)[:4]:
            data=get(f"https://web.archive.org/web/{ts}im_/{u}")
            if is_jpeg(data) and len(data)>25000:
                (d/f"{i:02d}.jpg").write_bytes(data); i+=1; saved=True; break
    print(f"{slug}: {i}/{len(norm)} saved")
print("REHARVEST DONE")
