"""
Build slug-to-wiki mappings for all articles missing images,
then download images from Wikipedia API.

This handles:
1. Non-TDIH articles: extracts Wikipedia source from front matter sources field
2. TDIH-02 articles: extracts Wikipedia source from front matter sources field
3. Downloads images using pithumbsize=1200 CDN thumbnails
4. Respects all API etiquette: maxlag, Retry-After, User-Agent, batching, delays
"""
import json
import os
import re
import sys
import time
import ssl
import urllib.request
import urllib.parse
import urllib.error

ROOT = os.path.join(os.path.dirname(__file__), "..")
ARTICLES_DIR = os.path.join(ROOT, "content", "articles")
IMAGES_DIR = os.path.join(ROOT, "static", "images", "articles")
MANIFEST_PATH = os.path.join(ROOT, "scripts", "slug-to-wiki.json")

USER_AGENT = "HistoryNewsBot/1.0 (https://github.com/gleifhe/historynews; educational history site) python-urllib"
API_URL = "https://en.wikipedia.org/w/api.php"

ssl_ctx = ssl.create_default_context()


def parse_front_matter(content):
    """Parse YAML front matter from article content."""
    if not content.startswith("---"):
        return {}
    end = content.index("---", 3)
    fm_text = content[3:end]
    result = {}
    for line in fm_text.split("\n"):
        line = line.strip()
        if ":" in line and not line.startswith("-"):
            key, _, val = line.partition(":")
            val = val.strip().strip('"')
            result[key.strip()] = val
    return result


def extract_wiki_title_from_sources(content):
    """Extract Wikipedia title from the sources list in front matter."""
    # Look for Wikipedia source line: "Wikipedia — Title — URL"
    m = re.search(r'Wikipedia\s*[—–-]\s*(.+?)\s*[—–-]\s*https?://en\.wikipedia\.org', content)
    if m:
        return m.group(1).strip()
    
    # Fallback: extract from Wikipedia URL
    m = re.search(r'https?://en\.wikipedia\.org/wiki/([^\s"]+)', content)
    if m:
        return urllib.parse.unquote(m.group(1).replace("_", " "))
    
    return None


def find_missing_images():
    """Find all articles that don't have a corresponding image."""
    missing = {}
    for fname in sorted(os.listdir(ARTICLES_DIR)):
        if not fname.endswith(".md") or fname == "_index.md":
            continue
        slug = fname[:-3]
        img_path = os.path.join(IMAGES_DIR, f"{slug}.jpg")
        if os.path.exists(img_path):
            continue
        
        filepath = os.path.join(ARTICLES_DIR, fname)
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        
        wiki_title = extract_wiki_title_from_sources(content)
        if wiki_title:
            missing[slug] = wiki_title
        else:
            # Try using title from front matter
            fm = parse_front_matter(content)
            title = fm.get("title", "")
            if title:
                missing[slug] = title
    
    return missing


def wiki_api_request(params):
    """Make a Wikipedia API request with maxlag and Retry-After support."""
    params["format"] = "json"
    params["maxlag"] = "5"
    
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                retry_after = int(e.headers.get("Retry-After", 5))
                print(f"  Rate limited ({e.code}), waiting {retry_after}s...")
                time.sleep(retry_after)
            else:
                raise
        except Exception as e:
            if attempt < 2:
                print(f"  Error: {e}, retrying...")
                time.sleep(2)
            else:
                raise
    return None


def batch_get_thumbnails(titles_map):
    """Batch query Wikipedia for thumbnail URLs. titles_map: {slug: wiki_title}"""
    results = {}  # slug -> thumbnail_url
    
    # Process in batches of 50
    items = list(titles_map.items())
    for i in range(0, len(items), 50):
        batch = items[i:i+50]
        titles_str = "|".join(wiki_title for _, wiki_title in batch)
        slug_by_title = {wiki_title: slug for slug, wiki_title in batch}
        
        print(f"  API batch {i//50 + 1}: querying {len(batch)} titles...")
        
        data = wiki_api_request({
            "action": "query",
            "titles": titles_str,
            "prop": "pageimages",
            "pithumbsize": "1200",
        })
        
        if not data or "query" not in data:
            continue
        
        for page_id, page in data["query"]["pages"].items():
            if int(page_id) < 0:
                continue  # Page not found
            title = page.get("title", "")
            thumb = page.get("thumbnail", {}).get("source", "")
            
            # Find matching slug
            slug = slug_by_title.get(title)
            if not slug:
                # Try normalized title matching
                for wiki_title, s in slug_by_title.items():
                    if wiki_title.lower() == title.lower():
                        slug = s
                        break
            
            if slug and thumb:
                results[slug] = thumb
        
        if i + 50 < len(items):
            time.sleep(1)  # Delay between batches
    
    return results


def download_image(url, dest_path):
    """Download an image with proper User-Agent."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as resp:
            data = resp.read()
            with open(dest_path, "wb") as f:
                f.write(data)
            return True
    except Exception as e:
        print(f"    Download failed: {e}")
        return False


def main():
    print("=" * 60)
    print("  STEP 1: Finding articles with missing images")
    print("=" * 60)
    
    missing = find_missing_images()
    print(f"  Found {len(missing)} articles without images\n")
    
    if not missing:
        print("  No missing images!")
        return
    
    # Update slug-to-wiki.json
    print("=" * 60)
    print("  STEP 2: Updating slug-to-wiki.json manifest")
    print("=" * 60)
    
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)
    
    added = 0
    for slug, wiki_title in missing.items():
        if slug not in manifest:
            manifest[slug] = wiki_title
            added += 1
    
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"  Added {added} new entries (total: {len(manifest)})\n")
    
    # Batch query Wikipedia for thumbnail URLs
    print("=" * 60)
    print("  STEP 3: Querying Wikipedia API for thumbnail URLs")
    print("=" * 60)
    
    thumbnails = batch_get_thumbnails(missing)
    print(f"  Found {len(thumbnails)} thumbnail URLs out of {len(missing)} articles\n")
    
    # Download images
    print("=" * 60)
    print(f"  STEP 4: Downloading {len(thumbnails)} images")
    print("=" * 60)
    
    os.makedirs(IMAGES_DIR, exist_ok=True)
    downloaded = 0
    failed = 0
    
    for slug, thumb_url in sorted(thumbnails.items()):
        dest = os.path.join(IMAGES_DIR, f"{slug}.jpg")
        if os.path.exists(dest):
            continue
        
        print(f"  [{downloaded+failed+1}/{len(thumbnails)}] {slug}")
        if download_image(thumb_url, dest):
            downloaded += 1
        else:
            failed += 1
        
        time.sleep(2)  # 2s delay between downloads
    
    print(f"\n  Downloaded: {downloaded}, Failed: {failed}")
    
    # Report articles that got no image
    no_image = set(missing.keys()) - set(thumbnails.keys())
    if no_image:
        print(f"\n  {len(no_image)} articles had no Wikipedia thumbnail:")
        for slug in sorted(no_image):
            print(f"    - {slug}")


if __name__ == "__main__":
    main()
