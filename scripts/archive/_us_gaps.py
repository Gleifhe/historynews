# Analyze US history coverage gaps
import re
from pathlib import Path

articles_dir = Path(__file__).parent.parent / 'content' / 'articles'

articles = []
for f in sorted(articles_dir.iterdir()):
    if not f.name.endswith('.md') or f.name == '_index.md':
        continue
    content = f.read_text(encoding='utf-8')
    title_m = re.search(r'title:\s*"([^"]+)"', content)
    era_m = re.search(r'era:\s*"([^"]+)"', content)
    hd_m = re.search(r'historydate:\s*"([^"]+)"', content)
    if title_m:
        articles.append({
            'slug': f.stem,
            'title': title_m.group(1),
            'era': era_m.group(1) if era_m else '',
            'date': hd_m.group(1) if hd_m else '',
        })

us_keywords = [
    'america', 'united states', 'congress', 'president', 'constitution',
    'civil war', 'civil rights', 'revolutionary', 'independence',
    'lincoln', 'washington', 'jefferson', 'roosevelt', 'kennedy', 'nixon',
    'vietnam', 'pearl harbor', 'gettysburg', 'appomattox',
    'emancipation', 'suffrage', '19th amendment',
    'nasa', 'apollo', 'moon landing', 'space shuttle',
    'manhattan project', 'trinity', 'hiroshima',
    'boston', 'new york', 'california', 'texas',
    'alamo', 'gold rush', 'transcontinental',
    'pentagon', 'september 11', 'watergate',
    'pony express', 'lewis and clark', 'louisiana purchase',
    'ellis island', 'statue of liberty',
    'martin luther king', 'rosa parks', 'selma',
    'montgomery bus', 'brown v. board',
    'cuban missile', 'bay of pigs',
    'korean war', 'afghanistan war',
    'wright brothers', 'kitty hawk', 'lindbergh',
    'ford motor', 'apple computer',
    'wall street', 'new deal', 'dust bowl',
    'prohibition', 'alcatraz', 'fbi',
    'trail of tears', 'wounded knee',
    'mayflower', 'plymouth', 'jamestown',
    'alaska', 'hawaii',
    'supreme court', 'bill of rights',
    'juneteenth', 'challenger',
    'katrina', 'kent state', 'woodstock',
]

us_eras = ['Civil War', 'Civil Rights Era', '1960s America', '1970s America', 'Watergate Era']

us_set = set()
for a in articles:
    text = (a['title'] + ' ' + a['era'] + ' ' + a['slug']).lower()
    if any(kw in text for kw in us_keywords) or a['era'] in us_eras:
        us_set.add(a['slug'])

us_articles = [a for a in articles if a['slug'] in us_set]

print(f'Found {len(us_articles)} US-related articles out of {len(articles)} total\n')

periods = [
    ('Colonial (1607-1775)', 0, 1776),
    ('Revolution & Founding (1776-1800)', 1776, 1801),
    ('Early Republic & Expansion (1800-1860)', 1801, 1861),
    ('Civil War & Reconstruction (1861-1877)', 1861, 1878),
    ('Gilded Age & Progressive (1878-1916)', 1878, 1917),
    ('World War I (1917-1919)', 1917, 1920),
    ('Roaring 20s & Depression (1920-1940)', 1920, 1941),
    ('World War II (1941-1945)', 1941, 1946),
    ('Cold War & Civil Rights (1946-1968)', 1946, 1969),
    ('Vietnam to Reagan (1969-1989)', 1969, 1990),
    ('Modern Era (1990-present)', 1990, 2030),
]

for label, start, end in periods:
    group = []
    for a in us_articles:
        ym = re.search(r'(\d{4})', a['date'])
        if ym:
            y = int(ym.group(1))
            if start <= y < end:
                group.append(a['title'])
    print(f'{label}: {len(group)} articles')
    for t in sorted(group):
        print(f'  - {t}')
    print()
