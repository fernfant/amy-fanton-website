import re, sys, json, pathlib, html as htmllib
import wb_imgs as W

OUT = pathlib.Path("/tmp/blog_data/new_text.json")
OUT.parent.mkdir(parents=True, exist_ok=True)

def cat(s):
    if any(k in s for k in ("newborn","maternity","pregnancy","baptism")): return "Newborn & Maternity"
    if any(k in s for k in ("engagement","anniversary","proposal","couples","lavender","phone-booth")): return "Engagements"
    if any(k in s for k in ("wedding","turks")): return "Weddings"
    if any(k in s for k in ("inspiration","tips")): return "Inspiration"
    if any(k in s for k in ("trip","travel","greece","argentina","connecticut")): return "Travel"
    return "Family"

def clean(t):
    t = re.sub(r'<[^>]+>', '', t)
    t = htmllib.unescape(t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def harvest(slug):
    raw = ""
    for ts in W.snaps(f"{W.SITE}/{slug}/"):
        raw = W.curl(f"https://web.archive.org/web/{ts}id_/http://www.{W.SITE}/{slug}/")
        if "entry-content" in raw or "wp-content/uploads" in raw:
            break
    if not raw:
        return {"slug": slug, "title": "", "date": "", "paras": [], "cat": cat(slug)}
    m = re.search(r'og:title"\s+content="([^"]*)"', raw) or re.search(r'<title>([^<]*)</title>', raw)
    title = ""
    if m:
        title = clean(m.group(1)); title = re.split(r"\s+[-|–—]\s+", title)[0].strip()
    m = (re.search(r'entry-date[^>]*datetime="([^"]*)"', raw)
         or re.search(r'article:published_time"\s+content="([^"]*)"', raw)
         or re.search(r'datetime="(20[0-9-]{8})', raw))
    date = m.group(1)[:10] if m else ""
    m = re.search(r'(class="entry-content".*?)(?=<footer|</article|class="(?:entry-footer|sharedaddy|nav-links|comments))', raw, re.S)
    body = m.group(1) if m else raw
    paras = [clean(p) for p in re.findall(r'<p[^>]*>(.*?)</p>', body, re.S)]
    paras = [p for p in paras if len(p) > 40 and "wp-content" not in p and "copyright" not in p.lower()]
    return {"slug": slug, "title": title, "date": date, "paras": paras,
            "npara": len(paras), "words": sum(len(p.split()) for p in paras), "cat": cat(slug)}

if __name__ == "__main__":
    recs = {}
    for slug in sys.argv[1:]:
        try:
            r = harvest(slug); recs[slug] = r
            print(f"{slug:55s} {r['date'] or '????-??-??'} {r['cat'][:16]:16} paras={r.get('npara',0):2} words={r.get('words',0):4}  {r['title'][:40]}")
        except Exception as e:
            print(f"{slug:55s} ERR {e}")
    OUT.write_text(json.dumps(recs, indent=1))
    print(f"\nwrote {len(recs)} -> {OUT}")
