# Scripts

Automation scripts for content creation, quality assurance, image management, and deployment.

## Quick Start

```bash
# Validate all articles
python scripts/validate-all.py

# Create a new article
python scripts/new-article.py --title "Title" --era "Era" --historydate "Date"

# Download images and generate thumbnails
python scripts/download-images-batch.py mappings.json
python scripts/generate-thumbnails.py

# Deploy
.\scripts\deploy.ps1
```

---

## Shared Module

### `utils.py`
Shared utilities imported by other scripts. **Do not run directly.**

| Function | Purpose |
|----------|---------|
| `get_article_files()` | Iterate sorted `.md` article files |
| `parse_front_matter(content)` | Parse YAML front matter to dict |
| `extract_body(content)` | Get body text after front matter |
| `check_url(url, timeout)` | HTTP HEAD with GET fallback → `(status, detail)` |
| `load_slug_to_wiki()` | Load slug→Wikipedia mapping from manifest |
| `wiki_api_request(params)` | Wikipedia API with maxlag, 3 retries, Retry-After |
| `wiki_batch_query(titles, prop)` | Batch query up to 50 Wikipedia titles |
| `download_image(url, dest)` | Download with proper User-Agent |
| `get_base_url()` | Read `baseURL` from `config.toml` |

**Constants:** `USER_AGENT`, `SSL_CTX`, `ROOT`, `ARTICLES_DIR`, `IMAGES_DIR`, `MANIFEST_PATH`

---

## Content Creation

### `new-article.py`
Create a single article scaffold with pre-populated front matter.
```
python scripts/new-article.py \
  --title "The Boston Tea Party" \
  --era "18th Century" \
  --historydate "December 16, 1773" \
  --source "Library of Congress" \
  [--slug boston-tea-party] \
  [--image "https://upload.wikimedia.org/..."]
```
Auto-generates slug from title, assigns next weight, downloads image locally if URL provided.

### `pull-article.py`
Pull content from a URL and create a draft article with source text as a reference comment.
```
python scripts/pull-article.py \
  --url "https://example.com/article" \
  --title "Title" --era "Era" --historydate "Date" \
  [--image "https://..."]
```
Requires: `pip install requests beautifulsoup4`

### `batch-create-articles.py`
Generate multiple articles from a topics JSON file.
```
python scripts/batch-create-articles.py scripts/topics-100.json
python scripts/batch-create-articles.py scripts/topics-100.json --dry-run
python scripts/batch-create-articles.py scripts/topics-100.json --limit 10
```
Topics JSON format: `[{"slug": "...", "title": "...", "headline": "...", "summary": "...", "historydate": "...", "era": "...", "wiki": "..."}, ...]`

### `generate-tdih.py`
Generate "This Day in History" articles from a TSV data file.
```
python scripts/generate-tdih.py                  # All days
python scripts/generate-tdih.py --month 7        # July only
python scripts/generate-tdih.py --day 07-04      # Single day
python scripts/generate-tdih.py --dry-run        # Preview
```
Reads from `tdih-events.tsv`. Adds `monthday` field to front matter for date-based lookups. Skips existing articles automatically.

### `generate-tdih-02.py`
Generate secondary "This Day in History" articles (second notable event per calendar day) with `-02` suffix.
```
python scripts/generate-tdih-02.py
```
Contains 130 curated second events spanning Ancient World to 21st Century. Skips existing `-02` articles automatically.

### `stats.py`
Quick workspace statistics: total articles, TDIH count, unique eras, script inventory.
```
python scripts/stats.py
```

### `schedule-articles.py`
Set future publication dates on articles for drip publishing. Hugo hides future-dated articles in production; the daily cron rebuild publishes them.
```
python scripts/schedule-articles.py slugs.txt --start 2026-06-01
python scripts/schedule-articles.py slugs.txt --start 2026-06-01 --per-day 3
python scripts/schedule-articles.py slugs.txt --dry-run
```

### `generate-social-posts.py`
Generate platform-specific social media posts from article front matter.
```
python scripts/generate-social-posts.py --csv social.csv
python scripts/generate-social-posts.py --era "Memorial Day" --count 10
```
Reads `baseURL` from `config.toml`. Outputs Twitter (280-char truncated), LinkedIn, and Facebook posts.

---

## Image Management

### `download-images-batch.py`
Batch download Wikipedia lead images using the API with proper etiquette.
```
python scripts/download-images-batch.py mappings.json
python scripts/download-images-batch.py mappings.json --force
python scripts/download-images-batch.py mappings.json --dry-run
```
Mappings format: `{"slug-name": "Wikipedia Article Title", ...}`

**API etiquette:** Batched 50 titles/call, `pithumbsize=1200` CDN thumbnails, `maxlag=5`, respects `Retry-After`, 2s delay between downloads.

### `optimize-images.py`
Resize and compress article images for web delivery.
```
python scripts/optimize-images.py                    # All images → 800px max, q80
python scripts/optimize-images.py --max-width 600    # Custom width
python scripts/optimize-images.py --dry-run          # Preview savings
```

### `generate-thumbnails.py`
Generate 400px-wide thumbnails in `static/images/articles/thumb/` for card images.
```
python scripts/generate-thumbnails.py                # Generate all
python scripts/generate-thumbnails.py --force        # Regenerate existing
python scripts/generate-thumbnails.py --width 300    # Custom width
```

### `localize-images.py`
Scan articles for remote image URLs and download them to local storage.
```
python scripts/localize-images.py [--force] [--dry-run]
```

### `audit-images.py`
Audit all article images for issues: missing files, wrong format, too small, too large.
```
python scripts/audit-images.py
```
Exits with code 1 if any issues found.

### `verify-image-accuracy.py`
Verify each image came from the correct Wikipedia article using the slug-to-wiki manifest.
```
python scripts/verify-image-accuracy.py [--article slug]
```

### `review-image-relevance.py`
Generate a checklist for manual image relevance review.
```
python scripts/review-image-relevance.py [--csv review.csv]
```

---

## Quality Assurance — Content

### `check-alt-text.py`
Flag generic, short, or missing image alt text (e.g., "image", "photo", empty).
```
python scripts/check-alt-text.py [--article slug]
```

### `check-reading-level.py`
Calculate Flesch-Kincaid reading level. Target: grade 8–10.
```
python scripts/check-reading-level.py [--article slug]
```

### `check-tone.py`
Flag editorializing language in historical narrative sections. Opinion is OK only in "Personal Growth" and "What This Means" sections.
```
python scripts/check-tone.py [--article slug]
```

### `plagiarism-check.py`
Check for text overlap with Wikipedia sources. Flags sentences with >80% word overlap.
```
python scripts/plagiarism-check.py [--article slug] [--threshold 0.7]
```
Uses `slug-to-wiki.json` manifest. Imports `wiki_api_request` from `utils.py`.

### `extract-quotes.py`
Extract all quoted text from articles for manual fact-checking.
```
python scripts/extract-quotes.py [--csv quotes.csv]
```

### `verify-quote-attribution.py`
Extract quotes with attributed speakers for verification.
```
python scripts/verify-quote-attribution.py [--csv attributions.csv]
```

---

## Quality Assurance — Media

### `check-video-embeds.py`
Verify YouTube embeds are available and embeddable using the oEmbed API.
```
python scripts/check-video-embeds.py
```
Note: oEmbed API may report videos as embeddable even when they return Error 153 in actual embed iframes. Use `verify-videos-deep.py` for thorough checking.

### `verify-videos.py`
Check all YouTube video embeds via oEmbed API (fast, but may miss embed-restricted videos).
```
python scripts/verify-videos.py
```

### `verify-videos-deep.py`
Deep-check all YouTube video embeds by loading the actual embed page. Catches Error 150, Error 153, age restrictions, and unavailable videos that oEmbed misses.
```
python scripts/verify-videos-deep.py
```

### `check-videos-scheduled.py`
Monthly re-check of YouTube video availability.
```
python scripts/check-videos-scheduled.py [--article slug]
```

### `check-image-licenses.py`
Verify Wikimedia image license status via the Commons API. Queries actual license metadata and flags non-free images.
```
python scripts/check-image-licenses.py [--article slug]
```

### `check-image-budget.py`
Track total image directory size and warn if over budget.
```
python scripts/check-image-budget.py
```

---

## Validation

### `validate-all.py`
**Primary validation gate.** Checks YAML front matter, cross-links, word count, sources, images, and eras in one pass.
```
python scripts/validate-all.py                    # Full check
python scripts/validate-all.py --article slug     # Single article
python scripts/validate-all.py --errors-only      # Suppress warnings
python scripts/validate-all.py --fix              # Auto-fix what's possible
```
Exits with code 1 on errors. Used by `deploy.ps1` as a pre-deploy gate.

### `validate-articles.py`
Older structure validator (required fields, image URLs, video format, word count). Superseded by `validate-all.py` for most use cases.
```
python scripts/validate-articles.py [--check-images]
```

### `quality-check.py`
Comprehensive quality check including content structure, SEO, and optional network checks.
```
python scripts/quality-check.py --full                  # All checks including network
python scripts/quality-check.py --check-images          # Test image URLs
python scripts/quality-check.py --check-videos          # Test video embeds
python scripts/quality-check.py --article slug          # Single article
```

### `fact-check-dates.py`
Cross-reference article dates against Wikipedia extracts.
```
python scripts/fact-check-dates.py [--article slug]
```

### `detect-anachronisms.py`
Flag terms anachronistic to the article's era (e.g., "internet" in a 1776 article).
```
python scripts/detect-anachronisms.py [--article slug]
```

### `detect-duplicates.py`
Find articles with >50% topic similarity based on title/summary word overlap.
```
python scripts/detect-duplicates.py
```

### `duplicate-summaries.py`
Detect near-duplicate summaries that could trigger SEO penalties.
```
python scripts/duplicate-summaries.py
```

### `find-orphan-articles.py`
Find articles with zero incoming cross-links from other articles.
```
python scripts/find-orphan-articles.py
```

### `score-sources.py`
Rank source quality by domain authority (Tier 1: .gov/.edu → Tier 4: blogs).
```
python scripts/score-sources.py [--article slug]
```

### `flag-stale-facts.py`
Identify claims containing statistics, "currently," or time-sensitive language that may need periodic re-verification.
```
python scripts/flag-stale-facts.py [--article slug]
```

### `check-memorial-day.py`
Quick quality check specific to the 75 Memorial Day articles.
```
python scripts/check-memorial-day.py
```

### `check-external-links.py`
HTTP HEAD all outbound links in article body text, flagging broken URLs.
```
python scripts/check-external-links.py [--article slug] [--timeout 15]
```

### `check-source-urls.py`
Verify all URLs in article source fields are reachable.
```
python scripts/check-source-urls.py [--article slug] [--timeout 10]
```

---

## Deployment

### `deploy.ps1`
One-command deployment pipeline: validate → audit images → Hugo build → git commit → git push.
```powershell
.\scripts\deploy.ps1
.\scripts\deploy.ps1 -SkipValidation
.\scripts\deploy.ps1 -DryRun
.\scripts\deploy.ps1 -Message "custom commit message"
```

### `build-and-deploy.py`
Python alternative to `deploy.ps1`.
```
python scripts/build-and-deploy.py [--push] [--skip-validation]
```

### `rollback.ps1`
Emergency revert to previous commit and redeploy. Validates input, checks for merge conflicts, shows visible push errors.
```powershell
.\scripts\rollback.ps1              # Revert last commit
.\scripts\rollback.ps1 -Commits 2   # Revert last 2 commits
```

---

## Data Files

| File | Format | Entries | Purpose |
|------|--------|--------:|---------|
| `slug-to-wiki.json` | JSON | 990 | Article slug → Wikipedia title mappings |
| `tdih-events.tsv` | TSV | 366 | This Day in History primary events (1 per calendar day) |
| `topics-100.json` | JSON | 108 | Batch article topics with metadata |
| `image-manifest.json` | JSON | varies | Image download tracking and history |

---

## Archived Scripts

`scripts/archive/` contains 33 one-off scripts used during initial content buildout. These are preserved for reference but should not be re-run:

- `fix-yaml-*.py` — YAML quoting fixes
- `fix-images-*.py` — Image download/conversion fixes
- `download-memorial-day-images.py` — Memorial Day batch download
- `tag-memorial-day.py` — Bulk era tagging
- `_build_manifest.py`, `_fix_ssl.py`, etc. — One-time maintenance scripts

---

## Typical Workflow

```
1. Create    →  new-article.py / batch-create-articles.py / generate-tdih.py / generate-tdih-02.py
2. Images    →  fix-missing-images.py → optimize-images.py → generate-thumbnails.py
3. Schedule  →  schedule-articles.py (optional — set future dates)
4. Validate  →  validate-all.py (must pass with 0 errors)
5. Quality   →  check-reading-level.py, check-tone.py, detect-duplicates.py
6. Deploy    →  deploy.ps1 (or manual git push)
7. Monitor   →  check-videos-scheduled.py, check-image-licenses.py (monthly)
```

## Exit Codes

All validation and QA scripts exit with code **1** when problems are found, making them usable as CI gates. Scripts that are informational only (e.g., `find-orphan-articles.py`) exit with code **0** regardless.
