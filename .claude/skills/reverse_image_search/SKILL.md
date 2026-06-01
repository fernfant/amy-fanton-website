---
name: reverse_image_search
description: Find MORE photos of a shoot (or the page where it was published) by reverse-image-searching one of Amy Fanton's existing site photos. Use when the user wants to track down the rest of a couple's/shoot's images online from a single photo we already have — e.g. to fill out a Journal post. Produces one-click reverse-search links for the user to run (Google Lens/Yandex/TinEye/Bing) plus an agent-side text-search fallback, then harvests Amy's photos from the feature page found (verifying her credit).
---

# Reverse Image Search

Given **one** of Amy's photos that's already on the site, find the rest of that
shoot online — usually a wedding-blog feature with the full gallery — and pull
the additional frames into the vault / a Journal post.

## ⚠️ Environment reality (read first)
The reverse-image engines (**Google Lens, TinEye, Yandex, Bing Visual**) are
**bot-protected, JavaScript-rendered, and blocked by the agent's browser
allowlist.** So the agent **cannot** upload-and-read matches directly:
`WebFetch` only returns the page title, and `navigate` is refused for those
domains. Don't waste turns retrying them. Use the two paths below.

## Paths
- Repo root: `/Users/fernando/Projects/amy-fanton-website`
- Helper: `.claude/skills/reverse_image_search/reverse_links.py`
- Live base: `https://www.fantonphotography.com/`

### Path A — visual reverse search (user runs it)
1. Pick a clean single-subject frame already **live** on the site (a gallery
   file or `images/originals/<descriptive>.jpg`). It must be committed +
   deployed so the engines can fetch it by URL.
2. Generate the deep-links:
   ```
   python3 .claude/skills/reverse_image_search/reverse_links.py <local-path-or-live-URL>
   ```
   This prints the public URL + Google Lens / Yandex / TinEye / Bing links.
3. Give the links to the user. They open them in their normal browser (no
   restrictions), eyeball the results, and paste back the **source/feature page
   URL** (and/or confirm which results are the same couple). Yandex is best for
   *other frames of the same people*; Lens/TinEye best for the *exact source*.

### Path B — agent text search (no upload needed)
Often faster: describe the shoot from the photo + post text — **subjects,
venue/landmark, wardrobe, colours, season** — and search:
```
WebSearch:  "Amy Fanton" <venue> <distinctive details>      (e.g. "Amy Fanton" Wisley greenhouse navy tuxedo)
```
Also check her hubs: Love My Dress / Rock My Wedding / Style Me Pretty / BLOVED
profiles and the site's own Press page. These frequently host the full gallery.

## Harvest (after the feature page is found)
Hand the feature URL to the **browse-photos-web** skill (or harvest manually):
download the full-resolution originals (bare path, no `WxH` resize prefix),
contact-sheet them, and add to the post / vault.

## Guardrails
- **⚠️ Verify the photographer credit before using ANY off-site photo.** Popular
  venues are shot by many photographers; only use images explicitly credited to
  **Amy Fanton** (credit line and/or `Fanton-Photography-NNN.jpg` filenames). If
  credited to anyone else (or uncredited), do not use them.
- **Single-couple integrity:** when filling a single-shoot post, every added
  frame must be the *same* couple — confirm at full size; never pad with
  maybe-matches (see the find_photos skill).
- These are Amy's authorized photos (no consent flag). Clothed only; never
  invent/AI-generate images. Always confirm before copying; never auto-publish.
