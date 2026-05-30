---
name: find_photos
description: For the Amy Fanton photography site — given a blog post URL or slug (e.g. http://localhost:8051/blog/london-wedding-editorial.html), read the post's text, infer what the photos should look like (subjects, location/landmarks, season, light, props), scan the image vault (Vault/_AllImages, including the Instagram sets), visually match candidate photos, and prompt the user before copying the chosen ones into the post and regenerating. Use whenever the user wants to find/add photos to a Journal post from existing vault images.
---

# Blog Photo Match

Find and add the right vault photos to a photoless (or under-filled) Journal post by reading the post text, inferring the scene, and visually matching against the local image vault. **Always get explicit confirmation before copying anything.**

## Paths (this project)

- Repo root: `/Users/fernando/Projects/amy-fanton-website`
- Post pages: `blog/<slug>.html`
- Post text: `/tmp/blog_data/new_text.json` (keyed by slug → `paras`), fallback `Vault/_AllText/*__<slug>.txt`, fallback the rendered `blog/<slug>.html`
- Flattened vault (all sources, incl. Instagram): `Vault/_AllImages/` — filenames are provenance-prefixed (e.g. `Instagram-Profile__ig_XXX.jpg`, `Wayback-Recovered__<slug>__NN.jpg`, `Facebook__….jpg`)
- Per-source folders: `Vault/{Instagram-Profile,Instagram-Tagged,Facebook,Wayback-Recovered,Screenshots}`
- **Generator reads each post's gallery from** `Vault/Wayback-Recovered/<slug>/` → outputs `images/blog/gallery/<slug>/`
- Generator: `tools/gen_blog.py` — run with `/tmp/pilenv/bin/python3 tools/gen_blog.py`
- Python venv with Pillow: `/tmp/pilenv/bin/python3`
- Contact-sheet helper: `.claude/skills/find_photos/contact_sheet.py`

## Workflow

### 1. Resolve the slug
From a URL like `http://localhost:8051/blog/<slug>.html` take `<slug>`. A bare slug is fine too. Confirm `blog/<slug>.html` exists.

### 2. Read the post text
Pull the paragraphs from `new_text.json[slug].paras` (preferred). If absent, read `Vault/_AllText/*__<slug>.txt`, else extract paragraph text from `blog/<slug>.html`. Also note the post's category and date.

### 3. Build a visual brief
From the text, write down the concrete things a matching photo would show. Be specific — this is the "pattern recognition" step:
- **Subjects:** couple / engagement / wedding / family / newborn / maternity / children
- **Location & landmarks:** e.g. Thames, a bridge (Westminster/Tower), Hyde Park, a garden/ruins, a beach, Greece, a phone booth, lavender field, a studio/home
- **Season & light:** winter/"bitter cold", autumn leaves, summer green, "clear sunny day", golden hour, overcast
- **Props / colors / wardrobe:** red coat, gown color, suits, ball gown, flowers
Restate the brief to the user in one or two lines so they can sanity-check your read.

### 4. Contact-sheet the vault
Generate labeled grids so you can actually look at the images (don't guess from filenames):
```
/tmp/pilenv/bin/python3 .claude/skills/find_photos/contact_sheet.py \
  --out /tmp/match_sheet Vault/_AllImages --per 48 --cols 6
```
View each `/tmp/match_sheet_NN.png` with the Read tool. ~440 images → ~9–10 sheets. To narrow first, sheet a likely source or use `--grep` (e.g. `--grep wedding`) or point at specific `Vault/<source>` / `Vault/Wayback-Recovered/<related-slug>` folders. For shortlisted images, open the full-size file to confirm the scene before recommending it.

### 4b. Augment from published sources when the vault is thin
The local vault is incomplete — many shoots were only partially recovered. If a post has few/no good vault matches, **go find more of Amy's own published photos** before settling:
1. **Check the site's own Press section + her directory profiles** (Rock My Wedding, Love My Dress) — a post often maps to a press feature with the full gallery.
2. **Web-search the specific shoot**: venue + couple + distinctive details + "Amy Fanton" (e.g. `Amy Fanton "Fig House" Los Angeles wedding`). The post text usually names the venue/colors/details — use them.
3. **Dead press page?** RMW (and others) 301 a removed *article* to the homepage (200 → `url_effective` = the homepage = dead). But the **image CDN usually still serves the files** — pull the gallery URLs from a Wayback capture of the page (`web.archive.org/cdx/search/cdx?url=<page>`, fetch a 200 snapshot with `id_`, grep for the shoot's image URLs incl. the Pinterest `media=` links), then download the **bare original path** (e.g. `rockmywedding.co.uk/wp-content/gallery/<slug>/<file>.jpg`, no `WxH/` resize prefix = largest). Throttle (~0.3s) to avoid rate-limiting.
4. **⚠️ CRITICAL — verify the photographer credit before using ANY off-site photo.** Popular venues are shot by many photographers; a feature of the *same venue* is often a *different couple by a different photographer*. Only use images explicitly credited to **Amy Fanton** (credit line and/or filename like `Fanton-Photography-NNN.jpg`). If the credit is anyone else (or absent), do **not** use them — treat like stock. Amy's text may also mention a second shooter; her published galleries are still credited to her studio, but never pull from a feature credited to another studio.

Staged downloads go in `/tmp/<slug>/`; contact-sheet and curate them the same as vault images. These are still Amy's authorized photos (no consent flag), but copyright-credit verification above is mandatory.

### 5. Rank candidates + duplicate check
First decide the **post type** — it flips the matching rule:
- **Single-shoot post** (one wedding/engagement/session, e.g. "Louise Roe's Dorney Court Wedding", "Goodbye London Couple's Shoot") → all photos must be the **same couple**. Never mix couples; pull only that shoot's frames.
- **Tips / advice / roundup / inspiration post** (e.g. "Best Tips for Beautiful Engagement Photos", "Best Proposal Photography Ideas") → the photos are **illustrative**, so a **variety from several different couples/sessions is correct and desired**. Pulling a few strong frames from multiple existing galleries (Hyde Park, Kensington, a proposal, a flower field…) is the right move — reuse across the source post and the tips post is fine/expected here, not a problem.

Pick the images that match the brief; for each note **why** it fits. For single-shoot posts: if a candidate's provenance shows it belongs to another shoot (`Wayback-Recovered__<other-slug>__…`), flag that reusing it would mix couples — let the user decide, don't silently reuse. For tips/roundup posts, that same cross-shoot variety is the goal.

### 6. Prompt for confirmation — DO NOT copy yet
**Always present at least 3 distinct candidate options**, each with a clear one-line description so the user can choose without opening the file. For every candidate give: `#N · filename · what the photo shows (subject/location/light/wardrobe) · why it matches the brief · any duplicate caveat`. If fewer than 3 vault images plausibly fit, say so explicitly and still surface the 3 closest (clearly labeling weaker matches) rather than narrowing to one.

Then ask which to add and which should be the **cover** (first image). Wait for an explicit answer. Offer selection options like "use #1 only", "use #1+#3", "use all", or "none / I'll add my own".

### 7. Copy + regenerate (after confirmation)
Copy the chosen files into `Vault/Wayback-Recovered/<slug>/`, named so the cover sorts first (zero-padded, e.g. `00_<desc>.jpg`, `01_…`). Then:
```
/tmp/pilenv/bin/python3 tools/gen_blog.py
```
Verify `blog/<slug>.html` now has a `post-hero` and the expected number of `gallery-item`s. Tell the user to refresh `http://localhost:8051/blog/<slug>.html`.

### 8. Hand off
Report the new pending count and that releasing a version (commit/tag/push) is a separate step the user can ask for.

## Guardrails
- These are Amy's (the user's wife's) authorized photos — no consent flag needed.
- Never add nude/boudoir maternity; clothed only.
- Never invent or download stock images — only use what's already in the vault.
- Always confirm before copying; never auto-publish.
