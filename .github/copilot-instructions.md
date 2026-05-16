---
applyTo: "**"
---

## History News — Hugo Best Practices

This site runs on Hugo v0.153.2 (extended). Follow these rules for all Hugo work:

### Content & Front Matter
- **Use archetypes** for new articles — run `hugo new articles/slug.md` or match the existing front matter format exactly
- **Required front matter fields**: title, headline, summary, date, historydate, era, source, image, imagealt, imagecaption, imagecredit, weight, sources
- **YAML strings**: Always use double quotes. Never use single quotes around strings containing apostrophes. Never use `<a href>` tags in YAML — use plain text: `"Source Name — URL"`
- **Dates**: Use `YYYY-MM-DD` format. Future dates hide articles from production builds (useful for scheduling)
- **Draft articles**: Use `draft: true` to hide without deleting. Preview locally with `hugo server -D`
- **Taxonomies**: Currently using `era` taxonomy. Articles can belong to one era. "Memorial Day" is a valid era value.

### Templates & Layouts
- **Layout lookup order**: Hugo checks `layouts/{type}/{layout}.html` → `layouts/{section}/{kind}.html` → `layouts/_default/{kind}.html`
- **Use `{{ define "main" }}`** blocks — they extend `baseof.html`
- **Use partials** for reusable components in `layouts/partials/`
- **Use shortcodes** for reusable content components (put in `layouts/shortcodes/`)
- **Render hooks** (`layouts/_default/_markup/render-*.html`) customize markdown rendering globally

### Performance
- **Use Hugo Pipes** for CSS/JS: `resources.Get | minify | fingerprint` — built-in minification and cache busting
- **Use `pithumbsize` for Wikipedia images** — CDN thumbnails, not raw uploads
- **Prefer `loading="lazy"` on images and iframes**
- **Hugo builds are fast** — 247 pages in ~2.5s. If builds slow down, check for expensive template operations (e.g., unscoped `range` over all pages)

### Content Organization
- **Sections** = folders under `content/`. Each section can have its own layout and list page
- **Page bundles**: For co-located assets, use `content/articles/slug/index.md` with images alongside
- **Data files**: Put JSON/YAML in `data/` — accessible via `.Site.Data.filename`

### URL & SEO
- **Permalinks** are set in config.toml. Current pattern: `/articles/:slug/`
- **Aliases** in front matter create redirects from old URLs
- **Sitemap** auto-generated at `/sitemap.xml`
- **RSS** auto-generated — already configured for home output

### Common Pitfalls (learned from this project)
- **Watch directories**: Hugo only watches directories that contain content or layouts. New top-level content may not hot-reload — restart the server
- **Taxonomy layout warning**: "found no layout file for kind taxonomy" — needs `layouts/_default/taxonomy.html` and `layouts/_default/term.html`
- **Goldmark unsafe HTML**: Set `[markup.goldmark.renderer] unsafe = true` to allow raw HTML in markdown (already configured)
- **Static files**: Everything in `static/` is copied verbatim to the output. No processing unless you use Hugo Pipes with `assets/`

## History News — External Service Guidelines

When working on the History News site, follow these rules for all external services:

### Wikipedia / Wikimedia API
- **Always use batched requests**: Up to 50 titles per API call using `titles=A|B|C`
- **Always use `pithumbsize=1200`** to get CDN-served thumbnail URLs (not `piprop=original`)
  - CDN thumbnails are pre-generated, cached globally, and won't trigger rate limits
  - They also auto-convert SVGs to PNG
- **Always include `maxlag=5`** in every API call — this backs off when servers are busy
- **Always set User-Agent**: `HistoryNewsBot/1.0 (https://github.com/gleifhe/historynews; educational history site) python-urllib`
- **Always respect `Retry-After` header** on 429/503 responses — read the header value, don't guess
- **Never guess Wikimedia file URLs** — always query the API first to get the real URL
- **Never download from `upload.wikimedia.org` directly** when CDN thumbnail URLs are available
- **Use GET requests** for read operations (they're cacheable)
- **Cache results locally** — save API responses to a manifest file to avoid repeat queries
- **Delay between downloads**: 2 seconds minimum between CDN thumbnail downloads
- **Attribution**: Wikimedia images are CC-BY-SA 4.0 or public domain. Include image_credit field in front matter when possible

### YouTube
- **Use oEmbed API** (`youtube.com/oembed?url=...`) for checking if a video exists and is embeddable
- **Never spoof browser User-Agent** when calling YouTube APIs — use a descriptive bot UA
- **Respect embed-disabled signals** — if a video returns `embeddable: false` or the embed page is blocked, don't use it
- **Embed via standard iframe** using `youtube.com/embed/{id}` with `loading="lazy"`
- **For bulk video search**: Use YouTube Data API v3 with an API key (not web scraping)

### Google Fonts
- **Use `preconnect`** hints for `fonts.googleapis.com` and `fonts.gstatic.com`
- **Use `display=swap`** to prevent invisible text during font loading
- **Pin specific weights** — don't load unnecessary weights
- **Consider self-hosting** fonts for GDPR compliance and performance (eliminates third-party requests)

### jsDelivr CDN
- **Always pin version numbers** (e.g., `@7.0.0`) — never use `@latest`
- **Add SRI integrity hash** (`integrity="sha256-..."`) for security
- **Consider bundling locally** for production to eliminate external dependency

### General API Etiquette
- **Never fabricate URLs** — always verify via API lookup first
- **Two-phase approach**: Phase 1 = fast API lookups (batch, cache to manifest), Phase 2 = downloads with rate limiting
- **Resume-safe operations**: Save progress after each step so interrupted runs can continue
- **Respect rate limits proactively** — don't wait to hit 429, space requests appropriately
- **Use JSON format** for all API responses
- **Log which Wikipedia article each image came from** for traceability and accuracy verification

### Ethical API Usage — Mandatory for ALL External Services
Before using ANY API or external service — whether listed above or new — you MUST:

1. **Read the official documentation first**: Find the API's terms of use, rate limit policy, and best practices page. Do not guess how an API works based on what seems to work.
2. **Identify the intended usage pattern**: Every API is designed for a specific access pattern. Use it as intended:
   - If the API offers batching, batch your requests
   - If the API offers CDN/thumbnail endpoints, use them instead of hitting origin servers
   - If the API offers a `maxlag`, `retry-after`, or backoff mechanism, implement it
3. **Set a proper User-Agent on every request**: Format: `HistoryNewsBot/1.0 (https://github.com/gleifhe/historynews; educational history site) library-name`. Never use a browser User-Agent for bot traffic. Never send requests with no User-Agent.
4. **Never assume rate limits — look them up**: Check the API documentation for explicit rate limits. If undocumented, start conservatively (1 request/second) and adjust based on response headers.
5. **Respect every rate-limit signal**:
   - `429 Too Many Requests` — read the `Retry-After` header for exact wait time. Do not guess.
   - `503 Service Unavailable` — the server is overloaded. Back off significantly.
   - `maxlag` responses — the API is telling you it's busy. Wait and retry.
6. **Cache aggressively**: Never request the same data twice. Save API responses to a local manifest or cache file. Check the cache before making any request.
7. **Use the least expensive request possible**: If a thumbnail URL is available, don't download the full-resolution original. If a search result gives you what you need, don't fetch the full page.
8. **Build resume-safe operations**: Save progress after every successful request so interrupted runs can continue without re-requesting data you already have.
9. **Log your API sources**: Record which API call produced each result (e.g., which Wikipedia article each image came from). This enables accuracy verification and troubleshooting without re-querying.
10. **When in doubt, ask before blasting**: If you're about to make more than 50 requests to any API, pause and verify you're using the optimal approach. One batched call is always better than 50 individual ones.

**Why this matters**: Getting throttled or blocked wastes time, violates the service's terms, and makes our bot a bad citizen. Every API we use is a free service run by nonprofits or open-source communities. We repay their generosity by being exemplary users, not by hammering their servers.
