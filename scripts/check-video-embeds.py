#!/usr/bin/env python3
"""
check-video-embeds.py — Test if YouTube videos are actually embeddable.

Uses YouTube's oEmbed API to check video availability and embeddability.
Per copilot-instructions.md: use oEmbed, proper bot User-Agent, no scraping.

Usage:
    python scripts/check-video-embeds.py
"""

import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

USER_AGENT = 'HistoryNewsBot/1.0 (https://github.com/gleifhe/historynews; educational history site) python-urllib'
CTX = ssl.create_default_context()
DELAY = 1.0


def check_embeddable(video_id):
    """
    Check if a YouTube video is embeddable via the oEmbed API.
    Returns (status, detail) where status is 'OK', 'BLOCKED', or 'ERROR'.
    """
    oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    req = urllib.request.Request(oembed_url, headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15, context=CTX) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            title = data.get('title', 'unknown')
            return 'OK', f'embeddable: {title[:60]}'
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return 'BLOCKED', 'embedding disabled or private'
        if e.code == 403:
            return 'BLOCKED', 'forbidden (age-restricted or blocked)'
        if e.code == 404:
            return 'BLOCKED', 'video not found or removed'
        if e.code == 429:
            retry = e.headers.get('Retry-After', '10')
            try:
                wait = int(retry)
            except ValueError:
                wait = 10
            time.sleep(wait)
            return 'ERROR', f'rate limited (429), retried after {wait}s'
        return 'ERROR', f'HTTP {e.code}'
    except urllib.error.URLError as e:
        return 'ERROR', f'URL error: {str(e.reason)[:40]}'
    except Exception as e:
        return 'ERROR', str(e)[:60]


def main():
    root = Path(__file__).parent.parent
    content_dir = root / 'content' / 'articles'

    results = {'OK': [], 'BLOCKED': [], 'ERROR': [], 'NONE': []}

    articles = sorted([f for f in content_dir.iterdir()
                       if f.suffix == '.md' and f.name != '_index.md'])

    print(f"Checking {len(articles)} articles for video embeddability...\n")

    for f in articles:
        slug = f.stem
        content = f.read_text(encoding='utf-8')

        match = re.search(r'video:\s*"https://www\.youtube\.com/embed/([^"]+)"', content)
        if not match:
            results['NONE'].append(slug)
            continue

        video_id = match.group(1)
        status, detail = check_embeddable(video_id)
        results[status].append((slug, video_id, detail))

        icon = {'OK': '+', 'BLOCKED': 'X', 'ERROR': '!'}[status]
        print(f"  [{icon}] {slug} | {video_id} | {detail}")

        time.sleep(DELAY)  # Be polite to YouTube

    # Summary
    print(f"\n{'='*60}")
    print(f"  VIDEO EMBED CHECK SUMMARY")
    print(f"{'='*60}")
    print(f"  Embeddable (OK):     {len(results['OK'])}")
    print(f"  BLOCKED:             {len(results['BLOCKED'])}")
    print(f"  ERROR:               {len(results['ERROR'])}")
    print(f"  No video field:      {len(results['NONE'])}")
    print(f"{'='*60}")

    if results['BLOCKED']:
        print(f"\n  BLOCKED videos that need replacement:")
        for slug, vid, detail in results['BLOCKED']:
            print(f"    {slug} | {vid} | {detail}")

    if results['ERROR']:
        print(f"\n  ERROR videos to investigate:")
        for slug, vid, detail in results['ERROR']:
            print(f"    {slug} | {vid} | {detail}")

    if results['BLOCKED'] or results['ERROR']:
        sys.exit(1)
    else:
        print(f"\n  ALL VIDEOS EMBEDDABLE")
        sys.exit(0)


if __name__ == '__main__':
    main()
