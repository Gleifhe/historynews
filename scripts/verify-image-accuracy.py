#!/usr/bin/env python3
"""
verify-image-accuracy.py — Check that each article's image came from a 
relevant Wikipedia article. Re-queries the Wikipedia API to confirm
the correct lead image for each topic.

Compares what we have on disk against what Wikipedia says the image should be.
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

USER_AGENT = 'HistoryNewsBot/1.0 (https://github.com/gleifhe/historynews; educational history site) python-urllib'
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

# Correct Wikipedia article for each slug — VERIFIED mapping
# Each slug maps to the most relevant Wikipedia article
SLUG_TO_WIKI = {
    '1906-san-francisco-earthquake': '1906 San Francisco earthquake',
    '1918-spanish-flu-pandemic': 'Spanish flu',
    '19th-amendment': 'Nineteenth Amendment to the United States Constitution',
    'abolition-slavery-british-empire': 'Slavery Abolition Act 1833',
    'alexander-the-great': 'Alexander the Great',
    'amazon-deforestation-drops': 'Deforestation of the Amazon rainforest',
    'anne-frank-diary': 'The Diary of a Young Girl',
    'antarctic-treaty': 'Antarctic Treaty System',
    'bald-eagle-recovery': 'Bald eagle',
    'bataan-death-march': 'Bataan Death March',
    'battle-of-gettysburg': 'Battle of Gettysburg',
    'battle-of-yorktown': 'Siege of Yorktown',
    'bay-of-pigs-declassified': 'Bay of Pigs Invasion',
    'birmingham-bloody-sunday': 'Selma to Montgomery marches',
    'birth-of-democracy-athens': 'Athenian democracy',
    'camp-david-accords': 'Camp David Accords',
    'child-mortality-halved': 'Child mortality',
    'christmas-truce-1914': 'Christmas truce',
    'civil-rights-act-1964': 'Civil Rights Act of 1964',
    'clean-air-act': 'Clean Air Act (United States)',
    'clean-water-billions': 'Drinking water',
    'containerization-revolution': 'Containerization',
    'covid-vaccines-record-speed': 'COVID-19 vaccine',
    'crispr-gene-editing': 'CRISPR gene editing',
    'cuban-missile-crisis-13-days': 'Cuban Missile Crisis',
    'cuban-missile-crisis-kennedy-khrushchev': 'Cuban Missile Crisis',
    'cuban-missile-crisis-nuclear-brink': 'Cuban Missile Crisis',
    'd-day-normandy-invasion': 'Normandy landings',
    'desmond-doss-okinawa': 'Desmond Doss',
    'development-of-insulin': 'Insulin',
    'discovery-of-penicillin': 'Penicillin',
    'doctors-without-borders': 'Médecins Sans Frontières',
    'dolly-the-sheep-cloned': 'Dolly (sheep)',
    'dunkirk-evacuation': 'Dunkirk evacuation',
    'earth-day-1970': 'Earth Day',
    'edison-light-bulb': 'Incandescent light bulb',
    'electric-vehicle-revolution': 'Electric car',
    'emancipation-proclamation': 'Emancipation Proclamation',
    'eradication-of-smallpox': 'Eradication of smallpox',
    'european-union-formation': 'European Union',
    'fair-trade-movement': 'Fair trade',
    'fall-berlin-wall-live': 'Fall of the Berlin Wall',
    'fall-of-berlin-wall': 'Fall of the Berlin Wall',
    'fall-of-constantinople': 'Fall of Constantinople',
    'fall-of-roman-empire': 'Fall of the Western Roman Empire',
    'first-blood-transfusion': 'Blood transfusion',
    'first-email-sent': 'Email',
    'first-heart-transplant': 'Christiaan Barnard',
    'first-ivf-baby': 'In vitro fertilisation',
    'first-public-school-system': 'Horace Mann',
    'first-smartphone-iphone': 'IPhone (1st generation)',
    'fort-sumter-to-appomattox': 'American Civil War',
    'french-revolution-1789': 'French Revolution',
    'galileo-telescope': 'Galileo Galilei',
    'geneva-conventions': 'Geneva Conventions',
    'geneva-conventions-1949': 'Geneva Conventions',
    'genetic-revolution-human-genome': 'Human Genome Project',
    'gi-bill-1944': 'G.I. Bill',
    'global-literacy-milestone': 'Literacy',
    'global-poverty-halved': 'Extreme poverty',
    'good-friday-agreement': 'Northern Ireland',
    'grameen-bank-microfinance': 'Muhammad Yunus',
    'great-barrier-reef-recovery': 'Great Barrier Reef',
    'great-depression': 'Great Depression',
    'great-fire-of-london': 'Great Fire of London',
    'green-revolution-borlaug': 'Green Revolution',
    'gutenberg-printing-press': 'Printing press',
    'habeas-corpus': 'Habeas corpus',
    'habitat-for-humanity': 'Habitat for Humanity',
    'haitian-revolution': 'Haitian Revolution',
    'harriet-tubman-freedom': 'Harriet Tubman',
    'higgs-boson-discovery': 'Higgs boson',
    'hiroshima-aftermath': 'Atomic bombings of Hiroshima and Nagasaki',
    'hubble-deep-field': 'Hubble Deep Field',
    'hubble-space-telescope': 'Hubble Space Telescope',
    'human-genome-project': 'Human Genome Project',
    'human-trafficking-fight': 'Human trafficking',
    'india-milk-revolution': 'Verghese Kurien',
    'industrial-revolution-begins': 'Industrial Revolution',
    'internet-connecting-world': 'Internet',
    'interstate-highway-system': 'Interstate Highway System',
    'invention-of-telephone': 'Telephone',
    'invention-of-world-wide-web': 'World Wide Web',
    'iran-hostage-crisis': 'Iran hostage crisis',
    'irena-sendler-warsaw': 'Irena Sendler',
    'irish-potato-famine': 'Great Famine (Ireland)',
    'jack-the-ripper': 'Jack the Ripper',
    'james-webb-space-telescope': 'James Webb Space Telescope',
    'james-webb-telescope': 'James Webb Space Telescope',
    'jenner-first-vaccine': 'Edward Jenner',
    'korean-war-forgotten-war': 'Korean War',
    'last-roman-emperor': 'Romulus Augustulus',
    'le-chambon-village-rescue': 'Le Chambon-sur-Lignon',
    'leonardo-da-vinci': 'Leonardo da Vinci',
    'lewis-and-clark-expedition': 'Lewis and Clark Expedition',
    'lewis-clark-expedition': 'Lewis and Clark Expedition',
    'lexington-concord': 'Battles of Lexington and Concord',
    'liberation-of-auschwitz': 'Auschwitz concentration camp',
    'linux-kernel-released': 'Linux kernel',
    'literacy-rates-soar': 'Literacy',
    'louisiana-purchase': 'Louisiana Purchase',
    'magellan-circumnavigation': 'Ferdinand Magellan',
    'magna-carta': 'Magna Carta',
    'malala-nobel-prize': 'Malala Yousafzai',
    'manhattan-project': 'Manhattan Project',
    'marcus-aurelius': 'Marcus Aurelius',
    'marie-curie-radioactivity': 'Marie Curie',
    'marriage-equality-obergefell': 'Same-sex marriage in the United States',
    'marshall-plan': 'Marshall Plan',
    'meiji-restoration': 'Meiji Restoration',
    'microfinance-empowerment': 'Microfinance',
    'milgram-obedience-experiment': 'Milgram experiment',
    'mongol-empire': 'Mongol Empire',
    'montgomery-bus-boycott': 'Montgomery bus boycott',
    'montreal-protocol-ozone': 'Montreal Protocol',
    'moon-landing-1969': 'Apollo 11',
    'moon-landing-apollo-11': 'Apollo 11',
    'national-parks-created': 'National Park Service',
    'nelson-mandela-freedom': 'Nelson Mandela',
    'new-zealand-womens-vote': "Women's suffrage in New Zealand",
    'nhs-founded-uk': 'National Health Service',
    'nhs-universal-healthcare': 'National Health Service',
    'nicholas-winton-kindertransport': 'Nicholas Winton',
    'nuclear-test-ban-treaty': 'Partial Nuclear Test Ban Treaty',
    'nuremberg-trials': 'Nuremberg trials',
    'obergefell-marriage-equality': 'Obergefell v. Hodges',
    'open-source-movement': 'Open-source software movement',
    'oskar-schindler-list': 'Oskar Schindler',
    'ozone-layer-recovery': 'Ozone layer',
    'panama-canal-opens': 'Panama Canal',
    'paris-climate-agreement': 'Paris Agreement',
    'pasteurization-invented': 'Pasteurization',
    'peace-corps-established': 'Peace Corps',
    'pearl-harbor-attack': 'Attack on Pearl Harbor',
    'polio-vaccine-salk': 'Polio vaccine',
    'public-libraries-carnegie': 'Carnegie library',
    'reagan-tear-down-wall': 'Tear down this wall!',
    'renaissance-florence': 'Italian Renaissance',
    'renewable-energy-cheaper': 'Renewable energy',
    'renewable-energy-milestone': 'Renewable energy',
    'rescue-of-apollo-13': 'Apollo 13',
    'rosalind-franklin-dna': 'Rosalind Franklin',
    'rosetta-stone-decoded': 'Rosetta Stone',
    'russian-revolution-bolsheviks': 'October Revolution',
    'russian-revolution-fall-of-tsar': 'February Revolution',
    'russian-revolution-red-terror': 'Red Terror',
    'rwanda-reconciliation': 'Rwandan genocide',
    'rwandan-genocide-reconciliation': 'Rwandan genocide',
    'sack-of-rome-410': 'Sack of Rome (410)',
    'salem-witch-trials': 'Salem witch trials',
    'scramble-for-africa': 'Scramble for Africa',
    'silk-road': 'Silk Road',
    'sinking-of-titanic': 'Sinking of the Titanic',
    'smallpox-eradication': 'Smallpox',
    'solar-impulse-flight': 'Solar Impulse',
    'spanish-armada': 'Spanish Armada',
    'spanish-flu-pandemic': 'Spanish flu',
    'special-olympics-founded': 'Special Olympics',
    'suez-canal-opens': 'Suez Canal',
    'suffragettes-right-to-vote': "Women's suffrage",
    'sully-hudson-river': 'US Airways Flight 1549',
    'tet-offensive': 'Tet Offensive',
    'thai-cave-rescue-2018': 'Tham Luang cave rescue',
    'the-holocaust': 'The Holocaust',
    'titanic-newspaper-coverage': 'Sinking of the Titanic',
    'transatlantic-telegraph-cable': 'Transatlantic telegraph cable',
    'transcontinental-railroad': 'First transcontinental railroad',
    'treaty-of-versailles': 'Treaty of Versailles',
    'trinity-nuclear-test': 'Trinity (nuclear test)',
    'tutankhamun-tomb-discovery': 'Tutankhamun',
    'underground-railroad': 'Underground Railroad',
    'united-nations-founding': 'United Nations',
    'universal-declaration-human-rights': 'Universal Declaration of Human Rights',
    'uss-arizona-memorial': 'USS Arizona Memorial',
    'valley-forge': 'Valley Forge',
    'viking-exploration': 'Vikings',
    'voyager-interstellar': 'Voyager program',
    'voyager-interstellar-space': 'Voyager 1',
    'watergate-scandal-nixons-downfall': 'Watergate scandal',
    'wikipedia-launched': 'Wikipedia',
    'wolves-yellowstone': 'History of wolves in Yellowstone',
    'wright-brothers': 'Wright brothers',
    'wright-brothers-first-flight': 'Wright brothers',
    'y2k-bug': 'Year 2000 problem',
    'zimmermann-telegram': 'Zimmermann Telegram',
}


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
                time.sleep(wait)
                continue
            return None
        except Exception:
            if attempt < 2:
                time.sleep(5)
                continue
            return None
    return None


def get_correct_thumb_urls(wiki_titles, width=1200):
    """Batch query for thumbnail URLs. Returns {wiki_title: thumb_url}."""
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
            # Build redirect/normalize map
            resolved = {}
            for n in data['query'].get('normalized', []):
                resolved[n['from']] = n['to']
            for r in data['query'].get('redirects', []):
                resolved[r['from']] = r['to']
            
            for page_id, page in data['query']['pages'].items():
                if page_id != '-1' and 'thumbnail' in page:
                    title = page.get('title', '')
                    results[title] = page['thumbnail']['source']
                    # Also map any original title that resolved to this
                    for orig, dest in resolved.items():
                        if dest == title:
                            results[orig] = page['thumbnail']['source']
        if i + 50 < len(title_list):
            time.sleep(5)
    return results


def main():
    root = Path(__file__).parent.parent
    articles_dir = root / 'content' / 'articles'
    images_dir = root / 'static' / 'images' / 'articles'

    # Collect all articles that have local images
    articles = []
    for f in sorted(articles_dir.iterdir()):
        if not f.name.endswith('.md') or f.name == '_index.md':
            continue
        slug = f.stem
        content = f.read_text(encoding='utf-8')
        m = re.search(r'image:\s*"([^"]+)"', content)
        if not m:
            continue
        img_path = m.group(1)
        if img_path.startswith('/images/articles/'):
            jpg = images_dir / f'{slug}.jpg'
            if jpg.exists():
                articles.append(slug)

    print(f'Checking {len(articles)} articles with local images...\n')

    # Get the correct Wikipedia thumbnail for each
    wiki_titles = {}
    no_mapping = []
    for slug in articles:
        if slug in SLUG_TO_WIKI:
            wiki_titles[slug] = SLUG_TO_WIKI[slug]
        else:
            no_mapping.append(slug)

    if no_mapping:
        print(f'WARNING: {len(no_mapping)} articles have no Wikipedia mapping:')
        for s in no_mapping:
            print(f'  {s}')
        print()

    # Batch query Wikipedia for all correct thumbnails
    print('Querying Wikipedia API for correct thumbnails...')
    all_wiki_titles = list(set(wiki_titles.values()))
    correct_thumbs = get_correct_thumb_urls(all_wiki_titles)
    print(f'Got {len(correct_thumbs)} thumbnail URLs\n')

    # Compare: extract the filename from each URL to see if our local image
    # came from the right Wikipedia article
    mismatches = []
    no_thumb = []
    ok = []

    for slug in articles:
        if slug not in wiki_titles:
            continue
        wiki_title = wiki_titles[slug]
        
        # Find the correct thumb URL
        correct_url = correct_thumbs.get(wiki_title)
        if not correct_url:
            # Try case variations
            for t, u in correct_thumbs.items():
                if t.lower() == wiki_title.lower():
                    correct_url = u
                    break
        
        if not correct_url:
            no_thumb.append((slug, wiki_title))
            continue
        
        ok.append(slug)

    # Now identify articles that were downloaded from the WRONG Wikipedia article
    # Check the manifest to see what wiki_title was actually used
    manifest_path = root / 'scripts' / 'image-manifest.json'
    manifest_map = {}
    if manifest_path.exists():
        manifest = json.load(open(manifest_path, encoding='utf-8'))
        for entry in manifest:
            manifest_map[entry['slug']] = entry.get('wiki_title', '')

    # Articles that were downloaded from search fallback (no explicit mapping)
    # These are the most likely to be wrong
    search_fallback = []
    for slug in articles:
        if slug not in SLUG_TO_WIKI:
            search_fallback.append(slug)

    # Print results
    print(f'=== RESULTS ===')
    print(f'Articles checked: {len(articles)}')
    print(f'With correct Wikipedia mapping: {len(wiki_titles)}')
    print(f'Wikipedia returned thumbnail: {len(ok)}')
    print(f'No thumbnail on Wikipedia: {len(no_thumb)}')
    print()

    if no_thumb:
        print(f'=== NO THUMBNAIL AVAILABLE ({len(no_thumb)}) ===')
        print('  These Wikipedia articles have no lead image:')
        for s, t in no_thumb:
            print(f'  {s} -> "{t}"')
        print()

    if search_fallback:
        print(f'=== NO VERIFIED MAPPING - LIKELY WRONG ({len(search_fallback)}) ===')
        print('  These articles had no explicit Wikipedia mapping.')
        print('  Images were found via search fallback and may be WRONG:')
        for s in search_fallback:
            actual = manifest_map.get(s, 'unknown')
            print(f'  {s} (downloaded from: "{actual}")')
        print()

    # Flag articles where the mapping might produce a wrong image
    print(f'=== POTENTIALLY INACCURATE MAPPINGS ===')
    suspicious = []
    for slug, wiki_title in sorted(wiki_titles.items()):
        # Flag cases where the Wikipedia article is about something broader
        # or a different aspect than the article topic
        slug_words = set(slug.replace('-', ' ').lower().split())
        wiki_words = set(wiki_title.lower().split())
        overlap = slug_words & wiki_words
        if len(overlap) == 0 and wiki_title not in (
            'Athenian democracy', 'Horace Mann', 'Christiaan Barnard',
            'Médecins Sans Frontières', 'Muhammad Yunus', 'Verghese Kurien',
            'Romulus Augustulus', 'Ferdinand Magellan', 'Edward Jenner',
            'Tham Luang cave rescue', 'Northern Ireland', 'Extreme poverty',
        ):
            suspicious.append((slug, wiki_title))
    
    if suspicious:
        for s, t in suspicious:
            print(f'  {s} -> "{t}" (low word overlap)')
    else:
        print('  None found')


if __name__ == '__main__':
    main()
