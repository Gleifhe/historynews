# History News Scripts Reference

Complete documentation for all automation scripts in `scripts/`.

## Quick Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `new-article.py` | Create article scaffold | `python scripts/new-article.py --title "..." --era "..." --historydate "..."` |
| `pull-article.py` | Pull content from URL into draft | `python scripts/pull-article.py --url "..." --title "..." --era "..."` |
| `download-images-batch.py` | Batch download Wikipedia images | `python scripts/download-images-batch.py mappings.json` |
| `localize-images.py` | Download remote images to local | `python scripts/localize-images.py` |
| `schedule-articles.py` | Set future dates for drip publish | `python scripts/schedule-articles.py slugs.txt --start 2026-06-01` |
| `generate-social-posts.py` | Generate social media posts | `python scripts/generate-social-posts.py --csv social.csv` |
| `validate-all.py` | Full quality validation | `python scripts/validate-all.py` |
| `quality-check.py` | Comprehensive quality + SEO | `python scripts/quality-check.py --full` |
| `deploy.ps1` | Validate → build → push | `.\scripts\deploy.ps1` |
| `rollback.ps1` | Emergency revert + redeploy | `.\scripts\rollback.ps1` |

---

## Shared Module

### `utils.py`
Shared utilities imported by other scripts. **Do not run directly.**

Provides:
- `get_article_files()` — iterate article .md files
- `parse_front_matter(content)` — parse YAML front matter to dict
- `extract_body(content)` — get body text after front matter
- `check_url(url)` — HTTP HEAD with GET fallback, returns `(status, detail)`
- `load_slug_to_wiki()` — load slug→Wikipedia mapping from `slug-to-wiki.json`
- `wiki_api_request(params)` — Wikipedia API with maxlag, retries, Retry-After
- `wiki_batch_query(titles, prop)` — batch query 50 titles at a time
- `download_image(url, dest_path)` — download with proper User-Agent
- `get_base_url()` — read baseURL from config.toml
- `USER_AGENT` — standard bot User-Agent string
- `SSL_CTX` — default SSL context (cert verification enabled)
- `ROOT`, `ARTICLES_DIR`, `IMAGES_DIR` — standard paths

### `slug-to-wiki.json`
990 slug→Wikipedia title mappings used by image and fact-checking scripts. Maintained as single source of truth. To add entries, edit this file directly or use `fix-missing-images.py` to auto-populate from article sources.

---

## Content Creation

### `new-article.py`
Create a new article scaffold with pre-populated front matter.

```
python scripts/new-article.py \
  --title "The Boston Tea Party" \
  --era "American Revolution" \
  --historydate "December 16, 1773" \
  --source "Library of Congress" \
  [--slug boston-tea-party] \
  [--image "https://upload.wikimedia.org/..."]
```

- Auto-generates slug from title if not provided
- Auto-assigns next weight number
- Downloads image locally if URL provided
- Creates `content/articles/{slug}.md`

### `pull-article.py`
Pull content from a URL and create a draft article with the source text embedded as a reference comment.

```
python scripts/pull-article.py \
  --url "https://example.com/article" \
  --title "Article Title" \
  --era "Era" \
  --historydate "Date" \
  [--image "https://..."]
```

Requires: `pip install requests beautifulsoup4`

---

## Image Management

### `download-images-batch.py`
Download Wikipedia lead images for articles using a JSON mapping file.

```
python scripts/download-images-batch.py mappings.json [--force] [--dry-run]
```

Mappings format: `{"slug-name": "Wikipedia Article Title", ...}`

API etiquette: batched (50/call), `pithumbsize=1200` CDN thumbnails, `maxlag=5`, `Retry-After`, 2s download delay.

### `localize-images.py`
Scan all articles for remote image URLs and download them to `static/images/articles/`.

```
python scripts/localize-images.py [--force] [--dry-run]
```

Skips articles that already have local images.

### `audit-images.py`
Audit all article images for issues: remote URLs, missing files, tiny/huge sizes, wrong format.

```
python scripts/audit-images.py
```

Exit code 1 if any issues found.

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
Flag generic, short, or missing image alt text.

```
python scripts/check-alt-text.py [--article slug]
```

Flags: "image", "photo", "picture", empty alt text, alt text < 10 chars.

### `check-reading-level.py`
Calculate Flesch-Kincaid reading level. Target: grade 8–10.

```
python scripts/check-reading-level.py [--article slug]
```

Flags articles below grade 6 (too simple) or above grade 12 (too academic).

### `check-tone.py`
Flag editorializing language in historical narrative sections.

```
python scripts/check-tone.py [--article slug]
```

Opinion language is OK in "Personal Growth" and "What This Means" sections only.

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

Exit code 1 if any videos are blocked or missing. Note: oEmbed API may miss embed-restricted videos (Error 153). Use `verify-videos-deep.py` for thorough checking.

### `verify-videos.py`
Fast check of all YouTube video embeds via oEmbed API.

```
python scripts/verify-videos.py
```

### `verify-videos-deep.py`
Deep-check all YouTube video embeds by loading the actual embed page. Catches Error 150 (playback restricted), Error 153 (player configuration / embed blocked), age restrictions, and unavailable videos that the oEmbed API misses.

```
python scripts/verify-videos-deep.py
```

### `check-videos-scheduled.py`
Monthly re-check of YouTube video availability.

```
python scripts/check-videos-scheduled.py [--article slug]
```

### `check-image-licenses.py`
Quarterly re-verify Wikimedia image license status via Commons API.

```
python scripts/check-image-licenses.py [--article slug]
```

Actually queries license metadata (LicenseShortName) and flags non-free images. Imports from `utils.py`.

### `check-image-budget.py`
Track total image directory size and warn if over budget.

```
python scripts/check-image-budget.py
```

---

## Validation & Verification

### `validate-all.py`
Unified quality check: YAML front matter, cross-links, word count, sources, images, eras.

```
python scripts/validate-all.py [--article slug] [--fix] [--errors-only]
```

This is the primary validation gate before deployment. Exit code 1 on errors.

### `validate-articles.py`
Structure validation: required fields, image URLs, video format, word count, source count.

```
python scripts/validate-articles.py [--check-images]
```

### `quality-check.py`
Comprehensive quality check including SEO, content structure, and optional network checks.

```
python scripts/quality-check.py [--check-images] [--check-videos] [--full] [--article slug]
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
Detect near-duplicate summaries (SEO penalty risk).

```
python scripts/duplicate-summaries.py
```

### `find-orphan-articles.py`
Find articles with zero incoming cross-links from other articles.

```
python scripts/find-orphan-articles.py
```

### `score-sources.py`
Rank source quality by domain authority (Tier 1: .gov/.edu, Tier 4: blogs).

```
python scripts/score-sources.py [--article slug]
```

### `flag-stale-facts.py`
Identify claims that may need periodic re-verification (statistics, "currently", etc.).

```
python scripts/flag-stale-facts.py [--article slug]
```

---

## Content Management

### `schedule-articles.py`
Set future dates on articles for drip publishing. Hugo hides future-dated articles.

```
python scripts/schedule-articles.py slugs.txt --start 2026-06-01 [--per-day 3] [--dry-run]
```

Requires a text file with one slug per line.

### `generate-social-posts.py`
Generate Twitter/LinkedIn/Facebook posts from article front matter.

```
python scripts/generate-social-posts.py [--era "Memorial Day"] [--csv social.csv] [--count 10]
```

Reads baseURL from config.toml (not hardcoded).

---

## Deployment

### `build-and-deploy.py`
Build Hugo site, validate, optionally push to git.

```
python scripts/build-and-deploy.py [--push] [--skip-validation]
```

### `deploy.ps1`
One-command validation → build → commit → push pipeline.

```
.\scripts\deploy.ps1 [-SkipValidation] [-DryRun] [-Message "commit msg"]
```

Steps: validate-all.py → audit-images.py → hugo --minify → git add/commit → git push.

### `rollback.ps1`
Emergency revert to previous commit and redeploy.

```
.\scripts\rollback.ps1 [-Commits 2]
```

Validates input, checks for merge conflicts, shows visible push errors.

---

## Typical Workflow

```
1. Create    →  new-article.py or pull-article.py or generate-tdih-02.py
2. Images    →  download-images-batch.py
3. Schedule  →  schedule-articles.py (optional)
4. Validate  →  validate-all.py
5. Quality   →  check-reading-level.py, check-tone.py, etc.
6. Deploy    →  deploy.ps1
7. Monitor   →  check-videos-scheduled.py, check-image-licenses.py (monthly)
```

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/azure-static-web-apps-red-stone-0ed2b5d10.yml`) runs:

1. **Build & Deploy** — Hugo build + Azure Static Web Apps upload
2. **Lighthouse CI** — Performance/accessibility/SEO audit (post-deploy)
3. **Accessibility** — pa11y-ci WCAG2AA check (post-deploy)
4. **Failure Notification** — Creates GitHub issue on build failure
5. **Daily Cron** — Rebuilds at 5 AM UTC to publish future-dated articles

## API Etiquette

All scripts follow the rules in `.github/copilot-instructions.md`:
- User-Agent: `HistoryNewsBot/1.0 (https://github.com/gleifhe/historynews; educational history site) python-urllib`
- Wikipedia: batched 50/call, `maxlag=5`, `pithumbsize=1200` CDN thumbnails
- Retry-After: always read header, never guess
- Rate limiting: 1s general, 2s downloads, 5s between API batches
- SSL: default certificate verification (no CERT_NONE)

## Archived Scripts

One-off fix scripts are in `scripts/archive/`. These were used during initial content buildout and should not be re-run:
- `fix-yaml-*.py` — YAML quoting fixes
- `fix-images-*.py` — Image download/conversion fixes
- `download-memorial-day-images.py` — Memorial Day batch download
- `tag-memorial-day.py` — Bulk era tagging

---

## Additional Scripts

### `generate-tdih-02.py`
Generate secondary "This Day in History" articles (second notable event per calendar day).

```
python scripts/generate-tdih-02.py
```

Contains 130 curated second events spanning from 551 BC to 2009. Creates `tdih-MM-DD-02.md` files. Skips existing articles.

### `stats.py`
Quick workspace statistics: total articles, TDIH count, unique eras, script inventory.

```
python scripts/stats.py
```
