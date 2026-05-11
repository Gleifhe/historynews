#!/usr/bin/env python3
"""
fix-all-images-final.py — Re-download images for ALL articles that lack
verified Wikipedia mappings, plus any known mismatches.

Uses pithumbsize CDN thumbnails from the correct Wikipedia article.
"""
import io
import json
import os
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

MAX_WIDTH = 1200
JPEG_QUALITY = 85
DL_DELAY = 2.0
USER_AGENT = 'HistoryNewsBot/1.0 (https://github.com/gleifhe/historynews; educational history site) python-urllib'
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

# Complete mapping for ALL articles that need re-downloading
FIXES = {
    # 47 unmapped articles (from original batch, may have wrong images)
    'apollo-11-mission': 'Apollo 11',
    'assassination-franz-ferdinand': 'Assassination of Archduke Franz Ferdinand',
    'berlin-airlift': 'Berlin Blockade',
    'berlin-wall-falls': 'Fall of the Berlin Wall',
    'black-death-plague': 'Black Death',
    'challenger-disaster': 'Space Shuttle Challenger disaster',
    'chernobyl-disaster': 'Chernobyl disaster',
    'civil-rights-march-on-washington': 'March on Washington for Jobs and Freedom',
    'communist-manifesto': 'The Communist Manifesto',
    'd-day-oral-histories': 'Normandy landings',
    'darwins-origin-of-species': 'On the Origin of Species',
    'declaration-of-independence': 'United States Declaration of Independence',
    'discovery-of-xrays': 'X-ray',
    'dust-bowl': 'Dust Bowl',
    'edison-electric-light': 'Incandescent light bulb',
    'end-of-apartheid-mandela': 'Nelson Mandela',
    'enigma-code-bletchley-park': 'Bletchley Park',
    'fall-of-saigon': 'Fall of Saigon',
    'first-black-hole-photo': 'Event Horizon Telescope',
    'founding-of-united-nations': 'United Nations',
    'giant-panda-recovery': 'Giant panda',
    'gps-civilian-access': 'Global Positioning System',
    'hindenburg-disaster': 'Hindenburg disaster',
    'hiroshima-nagasaki': 'Atomic bombings of Hiroshima and Nagasaki',
    'hope-diamond': 'Hope Diamond',
    'indian-independence-gandhi': 'Mahatma Gandhi',
    'international-space-station': 'International Space Station',
    'internet-on-911': 'September 11 attacks',
    'iwo-jima-flag-photo': 'Raising the Flag on Iwo Jima',
    'japanese-internment-order-9066': 'Internment of Japanese Americans',
    'jfk-assassination-photos': 'Assassination of John F. Kennedy',
    'johnstown-flood': 'Johnstown Flood',
    'lindbergh-kidnapping': 'Lindbergh kidnapping',
    'marshall-plan-rebuilds-europe': 'Marshall Plan',
    'michelangelo-sistine-chapel': 'Sistine Chapel ceiling',
    'moon-landing-headlines': 'Apollo 11',
    'nixon-resignation-speech': 'Resignation of Richard Nixon',
    'operation-paperclip': 'Operation Paperclip',
    'pearl-harbor-intelligence-failures': 'Attack on Pearl Harbor',
    'rosetta-stone': 'Rosetta Stone',
    'stanford-prison-experiment': 'Stanford prison experiment',
    'storming-of-the-bastille': 'Storming of the Bastille',
    'suffragette-emily-davison': 'Emily Davison',
    'tiananmen-square-tank-man': '1989 Tiananmen Square protests and massacre',
    'trial-of-socrates': 'Trial of Socrates',
    'triangle-shirtwaist-fire': 'Triangle Shirtwaist Factory fire',
    'whaling-moratorium': 'Whaling',
    # Known wrong image
    '1906-san-francisco-earthquake': '1906 San Francisco earthquake',
    '1918-spanish-flu-pandemic': 'Spanish flu',
    # 2 with no thumbnail - try alternative articles
    'anne-frank-diary': 'Anne Frank',
    'dolly-the-sheep-cloned': 'Dolly (sheep)',
    # Last 2 unfixed from previous run
    'good-friday-agreement': 'Northern Ireland',
    'doctors-without-borders': 'Médecins Sans Frontières',
}

root = Path(__file__).parent.parent
images_dir = root / 'static' / 'images' / 'articles'
articles_dir = root / 'content' / 'articles'


def wiki_api_request(params):
    base_url = 'https://en.wikipedia.org/w/api.php'
    params['format'] = 'json'
    params['maxlag'] = '5'
    url = f'{base_url}?{urllib.parse.urlencode(params)}'
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15, context=CTX) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                retry = e.headers.get('Retry-After', str(10 * (attempt + 1)))
                wait = int(retry) if retry.isdigit() else 10
                print(f' [HTTP {e.code}, wait {wait}s]', end='', flush=True)
                time.sleep(wait)
                continue
            return None
        except Exception:
            if attempt < 2:
                time.sleep(5)
                continue
            return None
    return None


def get_thumbnail_urls_batch(wiki_titles, width=1200):
    """Batch query for CDN thumbnail URLs."""
    results = {}
    title_list = list(set(wiki_titles))
    for i in range(0, len(title_list), 50):
        batch = title_list[i:i + 50]
        data = wiki_api_request({
            'action': 'query',
            'titles': '|'.join(batch),
            'prop': 'pageimages',
            'piprop': 'thumbnail',
            'pithumbsize': str(width),
            'redirects': '1',
        })
        if data and 'query' in data and 'pages' in data['query']:
            resolved = {}
            for n in data['query'].get('normalized', []):
                resolved[n['from']] = n['to']
            for r in data['query'].get('redirects', []):
                resolved[r['from']] = r['to']
            
            for page_id, page in data['query']['pages'].items():
                if page_id != '-1' and 'thumbnail' in page:
                    title = page.get('title', '')
                    results[title] = page['thumbnail']['source']
                    for orig, dest in resolved.items():
                        if dest == title:
                            results[orig] = page['thumbnail']['source']
        if i + 50 < len(title_list):
            time.sleep(5)
    return results


def download_and_convert(url, local_path):
    """Download and save as JPEG."""
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30, context=CTX) as resp:
                data = resp.read()
            img = Image.open(io.BytesIO(data))
            if img.width > MAX_WIDTH:
                ratio = MAX_WIDTH / img.width
                img = img.resize((MAX_WIDTH, int(img.height * ratio)), Image.LANCZOS)
            if img.mode in ('RGBA', 'P', 'LA'):
                img = img.convert('RGB')
            img.save(str(local_path), 'JPEG', quality=JPEG_QUALITY, optimize=True)
            size_kb = os.path.getsize(local_path) // 1024
            return True, f'{img.width}x{img.height}, {size_kb}KB'
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                retry = e.headers.get('Retry-After', '20')
                wait = int(retry) if retry.isdigit() else 20
                print(f' 429 wait {wait}s...', end=' ', flush=True)
                time.sleep(wait)
                continue
            return False, f'HTTP {e.code}'
        except Exception as e:
            return False, str(e)
    return False, 'Max retries'


def update_front_matter(filepath, new_image_path):
    content = filepath.read_text(encoding='utf-8')
    content = re.sub(r'image:\s*"[^"]*"', f'image: "{new_image_path}"', content, count=1)
    filepath.write_text(content, encoding='utf-8')


def main():
    print(f'Re-downloading {len(FIXES)} images from verified Wikipedia sources...\n')
    
    # Phase 1: Get all correct thumbnail URLs
    print('Phase 1: Querying Wikipedia API...')
    wiki_titles = list(set(FIXES.values()))
    thumb_urls = get_thumbnail_urls_batch(wiki_titles)
    
    # Map back to slugs
    slug_to_url = {}
    for slug, wiki_title in FIXES.items():
        url = thumb_urls.get(wiki_title)
        if not url:
            for t, u in thumb_urls.items():
                if t.lower() == wiki_title.lower():
                    url = u
                    break
        if url:
            slug_to_url[slug] = (url, wiki_title)
    
    found = len(slug_to_url)
    missing = [s for s in FIXES if s not in slug_to_url]
    print(f'Found: {found}/{len(FIXES)}')
    if missing:
        print(f'No thumbnail: {", ".join(missing)}')
    print()
    
    # Phase 2: Download
    print(f'Phase 2: Downloading {found} images...\n')
    fixed = 0
    failed = []
    
    for slug, (url, wiki_title) in sorted(slug_to_url.items()):
        local_path = images_dir / f'{slug}.jpg'
        hugo_path = f'/images/articles/{slug}.jpg'
        article_path = articles_dir / f'{slug}.md'
        
        # Delete existing
        if local_path.exists():
            try:
                local_path.unlink()
            except PermissionError:
                try:
                    temp = local_path.with_suffix('.old')
                    local_path.rename(temp)
                    temp.unlink()
                except Exception:
                    failed.append((slug, 'File locked'))
                    print(f'  {slug} — LOCKED')
                    continue
        
        print(f'  {slug}', end='', flush=True)
        success, detail = download_and_convert(url, local_path)
        time.sleep(DL_DELAY)
        
        if success:
            fixed += 1
            print(f' — OK ({detail}) [{wiki_title}]')
            if article_path.exists():
                update_front_matter(article_path, hugo_path)
        else:
            failed.append((slug, detail))
            print(f' — FAILED ({detail})')
    
    print(f'\n{"="*55}')
    print(f'  FINAL IMAGE FIX SUMMARY')
    print(f'{"="*55}')
    print(f'  Fixed:   {fixed}/{len(slug_to_url)}')
    print(f'  Failed:  {len(failed)}')
    print(f'  Missing: {len(missing)} (no Wikipedia thumbnail)')
    print(f'{"="*55}')
    if failed:
        print(f'\n  Failed:')
        for s, d in failed:
            print(f'    {s}: {d}')
    if missing:
        print(f'\n  No thumbnail:')
        for s in missing:
            print(f'    {s} -> "{FIXES[s]}"')


if __name__ == '__main__':
    main()
