---
applyTo: "**"
---

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
