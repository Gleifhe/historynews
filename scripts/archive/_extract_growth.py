# Extract personal growth themes from all articles
import re
from pathlib import Path
from collections import Counter

articles_dir = Path(__file__).parent.parent / 'content' / 'articles'

# Keywords that indicate personal growth lessons
THEME_KEYWORDS = {
    'courage': ['courage', 'brave', 'bravery', 'fearless', 'bold', 'daring', 'stand up', 'face your fears'],
    'persistence': ['persist', 'persever', 'never give up', 'keep going', 'endure', 'resilience', 'resilient', 'grit', 'determination', 'tenacity'],
    'leadership': ['leader', 'leadership', 'lead by example', 'inspire others', 'take charge', 'vision'],
    'integrity': ['integrity', 'honest', 'truth', 'principle', 'moral', 'ethical', 'stand for', 'conviction'],
    'adaptability': ['adapt', 'change', 'flexible', 'pivot', 'evolve', 'transform', 'reinvent'],
    'teamwork': ['team', 'together', 'cooperat', 'collaborat', 'unity', 'collective', 'allied', 'united'],
    'innovation': ['innovat', 'creative', 'invention', 'pioneer', 'breakthrough', 'new idea', 'think different'],
    'empathy': ['empathy', 'compassion', 'understand others', 'walk in', 'perspective', 'human dignity'],
    'justice': ['justice', 'equality', 'fairness', 'rights', 'freedom', 'liberty', 'oppression'],
    'learning': ['learn', 'education', 'knowledge', 'curiosity', 'discover', 'understand', 'wisdom'],
    'sacrifice': ['sacrifice', 'selfless', 'give up', 'serve others', 'greater good', 'duty'],
    'patience': ['patience', 'patient', 'long game', 'gradual', 'step by step', 'slow progress'],
    'accountability': ['accountab', 'responsib', 'own your', 'consequences', 'take ownership'],
    'communication': ['communicat', 'speak up', 'voice', 'express', 'listen', 'dialogue'],
    'preparation': ['prepar', 'ready', 'plan', 'training', 'practice', 'discipline'],
}

articles_with_growth = []
theme_counts = Counter()
theme_examples = {k: [] for k in THEME_KEYWORDS}

for f in sorted(articles_dir.iterdir()):
    if not f.name.endswith('.md') or f.name == '_index.md':
        continue
    content = f.read_text(encoding='utf-8')
    
    title_m = re.search(r'title:\s*"([^"]+)"', content)
    era_m = re.search(r'era:\s*"([^"]+)"', content)
    title = title_m.group(1) if title_m else f.stem
    era = era_m.group(1) if era_m else ''
    
    # Find growth-related sections
    body = content.split('---', 2)[2] if '---' in content else content
    
    # Look for growth/lesson sections
    growth_section = ''
    sections = re.split(r'\n##\s+', body)
    for section in sections:
        header = section.split('\n')[0].lower()
        if any(kw in header for kw in ['learn', 'growth', 'means for you', 'what this means', 'what we can']):
            growth_section = section
            break
    
    if not growth_section:
        continue
    
    # Extract bold lessons (** text **)
    bold_lessons = re.findall(r'\*\*([^*]+)\*\*', growth_section)
    
    # Classify themes
    found_themes = set()
    text_lower = growth_section.lower()
    for theme, keywords in THEME_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                found_themes.add(theme)
                break
    
    if found_themes or bold_lessons:
        articles_with_growth.append({
            'slug': f.stem,
            'title': title,
            'era': era,
            'themes': sorted(found_themes),
            'lessons': bold_lessons[:5],
        })
        for t in found_themes:
            theme_counts[t] += 1
            if len(theme_examples[t]) < 5:
                theme_examples[t].append((title, bold_lessons[0] if bold_lessons else ''))

print(f'Articles with growth content: {len(articles_with_growth)} / 757')
print(f'\n=== THEME FREQUENCY ===')
for theme, count in theme_counts.most_common():
    print(f'  {count:3d}  {theme}')

print(f'\n=== TOP LESSONS BY THEME ===')
for theme, count in theme_counts.most_common(10):
    print(f'\n  [{theme.upper()}] ({count} articles)')
    for title, lesson in theme_examples[theme]:
        if lesson:
            print(f'    "{lesson}" — {title}')
        else:
            print(f'    {title}')

print(f'\n=== SAMPLE BOLD LESSONS ===')
all_lessons = []
for a in articles_with_growth:
    for l in a['lessons']:
        if len(l) > 10 and len(l) < 100:
            all_lessons.append((l, a['title']))

for lesson, title in sorted(set(all_lessons))[:50]:
    print(f'  "{lesson}" — {title}')
