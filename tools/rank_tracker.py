#!/usr/bin/env python3
"""Track Search Console rankings for target keywords over time.

Usage:
  1. In Google Search Console -> Performance -> Search results, set date range,
     click EXPORT -> "CSV" (or "Google Sheets" then download). You get a zip with
     Queries.csv. Or use the "Pages"/"Queries" tab export.
  2. Run:  python3 tools/rank_tracker.py path/to/Queries.csv
     Add --date 2026-06-04 to label the snapshot (defaults to today).

It prints where you rank for each TARGET keyword, shows movement vs the last
snapshot, and lists "striking distance" queries (pos 4-20) — your easiest wins.
History is stored in tools/rank_history.json.
"""
import sys, csv, json, datetime, pathlib, argparse

ROOT = pathlib.Path(__file__).resolve().parent
HIST = ROOT / "rank_history.json"

# keywords we actively want to rank for — edit freely
TARGETS = [
    "london wedding photographer",
    "fine art wedding photographer london",
    "film wedding photographer london",
    "london newborn photographer",
    "hampstead newborn photographer",
    "london family photographer",
    "london maternity photographer",
    "london engagement photographer",
    "destination wedding photographer",
    "kensington photographer",
]

def load_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            key = {k.lower().strip(): v for k, v in r.items()}
            q = key.get("top queries") or key.get("query") or key.get("queries")
            if q is None:
                continue
            def num(*names):
                for n in names:
                    if n in key and key[n] not in ("", None):
                        return float(str(key[n]).replace("%", "").replace(",", ""))
                return 0.0
            rows.append({
                "q": q.strip().lower(),
                "clicks": int(num("clicks")),
                "impr": int(num("impressions")),
                "ctr": num("ctr"),
                "pos": num("position", "average position"),
            })
    return rows

def find(rows, kw):
    exact = [r for r in rows if r["q"] == kw]
    if exact:
        return exact[0]
    part = sorted([r for r in rows if kw in r["q"]], key=lambda r: -r["impr"])
    return part[0] if part else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    a = ap.parse_args()

    rows = load_csv(a.csv)
    if not rows:
        sys.exit("No query rows found — is this a GSC Queries export?")

    hist = json.loads(HIST.read_text()) if HIST.exists() else {}
    prev_dates = sorted(d for d in hist if d < a.date)
    prev = hist.get(prev_dates[-1]) if prev_dates else {}

    print(f"\n  TARGET KEYWORDS  ({a.date})")
    print("  " + "-" * 70)
    snap = {}
    for kw in TARGETS:
        r = find(rows, kw)
        if not r:
            print(f"  {kw:42} not ranking (no impressions)")
            continue
        snap[kw] = round(r["pos"], 1)
        delta = ""
        if kw in prev:
            d = prev[kw] - r["pos"]  # positive = moved up
            delta = f"  ▲{d:.1f}" if d > 0.5 else (f"  ▼{-d:.1f}" if d < -0.5 else "  =")
        matched = "" if r["q"] == kw else f"  (via \"{r['q']}\")"
        print(f"  {kw:42} pos {r['pos']:5.1f}  {r['impr']:>5} impr  {r['clicks']:>3} clk{delta}{matched}")

    strike = sorted([r for r in rows if 3.5 < r["pos"] <= 20 and r["impr"] >= 5],
                    key=lambda r: (-r["impr"], r["pos"]))[:15]
    print(f"\n  STRIKING DISTANCE  (pos 4-20, ≥5 impr — push these onto page 1)")
    print("  " + "-" * 70)
    for r in strike:
        print(f"  pos {r['pos']:5.1f}  {r['impr']:>5} impr  {r['ctr']:4.1f}% ctr   {r['q']}")

    hidden = sorted([r for r in rows if r["pos"] <= 10 and r["impr"] >= 20 and r["ctr"] < 2],
                    key=lambda r: -r["impr"])[:10]
    if hidden:
        print(f"\n  HIGH IMPRESSIONS, LOW CTR  (page-1 but few clicks — improve title/meta)")
        print("  " + "-" * 70)
        for r in hidden:
            print(f"  pos {r['pos']:5.1f}  {r['impr']:>5} impr  {r['ctr']:4.1f}% ctr   {r['q']}")

    hist[a.date] = snap
    HIST.write_text(json.dumps(hist, indent=1, sort_keys=True))
    print(f"\n  snapshot saved -> {HIST.name}  ({len(hist)} dates tracked)\n")

if __name__ == "__main__":
    main()
