#!/usr/bin/env python3
"""
fix-images-wikipedia.py — Find real images for articles using the Wikipedia API.

For each article that has a remote image URL (likely fabricated/broken),
this script:
  1. Extracts the article title from front matter
  2. Searches Wikipedia for the best matching article
  3. Gets the lead image (pageimage) from that Wikipedia article
  4. Downloads the image locally to static/images/articles/{slug}.jpg
  5. Updates the article's front matter to use the local path

Uses the Wikipedia API correctly per Wikimedia policy:
  - Batched requests (50 titles per call) to minimize API calls
  - pithumbsize=1200 to get CDN-served thumbnail URLs (not raw uploads)
  - maxlag=5 to back off when servers are busy
  - Retry-After header respected on 429 responses
  - Descriptive User-Agent with contact info (required by policy)

Usage:
    python scripts/fix-images-wikipedia.py              # Fix all broken
    python scripts/fix-images-wikipedia.py --dry-run     # Preview only
    python scripts/fix-images-wikipedia.py --article slug # Single article
    python scripts/fix-images-wikipedia.py --force        # Re-process already-local images
    python scripts/fix-images-wikipedia.py --test N       # Process only first N articles

Requirements:
    pip install Pillow   (optional, for resizing)
"""

import argparse
import io
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# Optional: image resizing
try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

# Config
MAX_WIDTH = 1200
JPEG_QUALITY = 85
API_DELAY = 5.0       # Seconds between batched API calls (batching keeps total calls low)
DL_DELAY = 2.0        # Seconds between CDN thumbnail downloads (CDN handles high traffic)
MAX_RETRIES = 3       # Retries for 429 rate limit errors
USER_AGENT = 'HistoryNewsBot/1.0 (https://github.com/gleifhe/historynews; educational history site) python-urllib'

# SSL context
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

# Manual mapping: article slug -> exact Wikipedia article title
# Covers all 108 articles that need image fixes
SLUG_TO_WIKI = {
    'abolition-slavery-british-empire': 'Slavery Abolition Act 1833',
    'amazon-deforestation-drops': 'Deforestation of the Amazon rainforest',
    'antarctic-treaty': 'Antarctic Treaty System',
    'bald-eagle-recovery': 'Bald eagle',
    'battle-of-gettysburg': 'Battle of Gettysburg',
    'battle-of-yorktown': 'Siege of Yorktown',
    'birmingham-bloody-sunday': 'Selma to Montgomery marches',
    'birth-of-democracy-athens': 'Athenian democracy',
    'camp-david-accords': 'Camp David Accords',
    'child-mortality-halved': 'Child mortality',
    'christmas-truce-1914': 'Christmas truce',
    'clean-air-act': 'Clean Air Act (United States)',
    'clean-water-billions': 'Drinking water',
    'containerization-revolution': 'Containerization',
    'covid-vaccines-record-speed': 'COVID-19 vaccine',
    'crispr-gene-editing': 'CRISPR gene editing',
    'cuban-missile-crisis-13-days': 'Cuban Missile Crisis',
    'cuban-missile-crisis-kennedy-khrushchev': 'Cuban Missile Crisis',
    'cuban-missile-crisis-nuclear-brink': 'Cuban Missile Crisis',
    'desmond-doss-okinawa': 'Desmond Doss',
    'development-of-insulin': 'Insulin',
    'discovery-of-penicillin': 'Penicillin',
    'doctors-without-borders': 'Médecins Sans Frontières',
    'dolly-the-sheep-cloned': 'Cloning',
    'dunkirk-evacuation': 'Dunkirk evacuation',
    'earth-day-1970': 'Earth Day',
    'european-union-formation': 'European Union',
    'fair-trade-movement': 'Fair trade',
    'fall-of-roman-empire': 'Fall of the Western Roman Empire',
    'first-blood-transfusion': 'Blood transfusion',
    'first-email-sent': 'Email',
    'first-heart-transplant': 'Christiaan Barnard',
    'first-ivf-baby': 'In vitro fertilisation',
    'first-public-school-system': 'Horace Mann',
    'fort-sumter-to-appomattox': 'American Civil War',
    'geneva-conventions-1949': 'Geneva Conventions',
    'gi-bill-1944': 'G.I. Bill',
    'global-literacy-milestone': 'Literacy',
    'global-poverty-halved': 'Extreme poverty',
    'good-friday-agreement': 'Good Friday Agreement',
    'grameen-bank-microfinance': 'Grameen Bank',
    'great-barrier-reef-recovery': 'Great Barrier Reef',
    'green-revolution-borlaug': 'Green Revolution',
    'gutenberg-printing-press': 'Printing press',
    'habitat-for-humanity': 'Habitat for Humanity',
    'harriet-tubman-freedom': 'Harriet Tubman',
    'higgs-boson-discovery': 'Higgs boson',
    'hubble-space-telescope': 'Hubble Space Telescope',
    'human-genome-project': 'Human Genome Project',
    'india-milk-revolution': 'Operation Flood',
    'invention-of-world-wide-web': 'World Wide Web',
    'irena-sendler-warsaw': 'Irena Sendler',
    'james-webb-telescope': 'James Webb Space Telescope',
    'jenner-first-vaccine': 'Edward Jenner',
    'last-roman-emperor': 'Romulus Augustulus',
    'le-chambon-village-rescue': 'Le Chambon-sur-Lignon',
    'leonardo-da-vinci': 'Leonardo da Vinci',
    'lewis-clark-expedition': 'Lewis and Clark Expedition',
    'lexington-concord': 'Battles of Lexington and Concord',
    'liberation-of-auschwitz': 'Auschwitz concentration camp',
    'magellan-circumnavigation': 'Ferdinand Magellan',
    'malala-nobel-prize': 'Malala Yousafzai',
    'marie-curie-radioactivity': 'Marie Curie',
    'marriage-equality-obergefell': 'Same-sex marriage in the United States',
    'milgram-obedience-experiment': 'Milgram experiment',
    'montgomery-bus-boycott': 'Montgomery bus boycott',
    'montreal-protocol-ozone': 'Montreal Protocol',
    'national-parks-created': 'National Park Service',
    'new-zealand-womens-vote': "Women's suffrage in New Zealand",
    'nhs-founded-uk': 'National Health Service',
    'nicholas-winton-kindertransport': 'Nicholas Winton',
    'nuclear-test-ban-treaty': 'Partial Nuclear Test Ban Treaty',
    'open-source-movement': 'Open-source software movement',
    'oskar-schindler-list': 'Oskar Schindler',
    'paris-climate-agreement': 'Paris Agreement',
    'pasteurization-invented': 'Pasteurization',
    'peace-corps-established': 'Peace Corps',
    'pearl-harbor-attack': 'Attack on Pearl Harbor',
    'polio-vaccine-salk': 'Polio vaccine',
    'public-libraries-carnegie': 'Carnegie library',
    'reagan-tear-down-wall': 'Tear down this wall!',
    'renewable-energy-cheaper': 'Renewable energy',
    'rescue-of-apollo-13': 'Apollo 13',
    'rosalind-franklin-dna': 'Rosalind Franklin',
    'russian-revolution-bolsheviks': 'October Revolution',
    'russian-revolution-fall-of-tsar': 'February Revolution',
    'russian-revolution-red-terror': 'Red Terror',
    'rwanda-reconciliation': 'Rwandan genocide',
    'sack-of-rome-410': 'Sack of Rome (410)',
    'smallpox-eradication': 'Eradication of smallpox',
    'solar-impulse-flight': 'Solar Impulse',
    'special-olympics-founded': 'Special Olympics',
    'sully-hudson-river': 'US Airways Flight 1549',
    'thai-cave-rescue-2018': 'Tham Luang cave rescue',
    'the-holocaust': 'The Holocaust',
    'titanic-newspaper-coverage': 'Sinking of the Titanic',
    'transatlantic-telegraph-cable': 'Transatlantic telegraph cable',
    'underground-railroad': 'Underground Railroad',
    'universal-declaration-human-rights': 'Universal Declaration of Human Rights',
    'uss-arizona-memorial': 'USS Arizona Memorial',
    'valley-forge': 'Valley Forge',
    'voyager-interstellar-space': 'Voyager 1',
    'wikipedia-launched': 'Wikipedia',
    'wolves-yellowstone': 'History of wolves in Yellowstone',
    'y2k-bug': 'Year 2000 problem',
    'zimmermann-telegram': 'Zimmermann Telegram',
}


MANIFEST_FILE = 'scripts/image-manifest.json'


def get_root():
    return Path(__file__).parent.parent


def get_image_dir():
    img_dir = get_root() / 'static' / 'images' / 'articles'
    img_dir.mkdir(parents=True, exist_ok=True)
    return img_dir


def to_wikimedia_thumbnail(url, width=1200):
    """Convert a Wikimedia full-size URL to a thumbnail URL.
    
    Full:  https://upload.wikimedia.org/wikipedia/commons/f/fd/File.jpg
    Thumb: https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/File.jpg/1200px-File.jpg
    """
    if 'upload.wikimedia.org' not in url:
        return url
    if '/thumb/' in url:
        return url
    match = re.match(
        r'(https://upload\.wikimedia\.org/wikipedia/\w+/)([a-f0-9]/[a-f0-9]{2})/(.+)',
        url
    )
    if match:
        base, hash_path, filename = match.group(1), match.group(2), match.group(3)
        thumb_url = f'{base}thumb/{hash_path}/{filename}/{width}px-{filename}'
        if thumb_url.lower().endswith('.svg'):
            thumb_url += '.png'
        return thumb_url
    return url


def get_wiki_thumb_url(wiki_title, width=1200):
    """Get a thumbnail URL directly from the Wikipedia API.
    
    Uses pithumbsize which goes through Wikipedia's thumbnail servers,
    potentially different rate limits than upload.wikimedia.org direct.
    """
    data = wiki_api_request({
        'action': 'query',
        'titles': wiki_title,
        'prop': 'pageimages',
        'piprop': 'thumbnail',
        'pithumbsize': str(width),
        'redirects': '1',
    })
    if data and 'query' in data and 'pages' in data['query']:
        for page_id, page in data['query']['pages'].items():
            if page_id != '-1' and 'thumbnail' in page:
                return page['thumbnail']['source']
    return None


def wiki_api_request(params):
    """Make a request to the Wikipedia API.
    
    Follows Wikimedia API etiquette:
    - Uses maxlag to back off when servers are busy
    - Respects Retry-After header on 429 responses
    - Descriptive User-Agent header
    """
    base_url = 'https://en.wikipedia.org/w/api.php'
    params['format'] = 'json'
    params['maxlag'] = '5'  # Back off if server lag > 5s
    url = f'{base_url}?{urllib.parse.urlencode(params)}'
    
    for attempt in range(3):
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=15, context=CTX) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code == 503:
                # Respect Retry-After header (Wikimedia policy)
                retry_after = e.headers.get('Retry-After', '')
                try:
                    wait = int(retry_after)
                except (ValueError, TypeError):
                    wait = 10 * (attempt + 1)
                print(f' [HTTP {e.code}, Retry-After: {wait}s]', end='', flush=True)
                time.sleep(wait)
                continue
            print(f' [API HTTP {e.code}]', end='', flush=True)
            return None
        except Exception as e:
            if attempt < 2:
                time.sleep(5)
                continue
            print(f' [API error: {e}]', end='', flush=True)
            return None
    return None


def title_to_search_query(title):
    """Convert an article title to a Wikipedia search query.
    
    Strips sensational/editorial phrases and keeps the factual core.
    """
    # Remove common editorial suffixes/patterns
    title = re.sub(r':\s+.*$', '', title)  # Everything after colon
    title = re.sub(r'\s*—\s*.*$', '', title)  # Everything after em dash
    title = re.sub(r'\s*[-–]\s+(How|Why|What|When|The [A-Z]).*$', '', title)
    # Remove common sensational words
    for word in ['Shocking', 'Amazing', 'Incredible', 'Revolutionary',
                 'Dramatic', 'Record', 'Historic', 'Groundbreaking']:
        title = title.replace(word + ' ', '')
    return title.strip()


def find_wikipedia_images_batch(slug_title_pairs):
    """Find lead images for multiple topics in a single Wikipedia API call.
    
    The API supports up to 50 titles per request.
    Returns dict: {wiki_title: image_url}
    """
    results = {}
    
    # Build list of Wikipedia titles to query
    wiki_titles = []
    slug_to_wiki_title = {}
    for slug, title in slug_title_pairs:
        wiki_title = SLUG_TO_WIKI.get(slug, slug.replace('-', ' ').title())
        slug_to_wiki_title[slug] = wiki_title
        if wiki_title not in wiki_titles:
            wiki_titles.append(wiki_title)
    
    # Query in batches of 50, using pithumbsize for CDN thumbnail URLs
    for batch_start in range(0, len(wiki_titles), 50):
        batch = wiki_titles[batch_start:batch_start + 50]
        titles_param = '|'.join(batch)
        
        data = wiki_api_request({
            'action': 'query',
            'titles': titles_param,
            'prop': 'pageimages',
            'piprop': 'thumbnail|original',
            'pithumbsize': str(MAX_WIDTH),
            'redirects': '1',
        })
        
        if data and 'query' in data and 'pages' in data['query']:
            # Build redirect map
            redirect_map = {}
            for r in data['query'].get('redirects', []):
                redirect_map[r['from']] = r['to']
            for n in data['query'].get('normalized', []):
                redirect_map[n['from']] = n['to']
            
            for page_id, page in data['query']['pages'].items():
                if page_id != '-1':
                    # Prefer thumbnail URL (served from CDN, less likely to 429)
                    # Fall back to original if no thumbnail available
                    if 'thumbnail' in page:
                        results[page.get('title', '')] = page['thumbnail']['source']
                    elif 'original' in page:
                        results[page.get('title', '')] = page['original']['source']
        
        if batch_start + 50 < len(wiki_titles):
            time.sleep(API_DELAY)
    
    # Map back to slugs
    slug_results = {}
    for slug, title in slug_title_pairs:
        wiki_title = slug_to_wiki_title[slug]
        # Try exact match first
        if wiki_title in results:
            slug_results[slug] = (results[wiki_title], wiki_title)
        else:
            # Try case-insensitive / normalized match
            for found_title, url in results.items():
                if found_title.lower() == wiki_title.lower():
                    slug_results[slug] = (url, found_title)
                    break
    
    return slug_results


def download_image(url, local_path):
    """Download an image and optionally resize it. Returns (success, detail).
    
    Respects Retry-After header on 429 responses (Wikimedia policy).
    CDN thumbnail URLs (from pithumbsize) are already resized server-side.
    """
    for attempt in range(MAX_RETRIES + 1):
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=30, context=CTX) as resp:
                data = resp.read()
                
                if HAS_PILLOW:
                    try:
                        img = Image.open(io.BytesIO(data))
                        # Only resize if still larger than MAX_WIDTH
                        # (CDN thumbs should already be sized, but just in case)
                        if img.width > MAX_WIDTH:
                            ratio = MAX_WIDTH / img.width
                            new_size = (MAX_WIDTH, int(img.height * ratio))
                            img = img.resize(new_size, Image.LANCZOS)
                        if img.mode in ('RGBA', 'P', 'LA'):
                            img = img.convert('RGB')
                        img.save(str(local_path), 'JPEG', quality=JPEG_QUALITY, optimize=True)
                        size_kb = os.path.getsize(local_path) // 1024
                        return True, f'{img.width}x{img.height}, {size_kb}KB'
                    except Exception as e:
                        with open(local_path, 'wb') as f:
                            f.write(data)
                        size_kb = len(data) // 1024
                        return True, f'raw ({e}), {size_kb}KB'
                else:
                    with open(local_path, 'wb') as f:
                        f.write(data)
                    size_kb = len(data) // 1024
                    return True, f'{size_kb}KB (no Pillow)'
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < MAX_RETRIES:
                # Respect Retry-After header
                retry_after = e.headers.get('Retry-After', '')
                try:
                    wait = int(retry_after)
                except (ValueError, TypeError):
                    wait = 20 * (attempt + 1)
                print(f'429, Retry-After: {wait}s...', end=' ', flush=True)
                time.sleep(wait)
                continue
            return False, f'HTTP {e.code}'
        except Exception as e:
            return False, str(e)
    return False, 'Max retries exceeded'


def update_article_image(filepath, new_image_path, new_image_alt=None):
    """Update an article's image field to point to the local path."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace image URL (handles both http and already-local paths)
    content = re.sub(
        r'image:\s*"[^"]*"',
        f'image: "{new_image_path}"',
        content,
        count=1
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    parser = argparse.ArgumentParser(description='Fix article images using Wikipedia API')
    parser.add_argument('--dry-run', action='store_true', help='Preview without downloading')
    parser.add_argument('--article', type=str, help='Process single article by slug')
    parser.add_argument('--force', action='store_true', help='Re-process already-local images')
    parser.add_argument('--test', type=int, help='Process only first N articles')
    parser.add_argument('--find-only', action='store_true', help='Phase 1: Find URLs via API, save manifest (no downloads)')
    parser.add_argument('--download-only', action='store_true', help='Phase 2: Download from manifest with rate limiting')
    args = parser.parse_args()

    root = get_root()
    content_dir = root / 'content' / 'articles'
    image_dir = get_image_dir()
    manifest_path = root / MANIFEST_FILE

    # === PHASE 2: Download from manifest ===
    if args.download_only:
        if not manifest_path.exists():
            print(f'No manifest found at {manifest_path}. Run --find-only first.')
            return
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        pending = [e for e in manifest if not e.get('downloaded')]
        if not pending:
            print('All images in manifest already downloaded.')
            return
        
        print(f'Downloading {len(pending)} images (20s between each)...\n')
        downloaded = 0
        failed = []
        
        for i, entry in enumerate(pending, 1):
            slug = entry['slug']
            image_url = entry['image_url']
            wiki_title = entry['wiki_title']
            filepath = Path(entry['filepath'])
            
            local_path = image_dir / f'{slug}.jpg'
            hugo_path = f'/images/articles/{slug}.jpg'
            
            # Skip if already downloaded on disk
            if local_path.exists() and not args.force:
                entry['downloaded'] = True
                downloaded += 1
                print(f'  [{i}/{len(pending)}] {slug} — already on disk, skipping')
                continue
            
            print(f'  [{i}/{len(pending)}] {slug}', end='', flush=True)
            
            # Download — image_url is already a CDN thumbnail URL from pithumbsize
            success, detail = download_image(image_url, local_path)
            
            if success:
                downloaded += 1
                entry['downloaded'] = True
                print(f' — OK ({detail})')
                update_article_image(filepath, hugo_path)
            else:
                failed.append((slug, detail))
                print(f' — FAILED ({detail})')
            
            # Save manifest after each download (resume-safe)
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            
            if i < len(pending):
                time.sleep(DL_DELAY)
        
        print(f'\n{"="*55}')
        print(f'  DOWNLOAD SUMMARY')
        print(f'{"="*55}')
        print(f'  Downloaded:  {downloaded}')
        print(f'  Failed:      {len(failed)}')
        print(f'{"="*55}')
        if failed:
            print(f'\n  Failed:')
            for slug, reason in failed:
                print(f'    {slug}: {reason}')
        return

    # === PHASE 1 (or combined): Collect articles needing fixes ===
    articles = []
    for f in sorted(content_dir.iterdir()):
        if not f.name.endswith('.md') or f.name == '_index.md':
            continue
        if args.article and f.stem != args.article:
            continue

        with open(f, 'r', encoding='utf-8') as fh:
            content = fh.read()

        title_match = re.search(r'title:\s*"([^"]+)"', content)
        if not title_match:
            continue
        title = title_match.group(1)

        image_match = re.search(r'image:\s*"([^"]+)"', content)
        if not image_match:
            continue
        current_image = image_match.group(1)

        if not current_image.startswith('http') and not args.force:
            continue

        local_path = image_dir / f'{f.stem}.jpg'
        if local_path.exists() and not args.force:
            continue

        articles.append({
            'slug': f.stem,
            'filepath': f,
            'title': title,
            'current_image': current_image,
        })

    if args.test:
        articles = articles[:args.test]

    if not articles:
        print('No articles need image fixes.')
        return

    # === Find URLs via Wikipedia API (batched — up to 50 titles per request) ===
    print(f'Finding images for {len(articles)} articles via Wikipedia API...\n')

    slug_title_pairs = [(a['slug'], a['title']) for a in articles]
    slug_results = find_wikipedia_images_batch(slug_title_pairs)

    manifest = []
    not_found = []

    for article in articles:
        slug = article['slug']
        if slug in slug_results:
            image_url, wiki_title = slug_results[slug]
            print(f'  {slug} — "{wiki_title}"')
            manifest.append({
                'slug': slug,
                'filepath': str(article['filepath']),
                'title': article['title'],
                'wiki_title': wiki_title,
                'image_url': image_url,
                'downloaded': False,
            })
        else:
            not_found.append(slug)
            print(f'  {slug} — NO IMAGE FOUND')

    found = len(manifest)

    # Save manifest
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print(f'\n{"="*55}')
    print(f'  API LOOKUP SUMMARY')
    print(f'{"="*55}')
    print(f'  Found:       {found}')
    print(f'  Not found:   {len(not_found)}')
    print(f'  Manifest:    {manifest_path}')
    print(f'{"="*55}')

    if not_found:
        print(f'\n  No image found for:')
        for slug in not_found:
            print(f'    {slug}')

    if args.find_only:
        print(f'\n  Run with --download-only to download all {found} images.')
        return

    # === Combined mode: also download ===
    print(f'\n  Now downloading {found} images (20s between each)...\n')
    downloaded = 0
    failed = []

    for i, entry in enumerate(manifest, 1):
        slug = entry['slug']
        image_url = entry['image_url']
        filepath = Path(entry['filepath'])
        
        local_path = image_dir / f'{slug}.jpg'
        hugo_path = f'/images/articles/{slug}.jpg'
        
        print(f'  [{i}/{found}] {slug}', end='', flush=True)
        
        # image_url is already a CDN thumbnail URL from pithumbsize
        success, detail = download_image(image_url, local_path)
        
        if success:
            downloaded += 1
            entry['downloaded'] = True
            print(f' — OK ({detail})')
            update_article_image(filepath, hugo_path)
        else:
            failed.append((slug, detail))
            print(f' — FAILED ({detail})')
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        if i < found:
            time.sleep(DL_DELAY)

    print(f'\n{"="*55}')
    print(f'  DOWNLOAD SUMMARY')
    print(f'{"="*55}')
    print(f'  Downloaded:  {downloaded}')
    print(f'  Failed:      {len(failed)}')
    print(f'{"="*55}')
    if failed:
        print(f'\n  Failed:')
        for slug, reason in failed:
            print(f'    {slug}: {reason}')


if __name__ == '__main__':
    main()
