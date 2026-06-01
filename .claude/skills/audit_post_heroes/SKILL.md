---
name: audit_post_heroes
description: Sweep every Journal post's hero/cover image and flag mismatches — wrong subject for the category (e.g. a bride on a newborn post), the studio logo used as a hero, promo/title-card graphics, missing heroes, or weak detail-only covers. Builds labeled contact sheets so all 63 covers can be eyeballed in one pass. Use when the user asks to audit/sweep blog cover images or after a regeneration. Read-only analysis; fixing a flagged cover is a separate step (use the find_photos skill).
---

# Audit Post Heroes

Find blog posts whose **hero/cover photo doesn't fit the post** so they can be corrected. Cover bugs seen in this project: a wedding/bride photo on a newborn post, the studio **logo** copied in as the first gallery image, a promotional **title-card graphic** instead of a photo, a weak **detail-only** shot (e.g. a cake) as the hero, and posts with **no hero** at all.

## Paths (this project)
- Repo root: `/Users/fernando/Projects/amy-fanton-website`
- Posts: `blog/<slug>.html` (skip `index.html`)
- Cover resolves to either `images/blog/<slug>.jpg` (manual cover) or `images/blog/gallery/<slug>/00.jpg` (first gallery frame), per `tools/gen_blog.py`
- Python+Pillow: `/tmp/pilenv/bin/python3`
- Helper: `.claude/skills/audit_post_heroes/audit_covers.py`

## Workflow

### 1. Run the audit
```
/tmp/pilenv/bin/python3 .claude/skills/audit_post_heroes/audit_covers.py
```
It prints a table `idx | slug | [category] | hero-filename | ⚑flags` and writes labeled contact sheets to `/tmp/cover_audit_NN.png` (each cell = the hero photo captioned with `idx slug [category]`, red if auto-flagged).

Auto-flags are only a pre-sort, **not** the answer:
- `NO-HERO` — post has no `post-hero` block
- `LOGO?` — hero filename looks like the studio logo
- `TINY` — hero < 600px long edge (often a logo/placeholder)
- `MISSING-FILE` — hero src doesn't resolve on disk

### 2. Eyeball every sheet
Read each `/tmp/cover_audit_NN.png` with the Read tool. For each cover ask: **does the photo match the slug + category?** Flag, by eye, anything the heuristics can't catch:
- **Wrong subject for the category** — a couple/bride on a *Newborn & Maternity* or *Family* post; a baby on a *Weddings* post.
- **Wrong shoot/place** — e.g. a "Santorini" post whose hero shows no Greece; a destination post with an unrelated studio shot.
- **Not a photo** — a title-card / announcement graphic, a logo, a flyer.
- **Weak hero** — a detail-only shot (cake, invitation, ring) where a portrait would carry the post better.
- **Category mismatch** — hero is fine but the `[category]` is wrong (e.g. a child session tagged *Engagements*).

### 3. Confirm suspects at full size
For anything uncertain, build a larger labeled strip of just the suspect heroes (resolve each hero src from the post HTML, thumbnail to ~480px, caption with the slug) and Read it. Don't rely on the small grid for close calls.

### 4. Report — don't fix here
Produce a tight list: `slug — [category] — what the hero shows — why it's wrong/weak — severity`. Group by severity (clear mismatch / weak / category-only). **This skill is read-only.** Fixing a cover (finding the right image + wiring it) is the `find_photos` skill's job; hand off per-post. Only after explicit confirmation should anything be copied/regenerated.

## Guardrails
- Read-only: never copy, overwrite, or regenerate from this skill.
- A detail/establishing shot isn't automatically "wrong" — flag it as *weak*, let the user decide.
- Tips/roundup/inspiration posts intentionally mix subjects; judge their hero on appeal, not single-shoot consistency.
