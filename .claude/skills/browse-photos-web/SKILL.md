---
name: browse-photos-web
description: For the Amy Fanton photography site — given a web URL that lists Amy's published features (e.g. a Style Me Pretty / Rock My Wedding / Love My Dress / Junebug search or profile page, like https://www.stylemepretty.com/search/posts/Amy%20fanton?page=1), probe the page, enumerate every feature credited to Amy Fanton, download HER photos into the vault, match each feature to an existing Journal post (or flag it as a new-post candidate), and update the posts. Use whenever the user wants to harvest Amy's off-site published galleries and fold them into the blog.
---

# Browse Photos (Web)

Probe a press/listing URL, pull Amy's **own credited** photos from each feature, and wire them into matching Journal posts. **Verify the photographer credit on every image, and confirm before publishing.**

## Paths (this project)
- Repo root: `/Users/fernando/Projects/amy-fanton-website`
- Generator: `tools/gen_blog.py` — run `/tmp/pilenv/bin/python3 tools/gen_blog.py`
- Python venv (Pillow): `/tmp/pilenv/bin/python3`
- Contact sheets: `.claude/skills/find_photos/contact_sheet.py`
- Post page: `blog/<slug>.html`; gallery output: `images/blog/gallery/<slug>/`; separate cover (optional): `images/blog/<slug>.jpg`
- **Where the generator reads a post's gallery from depends on its row in `gen_blog.py`:**
  - FEAT list (top of file): `("<slug>","...","<Cat>","<gdir>",...)` → reads `/tmp/feat_imgs/<gdir>/`
  - NEW_SRC posts: reads `Vault/Wayback-Recovered/<slug>/`
  - Always grep `gen_blog.py` for the slug first to learn which source dir it uses. Staging in the wrong dir = generator ignores it.
- Staging downloads: `/tmp/web_harvest/<feature-slug>/`

## Workflow

### 1. Probe the URL — enumerate Amy's features
Figure out the platform, then get the authoritative list of posts credited to Amy (don't trust the rendered count — a search page often pads with "related" results):
- **WordPress** (Style Me Pretty, Love My Dress, many blogs): `curl …/wp-json/wp/v2/posts?search=Amy%20Fanton&per_page=100&_fields=id,date,link,title`. Full-text only — misses posts where the credit isn't in the body.
- **Algolia-backed search** (SMP): the front-end JS holds a public search key. Fetch the React bundle, extract the app id (`<id>-dsn.algolia.net`), the 32-hex search key, and the index name (`indexName:"posts"`), then `POST https://<app>-dsn.algolia.net/1/indexes/<index>/query` with headers `X-Algolia-API-Key` / `X-Algolia-Application-Id` and body `{"query":"Amy Fanton","hitsPerPage":60}`. `nbHits` is the true count.
- **Static HTML**: grep the page for article links.
- **JS-rendered with no API found**: fall back to the Chrome MCP browser — load the URL, read the result anchors.
- Produce a list: `{title, date, url}` per feature.

### 2. For each feature — VERIFY CREDIT, then extract image URLs
- Fetch the feature (WP: `…/wp-json/wp/v2/posts/<id>?_fields=content,title`; else the page HTML).
- **⚠️ MANDATORY copyright check:** confirm the feature credits **Amy Fanton**. SMP stores per-image credits as a structured block in the content: `"credits":[{"type":"Photography","by":"Amy Fanton Photography",…}]`. Only use images whose credit is Amy Fanton. If a feature (or a specific image) is credited to another studio — **skip it** (popular venues are shot by many photographers). Treat anything not clearly Amy's as stock = do not use.
- Extract full-size image URLs. **SMP pattern:** `https://is.stylemepretty.com/submissions/uploads/<galleryId>/<imgId>$!900x.jpg` — the `$!900x` is a resize directive; request a larger size (e.g. `$!1200x`) or the biggest that returns a real JPEG. **Dead RMW/press article?** It often 301s to the homepage but the image CDN still serves files — recover URLs from a Wayback capture of the page, then pull the bare `/wp-content/gallery/<slug>/<file>.jpg` path (see find_photos step 4b).
- Download to `/tmp/web_harvest/<feature-slug>/`, validating each is a real JPEG (`file --mime-type`). Throttle (~0.3s) to avoid rate-limiting.

### 3. Match each feature to a Journal post
- List slugs (`ls blog/*.html`) and match by venue / location / couple / season / year (e.g. "Greek Island Elopement" → `santorini-elopement-photos`; "Elegant Argentinian" → `elegant-old-word-argentina-bridal-shoot`; "Will & Kate's Backyard" e-sesh → `kensington-engagement-session-…`).
- No match → **new-post candidate**: capture the SMP post text for the body, propose a slug/category/date, and confirm with the user before creating (new posts need a generator row + text source).

### 4. Curate (contact-sheet) + confirm — DO NOT publish yet
- Contact-sheet the downloaded set; open shortlisted full-size to confirm. Skip near-duplicates and anything off-brand. Never include nude/boudoir maternity (clothed only).
- Present a recommended set (cover + ordered gallery) with one-line descriptions, per the find_photos confirmation rules (≥3 options where it's a choice). Wait for explicit approval.

### 5. Wire in + regenerate (after confirmation)
- Grep `gen_blog.py` for the slug to find its source dir (FEAT `gdir` vs Vault folder). Copy chosen images there, zero-padded in display order (`00_*.jpg`…). For a distinct hero, set `images/blog/<slug>.jpg` (then that image won't duplicate in the gallery).
- **Clean the old output** (`rm images/blog/gallery/<slug>/*.jpg`) so no orphan files survive, then `/tmp/pilenv/bin/python3 tools/gen_blog.py`.
- Verify `blog/<slug>.html` has the expected `post-hero` + `gallery-item` count and 0 broken images (preview).

### 6. Hand off
Report per-feature: matched post, # photos added, any skipped-for-credit, any new-post candidates. Note that committing/tagging a release is a separate step the user requests. Note that FEAT-sourced images live in ephemeral `/tmp/feat_imgs/<gdir>` but the committed `images/blog/gallery/<slug>/` output is permanent.

## Guardrails
- These are Amy's (the user's wife's) authorized photos — no consent flag — **but** the per-image photographer-credit check in step 2 is mandatory: never publish a photo credited to another studio.
- Don't trust a search page's visible count; use the platform's API (`nbHits`, WP REST) for the real list.
- Never invent or download stock; only Amy-credited images.
- Always confirm before copying into a post; never auto-publish.
- Clothed only; never nude/boudoir maternity.
