#!/usr/bin/env python3
"""Check every backlink target against the live site; flag links that 404.

A backlink only passes authority if its TARGET URL resolves. Old links pointing
at dead /<slug>/ URLs leak equity. This reads an Ahrefs backlinks CSV export,
de-dupes by target URL, fetches each one (following redirects), and reports any
that don't end at 200 — sorted by the referring page's Domain Rating, so the
highest-value leaks surface first.

Usage:
  1. Ahrefs -> Backlinks -> Export -> CSV
  2. python3 tools/check_backlinks.py path/to/backlinks.csv
"""
import sys, csv, subprocess, collections

def col(row, *names):
    low = {k.lower().strip(): v for k, v in row.items()}
    for n in names:
        for k, v in low.items():
            if n in k:
                return v
    return ""

def status(url):
    try:
        out = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-L", "--max-time", "15",
             "-A", "Mozilla/5.0", "-w", "%{http_code} %{url_effective}", url],
            capture_output=True, text=True, timeout=20).stdout.strip()
        code, _, eff = out.partition(" ")
        return code, eff
    except Exception as e:
        return "ERR", str(e)

def main():
    if len(sys.argv) < 2:
        sys.exit("usage: check_backlinks.py <ahrefs_backlinks.csv>")
    rows = list(csv.DictReader(open(sys.argv[1], newline="", encoding="utf-8-sig")))
    if not rows:
        sys.exit("no rows — is this an Ahrefs backlinks CSV export?")

    # best DR seen per unique target URL
    targets = {}
    for r in rows:
        t = col(r, "target url", "target").strip()
        if not t.startswith("http"):
            continue
        dr = col(r, "domain rating", "dr ", "dr")
        try: dr = int(float(dr))
        except: dr = 0
        ref = col(r, "referring page url", "referring page", "source url")
        cur = targets.get(t)
        if not cur or dr > cur[0]:
            targets[t] = (dr, ref)

    print(f"checking {len(targets)} unique target URLs from {len(rows)} backlinks…\n")
    broken, ok = [], 0
    for t, (dr, ref) in targets.items():
        code, eff = status(t)
        if code == "200":
            ok += 1
        else:
            broken.append((dr, code, t, ref))

    broken.sort(reverse=True)
    print(f"  {ok} targets OK (200)   |   {len(broken)} NOT 200\n")
    if broken:
        print("  BROKEN TARGETS (fix these — highest referring DR first):")
        print("  " + "-" * 72)
        for dr, code, t, ref in broken:
            print(f"  DR{dr:>3}  [{code}]  {t}")
            print(f"           from: {ref}")
    else:
        print("  No broken targets — every backlink lands on a live page.")

if __name__ == "__main__":
    main()
