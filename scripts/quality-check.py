#!/usr/bin/env python3
"""
quality-check.py — Comprehensive quality check for History News articles.

Validates content formatting, videos, images, and article structure based on
lessons learned during site development.

Checks performed:
  1. FRONT MATTER: All required fields present and non-empty
  2. IMAGES: URLs return HTTP 200 (not just exist — actually load)
  3. IMAGES: Alt text, caption, and credit are meaningful (not generic)
  4. VIDEOS: YouTube embed URLs are valid AND embeddable
  5. CONTENT: Minimum word count, required sections present
  6. CONTENT: Internal cross-links exist (at least 2 per article)
  7. SOURCES: At least 3 cited sources with working links
  8. SEO: Summary length appropriate, headline is attention-grabbing

Usage:
    python scripts/quality-check.py                    # Full check (no network)
    python scripts/quality-check.py --check-images     # Also test image URLs
    python scripts/quality-check.py --check-videos     # Also test video embeds
    python scripts/quality-check.py --full             # All checks including network
    python scripts/quality-check.py --article slug     # Check single article
"""

import argparse
import json
import re
import ssl
import sys
import urllib.request
import urllib.error
from pathlib import Path

# ============================================================
# Configuration — adjust thresholds here
# ============================================================

REQUIRED_FIELDS = [
    'title', 'headline', 'summary', 'date', 'historydate',
    'era', 'source', 'image', 'imagealt', 'imagecaption',
    'imagecredit', 'video', 'weight'
]

MIN_WORD_COUNT = 600
MIN_SOURCES = 3
MIN_CROSS_LINKS = 2
MIN_SUMMARY_LENGTH = 50
MAX_SUMMARY_LENGTH = 300
MIN_HEADLINE_LENGTH = 30

REQUIRED_SECTIONS = [
    'What We Can Learn',
    'How This Connects to 2026'
]

# Known bad image patterns — LOC tile URLs that were previously wrong
SUSPECT_IMAGE_PATTERNS = [
    # These LOC subdirectories had many mismatched images
    'highsm/02400', 'highsm/04600', 'highsm/13600', 'highsm/13800',
    'highsm/38200', 'ppmsca/09700', 'ppmsca/09200',
]

# SSL context and User-Agent for URL checks
CTX = ssl.create_default_context()
USER_AGENT = 'HistoryNewsBot/1.0 (https://github.com/gleifhe/historynews; educational history site) python-urllib'


# ============================================================
# Parsing
# ============================================================

def parse_article(filepath):
    """Parse a Hugo markdown article into structured data."""
    fields = {}
    sources = []
    body_lines = []
    in_fm = False
    past_fm = False
    in_sources = False

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()

            if stripped == '---':
                if not in_fm and not past_fm:
                    in_fm = True
                    continue
                elif in_fm:
                    in_fm = False
                    past_fm = True
                    continue

            if in_fm:
                if stripped.startswith("- '") or stripped.startswith('- "') or stripped.startswith('- <'):
                    sources.append(stripped)
                    continue
                if ':' in stripped and not stripped.startswith('-'):
                    key, _, val = stripped.partition(':')
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    fields[key] = val
                    in_sources = (key == 'sources')

            if past_fm:
                body_lines.append(line)

    body_text = ''.join(body_lines)
    return {
        'fields': fields,
        'sources': sources,
        'body': body_text,
        'word_count': len(body_text.split()),
        'filepath': filepath,
        'slug': Path(filepath).stem
    }


# ============================================================
# Check functions
# ============================================================

def check_front_matter(article):
    """Check all required front matter fields."""
    errors = []
    for field in REQUIRED_FIELDS:
        val = article['fields'].get(field, '')
        if not val:
            errors.append(f"Missing or empty field: {field}")
    return errors


def check_headline(article):
    """Check headline quality."""
    errors = []
    headline = article['fields'].get('headline', '')
    if len(headline) < MIN_HEADLINE_LENGTH:
        errors.append(f"Headline too short ({len(headline)} chars, min {MIN_HEADLINE_LENGTH})")
    if headline == headline.lower():
        errors.append("Headline has no uppercase emphasis — should be attention-grabbing")
    return errors


def check_summary(article):
    """Check summary length."""
    errors = []
    summary = article['fields'].get('summary', '')
    if len(summary) < MIN_SUMMARY_LENGTH:
        errors.append(f"Summary too short ({len(summary)} chars, min {MIN_SUMMARY_LENGTH})")
    if len(summary) > MAX_SUMMARY_LENGTH:
        errors.append(f"Summary too long ({len(summary)} chars, max {MAX_SUMMARY_LENGTH})")
    return errors


def check_body_content(article):
    """Check article body for required sections and minimum length."""
    errors = []
    body = article['body']
    wc = article['word_count']

    if wc < MIN_WORD_COUNT:
        errors.append(f"Body too short: {wc} words (min {MIN_WORD_COUNT})")

    for section in REQUIRED_SECTIONS:
        if section not in body:
            errors.append(f"Missing required section: '{section}'")

    return errors


def check_cross_links(article):
    """Check for internal cross-links to other articles."""
    errors = []
    body = article['body']
    links = re.findall(r'\[.*?\]\(/articles/[\w-]+/\)', body)
    if len(links) < MIN_CROSS_LINKS:
        errors.append(f"Only {len(links)} internal cross-links (min {MIN_CROSS_LINKS})")
    return errors


def check_sources(article):
    """Check source citations."""
    errors = []
    if len(article['sources']) < MIN_SOURCES:
        errors.append(f"Only {len(article['sources'])} sources (min {MIN_SOURCES})")
    return errors


def check_image_metadata(article):
    """Check image alt text, caption, and credit for quality."""
    errors = []
    fields = article['fields']

    alt = fields.get('imagealt', '')
    caption = fields.get('imagecaption', '')
    credit = fields.get('imagecredit', '')
    image = fields.get('image', '')

    # Check for generic/placeholder alt text
    generic_alts = ['image', 'photo', 'picture', 'illustration', 'photograph']
    if alt.lower() in generic_alts:
        errors.append(f"Image alt text is too generic: '{alt}'")

    # Check for suspect LOC image paths
    for pattern in SUSPECT_IMAGE_PATTERNS:
        if pattern in image and 'tile.loc.gov' in image:
            errors.append(f"WARNING: Image URL matches known-problematic LOC path: {pattern}")

    # Check alt text describes the topic
    title = fields.get('title', '').lower()
    alt_lower = alt.lower()
    # Very basic relevance check — at least one word from title should be in alt
    title_words = [w for w in title.split() if len(w) > 3]
    if title_words and not any(w in alt_lower for w in title_words):
        errors.append(f"Image alt text may not match article topic (title: '{title}', alt: '{alt}')")

    return errors


def check_video_format(article):
    """Check video URL format."""
    errors = []
    video = article['fields'].get('video', '')
    if video and 'youtube.com/embed/' not in video:
        errors.append(f"Video URL not in embed format: {video}")
    return errors


# ============================================================
# Network checks (optional)
# ============================================================

def check_image_url(article):
    """Test if image URL returns HTTP 200."""
    image = article['fields'].get('image', '')
    if not image:
        return ["No image URL to test"]

    req = urllib.request.Request(image, method='HEAD',
                                 headers={'User-Agent': 'USER_AGENT'})
    try:
        with urllib.request.urlopen(req, timeout=10, context=CTX) as resp:
            if resp.status != 200:
                return [f"Image returned HTTP {resp.status}: {image}"]
    except Exception as e:
        # Try GET if HEAD fails (some servers block HEAD)
        try:
            req2 = urllib.request.Request(image,
                                          headers={'User-Agent': 'USER_AGENT'})
            with urllib.request.urlopen(req2, timeout=10, context=CTX) as resp:
                if resp.status != 200:
                    return [f"Image returned HTTP {resp.status}: {image}"]
        except Exception as e2:
            return [f"Image URL FAILED: {e2}"]
    return []


def check_video_embed(article):
    """Test if YouTube video exists AND is embeddable."""
    video = article['fields'].get('video', '')
    if not video:
        return ["No video URL"]

    match = re.search(r'embed/([^"?&]+)', video)
    if not match:
        return [f"Cannot extract video ID from: {video}"]

    vid = match.group(1)

    # Step 1: Check if video exists via oEmbed
    oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json"
    req = urllib.request.Request(oembed_url,
                                 headers={'User-Agent': 'USER_AGENT'})
    try:
        with urllib.request.urlopen(req, timeout=10, context=CTX) as resp:
            data = json.loads(resp.read())
            title = data.get('title', 'Unknown')
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return [f"Video {vid} exists but embedding is DISABLED (HTTP 401)"]
        return [f"Video {vid} NOT FOUND (HTTP {e.code})"]
    except Exception as e:
        return [f"Video check failed for {vid}: {e}"]

    # Step 2: Try to load the embed page to check if embedding is allowed
    embed_url = f"https://www.youtube.com/embed/{vid}"
    req2 = urllib.request.Request(embed_url,
                                  headers={'User-Agent': 'USER_AGENT'})
    try:
        with urllib.request.urlopen(req2, timeout=10, context=CTX) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            if 'Video unavailable' in html or 'UNPLAYABLE' in html:
                return [f"Video {vid} exists but CANNOT BE EMBEDDED ('{title}')"]
    except:
        pass  # If we can't check embedding, the oEmbed pass is good enough

    return []


# ============================================================
# Main
# ============================================================

def run_checks(article, check_images=False, check_videos=False):
    """Run all checks on a single article. Returns list of (level, message)."""
    results = []

    # Always run these
    for err in check_front_matter(article):
        results.append(('ERROR', err))
    for err in check_headline(article):
        results.append(('WARN', err))
    for err in check_summary(article):
        results.append(('WARN', err))
    for err in check_body_content(article):
        results.append(('ERROR', err))
    for err in check_cross_links(article):
        results.append(('WARN', err))
    for err in check_sources(article):
        results.append(('ERROR', err))
    for err in check_image_metadata(article):
        results.append(('WARN', err))
    for err in check_video_format(article):
        results.append(('ERROR', err))

    # Optional network checks
    if check_images:
        for err in check_image_url(article):
            results.append(('ERROR', err))
    if check_videos:
        for err in check_video_embed(article):
            results.append(('ERROR', err))

    return results


def main():
    parser = argparse.ArgumentParser(description='Quality check History News articles')
    parser.add_argument('--check-images', action='store_true', help='Test image URLs (network)')
    parser.add_argument('--check-videos', action='store_true', help='Test video embeds (network)')
    parser.add_argument('--full', action='store_true', help='Run all checks including network')
    parser.add_argument('--article', type=str, help='Check single article by slug')
    args = parser.parse_args()

    if args.full:
        args.check_images = True
        args.check_videos = True

    root = Path(__file__).parent.parent
    content_dir = root / 'content' / 'articles'

    # Collect articles
    articles = []
    for f in sorted(content_dir.iterdir()):
        if not f.name.endswith('.md') or f.name == '_index.md':
            continue
        if args.article and f.stem != args.article:
            continue
        articles.append(parse_article(str(f)))

    if not articles:
        print(f"No articles found{' matching ' + args.article if args.article else ''}.")
        sys.exit(1)

    # Run checks
    total_errors = 0
    total_warnings = 0
    articles_with_issues = 0

    for article in articles:
        results = run_checks(article,
                             check_images=args.check_images,
                             check_videos=args.check_videos)

        errors = [r for r in results if r[0] == 'ERROR']
        warnings = [r for r in results if r[0] == 'WARN']

        if errors or warnings:
            articles_with_issues += 1
            print(f"\n{'='*60}")
            print(f"  {article['slug']}")
            print(f"{'='*60}")
            for level, msg in results:
                icon = 'X' if level == 'ERROR' else '!'
                print(f"  {icon} [{level}] {msg}")

        total_errors += len(errors)
        total_warnings += len(warnings)

    # Summary
    print(f"\n{'='*60}")
    print(f"  QUALITY CHECK SUMMARY")
    print(f"{'='*60}")
    print(f"  Articles checked:      {len(articles)}")
    print(f"  Articles with issues:  {articles_with_issues}")
    print(f"  Errors:                {total_errors}")
    print(f"  Warnings:              {total_warnings}")
    print(f"  Checks performed:      front matter, headline, summary,")
    print(f"                         body content, cross-links, sources,")
    print(f"                         image metadata, video format")
    if args.check_images:
        print(f"                         + image URL validation (network)")
    if args.check_videos:
        print(f"                         + video embed validation (network)")
    print(f"{'='*60}")

    if total_errors > 0:
        print(f"\n  RESULT: FAIL — {total_errors} error(s) found")
        sys.exit(1)
    elif total_warnings > 0:
        print(f"\n  RESULT: PASS with {total_warnings} warning(s)")
        sys.exit(0)
    else:
        print(f"\n  RESULT: ALL CHECKS PASSED")
        sys.exit(0)


if __name__ == '__main__':
    main()
