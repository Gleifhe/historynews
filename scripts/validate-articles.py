#!/usr/bin/env python3
"""
validate-articles.py — Validate all History News articles.

Checks:
  - Required front matter fields are present and non-empty
  - Image URLs return HTTP 200
  - YouTube video embed URLs are properly formatted
  - Article body is at least 500 words
  - Sources section has at least 3 entries

Usage:
    python scripts/validate-articles.py
    python scripts/validate-articles.py --check-images   # Also test image URLs (slower)
"""

import os
import re
import sys
import argparse

try:
    import urllib.request
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False

REQUIRED_FIELDS = [
    'title', 'headline', 'summary', 'date', 'historydate',
    'era', 'source', 'image', 'weight'
]

def parse_front_matter(filepath):
    """Extract front matter fields from a Hugo markdown file."""
    fields = {}
    sources = []
    in_front_matter = False
    in_sources = False
    body_lines = []
    past_front_matter = False

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if stripped == '---':
                if not in_front_matter and not past_front_matter:
                    in_front_matter = True
                    continue
                elif in_front_matter:
                    in_front_matter = False
                    past_front_matter = True
                    continue

            if in_front_matter:
                if stripped.startswith("- '") or stripped.startswith('- "') or stripped.startswith('- <'):
                    sources.append(stripped)
                    continue
                if ':' in stripped and not stripped.startswith('-'):
                    key, _, val = stripped.partition(':')
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    fields[key] = val
                    if key == 'sources':
                        in_sources = True
                    else:
                        in_sources = False

            if past_front_matter:
                body_lines.append(line)

    fields['_sources_count'] = len(sources)
    fields['_body_word_count'] = len(' '.join(body_lines).split())
    return fields


def check_image_url(url):
    """Test if an image URL returns HTTP 200."""
    if not HAS_URLLIB:
        return None
    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'HistoryNews-Validator/1.0')
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        return False


def validate_article(filepath, check_images=False):
    """Validate a single article. Returns list of error strings."""
    errors = []
    filename = os.path.basename(filepath)
    fields = parse_front_matter(filepath)

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in fields or not fields[field]:
            errors.append(f'{filename}: Missing or empty field "{field}"')

    # Check sources count
    if fields.get('_sources_count', 0) < 3:
        errors.append(f'{filename}: Only {fields.get("_sources_count", 0)} sources (need at least 3)')

    # Check body length
    wc = fields.get('_body_word_count', 0)
    if wc < 500:
        errors.append(f'{filename}: Body is only {wc} words (minimum 500)')

    # Check video URL format
    video = fields.get('video', '')
    if video and 'youtube.com/embed/' not in video:
        errors.append(f'{filename}: Video URL not in embed format: {video}')

    # Check image URL
    image = fields.get('image', '')
    if check_images and image:
        if not check_image_url(image):
            errors.append(f'{filename}: Image URL returns non-200: {image}')

    return errors


def main():
    parser = argparse.ArgumentParser(description='Validate History News articles')
    parser.add_argument('--check-images', action='store_true', help='Test image URLs (slower)')
    args = parser.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    content_dir = os.path.join(root, 'content', 'articles')

    all_errors = []
    article_count = 0

    for f in sorted(os.listdir(content_dir)):
        if not f.endswith('.md') or f == '_index.md':
            continue
        article_count += 1
        filepath = os.path.join(content_dir, f)
        errors = validate_article(filepath, check_images=args.check_images)
        all_errors.extend(errors)

    print(f'Validated {article_count} articles.')

    if all_errors:
        print(f'\n{len(all_errors)} issue(s) found:\n')
        for e in all_errors:
            print(f'  ✗ {e}')
        sys.exit(1)
    else:
        print('All articles passed validation. ✓')
        sys.exit(0)


if __name__ == '__main__':
    main()
