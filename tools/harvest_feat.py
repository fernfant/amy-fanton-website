import re, subprocess, pathlib, sys

OUT = pathlib.Path("/tmp/feat_imgs")
OUT.mkdir(exist_ok=True)

def curl(url, dest):
    r = subprocess.run(["curl","-sSL","--max-time","60","-A","Mozilla/5.0",url,"-o",str(dest)],
                       capture_output=True)
    return dest.exists() and dest.stat().st_size > 3000

def strip_dim(u):
    # remove -600x400 style suffix to get full-res
    return re.sub(r"-\d{2,4}x\d{2,4}(\.\w+)$", r"\1", u)

jobs = {
  # slug : (html_file, wayback_ts or None for live, regex)
  "argentina-elopement": ("/tmp/feat_rmw_arg.html", "20191208080533",
        r'src="(https://www\.rockmywedding\.co\.uk/+wp-content/gallery/[^"]+\.jpg)"'),
  "maria-keith": ("/tmp/feat_rmw_mk.html", "20190919144047",
        r'src="(https://www\.rockmywedding\.co\.uk/+wp-content/gallery/[^"]+\.jpg)"'),
  "elizabeth-jacob": ("/tmp/feat_rmw_ej.html", "20191017125659",
        r'src="(https://www\.rockmywedding\.co\.uk/+wp-content/gallery/[^"]+\.jpg)"'),
  "sassi-holford-northumberland": ("/tmp/feat_lmd.html", None,
        r'(https://www\.lovemydress\.net/wp-content/uploads/2016/10/wpid\d+-sassi-holford[^"\' ]+\.jpg)'),
  "blush-pink-beach": ("/tmp/feat_bloved.html", None,
        r'(https://blovedblog\.com/wp-content/uploads/2016/09/bloved-wedding-blog-amy-fanton-photography[^"\' ]+\.jpg)'),
}

for slug,(hf,ts,rx) in jobs.items():
    raw = open(hf, errors="ignore").read()
    urls = re.findall(rx, raw)
    # full-res, dedup
    full = []
    seen = set()
    for u in urls:
        fu = strip_dim(u)
        key = fu.rsplit("/",1)[-1]
        if key in seen: continue
        seen.add(key); full.append(fu)
    d = OUT/slug; d.mkdir(exist_ok=True)
    ok = 0
    for i,u in enumerate(full):
        dl = f"https://web.archive.org/web/{ts}id_/{u}" if ts else u
        dest = d/f"{i:02d}_{u.rsplit('/',1)[-1]}"
        if curl(dl, dest): ok += 1
        else:
            dest.unlink(missing_ok=True)
    print(f"{slug}: {ok}/{len(full)} downloaded")

print("done")
