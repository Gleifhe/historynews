#!/usr/bin/env python3
"""
generate-social-posts.py — Generate social media posts from article front matter.

Creates platform-specific posts for Twitter/X, LinkedIn, and Facebook
from article titles, summaries, and URLs.

Usage:
    python scripts/generate-social-posts.py                    # All articles
    python scripts/generate-social-posts.py --era "Memorial Day"  # By era
    python scripts/generate-social-posts.py --csv social.csv   # Output CSV
    python scripts/generate-social-posts.py --count 10         # Latest 10
"""
import argparse
import csv
import re
from pathlib import Path

root = Path(__file__).parent.parent
articles_dir = root / 'content' / 'articles'


def get_base_url():
    """Read baseURL from config.toml."""
    config = root / 'config.toml'
    if config.exists():
        for line in config.read_text(encoding='utf-8').splitlines():
            m = re.match(r'baseURL\s*=\s*"([^"]+)"', line)
            if m:
                return m.group(1).rstrip('/')
    return 'https://red-stone-0ed2b5d10.7.azurestaticapps.net'


BASE_URL = get_base_url()

TWITTER_TEMPLATE = """{headline}

{summary}

Read the full story: {url}

#HistoryNews #History #{era_tag}"""

LINKEDIN_TEMPLATE = """{headline}

{summary}

What happened next — and what it means for us today — may surprise you.

Read the full story: {url}

#History #HistoryNews #{era_tag} #LessonsFromHistory"""

FACEBOOK_TEMPLATE = """{headline}

{summary}

Read the full story at History News: {url}"""


def era_to_hashtag(era):
    return re.sub(r'[^a-zA-Z0-9]', '', era)


def main():
    parser = argparse.ArgumentParser(description='Generate social media posts')
    parser.add_argument('--era', type=str, help='Filter by era')
    parser.add_argument('--csv', type=str, help='Output to CSV')
    parser.add_argument('--count', type=int, help='Limit number of articles')
    args = parser.parse_args()

    articles = []
    for f in sorted(articles_dir.iterdir()):
        if not f.name.endswith('.md') or f.name == '_index.md':
            continue
        content = f.read_text(encoding='utf-8')
        fm = content.split('---', 2)[1] if '---' in content else ''

        title = re.search(r'title:\s*"([^"]+)"', fm)
        headline = re.search(r'headline:\s*"([^"]+)"', fm)
        summary = re.search(r'summary:\s*"([^"]+)"', fm)
        era = re.search(r'era:\s*"([^"]+)"', fm)

        if not title or not summary:
            continue

        article = {
            'slug': f.stem,
            'title': title.group(1),
            'headline': headline.group(1) if headline else title.group(1),
            'summary': summary.group(1),
            'era': era.group(1) if era else 'History',
            'url': f'{BASE_URL}/articles/{f.stem}/',
        }

        if args.era and article['era'] != args.era:
            continue

        articles.append(article)

    if args.count:
        articles = articles[:args.count]

    print(f'Generating social posts for {len(articles)} articles...\n')

    posts = []
    for a in articles:
        era_tag = era_to_hashtag(a['era'])
        twitter = TWITTER_TEMPLATE.format(headline=a['headline'][:200], summary=a['summary'][:100], url=a['url'], era_tag=era_tag)
        linkedin = LINKEDIN_TEMPLATE.format(headline=a['headline'], summary=a['summary'], url=a['url'], era_tag=era_tag)
        facebook = FACEBOOK_TEMPLATE.format(headline=a['headline'], summary=a['summary'], url=a['url'])

        # Truncate Twitter to 280 chars
        if len(twitter) > 280:
            twitter = twitter[:277] + '...'

        posts.append({
            'slug': a['slug'],
            'era': a['era'],
            'twitter': twitter,
            'linkedin': linkedin,
            'facebook': facebook,
        })

    if args.csv:
        with open(args.csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['slug', 'era', 'twitter', 'linkedin', 'facebook'])
            writer.writeheader()
            writer.writerows(posts)
        print(f'Saved {len(posts)} posts to {args.csv}')
    else:
        for p in posts[:3]:
            print(f'--- {p["slug"]} ---')
            print(f'TWITTER:\n{p["twitter"]}\n')
        if len(posts) > 3:
            print(f'... and {len(posts) - 3} more. Run with --csv to export all.')

    print(f'\nTotal: {len(posts)} articles x 3 platforms = {len(posts) * 3} posts')


if __name__ == '__main__':
    main()
