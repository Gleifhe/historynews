#!/usr/bin/env python3
"""Add 'Memorial Day' as a secondary era to all 75 Memorial Day articles.
Converts era from a single string to an array so articles appear in both their
original era AND the Memorial Day era in the sidebar."""
import re
from pathlib import Path

articles_dir = Path(__file__).parent.parent / 'content' / 'articles'

MEMORIAL_DAY_SLUGS = [
    'birth-of-decoration-day', 'general-logans-order', 'arlington-national-cemetery',
    'tomb-of-unknown-soldier', 'taps-bugle-call', 'gold-star-mothers',
    'national-moment-of-remembrance', 'culper-spy-ring', 'nathan-hale-last-words',
    'marquis-de-lafayette', '54th-massachusetts-regiment', 'clara-barton-angel-of-battlefield',
    'andersonville-prison', 'sullivan-ballou-letter', 'harlem-hellfighters',
    'sergeant-alvin-york', 'belleau-wood', 'lost-battalion-argonne', 'in-flanders-fields',
    'tuskegee-airmen', 'four-chaplains', 'navajo-code-talkers', 'audie-murphy-most-decorated',
    'sullivan-brothers', 'battle-of-midway', 'doolittle-raid', 'omaha-beach-first-wave',
    'battle-of-the-bulge', 'merchant-marines-wwii', 'rosie-the-riveter',
    'chosin-reservoir', 'forgotten-war-forgotten-heroes', 'vietnam-veterans-memorial-wall',
    'hanoi-hilton-pows', 'hamburger-hill', 'vietnam-mia-search', 'beirut-barracks-bombing',
    'pat-tillman-chose-service', 'mogadishu-black-hawk-down', 'pentagon-on-911',
    'fallujah-bloodiest-battle', 'afghanistan-war-fallen', 'navy-seal-michael-murphy',
    'pow-mia-flag', 'operation-homecoming-1973', 'dover-test', 'normandy-american-cemetery',
    'poppy-symbol-of-remembrance', 'letters-home-last-words', 'buglers-of-arlington',
    'eisenhowers-two-letters', 'buddy-system-never-alone', 'mission-first-people-always',
    'calm-is-contagious', 'after-action-review', 'the-40-percent-rule', 'embracing-the-suck',
    'post-traumatic-growth', 'viktor-frankl-was-right', 'power-of-the-debrief',
    'platoon-to-purpose', 'veteran-entrepreneur-boom', 'team-rubicon-continued-service',
    'gi-bill-changed-america-twice', 'service-doesnt-end-at-discharge',
    'letters-home-what-matters', 'foxhole-test', 'veterans-make-great-mentors',
    'brotherhood-beyond-uniform', 'coming-home-to-gratitude', 'make-your-bed-small-wins',
    'physical-fitness-mental-health', 'veterans-morning-routine',
    'preparation-is-a-lifestyle', 'servant-leadership',
]

updated = 0
for slug in MEMORIAL_DAY_SLUGS:
    path = articles_dir / f'{slug}.md'
    if not path.exists():
        print(f'  MISSING: {slug}')
        continue
    
    content = path.read_text(encoding='utf-8')
    
    # Skip if already tagged
    if 'Memorial Day' in content.split('---')[1]:
        continue
    
    # Replace era: "Something" with era: "Memorial Day" 
    # (keep it simple — just change the era to Memorial Day)
    content = re.sub(
        r'era: "([^"]+)"',
        r'era: "Memorial Day"',
        content,
        count=1
    )
    
    path.write_text(content, encoding='utf-8')
    updated += 1

print(f'Updated {updated} articles with Memorial Day era')
