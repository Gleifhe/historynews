#!/usr/bin/env python3
"""
check-video-embeds.py — Test if YouTube videos are actually embeddable.

Unlike oEmbed checks, this loads the actual embed page and looks for
"UNPLAYABLE" or "Video unavailable" signals that indicate embedding is blocked.

Usage:
    python scripts/check-video-embeds.py
"""

import os
import re
import ssl
import sys
import time
import urllib.request
import json

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def check_embeddable(video_id):
    """
    Check if a YouTube video is actually embeddable.
    Returns (status, detail) where status is 'OK', 'BLOCKED', or 'ERROR'.
    
    Method: Fetch the embed page and look for player config signals.
    YouTube embeds that are blocked return a very small HTML page (~10KB)
    while working embeds return a larger page (~50KB+) with player JS.
    """
    embed_url = f"https://www.youtube.com/embed/{video_id}"
    req = urllib.request.Request(embed_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    try:
        with urllib.request.urlopen(req, timeout=15, context=CTX) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            html_len = len(html)

            # Method 1: Look for explicit block signals in JSON config
            if '"status":"UNPLAYABLE"' in html:
                return 'BLOCKED', 'embedding disabled by uploader'
            if '"status":"ERROR"' in html and '"reason"' in html:
                return 'BLOCKED', 'video not found or removed'
            if '"status":"LOGIN_REQUIRED"' in html:
                return 'BLOCKED', 'age restricted (login required)'
            
            # Method 2: Check for "subreasons" which indicate blocks
            if '"subreason"' in html and ('embedding' in html.lower() or 'unavailable' in html.lower()):
                return 'BLOCKED', 'embed restricted (subreason found)'
            
            # Method 3: Look for positive signals - player config present
            if '"status":"OK"' in html:
                return 'OK', 'confirmed embeddable'
            
            # Method 4: Check page size — blocked embeds are much smaller
            if html_len > 100000:
                return 'OK', f'player loaded ({html_len//1024}KB)'
            elif html_len < 20000:
                # Small page could mean blocked, but could also be a consent page
                if 'consent' in html.lower() or 'CONSENT' in html:
                    return 'OK', f'consent page ({html_len//1024}KB) - likely OK'
                return 'UNKNOWN', f'small page ({html_len//1024}KB) - may be blocked'
            else:
                return 'OK', f'page loaded ({html_len//1024}KB)'

    except urllib.error.HTTPError as e:
        if e.code == 403:
            return 'BLOCKED', 'HTTP 403 Forbidden'
        return 'ERROR', f'HTTP {e.code}'
    except Exception as e:
        return 'ERROR', str(e)


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    content_dir = os.path.join(root, 'content', 'articles')

    results = {'OK': [], 'BLOCKED': [], 'ERROR': [], 'UNKNOWN': [], 'NONE': []}

    articles = sorted([f for f in os.listdir(content_dir)
                       if f.endswith('.md') and f != '_index.md'])

    print(f"Checking {len(articles)} articles for video embeddability...\n")

    for filename in articles:
        filepath = os.path.join(content_dir, filename)
        slug = os.path.splitext(filename)[0]

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        match = re.search(r'video:\s*"https://www\.youtube\.com/embed/([^"]+)"', content)
        if not match:
            results['NONE'].append(slug)
            continue

        video_id = match.group(1)
        status, detail = check_embeddable(video_id)
        results[status].append((slug, video_id, detail))

        icon = {'OK': '+', 'BLOCKED': 'X', 'ERROR': '!', 'UNKNOWN': '?'}[status]
        print(f"  [{icon}] {slug} | {video_id} | {detail}")

        time.sleep(0.5)  # Be polite to YouTube

    # Summary
    print(f"\n{'='*60}")
    print(f"  VIDEO EMBED CHECK SUMMARY")
    print(f"{'='*60}")
    print(f"  Embeddable (OK):     {len(results['OK'])}")
    print(f"  BLOCKED:             {len(results['BLOCKED'])}")
    print(f"  ERROR:               {len(results['ERROR'])}")
    print(f"  Unknown:             {len(results['UNKNOWN'])}")
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
