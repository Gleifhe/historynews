# History News

**Where the Past Makes Headlines**

A Hugo-powered history site that presents historical events as breaking news stories. 757 articles spanning 5,000 years of human history, from Ancient Rome to the 21st century, each written as if the reporter were on the scene.

🔗 **Live site:** [red-stone-0ed2b5d10.7.azurestaticapps.net](https://red-stone-0ed2b5d10.7.azurestaticapps.net/)

---

## Overview

History News reimagines history through the lens of journalism. Every article is written in the present tense with newspaper-style headlines, primary source quotes, and vivid eyewitness-style reporting. Each article also includes personal growth lessons drawn from the events.

### Key Features

- **757 articles** across 35+ historical eras
- **366 "This Day in History" articles** — one landmark event for every calendar day
- **Personal Growth framework** — 15 principles distilled from historical events ([/growth/](https://red-stone-0ed2b5d10.7.azurestaticapps.net/growth/))
- **Era-based browsing** with sidebar filters (Ancient World → 21st Century)
- **Responsive images** with 400px thumbnails for cards and 800px hero images with `srcset`
- **Full-text search** powered by Fuse.js
- **Auto-deploy** via GitHub Actions to Azure Static Web Apps
- **Lighthouse scores:** 87 Performance · 95 Accessibility · 96 Best Practices · 100 SEO

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Static site generator | [Hugo](https://gohugo.io/) v0.153.2 (extended) |
| Hosting | [Azure Static Web Apps](https://azure.microsoft.com/en-us/products/app-service/static) (free tier) |
| CI/CD | GitHub Actions — auto-deploy on push + daily cron |
| CSS/JS | Hugo Pipes — minified, fingerprinted, SRI hashes |
| Search | [Fuse.js](https://www.fusejs.io/) v7.0.0 (client-side fuzzy search) |
| Fonts | Google Fonts — Playfair Display + Source Sans Pro |
| Image source | Wikimedia Commons via API (CDN thumbnails, CC-BY-SA/Public Domain) |
| Automation | 37 Python scripts + 2 PowerShell scripts |

---

## Project Structure

```
historynews/
├── archetypes/
│   └── articles.md              # Article template for `hugo new`
├── assets/
│   ├── css/style.css            # Main stylesheet (Hugo Pipes)
│   └── js/search.js             # Fuse.js search integration
├── content/
│   ├── articles/                # 757 article markdown files
│   │   ├── _index.md            # Section landing page
│   │   ├── moon-landing-headlines.md
│   │   ├── tdih-01-01-01.md     # This Day in History articles
│   │   └── ...
│   ├── growth.md                # Personal Growth framework page
│   └── memorial-day.md          # Memorial Day landing page
├── layouts/
│   ├── _default/
│   │   ├── baseof.html          # Base template (head, meta, scripts)
│   │   ├── taxonomy.html        # Era listing page
│   │   └── term.html            # Individual era page
│   ├── articles/
│   │   ├── list.html            # All articles index with era sidebar
│   │   └── single.html          # Individual article template
│   ├── growth/single.html       # Growth framework page
│   ├── memorial-day/single.html # Memorial Day landing page
│   ├── partials/                # Header, footer, nav components
│   ├── 404.html                 # Custom 404 page
│   ├── index.html               # Homepage
│   └── index.json               # JSON feed for search
├── static/
│   └── images/
│       └── articles/            # 757 article images (800px, ~110KB avg)
│           └── thumb/           # 757 thumbnails (400px, ~28KB avg)
├── scripts/                     # Automation scripts (see below)
├── docs/                        # Project documentation
├── .github/
│   ├── copilot-instructions.md  # AI coding guidelines
│   ├── workflows/               # CI/CD pipeline
│   ├── lighthouse/              # Lighthouse CI config
│   └── pa11y/                   # Accessibility audit config
├── config.toml                  # Hugo site configuration
├── staticwebapp.config.json     # Azure SWA config (headers, 404, MIME)
└── .gitattributes               # Git LFS tracking for images
```

---

## Getting Started

### Prerequisites

- [Hugo](https://gohugo.io/installation/) v0.153.2+ (extended edition)
- [Python](https://www.python.org/downloads/) 3.10+ (for automation scripts)
- [Pillow](https://pillow.readthedocs.io/) (`pip install Pillow`) for image processing
- [Git LFS](https://git-lfs.github.com/) for image storage

### Local Development

```bash
# Clone the repository
git clone https://github.com/Gleifhe/historynews.git
cd historynews

# Install Git LFS and pull images
git lfs install
git lfs pull

# Start the development server
hugo server --buildFuture

# Open http://localhost:1313
```

### Build for Production

```bash
hugo --minify
# Output is in public/
```

---

## Article Format

Articles use YAML front matter with this structure:

```yaml
---
title: "The Boston Tea Party"
headline: "TEA DUMPED IN HARBOR: Colonists Destroy 342 Chests of Tea"
summary: "On December 16, 1773, colonists dumped 342 chests of tea..."
date: 2026-05-20
historydate: "December 16, 1773"
era: "18th Century"
source: "Library of Congress"
image: "/images/articles/boston-tea-party.jpg"
imagealt: "Colonists dumping tea into Boston Harbor"
imagecaption: "The Boston Tea Party, 1773"
imagecredit: "Wikimedia Commons / Public Domain"
weight: 200
sources:
  - "Wikipedia — Boston Tea Party — https://en.wikipedia.org/wiki/Boston_Tea_Party"
  - "History.com — Boston Tea Party — https://www.history.com/topics"
  - "Library of Congress — Primary Sources — https://www.loc.gov"
---

Article body in markdown with ## section headings...
```

### Body Structure

Each article follows this pattern:
1. **Opening** — Breaking news framing from the historical moment
2. **Background** — Historical context (what led to this moment)
3. **What Happened** — Core narrative with primary source details
4. **Aftermath/Consequences** — Immediate and long-term impact
5. **What We Can Learn** — Personal growth lessons
6. **Connection to Today** — Relevance to 2026

### Eras

Articles are categorized into historical eras: Ancient World, Medieval, Renaissance, 16th–19th Century, Victorian Era, Colonial America, Gilded Age, Progressive Era, World War I/II, Cold War, Civil Rights Era, Space Age, 21st Century, and more.

---

## Scripts

37 active Python scripts and 2 PowerShell scripts automate content creation, quality assurance, and deployment. Full documentation: [docs/scripts-reference.md](docs/scripts-reference.md).

### Content Creation

| Script | Purpose |
|--------|---------|
| `new-article.py` | Create a single article scaffold |
| `pull-article.py` | Pull content from a URL into a draft |
| `batch-create-articles.py` | Generate articles from a topics JSON file |
| `generate-tdih.py` | Generate "This Day in History" articles from TSV data |

### Image Management

| Script | Purpose |
|--------|---------|
| `download-images-batch.py` | Batch download Wikipedia lead images via API |
| `generate-thumbnails.py` | Generate 400px thumbnails for responsive images |
| `optimize-images.py` | Resize and compress images for web |
| `audit-images.py` | Audit all images for missing, corrupt, or oversized files |

### Quality Assurance

| Script | Purpose |
|--------|---------|
| `validate-all.py` | Unified validation (YAML, links, images, word count) |
| `check-reading-level.py` | Flesch-Kincaid reading level (target grade 8–10) |
| `check-tone.py` | Flag editorializing in historical sections |
| `plagiarism-check.py` | Check text overlap with Wikipedia sources |
| `check-video-embeds.py` | Verify YouTube embeds via oEmbed API |
| `check-image-licenses.py` | Verify Wikimedia image license status |
| `detect-duplicates.py` | Find articles with >50% topic overlap |

### Deployment

| Script | Purpose |
|--------|---------|
| `deploy.ps1` | One-command: validate → build → commit → push |
| `rollback.ps1` | Emergency revert to previous commit |

### Shared Module

`utils.py` provides shared functions imported by other scripts:
- Article iteration and front matter parsing
- Wikipedia API wrapper (batching, maxlag, Retry-After)
- URL checking with HEAD/GET fallback
- Image downloading with proper User-Agent

### Data Files

| File | Purpose |
|------|---------|
| `slug-to-wiki.json` | 819 article slug → Wikipedia title mappings |
| `tdih-events.tsv` | 366 "This Day in History" events (1 per calendar day) |
| `topics-100.json` | 108 batch article topics with metadata |

---

## CI/CD Pipeline

The GitHub Actions workflow runs automatically on every push:

```
Push to master
  ├── Build and Deploy Job        Hugo build → Azure Static Web Apps
  ├── Lighthouse Audit            Performance, a11y, SEO scoring
  ├── Accessibility Audit         pa11y-ci WCAG2AA compliance
  └── Notify on Failure           Creates GitHub issue if build fails
```

A daily cron job (`0 5 * * *` UTC) rebuilds the site to publish future-dated articles.

### Deployment Configuration

- **Azure Static Web Apps** — auto-provisioned from GitHub
- **Custom headers** — CSP, X-Frame-Options, Referrer-Policy (in `staticwebapp.config.json`)
- **Git LFS** — images tracked via `.gitattributes`, checked out in CI with `lfs: true`

---

## Performance

| Metric | Score |
|--------|-------|
| Lighthouse Performance | 87–89 |
| Lighthouse Accessibility | 95 |
| Lighthouse Best Practices | 96 |
| Lighthouse SEO | 100 |
| First Contentful Paint | 1.5s |
| Largest Contentful Paint | 1.5–1.8s |
| Total Blocking Time | 0–10ms |
| Cumulative Layout Shift | 0.003–0.007 |

### Image Optimization

- Full images: 800px max width, JPEG quality 80 (~110 KB avg)
- Thumbnails: 400px width, JPEG quality 75 (~28 KB avg)
- Card images use thumbnails (75% bandwidth reduction)
- Article hero uses `srcset` for responsive loading
- All images lazy-loaded with `loading="lazy"`

---

## API Etiquette

All scripts follow strict API etiquette (detailed in [.github/copilot-instructions.md](.github/copilot-instructions.md)):

- **User-Agent:** `HistoryNewsBot/1.0 (https://github.com/gleifhe/historynews; educational history site) python-urllib`
- **Wikipedia API:** Batched 50 titles/call, `maxlag=5`, `pithumbsize=1200` CDN thumbnails
- **Rate limiting:** 1s between requests, 2s between downloads, 5s between API batches
- **Retry-After:** Always read and respect the header on 429/503 responses
- **Caching:** Results cached to `slug-to-wiki.json` to avoid repeat queries

---

## Documentation

| Document | Location |
|----------|----------|
| Scripts reference | [docs/scripts-reference.md](docs/scripts-reference.md) |
| Staging environments | [docs/staging-environment.md](docs/staging-environment.md) |
| Uptime monitoring | [docs/uptime-monitoring.md](docs/uptime-monitoring.md) |
| Analytics setup | [docs/analytics-setup.md](docs/analytics-setup.md) |
| AI coding guidelines | [.github/copilot-instructions.md](.github/copilot-instructions.md) |

---

## Contributing

1. Create a feature branch: `git checkout -b feature/your-change`
2. Make changes and test locally: `hugo server --buildFuture`
3. Run validation: `python scripts/validate-all.py`
4. Push and open a PR — Azure SWA creates a preview environment automatically
5. Merge to `master` after review — auto-deploys to production

### Creating a New Article

```bash
# Option 1: Use Hugo archetype
hugo new articles/your-article-slug.md

# Option 2: Use the scaffold script
python scripts/new-article.py --title "Your Title" --era "Era Name" --historydate "Month Day, Year"

# Option 3: Batch create from a topics file
python scripts/batch-create-articles.py topics.json
```

After creating articles, download images and validate:

```bash
python scripts/download-images-batch.py mappings.json
python scripts/generate-thumbnails.py
python scripts/validate-all.py
```

---

## License

Content sourced from public domain archives and Wikimedia Commons (CC-BY-SA 4.0 / Public Domain). See individual article `imagecredit` fields for specific attributions.
