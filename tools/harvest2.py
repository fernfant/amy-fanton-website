import re, subprocess, pathlib
OUT = pathlib.Path("/tmp/feat_imgs"); OUT.mkdir(exist_ok=True)
def curl(url, dest):
    subprocess.run(["curl","-sSL","--max-time","60",url,"-o",str(dest)], capture_output=True)
    return dest.exists() and dest.stat().st_size > 4000
jobs = {
  "neon-pimlico": ("/tmp/feat_rmw_neon.html","20200815165215",
     r'(https://www\.rockmywedding\.co\.uk/+wp-content/gallery/Pimlico-Road-Shoot/[^"]+\.jpg)'),
  "lavender-fields": ("/tmp/feat_rmw_lav.html","20170707061302",
     r'(https://www\.rockmywedding\.co\.uk/+wp-content/gallery/lavender-fields-shoot/[^"]+\.jpg)'),
}
for slug,(hf,ts,rx) in jobs.items():
    raw=open(hf,errors="ignore").read()
    urls=[]
    seen=set()
    for u in re.findall(rx,raw):
        k=u.rsplit("/",1)[-1]
        if k in seen: continue
        seen.add(k); urls.append(u)
    d=OUT/slug; d.mkdir(exist_ok=True)
    ok=0
    for i,u in enumerate(urls[:18]):
        dest=d/f"{i:02d}_{u.rsplit('/',1)[-1]}"
        if curl(f"https://web.archive.org/web/{ts}id_/{u}",dest): ok+=1
        else: dest.unlink(missing_ok=True)
    print(f"{slug}: {ok}/{min(len(urls),18)}")
print("done2")
