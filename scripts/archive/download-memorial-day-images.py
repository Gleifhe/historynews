#!/usr/bin/env python3
"""Download images for all 75 Memorial Day articles using the verified Wikipedia API approach."""
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

# Slug -> Wikipedia article title (verified mappings)
SLUG_TO_WIKI = {
    'birth-of-decoration-day': 'Memorial Day',
    'general-logans-order': 'Memorial Day',
    'arlington-national-cemetery': 'Arlington National Cemetery',
    'tomb-of-unknown-soldier': 'Tomb of the Unknown Soldier (Arlington)',
    'taps-bugle-call': 'Taps (bugle call)',
    'gold-star-mothers': 'American Gold Star Mothers',
    'national-moment-of-remembrance': 'National Moment of Remembrance',
    'culper-spy-ring': 'Culper Ring',
    'nathan-hale-last-words': 'Nathan Hale',
    'marquis-de-lafayette': 'Marquis de Lafayette',
    '54th-massachusetts-regiment': '54th Massachusetts Infantry Regiment',
    'clara-barton-angel-of-battlefield': 'Clara Barton',
    'andersonville-prison': 'Andersonville National Historic Site',
    'sullivan-ballou-letter': 'Sullivan Ballou',
    'harlem-hellfighters': '369th Infantry Regiment',
    'sergeant-alvin-york': 'Alvin C. York',
    'belleau-wood': 'Battle of Belleau Wood',
    'lost-battalion-argonne': 'Lost Battalion (World War I)',
    'in-flanders-fields': 'In Flanders Fields',
    'tuskegee-airmen': 'Tuskegee Airmen',
    'four-chaplains': 'Four Chaplains',
    'navajo-code-talkers': 'Code talker',
    'audie-murphy-most-decorated': 'Audie Murphy',
    'sullivan-brothers': 'Sullivan brothers',
    'battle-of-midway': 'Battle of Midway',
    'doolittle-raid': 'Doolittle Raid',
    'omaha-beach-first-wave': 'Omaha Beach',
    'battle-of-the-bulge': 'Battle of the Bulge',
    'merchant-marines-wwii': 'United States Merchant Marine',
    'rosie-the-riveter': 'Rosie the Riveter',
    'chosin-reservoir': 'Battle of Chosin Reservoir',
    'forgotten-war-forgotten-heroes': 'Korean War',
    'vietnam-veterans-memorial-wall': 'Vietnam Veterans Memorial',
    'hanoi-hilton-pows': 'Hoa Lo Prison',
    'hamburger-hill': 'Battle of Hamburger Hill',
    'vietnam-mia-search': 'Defense POW/MIA Accounting Agency',
    'beirut-barracks-bombing': '1983 Beirut barracks bombings',
    'pat-tillman-chose-service': 'Pat Tillman',
    'mogadishu-black-hawk-down': 'Battle of Mogadishu (1993)',
    'pentagon-on-911': 'American Airlines Flight 77',
    'fallujah-bloodiest-battle': 'Second Battle of Fallujah',
    'afghanistan-war-fallen': 'War in Afghanistan (2001-2021)',
    'navy-seal-michael-murphy': 'Michael P. Murphy',
    'pow-mia-flag': 'POW/MIA flag',
    'operation-homecoming-1973': 'Operation Homecoming',
    'dover-test': 'Dover Air Force Base',
    'normandy-american-cemetery': 'Normandy American Cemetery and Memorial',
    'poppy-symbol-of-remembrance': 'Remembrance poppy',
    'letters-home-last-words': 'Veterans History Project',
    'buglers-of-arlington': '3rd U.S. Infantry Regiment',
    'eisenhowers-two-letters': 'Dwight D. Eisenhower',
    'buddy-system-never-alone': 'Buddy system',
    'mission-first-people-always': 'United States Army',
    'calm-is-contagious': 'United States Navy SEALs',
    'after-action-review': 'After-action review',
    'the-40-percent-rule': 'David Goggins',
    'embracing-the-suck': 'United States Army Rangers',
    'post-traumatic-growth': 'Post-traumatic growth',
    'viktor-frankl-was-right': "Man's Search for Meaning",
    'power-of-the-debrief': 'After-action review',
    'platoon-to-purpose': 'United States Department of Veterans Affairs',
    'veteran-entrepreneur-boom': 'Small Business Administration',
    'team-rubicon-continued-service': 'Team Rubicon',
    'gi-bill-changed-america-twice': 'G.I. Bill',
    'service-doesnt-end-at-discharge': 'Volunteering',
    'letters-home-what-matters': 'Veterans History Project',
    'foxhole-test': 'Foxhole',
    'veterans-make-great-mentors': 'Mentorship',
    'brotherhood-beyond-uniform': 'Military brat',
    'coming-home-to-gratitude': 'Gratitude',
    'make-your-bed-small-wins': 'William H. McRaven',
    'physical-fitness-mental-health': 'Exercise and mental health',
    'veterans-morning-routine': 'Reveille',
    'preparation-is-a-lifestyle': 'Jim Mattis',
    'servant-leadership': 'Servant leadership',
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
                retry_after = e.headers.get('Retry-After', '')
                try:
                    wait = int(retry_after)
                except ValueError:
                    wait = 10 * (attempt + 1)
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
                time.sleep(wait)
                continue
            return False, f'HTTP {e.code}'
        except Exception as e:
            return False, str(e)
    return False, 'Max retries'


def main():
    # Only process articles that need images
    to_download = {}
    for slug, wiki_title in SLUG_TO_WIKI.items():
        local_path = images_dir / f'{slug}.jpg'
        if not local_path.exists():
            to_download[slug] = wiki_title

    if not to_download:
        print('All images already downloaded.')
        return

    print(f'Downloading images for {len(to_download)} articles...\n')

    # Phase 1: Batch API lookup (2 calls max for 75 titles)
    print('Phase 1: Wikipedia API lookup...')
    thumb_urls = get_thumbnail_urls_batch(list(to_download.values()))
    
    slug_to_url = {}
    for slug, wiki_title in to_download.items():
        url = thumb_urls.get(wiki_title)
        if not url:
            for t, u in thumb_urls.items():
                if t.lower() == wiki_title.lower():
                    url = u
                    break
        if url:
            slug_to_url[slug] = (url, wiki_title)

    print(f'Found: {len(slug_to_url)}/{len(to_download)}')
    missing = [s for s in to_download if s not in slug_to_url]
    if missing:
        print(f'No thumbnail: {", ".join(missing)}')
    print()

    # Phase 2: Download with 2s delay
    print(f'Phase 2: Downloading {len(slug_to_url)} images...\n')
    ok = 0
    fail = []
    for slug, (url, wiki_title) in sorted(slug_to_url.items()):
        local_path = images_dir / f'{slug}.jpg'
        print(f'  {slug}', end='', flush=True)
        success, detail = download_and_convert(url, local_path)
        time.sleep(DL_DELAY)
        if success:
            ok += 1
            print(f' — OK ({detail})')
        else:
            fail.append((slug, detail))
            print(f' — FAILED ({detail})')

    print(f'\n  Downloaded: {ok}, Failed: {len(fail)}, No thumb: {len(missing)}')
    if fail:
        for s, d in fail:
            print(f'    {s}: {d}')


if __name__ == '__main__':
    main()
