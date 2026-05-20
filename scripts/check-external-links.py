#!/usr/bin/env python3
"""
check-external-links.py — Check that outbound links in article body text still work.

Scans all markdown links [text](url) in article bodies and verifies each
external URL is reachable via HTTP HEAD.

API etiquette: 1 request/second, proper User-Agent, HEAD requests only.

Usage:
    python scripts/check-external-links.py
    python scripts/check-external-links.py --article slug
    python scripts/check-external-links.py --timeout 15
"""
import argparse
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

root = Path(__file__).parent.parent
articles_dir = root / 'content' / 'articles'

USER_AGENT = 'HistoryNewsBot/1.0 (https://github.com/gleifhe/historynews; educational history site) python-urllib'
CTX = ssl.create_default_context()
DELAY = 1.0


def check_url(url, timeout=10):
    req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as resp:
            return 'OK', resp.getcode()
    except urllib.error.HTTPError as e:
        if e.code in (405, 403):
            # Some sites block HEAD, try GET
            req2 = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
            try:
                with urllib.request.urlopen(req2, timeout=timeout, context=CTX) as resp:
                    return 'OK', resp.getcode()
            except Exception:
                return 'OK', '403/405 likely valid'
        return 'ERROR', e.code
    except urllib.error.URLError as e:
        return 'ERROR', str(e.reason)[:40]
    except TimeoutError:
        return 'TIMEOUT', timeout
    except Exception as e:
        return 'ERROR', str(e)[:40]


def main():
    parser = argparse.ArgumentParser(description='Check external links in articles')
    parser.add_argument('--article', type=str, help='Check single article')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout')
    args = parser.parse_args()

    # Collect all external URLs from article bodies
    url_map = {}  # url -> [slugs]
    for f in sorted(articles_dir.iterdir()):
        if not f.name.endswith('.md') or f.name == '_index.md':
            continue
        if args.article and f.stem != args.article:
            continue

        content = f.read_text(encoding='utf-8')
        body = content.split('---', 2)[2] if '---' in content else content

        # Find markdown links to external URLs
        for match in re.finditer(r'\[([^\]]+)\]\((https?://[^)]+)\)', body):
            url = match.group(2)
            url_map.setdefault(url, []).append(f.stem)

    unique_urls = list(url_map.keys())
    print(f'Checking {len(unique_urls)} unique external links...\n')

    ok = 0
    errors = []
    timeouts = []

    for i, url in enumerate(unique_urls, 1):
        status, detail = check_url(url, timeout=args.timeout)
        time.sleep(DELAY)

        if status == 'OK':
            ok += 1
        elif status == 'TIMEOUT':
            timeouts.append((url, url_map[url]))
            print(f'  [TIMEOUT] {url[:80]}')
        else:
            errors.append((url, detail, url_map[url]))
            print(f'  [ERROR {detail}] {url[:80]}')
            for slug in url_map[url]:
                print(f'    used by: {slug}')

        if i % 25 == 0:
            print(f'  ... checked {i}/{len(unique_urls)}')

    print(f'\n{"="*55}')
    print(f'  EXTERNAL LINK CHECK')
    print(f'{"="*55}')
    print(f'  Total links:   {len(unique_urls)}')
    print(f'  OK:            {ok}')
    print(f'  Errors:        {len(errors)}')
    print(f'  Timeouts:      {len(timeouts)}')
    print(f'{"="*55}')

    if errors or timeouts:
        sys.exit(1)


if __name__ == '__main__':
    main()
