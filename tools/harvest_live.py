import re, subprocess, pathlib
FEAT = pathlib.Path("/tmp/feat_imgs")

def get(url, t=60):
    return subprocess.run(["curl","-sSL","--max-time",str(t),"-A","Mozilla/5.0",url],capture_output=True).stdout
def is_jpeg(b): return b[:3]==b"\xff\xd8\xff"

JOBS = [
 ("hermione-lmd",
  "https://www.lovemydress.net/blog/2015/09/hermione-nature-inspired-headpieces-hair-vines.html",
  r'(https://www\.lovemydress\.net/wp-content/uploads/[^"\' ]+\.jpe?g)'),
 ("argentina-bloved",
  "https://blovedblog.com/old-world-argentina-wedding-inspiration",
  r'(https://blovedblog\.com/wp-content/uploads/[^"\' ]+\.jpe?g)'),
]

def strip_size(u): return re.sub(r'-\d{2,4}x\d{2,4}(\.\w+)$', r'\1', u)

for slug,url,rx in JOBS:
    html = get(url).decode("utf8","ignore")
    raw = re.findall(rx, html, re.I)
    cands=[]
    for u in raw:
        if re.search(r'logo|avatar|gravatar|icon|badge|button|emoji|/wp-content/uploads/20(0|1)[0-4]/',u,re.I): continue
        cands.append(strip_size(u))
    cands=list(dict.fromkeys(cands))
    # keep amy fanton images preferentially
    amy=[u for u in cands if re.search(r'fanton',u,re.I)]
    use = amy if len(amy)>=6 else cands
    d=FEAT/slug; d.mkdir(parents=True, exist_ok=True)
    for f in d.iterdir():
        if f.is_file(): f.unlink()
    i=0
    for u in use:
        if i>=30: break
        data=get(u)
        if is_jpeg(data) and len(data)>25000:
            (d/f"{i:02d}.jpg").write_bytes(data); i+=1
    print(f"{slug}: html={len(html)}B cands={len(cands)} amy={len(amy)} saved={i}")
print("LIVE HARVEST DONE")
