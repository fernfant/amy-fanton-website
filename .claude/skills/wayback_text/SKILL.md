---
name: wayback_text
description: Recover the VERBATIM body text of an old fantonphotography.com Journal post from the Wayback Machine and put it into the rebuilt post. Use when a post's text is thin/paraphrased/wrong (e.g. only a Facebook caption) and the user wants it to match what the original site actually said. Pairs with find_photos / browse-photos-web (which recover photos) — this recovers the words.
---

# Wayback Text

Pull the **exact** original write-up for a post from the Internet Archive and
load it into the post body — faithfully, no paraphrasing.

## Paths
- Repo root: `/Users/fernando/Projects/amy-fanton-website`
- Helper: `.claude/skills/wayback_text/wayback_text.py`
- Post text source the generator reads: `/tmp/blog_data/posts.json`
  (a list of `{"slug","title","date","paras":[...]}`; the post body = these
  `paras`, split into `<p>` by `gen_blog.py`). For a CUR post, also blank its
  inline `fb` lead in `gen_blog.py` if you want the body to be *only* the
  recovered text.
- Generator: `/tmp/pilenv/bin/python3 tools/gen_blog.py`

## Workflow
1. **Get the snapshot.** Prefer a specific Wayback URL the user gives
   (`https://web.archive.org/web/<ts>/http://www.fantonphotography.com/<slug>/`).
   A live/original URL also works — the helper finds the latest 200 snapshot via
   the CDX API.
2. **Extract verbatim** (needs network → run with the sandbox disabled):
   ```
   python3 .claude/skills/wayback_text/wayback_text.py "<wayback-or-live-url>"
   ```
   It prints the slug, each paragraph, and a ready-to-paste JSON `paras` array.
   Extraction decodes HTML entities and collapses internal whitespace **only** —
   wording and spelling are left exactly as archived (don't "fix" typos unless
   the user asks; the goal is to *match* the original).
3. **Write it into `posts.json`** under the post's slug (keep its existing
   `date`; set `title`). Easiest is a tiny Python step that extracts straight
   from the fetched HTML and writes `paras`, so the copy is guaranteed faithful
   (no re-typing). If the slug was renamed, re-key the entry to the new slug.
4. **Regenerate + verify:** `gen_blog.py`, then confirm `blog/<slug>.html`'s
   `post-body` starts with the real opening line and the auto meta-description
   reflects it.

## Guardrails
- **Faithful, not edited** — match the archived text; no rewriting/summarising.
- Only Amy's own posts (her words; no consent flag). Verify the snapshot is the
  right post/shoot before importing.
- `posts.json` lives in `/tmp` (ephemeral) like the rest of the post text —
  same fragility as every other post; fine for regeneration.
