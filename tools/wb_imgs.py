import subprocess, re, sys, pathlib, json

OUT = pathlib.Path("/tmp/feat_imgs/auto")
SITE = "fantonphotography.com"
MASTER = pathlib.Path("/tmp/wb_master.json")

def curl(url, t=90, binary=False):
    r = subprocess.run(["curl","-sSL","--max-time",str(t),"-A","Mozilla/5.0",url],
                       capture_output=True)
    return r.stdout if binary else r.stdout.decode("utf-8","ignore")

def is_img(b): return b[:3]==b"\xff\xd8\xff" or b[:8]==b"\x89PNG\r\n\x1a\n"

def stem_of(path):
    # path like 2014/07/11-web1-1024x682.jpg  -> (key without WxH, width)
    m = re.search(r'(\d{4}/\d{2}/.+?)(?:-(\d{2,4})x(\d{2,4}))?(\.\w+)$', path)
    if not m: return None, 0
    key = m.group(1) + m.group(4)          # folder/name.ext  (no size)
    w = int(m.group(2)) if m.group(2) else 99999  # original (no suffix) ranks highest
    return key.lower(), w

def build_master():
    raw = curl(f"https://web.archive.org/cdx/search/cdx?url={SITE}/wp-content/uploads/*"
               f"&output=text&fl=timestamp,original&filter=statuscode:200"
               f"&collapse=urlkey", t=180)
    idx = {}  # key -> (best_width, original_url, timestamp)
    for line in raw.splitlines():
        parts = line.split()
        if len(parts) < 2: continue
        ts, original = parts[0], parts[1]
        m = re.search(r'/wp-content/uploads/(\d{4}/\d{2}/[^?\s]+\.(?:jpg|jpeg|png))$', original, re.I)
        if not m: continue
        rel = m.group(1)
        key, w = stem_of(rel)
        if key is None: continue
        cur = idx.get(key)
        if cur is None or w > cur[0]:
            idx[key] = (w, original, ts)
    MASTER.write_text(json.dumps(idx))
    return idx

def load_master():
    if MASTER.exists():
        return json.loads(MASTER.read_text())
    return build_master()

def snaps(path):
    raw = curl(f"https://web.archive.org/cdx/search/cdx?url={path}&output=text&fl=timestamp&filter=statuscode:200&collapse=timestamp:8")
    return sorted(l.strip() for l in raw.splitlines() if l.strip())

def referenced_keys(slug):
    keys = []
    seen = set()
    for ts in snaps(f"{SITE}/{slug}/"):
        html = curl(f"https://web.archive.org/web/{ts}id_/http://www.{SITE}/{slug}/")
        for u in re.findall(r'fantonphotography\.com/wp-content/uploads/(\d{4}/\d{2}/[^"\'?\s>]+\.(?:jpg|jpeg|png))', html, re.I):
            k,_ = stem_of(u)
            if k and k not in seen:
                seen.add(k); keys.append(k)
        if keys:
            break  # earliest snapshot with upload refs wins
    return keys

def harvest(slug, idx, maxn=30):
    d = OUT/slug
    d.mkdir(parents=True, exist_ok=True)
    for f in d.iterdir():
        if f.is_file(): f.unlink()
    keys = referenced_keys(slug)
    avail = [k for k in keys if k in idx]
    saved = 0
    for k in avail:
        if saved >= maxn: break
        _, original, ts = idx[k]
        data = curl(f"https://web.archive.org/web/{ts}im_/{original}", binary=True)
        if is_img(data) and len(data) > 20000:
            ext = ".png" if data[:8]==b"\x89PNG\r\n\x1a\n" else ".jpg"
            (d/f"{saved:02d}{ext}").write_bytes(data); saved += 1
    return len(keys), len(avail), saved

if __name__ == "__main__":
    if sys.argv[1:] == ["--build"]:
        idx = build_master(); print(f"master images: {len(idx)}"); sys.exit()
    idx = load_master()
    print(f"[master {len(idx)} imgs]")
    for slug in sys.argv[1:]:
        try:
            refs, avail, saved = harvest(slug, idx)
            print(f"{slug:55s} refs={refs:3d} archived={avail:3d} saved={saved}")
        except Exception as e:
            print(f"{slug:55s} ERR {e}")
    print("DONE")
