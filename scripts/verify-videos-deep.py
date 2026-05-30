"""
Check all YouTube video embeds by loading the actual embed page.
Catches Error 153 (embed-restricted) that oEmbed API misses.
"""
import os
import re
import ssl
import time
import urllib.request
import urllib.error

ARTICLES_DIR = os.path.join(os.path.dirname(__file__), "..", "content", "articles")
UA = "HistoryNewsBot/1.0 (https://github.com/gleifhe/historynews) python-urllib"
ctx = ssl.create_default_context()


def main():
    # Collect all videos
    videos = []
    for fname in sorted(os.listdir(ARTICLES_DIR)):
        if not fname.endswith(".md") or fname == "_index.md":
            continue
        with open(os.path.join(ARTICLES_DIR, fname), encoding="utf-8") as f:
            content = f.read()
        m = re.search(r'video:\s*"https?://(?:www\.)?youtube\.com/embed/([^"]+)"', content)
        if m:
            videos.append((fname[:-3], m.group(1)))

    print(f"Checking {len(videos)} video embeds by loading embed pages...\n")

    broken = []
    for i, (slug, vid_id) in enumerate(videos):
        embed_url = "https://www.youtube.com/embed/" + vid_id
        req = urllib.request.Request(embed_url, headers={"User-Agent": UA})
        status = "OK"
        detail = ""

        try:
            with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                if "Video unavailable" in body:
                    status = "UNAVAILABLE"
                    detail = "Video unavailable"
                elif "Error 150" in body:
                    status = "ERROR 150"
                    detail = "Playback restricted by owner"
                elif "Error 153" in body:
                    status = "ERROR 153"
                    detail = "Player configuration error (embed blocked)"
                elif "UNPLAYABLE" in body:
                    status = "UNPLAYABLE"
                    detail = "Marked as unplayable"
                elif "Sign in to confirm" in body:
                    status = "AGE_RESTRICTED"
                    detail = "Requires sign-in (age restricted)"
        except urllib.error.HTTPError as e:
            status = f"HTTP {e.code}"
            detail = str(e.reason)
        except Exception as e:
            status = "ERROR"
            detail = str(e)

        if status != "OK":
            broken.append((slug, vid_id, status, detail))
            print(f"  FAIL: {slug} | {vid_id} | {status} | {detail}")

        if (i + 1) % 25 == 0:
            print(f"  ... checked {i + 1}/{len(videos)}")

        time.sleep(0.5)

    print(f"\n{'=' * 55}")
    print(f"  Total videos checked: {len(videos)}")
    print(f"  Working: {len(videos) - len(broken)}")
    print(f"  Broken:  {len(broken)}")
    print(f"{'=' * 55}")

    if broken:
        print("\nBroken videos:")
        for slug, vid_id, status, detail in broken:
            print(f"  {slug}")
            print(f"    Video: https://youtube.com/watch?v={vid_id}")
            print(f"    Error: {status} - {detail}")


if __name__ == "__main__":
    main()
