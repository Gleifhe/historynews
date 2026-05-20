#!/usr/bin/env python3
"""
score-sources.py — Rank article source quality by domain authority.

Assigns quality tiers to source URLs:
  - Tier 1 (excellent): .gov, .edu, .mil, major archives
  - Tier 2 (good):      .org (established), major news, Wikipedia
  - Tier 3 (acceptable): .com (established publishers), major media
  - Tier 4 (weak):      blogs, personal sites, unknown domains

Flags articles that rely primarily on Tier 3-4 sources.

Usage:
    python scripts/score-sources.py
    python scripts/score-sources.py --article slug
"""
import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

root = Path(__file__).parent.parent
articles_dir = root / 'content' / 'articles'

# Domain classification
TIER_1 = {
    '.gov', '.edu', '.mil',
    'archives.gov', 'loc.gov', 'nps.gov', 'si.edu', 'army.mil',
    'navy.mil', 'usmc.mil', 'af.mil', 'defense.gov',
    'smithsonianmag.com', 'jstor.org', 'doi.org',
}

TIER_2_DOMAINS = {
    'wikipedia.org', 'britannica.com', 'history.com',
    'nytimes.com', 'washingtonpost.com', 'bbc.co.uk', 'bbc.com',
    'pbs.org', 'npr.org', 'reuters.com', 'apnews.com',
    'nationalgeographic.com', 'theatlantic.com', 'newyorker.com',
    'abmc.gov', 'va.gov', 'congress.gov',
}

TIER_3_DOMAINS = {
    'amazon.com', 'goodreads.com', 'imdb.com',
    'medium.com', 'substack.com',
}


def classify_url(url):
    """Classify a URL into a quality tier."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if not domain:
            return 0, 'no domain'

        # Remove www.
        domain = domain.replace('www.', '')

        # Check TLD
        for tld in ['.gov', '.edu', '.mil']:
            if domain.endswith(tld):
                return 1, domain

        # Check specific domains
        for d in TIER_1:
            if domain.endswith(d):
                return 1, domain

        for d in TIER_2_DOMAINS:
            if domain.endswith(d) or domain == d:
                return 2, domain

        # .org is generally good
        if domain.endswith('.org'):
            return 2, domain

        for d in TIER_3_DOMAINS:
            if domain.endswith(d) or domain == d:
                return 3, domain

        # Known publishers
        if any(pub in domain for pub in ['university', 'museum', 'library', 'institute', 'foundation']):
            return 2, domain

        # Default .com
        if domain.endswith('.com'):
            return 3, domain

        return 3, domain

    except Exception:
        return 4, 'unparseable'


def main():
    parser = argparse.ArgumentParser(description='Score source quality')
    parser.add_argument('--article', type=str, help='Check single article')
    args = parser.parse_args()

    article_scores = []

    for f in sorted(articles_dir.iterdir()):
        if not f.name.endswith('.md') or f.name == '_index.md':
            continue
        if args.article and f.stem != args.article:
            continue

        content = f.read_text(encoding='utf-8')
        fm = content.split('---', 2)[1] if '---' in content else ''

        # Extract URLs from sources
        urls = re.findall(r'https?://[^\s"\'<>]+', fm)
        urls = [u.rstrip('.,;:)') for u in urls]

        if not urls:
            article_scores.append({
                'slug': f.stem,
                'avg_tier': 4,
                'tiers': [],
                'urls': [],
            })
            continue

        tiers = []
        details = []
        for url in urls:
            tier, domain = classify_url(url)
            tiers.append(tier)
            details.append((tier, domain, url[:80]))

        avg = sum(tiers) / len(tiers) if tiers else 4
        article_scores.append({
            'slug': f.stem,
            'avg_tier': avg,
            'tiers': tiers,
            'details': details,
        })

    # Sort by worst average
    article_scores.sort(key=lambda x: -x['avg_tier'])

    # Stats
    tier1_count = sum(1 for a in article_scores if a['avg_tier'] <= 1.5)
    tier2_count = sum(1 for a in article_scores if 1.5 < a['avg_tier'] <= 2.5)
    tier3_count = sum(1 for a in article_scores if 2.5 < a['avg_tier'] <= 3.5)
    weak_count = sum(1 for a in article_scores if a['avg_tier'] > 3.5)

    print(f'Source Quality Report — {len(article_scores)} articles\n')
    print(f'  Tier 1 (excellent — .gov/.edu/.mil): {tier1_count}')
    print(f'  Tier 2 (good — .org/major news):     {tier2_count}')
    print(f'  Tier 3 (acceptable — .com):           {tier3_count}')
    print(f'  Weak (blogs/unknown):                 {weak_count}')

    # Show weakest articles
    weak_articles = [a for a in article_scores if a['avg_tier'] > 2.5]
    if weak_articles:
        print(f'\n⚠️  ARTICLES WITH WEAK SOURCES ({len(weak_articles)}):')
        for a in weak_articles[:20]:
            print(f'\n  {a["slug"]} (avg tier: {a["avg_tier"]:.1f}):')
            for tier, domain, url in a.get('details', []):
                icon = '🟢' if tier <= 1 else '🟡' if tier <= 2 else '🔴'
                print(f'    {icon} Tier {tier}: {domain}')
    else:
        print(f'\n✅ All articles have acceptable source quality')
    if weak_articles:
        sys.exit(1)

if __name__ == '__main__':
    main()
