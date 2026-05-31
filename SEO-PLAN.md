# SEO Plan — Amy Fanton Photography

Goal: rank for **fine-art / film wedding photography in London** (and destination), and turn searches into enquiries. The site is fast, static, and now HTTPS — a strong technical base. This plan is the prioritised path from "indexable" to "ranking + converting."

Target audience: engaged couples (and family/newborn clients) searching London + destination wedding photographers. They search by **style + place + intent**.

---

## 1. Keyword strategy (what to rank for)

Map one **primary** keyword per important page; weave **secondary** terms into headings/copy/alt text naturally.

| Page | Primary keyword | Secondary |
|---|---|---|
| Home | `fine art wedding photographer London` | film wedding photography, luxury wedding photographer London |
| Portfolio → Weddings | `London wedding photographer` | English country garden wedding, destination wedding photographer |
| Portfolio → Family | `London family photographer` | natural family photography London |
| Portfolio → Newborn | `London newborn photographer` | lifestyle newborn photography |
| Journal posts | long-tail per shoot | e.g. `Hengrave Hall wedding photographer`, `Santorini elopement photographer`, `Dorney Court wedding` |
| (new) About/Investment | `wedding photography prices London` | wedding photographer cost UK |

**Why long-tail wins for her:** the Journal already targets dozens of specific venues/locations (Hengrave Hall, Dorney Court, Lake Annecy, Santorini, Mayfield Lavender…). Venue + "wedding photographer" is low-competition, high-intent — couples who booked that venue search exactly that. This is her biggest organic opportunity.

**How to find/track:** Google Search Console (free) → Performance → Queries shows what she already gets impressions for. Google autocomplete + "People also ask" + free tiers of Ahrefs/Ubersuggest for volume. (The course's Lesson 10 builds the workflow.)

---

## 2. Technical SEO

### Done ✅
- HTTPS (Cloudflare), `robots.txt`, `sitemap.xml` (auto-generated, 65 URLs), canonical URLs, per-page `<title>` + meta description, Open Graph + Twitter cards + 1200×630 share images, favicon, intrinsic image dimensions (no layout shift), lazy-loading, mobile-responsive.

### To do
- [ ] **Structured data (schema.org JSON-LD)** — biggest technical gap. Add:
  - `LocalBusiness`/`Photographer` on the home (name, area served, sameAs → IG/FB, priceRange).
  - `Article`/`ImageObject` on Journal posts (headline, datePublished, image, author).
  - `BreadcrumbList` on posts. *(Course Lesson 5 builds the generator; wire into `index.html` + `gen_blog.py`.)*
- [ ] **Unique meta descriptions per post** — currently templated ("— wedding and portrait photography by Amy Fanton"). Use each post's first sentence. *(One change in `gen_blog.py`.)*
- [ ] **Descriptive image filenames** — `photo-17.jpg` says nothing to Google; `golden-hour-wedding-kiss-london.jpg` does. Rename portfolio masters + use keyword-rich `alt` (alt is already good on most). *(Big-ish; do for hero + top portfolio images first.)*
- [ ] **Submit sitemap to Google Search Console + Bing Webmaster** (verify domain, submit `sitemap.xml`). This is step one of actually getting indexed/measured.
- [ ] **Self-referencing canonical on the home** — present ✅; ensure apex→www is one canonical (Cloudflare/redirect already sends apex→www).

## 3. On-page / content SEO
- [ ] **H1 per page** — the home's H1 is the logo image; add a real (visually-hidden if needed) `<h1>` with the primary keyword, e.g. "Fine Art Wedding Photographer in London". Posts already have a proper `<h1>` (the title). 
- [ ] **Fill the photoless Journal posts** (see `NEEDED-ORIGINALS.md`) — thin pages with text + 1 image are weak; Google favours rich, image-supported posts. Needs Amy's originals.
- [ ] **Internal linking** — link Journal posts to the relevant Portfolio category and to related posts (e.g. all "London engagement" posts cross-link). Spreads authority + keeps visitors on-site.
- [ ] **Venue/location angle in post copy** — make sure the venue name appears in the post `<title>`, first paragraph, and an `alt`. Many already do; audit with the course tool.

## 4. Local SEO (high ROI for a London photographer)
- [ ] **Google Business Profile** — create/claim it (category: Wedding photographer; service area: London + travels worldwide). This is often the single biggest lever for a local service; it can rank in the map pack and gather reviews. *(Amy/Fernando sets up; can't be automated.)*
- [ ] **NAP consistency** — same Name/Address-or-area/Phone across the site footer, GBP, WeddingWire, Bridebook, Love My Dress directory.
- [ ] **Reviews** — funnel happy couples to leave Google reviews (and surface them as testimonials on-site — already in the IMPROVEMENTS plan).

## 5. Off-page / authority
- [ ] **Press backlinks** — the Press features (Rock My Wedding, Love My Dress, Style Me Pretty, Junebug) are real editorial backlinks. Ensure each links back to the site (most do). Pursue more features — each is a high-authority link.
- [ ] **Vendor cross-links** — venues/planners/florists she's worked with often list "preferred photographers." Ask for a link.

## 6. Measurement & scoring (close the loop)
- [ ] **Google Search Console** — verify + submit sitemap; watch Queries, CTR, average position, Coverage (indexed pages), Core Web Vitals.
- [ ] **Track a keyword set** monthly (the target keywords above) — position + impressions + clicks.
- [ ] **Site SEO score** — run a repeatable audit (the course's capstone tool scores robots/sitemap/titles/meta/schema/headings/images/links/perf into a 0–100 with a fix-list). Re-run after each change.

---

## Priority order (impact × effort)
1. **Submit to Search Console + Bing** (measure first) — *quick, foundational.*
2. **Structured data (schema.org)** — *medium; the biggest missing technical signal.*
3. **Real `<h1>` + unique meta descriptions** — *quick.*
4. **Google Business Profile + reviews** — *medium; biggest local lever (Amy's action).*
5. **Fill thin posts + internal linking** — *ongoing; needs Amy's photos.*
6. **Descriptive image filenames/alt for top images** — *medium.*

The `learn-seo` course (in `~/Projects/learn-seo`) builds the tooling to *do and verify* most of items 2–6 against this site, step by step.
