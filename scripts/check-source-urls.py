#!/usr/bin/env python3
"""
check-source-urls.py — Verify that all source URLs in articles are reachable.

Sends HTTP HEAD requests to every URL found in article source fields.
Flags 404s, timeouts, redirects, and unreachable domains.

Usage:
    python scripts/check-source-urls.py              # Check all
    python scripts/check-source-urls.py --article slug  # Check one
    python scripts/check-source-urls.py --timeout 10    # Custom timeout

Follows API etiquette:
    - 1 second delay between requests
    - Proper User-Agent
    - HEAD requests only (minimal bandwidth)
"""
import argparse
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

root = Path(__file__).parent.parent
articles_dir = root / 'content' / 'articles'

USER_AGENT = 'HistoryNewsBot/1.0 (https://github.com/gleifhe/historynews; educational history site; link checker)'
CTX = ssl.create_default_context()

DELAY = 1.0  # seconds between requests


def extract_urls_from_sources(content):
    """Extract URLs from source lines in front matter."""
    urls = []
    # Match URLs in source lines: "Source Name — https://example.com"
    # or bare URLs
    for match in re.finditer(r'https?://[^\s"\'<>]+', content.split('---', 2)[1] if '---' in content else ''):
        url = match.group(0).rstrip('.,;:)')
        urls.append(url)
    return urls


def check_url(url, timeout=10):
    """Check if a URL is reachable via HEAD request. Returns (status, detail)."""
    req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as resp:
            code = resp.getcode()
            final_url = resp.geturl()
            if final_url != url:
                return 'REDIRECT', f'{code} → {final_url[:80]}'
            return 'OK', str(code)
    except urllib.error.HTTPError as e:
        # Some servers block HEAD, try GET
        if e.code == 405 or e.code == 403:
            req2 = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
            try:
                with urllib.request.urlopen(req2, timeout=timeout, context=CTX) as resp:
                    return 'OK', str(resp.getcode())
            except urllib.error.HTTPError as e2:
                return 'ERROR', f'HTTP {e2.code}'
            except Exception:
                return 'OK', '405/403 but likely valid'
        return 'ERROR', f'HTTP {e.code}'
    except urllib.error.URLError as e:
        return 'ERROR', f'URL Error: {e.reason}'
    except TimeoutError:
        return 'TIMEOUT', f'No response in {timeout}s'
    except Exception as e:
        return 'ERROR', str(e)[:80]


def main():
    parser = argparse.ArgumentParser(description='Check source URLs in articles')
    parser.add_argument('--article', type=str, help='Check single article')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds')
    args = parser.parse_args()

    # Collect all URLs
    url_map = {}  # url -> [slugs that use it]
    for f in sorted(articles_dir.iterdir()):
        if not f.name.endswith('.md') or f.name == '_index.md':
            continue
        if args.article and f.stem != args.article:
            continue
        content = f.read_text(encoding='utf-8')
        urls = extract_urls_from_sources(content)
        for url in urls:
            url_map.setdefault(url, []).append(f.stem)

    unique_urls = list(url_map.keys())
    print(f'Checking {len(unique_urls)} unique source URLs across {len(set(s for slugs in url_map.values() for s in slugs))} articles...\n')

    ok = 0
    redirects = 0
    errors = []
    timeouts = []

    for i, url in enumerate(unique_urls, 1):
        status, detail = check_url(url, timeout=args.timeout)
        time.sleep(DELAY)

        if status == 'OK':
            ok += 1
        elif status == 'REDIRECT':
            redirects += 1
        elif status == 'TIMEOUT':
            timeouts.append((url, url_map[url]))
            print(f'  ⏱️  TIMEOUT: {url[:80]}')
            for slug in url_map[url]:
                print(f'       used by: {slug}')
        else:
            errors.append((url, detail, url_map[url]))
            print(f'  ❌ {detail}: {url[:80]}')
            for slug in url_map[url]:
                print(f'       used by: {slug}')

        # Progress every 50
        if i % 50 == 0:
            print(f'  ... checked {i}/{len(unique_urls)}')

    print(f'\n{"="*55}')
    print(f'  SOURCE URL CHECK SUMMARY')
    print(f'{"="*55}')
    print(f'  Total URLs:    {len(unique_urls)}')
    print(f'  OK:            {ok}')
    print(f'  Redirects:     {redirects}')
    print(f'  Errors:        {len(errors)}')
    print(f'  Timeouts:      {len(timeouts)}')
    print(f'{"="*55}')

    if errors or timeouts:
        sys.exit(1)


if __name__ == '__main__':
    main()
