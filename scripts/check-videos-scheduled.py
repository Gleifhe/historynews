#!/usr/bin/env python3
"""
check-videos-scheduled.py — Re-check all YouTube video embeds for availability.

Sends oEmbed requests to verify each video ID is still valid and embeddable.
Designed to run monthly via cron or manually before major deploys.

API etiquette: 1 request/second, proper User-Agent, no browser spoofing.

Usage:
    python scripts/check-videos-scheduled.py
    python scripts/check-videos-scheduled.py --article slug
"""
import argparse
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

root = Path(__file__).parent.parent
articles_dir = root / 'content' / 'articles'

USER_AGENT = 'HistoryNewsBot/1.0 (https://github.com/gleifhe/historynews; educational history site)'
CTX = ssl.create_default_context()
DELAY = 1.0


def check_video(video_id):
    """Check if a YouTube video exists via oEmbed API."""
    url = f'https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json'
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=10, context=CTX) as resp:
            data = json.loads(resp.read())
            return 'OK', data.get('title', 'Unknown')
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return 'EMBED_DISABLED', 'Embedding not allowed'
        elif e.code == 404:
            return 'NOT_FOUND', 'Video does not exist'
        elif e.code in (429, 503):
            retry_after = e.headers.get('Retry-After', '')
            try:
                wait = int(retry_after)
            except ValueError:
                wait = 30
            time.sleep(wait)
            return 'ERROR', f'Rate limited ({e.code}), waited {wait}s'
        return 'ERROR', f'HTTP {e.code}'
    except Exception as e:
        return 'ERROR', str(e)[:60]


def main():
    parser = argparse.ArgumentParser(description='Check YouTube video availability')
    parser.add_argument('--article', type=str, help='Check single article')
    args = parser.parse_args()

    # Collect all video IDs
    videos = {}  # video_id -> [slugs]
    for f in sorted(articles_dir.iterdir()):
        if not f.name.endswith('.md') or f.name == '_index.md':
            continue
        if args.article and f.stem != args.article:
            continue

        content = f.read_text(encoding='utf-8')
        match = re.search(r'video:\s*"https://www\.youtube\.com/embed/([^"]+)"', content)
        if match:
            vid = match.group(1)
            videos.setdefault(vid, []).append(f.stem)

    unique_ids = list(videos.keys())
    print(f'Checking {len(unique_ids)} unique YouTube videos across {sum(len(v) for v in videos.values())} articles...\n')

    ok = 0
    problems = []

    for i, vid in enumerate(unique_ids, 1):
        status, detail = check_video(vid)
        time.sleep(DELAY)

        if status == 'OK':
            ok += 1
        else:
            problems.append((vid, status, detail, videos[vid]))
            print(f'  [{status}] {vid}: {detail}')
            for slug in videos[vid]:
                print(f'    used by: {slug}')

        if i % 50 == 0:
            print(f'  ... checked {i}/{len(unique_ids)}')

    print(f'\n{"="*55}')
    print(f'  VIDEO CHECK SUMMARY')
    print(f'{"="*55}')
    print(f'  Unique videos:   {len(unique_ids)}')
    print(f'  OK:              {ok}')
    print(f'  Problems:        {len(problems)}')
    print(f'{"="*55}')

    if problems:
        sys.exit(1)
    else:
        print(f'\n  [OK] All videos are available and embeddable')


if __name__ == '__main__':
    main()
