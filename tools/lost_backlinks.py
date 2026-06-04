#!/usr/bin/env python3
"""Detect recently LOST backlinks/referring domains from high-authority sites.

Ahrefs doesn't expose "lost links" in its free tool or via any connector we have,
so this works on snapshots YOU export: each run, save an Ahrefs "Referring domains"
(or "Backlinks") CSV. This diffs the newest export against the previous snapshot and
reports referring domains that disappeared — filtered to high DR (default >= 30),
which is what's worth acting on.

Usage:
  python3 tools/lost_backlinks.py path/to/ahrefs-referring-domains.csv [--dr 30] [--date 2026-06-08]

Output: a Slack-ready summary of lost (and newly gained) high-authority domains.
Snapshots are stored in tools/backlink_snapshots/.
"""
import sys, csv, json, argparse, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SNAP = ROOT / "backlink_snapshots"

def col(row, *names):
    low = {k.lower().strip(): v for k, v in row.items()}
    for n in names:
        for k, v in low.items():
            if n in k:
                return v
    return ""

def load(path):
    """Return {domain: dr} from an Ahrefs referring-domains or backlinks CSV."""
    out = {}
    for r in csv.DictReader(open(path, newline="", encoding="utf-8-sig")):
        dom = col(r, "referring domain", "domain", "referring page url", "referring page")
        dom = dom.replace("https://", "").replace("http://", "").split("/")[0].lower().strip()
        if dom.startswith("www."):
            dom = dom[4:]
        if not dom:
            continue
        dr = col(r, "domain rating", "dr ", "dr")
        try: dr = int(float(dr))
        except: dr = 0
        out[dom] = max(out.get(dom, 0), dr)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--dr", type=int, default=30, help="min DR to report (default 30)")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    a = ap.parse_args()

    SNAP.mkdir(exist_ok=True)
    cur = load(a.csv)
    prev_files = sorted(SNAP.glob("*.json"))
    prev = json.loads(prev_files[-1].read_text()) if prev_files else None

    snap_path = SNAP / f"{a.date}.json"
    snap_path.write_text(json.dumps(cur, indent=1, sort_keys=True))

    if prev is None:
        print(f"Baseline snapshot saved ({len(cur)} referring domains). "
              f"Re-run next week with a fresh export to detect lost links.")
        return

    lost = sorted(((d, prev[d]) for d in prev if d not in cur and prev[d] >= a.dr),
                  key=lambda x: -x[1])
    gained = sorted(((d, cur[d]) for d in cur if d not in prev and cur[d] >= a.dr),
                    key=lambda x: -x[1])

    # Slack-ready summary
    lines = [f"*Backlink watch — {a.date}*  (referring domains DR ≥ {a.dr})",
             f"Total referring domains: {len(cur)}  ({len(cur)-len(prev):+d} vs last snapshot)"]
    if lost:
        lines.append(f"\n:warning: *Lost {len(lost)} high-authority referring domain(s):*")
        for d, dr in lost:
            lines.append(f"  • DR{dr}  {d}")
    else:
        lines.append("\n:white_check_mark: No high-authority referring domains lost.")
    if gained:
        lines.append(f"\n:tada: *Gained {len(gained)}:*")
        for d, dr in gained:
            lines.append(f"  • DR{dr}  {d}")
    summary = "\n".join(lines)

    print(summary)
    (SNAP / f"{a.date}-summary.txt").write_text(summary)
    print(f"\n(summary saved to {SNAP.name}/{a.date}-summary.txt — paste into Slack, or wire a Slack connector to auto-post)")

if __name__ == "__main__":
    main()
