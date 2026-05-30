---
name: Improve_Fanton_Photography
description: For the Amy Fanton photography site — research peer/competitor fine-art wedding & portrait photography websites, audit Amy's current site against them and against web best practices, and produce a prioritized, actionable list of improvement suggestions (first impression, design/UX, portfolio, storytelling, social proof, conversion/inquiry, journal/SEO, performance, accessibility, technical). Use when the user wants ideas to make the site better, a competitive review, or a site audit. READ-ONLY / ADVISORY — it proposes changes and rates the site; it does NOT edit the site unless the user approves specific changes afterward.
---

# Improve Fanton Photography

Look outward (what the best photographer sites do), look inward (what Amy's site does), and return a **prioritized, concrete** improvement plan. Be specific and honest — cite real examples and name the exact file/section to change. **Do not edit the site as part of this skill; only recommend.** If the user then picks suggestions, implement them as a separate step.

## Paths (this project)
- Repo root: `/Users/fernando/Projects/amy-fanton-website`
- Home: `index.html` · styles: `styles.css` · journal generator: `tools/gen_blog.py` · posts: `blog/*.html`
- Live site: `https://www.fantonphotography.com` (GitHub Pages, fronted by Cloudflare for HTTPS)
- Current shape (keep in mind, re-verify each run as it evolves): single-page home with **hero → intro → Portfolio (Weddings incl. a Destination subsection / Family & Children / Newborn & Maternity) → About → Press (styled wordmark cards) → Contact (enquiry form + WhatsApp button + socials)**; a **Journal** (60+ posts via the generator); a private **Studio** post-composer page.

## Workflow

### 1. Audit Amy's current site (inward)
Read `index.html` + `styles.css` and skim the Journal. Build a factual map of what exists, then run the quick technical checks below. Note strengths AND gaps. Cover:
- **First impression / hero** — image quality, headline, value proposition, CTA above the fold.
- **Navigation / IA** — labels, order, mobile menu, how fast a visitor reaches Portfolio + Contact.
- **Portfolio** — curation, grouping, image sizes, load behaviour, lightbox, captions.
- **Storytelling / About** — photographer's voice, face/photo, approach, locations served.
- **Social proof** — Press, testimonials/reviews, real-wedding features.
- **Conversion / inquiry** — contact form fields, response promise, WhatsApp/email, pricing or "investment" guidance, FAQ, process/what-to-expect.
- **Journal / SEO** — post quality, internal linking, categories, titles/meta, freshness.
- **Brand** — typography, colour, logo, consistency, whitespace.

Quick technical checks (grep/inspect, don't guess):
```
grep -c 'meta name="description"' index.html blog/*.html | head        # meta descriptions present?
grep -oE '<meta property="og:[^"]+"' index.html | sort -u              # Open Graph / social-share tags?
ls favicon* site.webmanifest sitemap.xml robots.txt 2>/dev/null        # discoverability basics
grep -c 'alt=""' index.html blog/*.html                                # empty alt text (a11y/SEO)
grep -rc 'width=' index.html | head                                    # intrinsic image dims (CLS)
grep -ic 'testimonial\|review\|"\bloved\b"' index.html                  # any testimonials?
grep -ic 'pricing\|investment\|faq\|frequently asked' index.html       # pricing/FAQ signals
```
Also note: page weight (lots of full-size JPEGs?), `loading="lazy"` usage, responsive/mobile behaviour, and HTTPS (now via Cloudflare).

### 2. Study peer / competitor sites (outward)
Pick ~4–6 respected fine-art wedding/portrait photographer sites and study each (WebSearch + WebFetch the homepage, portfolio, about, contact, journal, info/pricing). Good reference set (refresh/extend as needed):
- **KT Merry**, **Jose Villa**, **Elizabeth Messina**, **Jen Huang**, **Erich McVey**, **Taylor & Porter**, **Rebecca Yale**, **Joel Serrato**.
- Plus 1–2 strong London/UK fine-art peers for local relevance (search "fine art wedding photographer London").
For each, capture what they do well that's *transferable*: hero treatment, how they present portfolio (full-bleed vs grid), the About voice, how they drive inquiries (clear CTA, investment guide, process page, FAQ), testimonials placement, journal/SEO depth, performance, mobile.

### 3. Compare across dimensions → gaps
For each dimension (first impression, IA, portfolio, storytelling, social proof, conversion, journal/SEO, performance, a11y, brand): state **what the best do**, **what Amy's site does**, the **gap**, and a **concrete suggestion** naming the file/section. Avoid generic advice ("improve SEO") — be specific ("add a `<meta name="description">` per blog post in `gen_blog.py`'s HEAD template; currently absent").

### 4. Prioritise
Rank suggestions by **impact × effort**. Lead with high-impact / low-effort wins. Tag each: `quick` (minutes), `medium` (an hour), `big` (a project). Group into: **Do now / Worth doing / Nice to have**.

### 5. Deliver the report
Present a tight, skimmable report:
- One-paragraph verdict + an honest score per dimension (e.g. /5).
- The prioritised suggestion list (impact, effort, exact location).
- 3–5 "if you only do three things" picks.
Optionally offer to save it to `IMPROVEMENTS.md` in the repo (ask first). Then offer to implement any the user selects — as a **separate** step, following all the usual project rules.

## Guardrails
- **Advisory only** — never edit `index.html`, `styles.css`, posts, or the generator as part of this skill. Recommend; implement only after the user picks.
- Respect standing project constraints in any suggestion: **Amy's own authorised photos only, never stock**; clothed-only (no nude/boudoir maternity); never auto-publish; don't suggest hosting publications' copyrighted logo files (styled wordmarks instead).
- Be concrete and honest — cite the peer example and the exact file/line to change. No vague filler.
- Don't suggest things that fight the brand (it's a calm, elegant fine-art aesthetic — recommend within that, not a loud redesign) unless the user asks for a rethink.
