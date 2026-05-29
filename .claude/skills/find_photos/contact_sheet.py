#!/usr/bin/env python3
"""Build labeled contact sheets from image folders so the agent can eyeball matches.

Usage:
  contact_sheet.py --out /tmp/sheet SRC [SRC ...] [--per 48] [--cols 6] [--cell 240] [--grep couple]

Writes /tmp/sheet_01.png, _02.png ... Each cell is labeled with the file's
provenance (parent folder) + name so the agent can spot duplicates / source.
Requires Pillow. Run with the project venv: /tmp/pilenv/bin/python3
"""
import sys, argparse, pathlib
from PIL import Image, ImageDraw

EXT = {".jpg", ".jpeg", ".png"}

def gather(srcs, pat):
    files = []
    for s in srcs:
        p = pathlib.Path(s)
        if not p.exists():
            continue
        for f in sorted(p.rglob("*")):
            if f.suffix.lower() in EXT and not f.name.startswith("._"):
                if pat and pat.lower() not in f.name.lower():
                    continue
                files.append(f)
    return files

def render(files, out, per, cols, cell):
    lbl = 26
    sheets = []
    for s in range(0, len(files), per):
        chunk = files[s:s + per]
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * cell, rows * (cell + lbl)), "white")
        d = ImageDraw.Draw(sheet)
        for i, f in enumerate(chunk):
            try:
                im = Image.open(f).convert("RGB")
            except Exception:
                continue
            im.thumbnail((cell - 6, cell - 6))
            x, y = (i % cols) * cell, (i // cols) * (cell + lbl)
            sheet.paste(im, (x + 3, y + 3 + lbl))
            d.text((x + 3, y + 2), f.parent.name[:34], fill="navy")
            d.text((x + 3, y + 14), f.name[:34], fill="black")
        n = s // per + 1
        path = f"{out}_{n:02d}.png"
        sheet.save(path)
        sheets.append((path, len(chunk)))
    return sheets

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("srcs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--per", type=int, default=48)
    ap.add_argument("--cols", type=int, default=6)
    ap.add_argument("--cell", type=int, default=240)
    ap.add_argument("--grep", default="")
    a = ap.parse_args()
    files = gather(a.srcs, a.grep)
    if not files:
        print("no images found"); sys.exit(1)
    sheets = render(files, a.out, a.per, a.cols, a.cell)
    print(f"{len(files)} images -> {len(sheets)} sheet(s)")
    for path, n in sheets:
        print(f"  {path}  ({n} imgs)")

if __name__ == "__main__":
    main()
