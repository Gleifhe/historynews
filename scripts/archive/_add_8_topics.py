"""One-off: Add 8 unique topics and generate articles + download images."""
import json
from pathlib import Path

root = Path(__file__).parent.parent
topics_path = root / 'scripts' / 'topics-100.json'
topics = json.loads(topics_path.read_text(encoding='utf-8'))
existing = {f.stem for f in (root / 'content' / 'articles').iterdir() if f.name.endswith('.md') and f.name != '_index.md'}
existing_slugs = {t['slug'] for t in topics}

extra = [
    {"slug": "mongol-siege-of-baghdad", "title": "The Mongol Siege of Baghdad", "headline": "CITY OF WISDOM DESTROYED: Mongol Horde Sacks Baghdad, Ending the Islamic Golden Age", "summary": "In February 1258, Mongol forces under Hulagu Khan sacked Baghdad, destroying the House of Wisdom and killing an estimated 200,000 to one million people, ending five centuries of Abbasid caliphate rule.", "historydate": "February 10, 1258", "era": "Medieval", "wiki": "Siege of Baghdad (1258)"},
    {"slug": "defenestration-of-prague", "title": "The Defenestration of Prague", "headline": "THROWN FROM THE WINDOW: Prague Incident Sparks Thirty Years of War Across Europe", "summary": "On May 23, 1618, Protestant nobles threw two Catholic imperial governors out of a window in Prague Castle, triggering the Thirty Years War that would kill eight million people across Europe.", "historydate": "May 23, 1618", "era": "17th Century", "wiki": "Defenestrations of Prague"},
    {"slug": "louisiana-purchase-negotiations", "title": "The Louisiana Purchase Negotiations", "headline": "CONTINENT FOR SALE: Napoleon Offers to Sell 828,000 Square Miles for Just $15 Million", "summary": "In April 1803, Napoleon unexpectedly offered to sell the entire Louisiana Territory to the United States, doubling the nation's size overnight for roughly four cents per acre.", "historydate": "April 30, 1803", "era": "18th Century", "wiki": "Louisiana Purchase"},
    {"slug": "invention-of-telephone-bell", "title": "Alexander Graham Bell and the Telephone", "headline": "MR. WATSON, COME HERE: Bell Transmits First Intelligible Speech by Wire", "summary": "On March 10, 1876, Alexander Graham Bell spoke the first words ever transmitted by telephone to his assistant Thomas Watson, launching a communications revolution that would connect the world.", "historydate": "March 10, 1876", "era": "Industrial Age", "wiki": "Telephone"},
    {"slug": "great-tokyo-earthquake-1923", "title": "The Great Kanto Earthquake", "headline": "TOKYO IN RUINS: Massive Earthquake and Firestorm Kill 140,000 in Japan's Worst Natural Disaster", "summary": "On September 1, 1923, a magnitude 7.9 earthquake struck the Kanto region of Japan, triggering firestorms that destroyed Tokyo and Yokohama, killing approximately 140,000 people.", "historydate": "September 1, 1923", "era": "Roaring Twenties", "wiki": "1923 Great Kantō earthquake"},
    {"slug": "suez-canal-nationalization", "title": "Nasser Nationalizes the Suez Canal", "headline": "CANAL SEIZED: Egypt's Nasser Takes Control of Suez, Defying Britain and France", "summary": "On July 26, 1956, Egyptian President Gamal Abdel Nasser nationalized the Suez Canal, provoking an international crisis that ended European colonial dominance in the Middle East.", "historydate": "July 26, 1956", "era": "Cold War", "wiki": "Suez Crisis"},
    {"slug": "nelson-mandela-inauguration", "title": "Nelson Mandela's Inauguration", "headline": "RAINBOW NATION: Mandela Sworn In as South Africa's First Black President Before 100,000 Jubilant Citizens", "summary": "On May 10, 1994, Nelson Mandela was inaugurated as South Africa's first Black president in Pretoria, marking the definitive end of apartheid before a crowd of 100,000 and dignitaries from 140 countries.", "historydate": "May 10, 1994", "era": "Peace & Cooperation", "wiki": "Inauguration of Nelson Mandela"},
    {"slug": "first-television-broadcast", "title": "The First Television Broadcast", "headline": "PICTURES THROUGH THE AIR: BBC Launches World's First Regular Television Service", "summary": "On November 2, 1936, the BBC launched the world's first regular high-definition television service from Alexandra Palace in London, beginning a medium that would transform culture, politics, and daily life.", "historydate": "November 2, 1936", "era": "Great Depression", "wiki": "History of television"},
]

# Verify no duplicates
for t in extra:
    if t['slug'] in existing or t['slug'] in existing_slugs:
        print(f"  DUPE: {t['slug']} — skipping")
    else:
        topics.append(t)
        print(f"  Added: {t['slug']}")

topics_path.write_text(json.dumps(topics, indent=2, ensure_ascii=False), encoding='utf-8')
print(f"\nTopics file now has {len(topics)} entries")
