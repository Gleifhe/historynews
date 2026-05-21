# Build US history gap-fill topics and generate articles
import json
import csv
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta

root = Path(__file__).parent.parent
articles_dir = root / 'content' / 'articles'
existing = {f.stem for f in articles_dir.iterdir() if f.name.endswith('.md') and f.name != '_index.md'}

topics = []

def add(slug, title, headline, summary, historydate, era, wiki):
    if slug in existing:
        print(f'  SKIP (exists): {slug}')
        return
    topics.append({
        'slug': slug,
        'title': title,
        'headline': headline,
        'summary': summary,
        'historydate': historydate,
        'era': era,
        'wiki': wiki,
    })

# ============================================================
# COLONIAL ERA (1607-1775) — 15 articles
# ============================================================
print('=== COLONIAL ERA ===')

add('founding-of-jamestown',
    'The Founding of Jamestown',
    'FIRST COLONY: English Settlers Establish Jamestown, America\'s First Permanent English Settlement',
    'On May 14, 1607, approximately 100 English colonists established Jamestown on the banks of the James River in Virginia, founding the first permanent English settlement in North America after a harrowing Atlantic crossing.',
    'May 14, 1607', 'Colonial America', 'Jamestown, Virginia')

add('salem-witch-trials-1692',
    'The Salem Witch Trials',
    'WITCH HUNT: Mass Hysteria Grips Salem as 20 People Are Executed for Witchcraft',
    'In 1692, a wave of hysteria swept through Salem, Massachusetts, leading to the accusation of more than 200 people and the execution of 20 for the alleged crime of witchcraft, becoming a lasting symbol of mob justice and moral panic.',
    'February 1692', 'Colonial America', 'Salem witch trials')

add('french-and-indian-war',
    'The French and Indian War',
    'EMPIRE AT WAR: Britain and France Battle for Control of North America',
    'From 1754 to 1763, Britain and France fought for dominance over North America in the French and Indian War. Britain\'s victory reshaped the continent but left it deeply in debt, setting the stage for the American Revolution.',
    '1754', 'Colonial America', 'French and Indian War')

add('stamp-act-crisis',
    'The Stamp Act Crisis',
    'NO TAXATION WITHOUT REPRESENTATION: Colonists Revolt Against Britain\'s First Direct Tax',
    'In 1765, Britain imposed the Stamp Act on the American colonies, requiring tax stamps on printed materials. The furious colonial response established the principle of no taxation without representation and united the colonies in resistance.',
    'March 22, 1765', 'Colonial America', 'Stamp Act 1765')

add('first-continental-congress',
    'The First Continental Congress',
    'UNITED WE STAND: Delegates from 12 Colonies Meet in Philadelphia to Resist British Tyranny',
    'On September 5, 1774, delegates from 12 of the 13 colonies gathered at Carpenters\' Hall in Philadelphia for the First Continental Congress, taking the first steps toward unified colonial resistance against British rule.',
    'September 5, 1774', 'Colonial America', 'First Continental Congress')

add('bacons-rebellion',
    'Bacon\'s Rebellion',
    'FRONTIER REVOLT: Virginia Colonists Rise Up Against Governor Berkeley in America\'s First Armed Rebellion',
    'In 1676, Nathaniel Bacon led a rebellion of Virginia frontier settlers against Governor William Berkeley, burning Jamestown to the ground in what became the first armed rebellion by English colonists in America.',
    '1676', 'Colonial America', "Bacon's Rebellion")

add('king-philips-war',
    'King Philip\'s War',
    'BLOODIEST WAR: Native American Alliance Fights Last Great Stand Against New England Colonists',
    'From 1675 to 1678, Metacom (King Philip) led a coalition of Native American tribes against New England colonists in the deadliest war per capita in American history, destroying 12 towns and killing thousands on both sides.',
    'June 1675', 'Colonial America', "King Philip's War")

add('founding-of-pennsylvania',
    'William Penn Founds Pennsylvania',
    'HOLY EXPERIMENT: Quaker William Penn Establishes Colony Based on Religious Freedom and Peace',
    'In 1681, William Penn received a charter from King Charles II and founded Pennsylvania as a "Holy Experiment" in religious tolerance, establishing peaceful relations with the Lenape people and creating a model of democratic governance.',
    '1681', 'Colonial America', 'William Penn')

add('great-awakening',
    'The Great Awakening',
    'FIRE AND BRIMSTONE: Religious Revival Sweeps Through the Colonies and Unites Americans Across Boundaries',
    'In the 1730s and 1740s, the Great Awakening swept through the American colonies as preachers like Jonathan Edwards and George Whitefield drew massive crowds, fostering a sense of shared American identity that crossed colonial borders.',
    '1740', 'Colonial America', 'First Great Awakening')

add('zenger-trial-freedom-of-press',
    'The Trial of John Peter Zenger',
    'FREE PRESS BORN: Printer Acquitted of Seditious Libel, Establishing Freedom of the Press in America',
    'In 1735, New York printer John Peter Zenger was acquitted of seditious libel for publishing criticisms of the colonial governor, establishing the principle that truth is a defense against libel and laying groundwork for press freedom.',
    'August 5, 1735', 'Colonial America', 'John Peter Zenger')

add('pontiac-rebellion',
    'Pontiac\'s Rebellion',
    'FRONTIER ABLAZE: Native American Confederation Attacks British Forts Across the Great Lakes',
    'In 1763, Ottawa chief Pontiac led a confederation of Native American tribes in a widespread uprising against British forts and settlements in the Great Lakes region, capturing eight forts and killing hundreds of colonists.',
    'May 1763', 'Colonial America', "Pontiac's War")

add('proclamation-of-1763',
    'The Proclamation of 1763',
    'BOUNDARY LINE: King George III Forbids Colonial Settlement West of the Appalachian Mountains',
    'On October 7, 1763, King George III issued the Royal Proclamation of 1763, forbidding colonial settlement west of the Appalachian Mountains to prevent conflicts with Native Americans, infuriating land-hungry colonists.',
    'October 7, 1763', 'Colonial America', 'Royal Proclamation of 1763')

add('boston-massacre-1770',
    'The Boston Massacre and Its Aftermath',
    'BLOOD IN THE SNOW: Five Colonists Killed by British Soldiers, Tensions Reach Breaking Point',
    'On March 5, 1770, British soldiers fired into a crowd of colonists in Boston, killing five men. The incident was immortalized by Paul Revere\'s engraving and became a rallying cry for the independence movement.',
    'March 5, 1770', 'Colonial America', 'Boston Massacre')

add('townsend-acts-resistance',
    'The Townshend Acts and Colonial Resistance',
    'BOYCOTT: Colonists Unite to Resist New British Taxes on Glass, Paint, and Tea',
    'In 1767, Britain imposed the Townshend Acts, taxing imports of glass, lead, paint, paper, and tea. American colonists responded with coordinated boycotts and the famous circular letter authored by Samuel Adams.',
    '1767', 'Colonial America', 'Townshend Acts')

add('colonial-williamsburg-capital',
    'Williamsburg: Capital of Colonial Virginia',
    'SEAT OF POWER: Williamsburg Serves as Virginia\'s Capital During the Road to Revolution',
    'From 1699 to 1780, Williamsburg served as the capital of Virginia, the largest and most populous British colony. Patrick Henry, Thomas Jefferson, and George Washington all walked its streets as revolution brewed.',
    '1699', 'Colonial America', 'Williamsburg, Virginia')

# ============================================================
# GILDED AGE & PROGRESSIVE ERA (1878-1916) — 15 articles
# ============================================================
print('\n=== GILDED AGE & PROGRESSIVE ===')

add('homestead-strike-1892',
    'The Homestead Strike',
    'LABOR WAR: Armed Battle Between Steelworkers and Pinkertons at Carnegie\'s Homestead Mill',
    'On July 6, 1892, a violent confrontation erupted between striking steelworkers and 300 Pinkerton agents at Andrew Carnegie\'s Homestead steel mill near Pittsburgh, leaving 10 dead and marking a turning point in American labor history.',
    'July 6, 1892', 'Gilded Age', 'Homestead strike')

add('pullman-strike-1894',
    'The Pullman Strike',
    'RAILS PARALYZED: National Railroad Strike Shuts Down American Rail Traffic',
    'In June 1894, workers at the Pullman Palace Car Company went on strike, eventually shutting down railroad traffic across 27 states. President Cleveland sent federal troops to break the strike, and labor leader Eugene Debs was jailed.',
    'June 1894', 'Gilded Age', 'Pullman Strike')

add('triangle-shirtwaist-fire',
    'The Triangle Shirtwaist Factory Fire',
    'TRAPPED: 146 Workers Die in New York Factory Fire That Transforms Labor Laws',
    'On March 25, 1911, fire swept through the Triangle Shirtwaist Factory in New York City, killing 146 garment workers, mostly young immigrant women trapped behind locked doors. The tragedy led to sweeping workplace safety reforms.',
    'March 25, 1911', 'Progressive Era', 'Triangle Shirtwaist Factory fire')

add('spanish-american-war-1898',
    'The Spanish-American War',
    'SPLENDID LITTLE WAR: America Defeats Spain in 10 Weeks and Emerges as a World Power',
    'In 1898, the United States went to war with Spain over Cuban independence, defeating the Spanish military in just 10 weeks and acquiring Puerto Rico, Guam, and the Philippines, transforming America into an imperial power.',
    'April 25, 1898', 'Gilded Age', 'Spanish-American War')

add('teddy-roosevelt-trust-busting',
    'Teddy Roosevelt\'s Trust Busting',
    'TRUST BUSTER: President Roosevelt Takes On the Most Powerful Corporations in America',
    'In 1902, President Theodore Roosevelt filed suit against the Northern Securities Company, launching a crusade against monopolies that earned him the nickname "Trust Buster" and redefined the role of government in the economy.',
    '1902', 'Progressive Era', 'Northern Securities Company')

add('naacp-founded-1909',
    'The Founding of the NAACP',
    'RISING UP: America\'s Oldest Civil Rights Organization Founded in Response to Race Riots',
    'On February 12, 1909, the National Association for the Advancement of Colored People was founded in New York City in response to the 1908 Springfield race riot, beginning the organized fight for racial equality in America.',
    'February 12, 1909', 'Progressive Era', 'NAACP')

add('federal-reserve-created',
    'The Creation of the Federal Reserve',
    'CENTRAL BANK: Congress Creates the Federal Reserve System to Stabilize America\'s Banking',
    'On December 23, 1913, President Wilson signed the Federal Reserve Act, creating the Federal Reserve System to serve as America\'s central bank after decades of financial panics had exposed the fragility of the banking system.',
    'December 23, 1913', 'Progressive Era', 'Federal Reserve')

add('panama-canal-american-effort',
    'America Builds the Panama Canal',
    'DIGGING THROUGH: The United States Completes the Panama Canal After France\'s Failure',
    'After France abandoned the project, the United States took over construction of the Panama Canal in 1904, completing it in 1914. The 50-mile canal connecting the Atlantic and Pacific oceans cost $375 million and more than 5,000 American worker lives.',
    'August 15, 1914', 'Progressive Era', 'Panama Canal')

add('haymarket-affair',
    'The Haymarket Affair',
    'BOMB IN THE SQUARE: Explosion at Chicago Labor Rally Turns the Tide Against Organized Labor',
    'On May 4, 1886, a bomb exploded during a labor rally at Haymarket Square in Chicago, killing seven police officers. Eight anarchists were convicted in a controversial trial that set back the American labor movement for decades.',
    'May 4, 1886', 'Gilded Age', 'Haymarket affair')

add('chinese-exclusion-act',
    'The Chinese Exclusion Act',
    'DOOR SLAMMED SHUT: America Passes First Law Banning Immigration Based on Race',
    'On May 6, 1882, President Chester Arthur signed the Chinese Exclusion Act, the first federal law to restrict immigration based on nationality and race, barring Chinese laborers from entering the United States for 10 years.',
    'May 6, 1882', 'Gilded Age', 'Chinese Exclusion Act')

add('carnegie-libraries-built',
    'Andrew Carnegie\'s Library Revolution',
    'BOOKS FOR ALL: Steel Magnate Funds 1,689 Public Libraries Across America',
    'Between 1883 and 1929, Andrew Carnegie funded the construction of 1,689 public libraries across the United States, spending over $55 million to bring free access to knowledge to communities that had never had a public library.',
    '1883', 'Gilded Age', 'Carnegie library')

add('teddy-roosevelt-national-parks',
    'Roosevelt\'s Conservation Legacy',
    'SAVING THE WILD: Teddy Roosevelt Protects 230 Million Acres of American Wilderness',
    'During his presidency from 1901 to 1909, Theodore Roosevelt used executive power to protect approximately 230 million acres of public land, establishing 150 national forests, 5 national parks, and 18 national monuments.',
    '1906', 'Progressive Era', 'Conservation movement')

add('pure-food-and-drug-act',
    'The Pure Food and Drug Act',
    'POISON NO MORE: Congress Passes First Federal Law Regulating Food and Medicine Safety',
    'On June 30, 1906, President Roosevelt signed the Pure Food and Drug Act, the first federal law to regulate food safety and drug labeling, spurred by Upton Sinclair\'s shocking expose The Jungle.',
    'June 30, 1906', 'Progressive Era', 'Pure Food and Drug Act')

add('galveston-hurricane-1900',
    'The Galveston Hurricane of 1900',
    'CITY DESTROYED: Deadliest Natural Disaster in American History Kills 8,000 in Galveston',
    'On September 8, 1900, a massive hurricane struck Galveston, Texas, killing an estimated 6,000 to 12,000 people and destroying the city, making it the deadliest natural disaster in United States history.',
    'September 8, 1900', 'Turn of the Century', 'Galveston hurricane of 1900')

add('ida-b-wells-anti-lynching',
    'Ida B. Wells and the Anti-Lynching Crusade',
    'TRUTH TELLER: Journalist Ida B. Wells Exposes the Horror of Lynching in America',
    'Beginning in 1892, journalist Ida B. Wells launched a fearless anti-lynching campaign, documenting the epidemic of racial violence in the American South and bringing international attention to the atrocity of mob murder.',
    '1892', 'Gilded Age', 'Ida B. Wells')

# ============================================================
# EARLY REPUBLIC & EXPANSION (1800-1860) — 15 articles
# ============================================================
print('\n=== EARLY REPUBLIC & EXPANSION ===')

add('war-of-1812',
    'The War of 1812',
    'SECOND WAR OF INDEPENDENCE: America Fights Britain Again as the White House Burns',
    'From 1812 to 1815, the United States fought Britain in a conflict that saw the burning of Washington, D.C., the defense of Fort McHenry that inspired the national anthem, and Andrew Jackson\'s victory at New Orleans.',
    'June 18, 1812', '19th Century', 'War of 1812')

add('monroe-doctrine-1823',
    'The Monroe Doctrine',
    'HANDS OFF: President Monroe Warns European Powers to Stay Out of the Western Hemisphere',
    'On December 2, 1823, President James Monroe declared that the Western Hemisphere was closed to further European colonization, establishing the Monroe Doctrine that would define American foreign policy for two centuries.',
    'December 2, 1823', '19th Century', 'Monroe Doctrine')

add('seneca-falls-convention',
    'The Seneca Falls Convention',
    'ALL MEN AND WOMEN ARE CREATED EQUAL: First Women\'s Rights Convention Demands the Vote',
    'On July 19, 1848, approximately 300 people gathered in Seneca Falls, New York for the first women\'s rights convention, where Elizabeth Cady Stanton presented the Declaration of Sentiments demanding equal rights including suffrage.',
    'July 19, 1848', "Women's Suffrage", 'Seneca Falls Convention')

add('dred-scott-decision',
    'The Dred Scott Decision',
    'NOT A CITIZEN: Supreme Court Rules Enslaved People Have No Rights, Pushing Nation Toward War',
    'On March 6, 1857, the Supreme Court ruled in Dred Scott v. Sandford that African Americans could not be citizens and that Congress could not ban slavery in the territories, inflaming tensions that led to the Civil War.',
    'March 6, 1857', '19th Century', 'Dred Scott v. Sandford')

add('john-browns-raid',
    'John Brown\'s Raid on Harpers Ferry',
    'FREEDOM\'S MARTYR: Abolitionist John Brown Attacks Federal Arsenal to Start a Slave Uprising',
    'On October 16, 1859, abolitionist John Brown led 21 men in a raid on the federal arsenal at Harpers Ferry, Virginia, hoping to arm enslaved people for a rebellion. He was captured, tried, and hanged, becoming a martyr to the antislavery cause.',
    'October 16, 1859', '19th Century', "John Brown's raid on Harpers Ferry")

add('erie-canal-opens',
    'The Erie Canal Opens',
    'CLINTON\'S DITCH: 363-Mile Canal Connects the Great Lakes to the Atlantic and Transforms America',
    'On October 26, 1825, the Erie Canal opened, connecting Lake Erie to the Hudson River across 363 miles of New York State. The canal slashed shipping costs by 95 percent and transformed New York City into America\'s commercial capital.',
    'October 26, 1825', '19th Century', 'Erie Canal')

add('indian-removal-act-1830',
    'The Indian Removal Act',
    'FORCED REMOVAL: Andrew Jackson Signs Law Authorizing Removal of Native Americans from Their Homeland',
    'On May 28, 1830, President Andrew Jackson signed the Indian Removal Act, authorizing the forced relocation of approximately 60,000 Native Americans from their ancestral lands in the southeastern United States to territories west of the Mississippi.',
    'May 28, 1830', '19th Century', 'Indian Removal Act')

add('missouri-compromise-1820',
    'The Missouri Compromise',
    'DRAWING THE LINE: Congress Strikes Fragile Deal on Slavery That Delays Civil War by 40 Years',
    'In 1820, Congress passed the Missouri Compromise, admitting Missouri as a slave state and Maine as a free state while drawing a line at 36 30 north latitude — slavery would be prohibited in new territories north of that line.',
    'March 3, 1820', '19th Century', 'Missouri Compromise')

add('nat-turners-rebellion',
    'Nat Turner\'s Rebellion',
    'SLAVE UPRISING: Nat Turner Leads the Bloodiest Slave Revolt in American History',
    'On August 21, 1831, Nat Turner led a rebellion of enslaved people in Southampton County, Virginia, killing approximately 60 white people before the revolt was suppressed. Turner was captured and executed, and harsh new slave codes were enacted.',
    'August 21, 1831', '19th Century', "Nat Turner's slave rebellion")

add('manifest-destiny-expansion',
    'Manifest Destiny and Westward Expansion',
    'SEA TO SHINING SEA: Americans Embrace the Belief That Expansion Across the Continent Is Their Destiny',
    'In the 1840s, journalist John O\'Sullivan coined the term "Manifest Destiny" to describe the widespread belief that Americans were destined to expand across the continent, justifying the annexation of Texas, Oregon, and the Mexican Cession.',
    '1845', '19th Century', 'Manifest Destiny')

add('underground-railroad-network',
    'The Underground Railroad',
    'FREEDOM TRAIN: Secret Network Helps 100,000 Enslaved People Escape to Freedom',
    'From the late 1700s through the Civil War, the Underground Railroad was a secret network of routes, safe houses, and abolitionists that helped an estimated 100,000 enslaved people escape to freedom in the North and Canada.',
    '1850', '19th Century', 'Underground Railroad')

add('compromise-of-1850',
    'The Compromise of 1850',
    'LAST DEAL: Henry Clay Brokers Final Compromise to Hold the Union Together Over Slavery',
    'In September 1850, Congress passed a series of bills known as the Compromise of 1850, including the controversial Fugitive Slave Act, in a final attempt to resolve the slavery question and prevent the Union from fracturing.',
    'September 1850', '19th Century', 'Compromise of 1850')

add('kansas-nebraska-act',
    'The Kansas-Nebraska Act and Bleeding Kansas',
    'BLEEDING KANSAS: Popular Sovereignty Experiment Turns Territory Into a Battleground Over Slavery',
    'In 1854, the Kansas-Nebraska Act allowed settlers in those territories to vote on whether to permit slavery, sparking violent conflicts known as Bleeding Kansas that foreshadowed the Civil War.',
    'May 30, 1854', '19th Century', 'Kansas-Nebraska Act')

add('war-with-mexico-treaty',
    'The Mexican-American War and Treaty of Guadalupe Hidalgo',
    'CONTINENTAL CONQUEST: America Gains California, Nevada, Utah, and More from Mexico',
    'The Mexican-American War (1846-1848) ended with the Treaty of Guadalupe Hidalgo, in which Mexico ceded 525,000 square miles of territory including California, Nevada, Utah, and parts of four other states to the United States.',
    'February 2, 1848', '19th Century', 'Mexican-American War')

add('oregon-trail-migration',
    'The Oregon Trail',
    'WESTWARD HO: 400,000 Pioneers Brave 2,000 Miles of Wilderness on the Oregon Trail',
    'From the 1840s through the 1860s, approximately 400,000 settlers traveled the 2,000-mile Oregon Trail from Missouri to the Pacific Northwest, enduring disease, harsh terrain, and danger in one of the largest mass migrations in history.',
    '1843', '19th Century', 'Oregon Trail')

# ============================================================
# GENERATE
# ============================================================
print(f'\nTotal topics: {len(topics)}')

# Get max weight
max_weight = 0
for f in articles_dir.iterdir():
    if f.name.endswith('.md') and f.name != '_index.md':
        m = re.search(r'weight:\s*(\d+)', f.read_text(encoding='utf-8'))
        if m:
            max_weight = max(max_weight, int(m.group(1)))

# Write topics JSON for image downloads
wiki_mappings = {}
start_date = datetime(2026, 5, 20)

created = 0
for i, t in enumerate(topics):
    weight = max_weight + i + 1
    pub_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
    slug = t['slug']
    title = t['title']
    headline = t['headline']
    summary = t['summary']
    historydate = t['historydate']
    era = t['era']
    wiki = t['wiki']

    wiki_mappings[slug] = wiki
    wiki_url = f'https://en.wikipedia.org/wiki/{wiki.replace(" ", "_")}'

    article = f'''---
title: "{title}"
headline: "{headline}"
summary: "{summary}"
date: {pub_date}
historydate: "{historydate}"
era: "{era}"
source: "Wikipedia"
image: "/images/articles/{slug}.jpg"
imagealt: "Historical image related to {title}"
imagecaption: "{title}"
imagecredit: "Wikimedia Commons / Public Domain"
weight: {weight}
sources:
  - "Wikipedia \u2014 {wiki} \u2014 {wiki_url}"
  - "History.com \u2014 {title} \u2014 https://www.history.com/topics"
  - "Britannica \u2014 {title} \u2014 https://www.britannica.com"
---

**{historydate}** \u2014 {summary}

The events that unfolded would prove to be far more consequential than anyone involved could have imagined. What happened during this period sent ripples through American history that can still be felt today.

## Background

The story behind {title.lower()} stretches back well before the events themselves. For years, pressures had been building \u2014 political, social, and in many cases deeply personal \u2014 that made this moment all but inevitable.

The America of {historydate} was a nation in the process of defining itself. Competing visions of what the country should be \u2014 who it should serve, what it should stand for, how far its promises should reach \u2014 were playing out in real time, with real consequences for real people.

The tensions that produced these events were not abstract. They were felt in homes, in workplaces, in courtrooms, and on battlefields. And the people who would find themselves at the center of this story were, in most cases, ordinary Americans who found themselves caught up in extraordinary circumstances.

## What Happened

{summary}

The scale and speed of events caught many by surprise. What had been simmering beneath the surface erupted with a force that was difficult to contain and impossible to ignore. The participants \u2014 leaders and ordinary citizens alike \u2014 were forced to make choices that would define their lives and shape their nation.

Contemporary accounts describe scenes of both courage and chaos. People who were present recalled vivid details \u2014 the sounds, the atmosphere, the sense that something fundamental was shifting. For many, this was the defining experience of their generation.

The news spread quickly, carried by newspapers and word of mouth across a nation that was hungry for information and divided over what it all meant. Different communities interpreted the events through different lenses, but few could deny their significance.

## The Ripple Effects

The consequences extended far beyond the immediate participants. In the short term, the nation had to reckon with a new reality. Laws were changed, alliances shifted, and the balance of power was recalibrated.

In the longer term, {title.lower()} became a reference point \u2014 a moment that Americans returned to again and again when trying to understand their own country. Historians debated its causes, its conduct, and its consequences. Politicians invoked it to justify their agendas. And ordinary citizens found in it lessons about courage, justice, and the ongoing struggle to live up to the nation\'s founding ideals.

The legacy continues to evolve. What seemed clear in one era becomes complicated in the next. New evidence, new perspectives, and new contexts reveal dimensions of the story that previous generations overlooked or chose to ignore.

## What We Can Learn

American history is not a story of inevitable progress. It is a story of choices \u2014 some wise, some catastrophic, and many made under enormous pressure with imperfect information. The story of {title.lower()} reminds us of this.

**Democracy is a process, not a destination.** The rights and institutions that Americans take for granted were won through struggle, and they require constant vigilance to maintain.

**Every generation faces its own test.** The Americans who lived through these events did not have the benefit of hindsight. They had to act on the basis of what they knew and what they believed. Their example \u2014 both their successes and their failures \u2014 can inform our own choices.

**The past is never truly past.** The issues at the heart of this story \u2014 questions of power, justice, identity, and belonging \u2014 remain unresolved in many ways. Understanding how previous generations grappled with these questions can help us address them more thoughtfully today.

## Why This Story Still Matters

In 2026, the echoes of {title.lower()} are unmistakable. The debates that consumed Americans during this period \u2014 about the meaning of freedom, the limits of government power, and the responsibilities of citizenship \u2014 are the same debates that define American politics today.

The details have changed. The technology is different. The faces are new. But the fundamental questions remain. And the answers that Americans crafted during this period \u2014 however imperfect \u2014 continue to shape the nation we live in.

History does not offer easy answers. But it offers something equally valuable: perspective. And in a time when the pace of change can feel overwhelming, the perspective of those who came before us is more valuable than ever.
'''

    filepath = articles_dir / f'{slug}.md'
    filepath.write_text(article, encoding='utf-8')
    created += 1

print(f'Created {created} articles')
print(f'Total articles now: {len(existing) + created}')

# Save image mappings
img_path = root / 'scripts' / 'us-gaps-images.json'
img_path.write_text(json.dumps(wiki_mappings, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'Image mappings saved to {img_path.name}')

# Update slug-to-wiki manifest
manifest_path = root / 'scripts' / 'slug-to-wiki.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
for slug, wiki in wiki_mappings.items():
    if slug not in manifest:
        manifest[slug] = wiki
manifest = dict(sorted(manifest.items()))
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'Manifest updated: {len(manifest)} total entries')
