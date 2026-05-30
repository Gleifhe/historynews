"""Check all YouTube video embeds for playability using oEmbed API."""
import os
import re
import json
import urllib.request
import urllib.error
import ssl
import time

ARTICLES_DIR = os.path.join(os.path.dirname(__file__), "..", "content", "articles")
UA = "HistoryNewsBot/1.0 (https://github.com/gleifhe/historynews) python-urllib"
ctx = ssl.create_default_context()


def main():
    videos = []
    for fname in sorted(os.listdir(ARTICLES_DIR)):
        if not fname.endswith(".md") or fname == "_index.md":
            continue
        with open(os.path.join(ARTICLES_DIR, fname), encoding="utf-8") as f:
            content = f.read()
        m = re.search(r'video:\s*"https?://(?:www\.)?youtube\.com/embed/([^"]+)"', content)
        if m:
            videos.append((fname[:-3], m.group(1)))

    print(f"Found {len(videos)} articles with video embeds")
    print("Checking via YouTube oEmbed API...\n")

    failed = []
    for i, (slug, vid_id) in enumerate(videos):
        oembed_url = "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=" + vid_id + "&format=json"
        req = urllib.request.Request(oembed_url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                resp.read()
        except urllib.error.HTTPError as e:
            failed.append((slug, vid_id, f"HTTP {e.code}"))
            print(f"  BROKEN: {slug} | {vid_id} | HTTP {e.code}")
        except Exception as e:
            failed.append((slug, vid_id, str(e)))
            print(f"  BROKEN: {slug} | {vid_id} | {e}")

        if (i + 1) % 50 == 0:
            print(f"  ... checked {i + 1}/{len(videos)}")
        time.sleep(0.3)

    print(f"\n{'='*50}")
    print(f"  Total videos checked: {len(videos)}")
    print(f"  Working: {len(videos) - len(failed)}")
    print(f"  Broken: {len(failed)}")
    print(f"{'='*50}")

    if failed:
        print("\nBroken videos:")
        for slug, vid_id, reason in failed:
            print(f"  {slug}: https://youtube.com/watch?v={vid_id} ({reason})")


if __name__ == "__main__":
    main()
