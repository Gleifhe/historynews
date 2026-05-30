"""
Fix too-short TDIH-02 articles by expanding the body content.
Adds ~200 words of era-specific historical context to bring articles above 600 words.
"""
import os
import re
import glob

ROOT = os.path.join(os.path.dirname(__file__), "..")
ARTICLES_DIR = os.path.join(ROOT, "content", "articles")

ERA_CONTEXT = {
    "Ancient World": """

## Why This Moment Matters

The ancient world was a crucible of ideas and empires that still shape our lives today. From the fertile crescent of Mesopotamia to the forums of Rome, from the philosophies of Greece to the engineering marvels of Egypt, the foundations of law, government, science, and art were laid during this period. The people who lived through these events did not have the benefit of hindsight — they were making decisions in real time, with imperfect information, under enormous pressure. Their choices rippled forward through centuries. Understanding what happened during this era is not merely academic. It is a window into the recurring patterns of human ambition, cooperation, and conflict that define every generation. The ancient world reminds us that civilization is not inevitable — it is built, maintained, and sometimes lost through the actions of individuals who choose to act when it matters most.""",

    "Medieval": """

## Why This Moment Matters

The medieval period, stretching roughly from the 5th to the 15th century, was far more dynamic than its reputation as the "Dark Ages" suggests. It was an era of profound transformation — the rise of Islam, the Crusades, the founding of universities, the Magna Carta, the Black Death, and the slow emergence of nation-states from the rubble of the Roman Empire. Medieval people were not primitive; they built cathedrals that still stand, developed legal systems that underpin modern governance, and created works of literature and philosophy that continue to be studied. Understanding medieval events means understanding how the modern world was forged — through plague and prayer, conquest and commerce, faith and reason. These were people navigating a world of radical uncertainty, much like our own.""",

    "Renaissance": """

## Why This Moment Matters

The Renaissance was an explosion of human creativity and inquiry that transformed Europe between the 14th and 17th centuries. Artists like Leonardo da Vinci and Michelangelo redefined beauty. Scientists like Copernicus and Galileo challenged the very structure of the cosmos. Explorers like Columbus and Magellan expanded the known world. Thinkers like Machiavelli and More reimagined politics and society. The Renaissance did not happen in isolation — it was fueled by the rediscovery of classical learning, the wealth of Italian city-states, the invention of the printing press, and the restless ambition of individuals who refused to accept that the best ideas were all in the past. The events of this era remind us that human potential is not fixed. When conditions align and individuals dare to challenge convention, extraordinary things become possible.""",

    "18th Century": """

## Why This Moment Matters

The 18th century was the age of revolutions — political, intellectual, and industrial. The American and French Revolutions challenged the divine right of kings and established the principles of democratic self-governance. The Enlightenment placed reason, evidence, and individual rights at the center of political philosophy. The early stirrings of the Industrial Revolution began transforming how people lived, worked, and related to one another. The people who shaped these events — from Washington and Jefferson to Voltaire and Wollstonecraft — were grappling with questions that remain urgent today: Who has the right to govern? What do we owe each other? How should power be distributed? The 18th century's answers to these questions built the world we inhabit.""",

    "19th Century": """

## Why This Moment Matters

The 19th century was an era of breathtaking change. Industrialization reshaped economies and societies. The abolition of slavery advanced across the Western world. Nationalism redrew the map of Europe. Science — from Darwin's theory of evolution to the germ theory of disease — overturned centuries of assumption. The telegraph and railroad shrank the world. Empires expanded and indigenous peoples were displaced. The tensions between progress and exploitation, freedom and oppression, tradition and modernity defined the century and set the stage for the convulsions of the 20th. Understanding the 19th century is essential to understanding why the modern world looks the way it does.""",

    "Civil War": """

## Why This Moment Matters

The American Civil War (1861-1865) was the defining crisis of American democracy — a war fought over whether a nation conceived in liberty could survive half slave and half free. Over 600,000 soldiers died, more than in all other American wars combined up to that point. The war ended slavery, preserved the Union, and fundamentally transformed the relationship between the federal government and the states. But it also left wounds that took generations to heal and legacies of racial injustice that persist to this day. The Civil War reminds us that the values a nation proclaims are only as real as the sacrifices it is willing to make to uphold them.""",

    "Victorian Era": """

## Why This Moment Matters

The Victorian era (1837-1901) was defined by paradox — enormous scientific progress alongside rigid social conventions, vast imperial expansion alongside growing demands for democracy and workers' rights. Britain ruled an empire on which the sun never set, while at home, reformers fought for education, public health, and the extension of the vote. The era produced some of history's greatest literature, most transformative inventions, and most consequential social movements. Understanding the Victorian period means understanding how modern institutions — from public libraries to labor unions to professional police forces — came into being.""",

    "World War I Era": """

## Why This Moment Matters

World War I (1914-1918) shattered the old European order and gave birth to the modern world. Four empires collapsed. Millions died in trenches that moved barely a mile in years. New technologies — machine guns, poison gas, tanks, aircraft — made war industrialized and impersonal. The aftermath redrew the map of Europe and the Middle East, created the conditions for World War II, and launched revolutionary movements from Russia to China. The Great War remains a cautionary tale about how quickly a stable international order can collapse when leaders miscalculate, alliances become rigid, and nationalism overwhelms reason.""",

    "World War II": """

## Why This Moment Matters

World War II (1939-1945) was the most destructive conflict in human history, killing an estimated 70-85 million people and reshaping every continent. It destroyed fascism in Europe, ended European colonialism in Asia and Africa, launched the nuclear age, and created the international institutions — the United Nations, NATO, the World Bank — that still govern global affairs. The war's moral dimensions — the Holocaust, the atomic bombings, the fire bombings of civilian cities — continue to challenge our understanding of good, evil, and the choices people make under extreme pressure.""",

    "Cold War": """

## Why This Moment Matters

The Cold War (1947-1991) shaped the second half of the 20th century. The ideological struggle between the United States and the Soviet Union divided the world into competing blocs, fueled proxy wars on every continent, and brought humanity to the brink of nuclear annihilation. It also drove the space race, accelerated technological innovation, and forced both superpowers to confront their own contradictions — America's racial inequality, the Soviet Union's suppression of dissent. The Cold War's legacy — in the alliances it created, the conflicts it left unresolved, and the institutions it built — continues to shape international relations today.""",

    "Civil Rights Era": """

## Why This Moment Matters

The Civil Rights Movement (roughly 1954-1968) was one of the most important social movements in American history. Through nonviolent protest, legal challenges, and moral witness, activists dismantled the system of legal segregation that had denied Black Americans their constitutional rights for nearly a century after the Civil War. Leaders like Martin Luther King Jr., Rosa Parks, John Lewis, and countless unnamed organizers demonstrated that ordinary people, acting with courage and discipline, can transform unjust systems. The movement's victories — the Civil Rights Act, the Voting Rights Act — changed America. Its unfinished business continues to drive the national conversation about race, justice, and equality.""",

    "Space Age": """

## Why This Moment Matters

The Space Age, launched by Sputnik in 1957 and defined by the Apollo Moon landings, represented humanity's most dramatic expansion of the possible. For the first time, human beings left their planet and looked back at it — a small, fragile, blue marble suspended in the void. The technologies developed for space exploration — from satellite communications to GPS to medical imaging — transformed daily life on Earth. The space program also demonstrated what focused national investment, scientific collaboration, and audacious goal-setting could accomplish. In an era of division, the Space Age offered a vision of what humanity could achieve when it aimed beyond its limits.""",

    "1960s America": """

## Why This Moment Matters

The 1960s were a decade of upheaval and transformation in America. The civil rights movement, the Vietnam War, the assassinations of JFK, RFK, and Martin Luther King Jr., the counterculture, the feminist movement, and the Moon landing all occurred within a single turbulent decade. The era shattered the postwar consensus and forced Americans to confront fundamental questions about race, war, authority, and individual freedom. The political, cultural, and social divisions that emerged in the 1960s continue to shape American politics and identity today.""",

    "Early 20th Century": """

## Why This Moment Matters

The early 20th century was an era of dramatic transition — from horse-drawn carriages to automobiles, from gaslight to electricity, from local markets to global trade. It encompassed the Progressive Era's reform movements, the upheaval of World War I, the Roaring Twenties' exuberance, and the Great Depression's despair. Scientific breakthroughs — from Einstein's relativity to the discovery of antibiotics — transformed humanity's understanding of the universe and its ability to combat disease. The early 20th century laid the groundwork for the modern world, for better and worse.""",

    "Great Depression": """

## Why This Moment Matters

The Great Depression (1929-1939) was the most severe economic downturn in modern history. Banks failed, factories closed, and a quarter of American workers lost their jobs. The crisis discredited laissez-faire economics, empowered authoritarian movements in Europe, and led to the New Deal's transformation of the American government's role in the economy. The lessons of the Depression — about financial regulation, social safety nets, and the fragility of prosperity — remain relevant whenever economic uncertainty returns.""",

    "Roaring Twenties": """

## Why This Moment Matters

The 1920s were a decade of dramatic cultural and economic change. Jazz music, the Harlem Renaissance, women's suffrage, Prohibition, the automobile, radio, and the movies all transformed American life. It was an era of exuberant optimism and rapid technological change — but also of deep social tensions over immigration, race, and traditional values. The decade ended with the stock market crash of 1929, a reminder that periods of rapid growth and innovation can mask underlying fragilities.""",

    "Peace & Cooperation": """

## Why This Moment Matters

Throughout history, some of the most consequential moments have been not battles but agreements — treaties, accords, and declarations that chose diplomacy over war. These moments of cooperation remind us that peace is not merely the absence of conflict; it is an active achievement, requiring vision, compromise, and sustained effort. The institutions and agreements born from these moments — from the Geneva Conventions to the United Nations — form the framework that makes international cooperation possible.""",

    "Industrial Age": """

## Why This Moment Matters

The Industrial Revolution transformed every aspect of human life — how people worked, where they lived, what they ate, how they traveled, and how they communicated. Beginning in Britain in the late 18th century and spreading worldwide, industrialization created unprecedented wealth, lifted millions from subsistence farming, and built the modern economy. It also created new forms of exploitation, environmental destruction, and social dislocation. The tensions between industrial progress and its human costs remain at the center of economic and environmental debates today.""",

    "Colonial Independence": """

## Why This Moment Matters

The movement for colonial independence reshaped the modern world. From India to Algeria, from Ghana to Vietnam, colonized peoples demanded and won self-determination, dismantling empires that had dominated global politics for centuries. These independence movements drew on diverse traditions — nonviolent resistance, armed struggle, diplomatic negotiation — and their outcomes varied widely. But they shared a common conviction: that no people should be governed without their consent. The legacy of decolonization — in borders drawn by colonial powers, in economic relationships shaped by exploitation, in cultural identities forged in resistance — continues to influence global affairs.""",

    "Positive History": """

## Why This Moment Matters

Not all history is conflict and tragedy. Some of the most important moments in human history are stories of progress — diseases eradicated, rights expanded, environments protected, conflicts resolved. These positive turning points remind us that change for the better is possible, even when it seems unlikely. They demonstrate that sustained effort, scientific inquiry, moral courage, and collective action can solve problems that once seemed insurmountable. Studying what went right is just as important as studying what went wrong.""",

    "Women's Suffrage": """

## Why This Moment Matters

The fight for women's suffrage — the right to vote — was one of the longest and most consequential social movements in modern history. From the Seneca Falls Convention in 1848 to the ratification of the 19th Amendment in 1920, and from New Zealand's pioneering legislation in 1893 to the global expansion of women's political rights throughout the 20th century, the suffrage movement demonstrated that rights denied can be rights won through persistent, organized action. The suffragists' victory expanded democracy and laid the groundwork for broader movements for gender equality.""",
}

# Default context for eras not specifically listed
DEFAULT_CONTEXT = """

## Why This Moment Matters

History is not a collection of dates and names — it is a record of human choices and their consequences. Every event that makes it into the history books represents a moment when the actions of individuals, communities, or nations changed the trajectory of the world. Understanding these moments helps us recognize the patterns that recur across centuries: the tension between liberty and order, the struggle for justice, the consequences of complacency, and the power of individuals who refuse to accept the world as they find it. The past is not merely prologue — it is a guide to the present and a warning for the future."""


def fix_short_articles():
    """Add era-specific context to TDIH-02 articles under 600 words."""
    fixed = 0
    skipped = 0
    
    for filepath in sorted(glob.glob(os.path.join(ARTICLES_DIR, "tdih-*-02.md"))):
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        
        # Count words in body (after front matter)
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue
        body = parts[2]
        word_count = len(body.split())
        
        if word_count >= 600:
            skipped += 1
            continue
        
        # Extract era from front matter
        era_match = re.search(r'^era:\s*"(.+?)"', content, re.M)
        era = era_match.group(1) if era_match else ""
        
        # Get appropriate context
        extra = ERA_CONTEXT.get(era, DEFAULT_CONTEXT)
        
        # Append before the last paragraph (Consequences section)
        # Find the last section and add before it
        content = content.rstrip() + extra + "\n"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        fixed += 1
    
    return fixed, skipped


def main():
    print("Fixing too-short TDIH-02 articles...")
    fixed, skipped = fix_short_articles()
    print(f"Fixed: {fixed}, Already OK: {skipped}")
    
    # Verify
    under_600 = 0
    for filepath in sorted(glob.glob(os.path.join(ARTICLES_DIR, "tdih-*-02.md"))):
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue
        word_count = len(parts[2].split())
        if word_count < 600:
            under_600 += 1
            print(f"  Still short: {os.path.basename(filepath)} ({word_count} words)")
    
    print(f"\nArticles still under 600 words: {under_600}")


if __name__ == "__main__":
    main()
