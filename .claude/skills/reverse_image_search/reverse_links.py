"""
reverse_links.py — given one of Amy's site photos, print its public URL and
ready-to-click reverse-image-search deep-links (TinEye, Google Lens, Yandex,
Bing). The user opens these to find where the shoot was published online; the
agent then harvests Amy's photos from that feature page.

Why links (not auto): the reverse-image engines are bot-protected + JS-rendered
and blocked by the agent's browser allowlist, so the agent can't read their
results directly. The user's normal browser can. (Yandex is usually best at
surfacing OTHER frames of the same people; Google Lens/TinEye best at finding
the exact source page.)

Run:
  python3 .claude/skills/reverse_image_search/reverse_links.py images/blog/gallery/<slug>/<file>.jpg
  python3 .claude/skills/reverse_image_search/reverse_links.py https://www.fantonphotography.com/....jpg
"""
import sys, urllib.parse, pathlib

BASE = "https://www.fantonphotography.com/"

def to_public_url(arg):
    if arg.startswith(("http://", "https://")):
        return arg
    # local repo path -> live URL (image must be committed + deployed)
    rel = pathlib.Path(arg)
    parts = rel.parts
    if "images" in parts:
        rel = pathlib.Path(*parts[parts.index("images"):])
    return BASE + str(rel).lstrip("/")

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    img = to_public_url(sys.argv[1])
    e = urllib.parse.quote(img, safe="")
    print(f"\nPUBLIC IMAGE URL (must be live on the site):\n  {img}\n")
    print("Open these in your browser, find the source/feature page, paste the URL back:\n")
    print(f"  Google Lens : https://lens.google.com/uploadbyurl?url={e}")
    print(f"  Yandex      : https://yandex.com/images/search?rpt=imageview&url={e}")
    print(f"  TinEye      : https://tineye.com/search?url={e}")
    print(f"  Bing        : https://www.bing.com/images/search?view=detailv2&iss=sbi&q=imgurl:{e}")
    print("\nTip: Yandex tends to surface OTHER photos from the same shoot; "
          "Lens/TinEye find the exact source page.\n")

if __name__ == "__main__":
    main()
