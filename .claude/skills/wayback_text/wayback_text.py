"""
wayback_text.py — pull the VERBATIM body text of an old fantonphotography.com
post from the Wayback Machine, ready to drop into /tmp/blog_data/posts.json.

Give it either a Wayback snapshot URL (best — exactly the capture you want) or a
live/original URL (it will look up the latest 200 snapshot via the CDX API).

  python3 .claude/skills/wayback_text/wayback_text.py \
      https://web.archive.org/web/20200224222225/http://www.fantonphotography.com/tigre-argentina-wedding-photography/

  python3 .claude/skills/wayback_text/wayback_text.py \
      http://www.fantonphotography.com/tigre-argentina-wedding-photography/   # auto-finds a snapshot

Prints the slug, the verbatim paragraphs, and a JSON `paras` array. Needs network
(run with the sandbox disabled). Extraction is faithful: HTML entities decoded,
internal whitespace collapsed, but wording/spelling left exactly as archived.
"""
import sys, re, html, json, urllib.request, urllib.parse

UA = {"User-Agent": "Mozilla/5.0"}

def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode("utf-8", "ignore")

def latest_snapshot(orig):
    host_path = re.sub(r"^https?://", "", orig)
    cdx = ("http://web.archive.org/cdx/search/cdx?url=" + urllib.parse.quote(host_path)
           + "&filter=statuscode:200&filter=mimetype:text/html&collapse=digest&output=json&limit=-5")
    rows = json.loads(fetch(cdx))
    if len(rows) < 2:
        raise SystemExit("no Wayback snapshot found for " + orig)
    ts, original = rows[-1][1], rows[-1][2]
    return f"https://web.archive.org/web/{ts}id_/{original}"

def extract_paras(htmltext):
    t = re.sub(r"(?s)<(script|style|noscript)[^>]*>.*?</\1>", " ", htmltext)
    out = []
    for m in re.findall(r"<p[^>]*>(.*?)</p>", t, re.S):
        txt = html.unescape(re.sub("<[^>]+>", "", m))
        txt = re.sub(r"[ \t\r\n]+", " ", txt).strip()
        low = txt.lower()
        if len(txt) >= 60 and "wayback" not in low and "archive.org" not in low and "internet archive" not in low:
            out.append(txt)
    return out

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    url = sys.argv[1]
    if "web.archive.org" not in url:
        url = latest_snapshot(url)
        print("# resolved snapshot:", url)
    slug = re.sub(r"/$", "", url).rsplit("/", 1)[-1]
    paras = extract_paras(fetch(url))
    print(f"\n# slug: {slug}\n# {len(paras)} paragraph(s)\n")
    for i, p in enumerate(paras):
        print(f"[{i}] {p}\n")
    print("# JSON paras (paste into posts.json for this slug):")
    print(json.dumps(paras, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
