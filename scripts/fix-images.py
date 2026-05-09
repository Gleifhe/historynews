#!/usr/bin/env python3
"""
fix-images.py — Replace all mismatched images with verified LOC and Wikimedia URLs.

Uses the Wikimedia API and LOC search API to find topically relevant images,
then updates article front matter.

Usage:
    python scripts/fix-images.py
"""

import json
import os
import re
import time
import urllib.request
import urllib.error
import ssl

# Disable SSL verification for testing
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def wikimedia_image_url(filename):
    """Get a verified image URL from Wikimedia Commons via API."""
    encoded = urllib.request.quote(filename.replace(' ', '_'))
    api_url = f"https://en.wikipedia.org/w/api.php?action=query&titles=File:{encoded}&prop=imageinfo&iiprop=url&iiurlwidth=1024&format=json"
    req = urllib.request.Request(api_url, headers={'User-Agent': 'HistoryNews/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = json.loads(resp.read())
            pages = data['query']['pages']
            for page_id, page in pages.items():
                if page_id != '-1' and 'imageinfo' in page:
                    info = page['imageinfo'][0]
                    return info.get('thumburl') or info.get('url')
    except Exception as e:
        print(f"  Wikimedia API error for {filename}: {e}")
    return None


def verify_url(url):
    """Check if a URL returns 200."""
    req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'HistoryNews/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            return resp.status == 200
    except:
        # Try GET if HEAD fails
        try:
            req2 = urllib.request.Request(url, headers={'User-Agent': 'HistoryNews/1.0'})
            with urllib.request.urlopen(req2, timeout=10, context=ctx) as resp:
                return resp.status == 200
        except:
            return False


# Map of article slug -> (wikimedia_filename, alt_text, caption, credit)
IMAGE_MAP = {
    "berlin-wall-falls": (
        "West_and_East_Germans_at_the_Brandenburg_Gate_in_1989.jpg",
        "Crowds gather at the Brandenburg Gate as the Berlin Wall falls, November 1989",
        "East and West Germans celebrate at the Brandenburg Gate after the fall of the Berlin Wall",
        "Wikimedia Commons / Public Domain"
    ),
    "zimmermann-telegram": (
        "Zimmermann_Telegram_as_Received_by_the_German_Ambassador_to_Mexico_-_NARA_-_302025.jpg",
        "The decoded Zimmermann Telegram as received by the German Ambassador to Mexico",
        "The Zimmermann Telegram — the secret message that helped draw America into World War I",
        "National Archives / Wikimedia Commons"
    ),
    "enigma-code-bletchley-park": (
        "Enigma-plugboard.jpg",
        "The plugboard of a German Enigma cipher machine",
        "The plugboard of an Enigma machine — the device that Nazi Germany believed produced unbreakable codes",
        "Wikimedia Commons / Public Domain"
    ),
    "chernobyl-disaster": (
        "Chernobyl_Nuclear_Power_Plant.jpg",
        "The Chernobyl Nuclear Power Plant showing the damaged Reactor 4 sarcophagus",
        "The Chernobyl Nuclear Power Plant in Ukraine — site of the worst nuclear disaster in history",
        "Wikimedia Commons / Public Domain"
    ),
    "milgram-obedience-experiment": (
        "Milgram_experiment_v2.svg",
        "Diagram of the Milgram obedience experiment setup",
        "Diagram showing the setup of Stanley Milgram's obedience experiment at Yale University",
        "Wikimedia Commons / CC BY-SA"
    ),
    "stanford-prison-experiment": (
        "Philip_Zimbardo_at_his_home_office.jpg",
        "Philip Zimbardo, the psychologist who conducted the Stanford Prison Experiment",
        "Dr. Philip Zimbardo, who designed the Stanford Prison Experiment in 1971",
        "Wikimedia Commons / CC BY-SA"
    ),
    "internet-on-911": (
        "WTC_smoking_on_9-11.jpeg",
        "The World Trade Center towers burning on September 11, 2001",
        "Smoke pours from the World Trade Center towers on the morning of September 11, 2001",
        "Wikimedia Commons / Public Domain"
    ),
    "tiananmen-square-tank-man": (
        "Tianasquare.jpg",
        "Tiananmen Square in Beijing, China",
        "Tiananmen Square in Beijing — the site of the 1989 pro-democracy protests and the famous Tank Man standoff",
        "Wikimedia Commons / CC BY-SA"
    ),
    "challenger-disaster": (
        "Challenger_explosion.jpg",
        "The Space Shuttle Challenger explodes 73 seconds after launch, January 28, 1986",
        "The Space Shuttle Challenger breaks apart over the Atlantic Ocean, January 28, 1986",
        "NASA / Wikimedia Commons"
    ),
    "rosalind-franklin-dna": (
        "DNA_simple2.svg",
        "The double helix structure of DNA",
        "The double helix structure of DNA — the discovery that Rosalind Franklin's X-ray work made possible",
        "Wikimedia Commons / Public Domain"
    ),
    "hope-diamond": (
        "Hope_Diamond.jpg",
        "The Hope Diamond on display at the Smithsonian National Museum of Natural History",
        "The Hope Diamond — a 45.52-carat deep blue diamond with a legendary and supposedly cursed history",
        "Wikimedia Commons / Public Domain"
    ),
    "bay-of-pigs-declassified": (
        "President_Kennedy_and_his_advisors_during_the_Bay_of_Pigs_Invasion.png",
        "President Kennedy meets with advisors during the Bay of Pigs crisis, April 1961",
        "President John F. Kennedy confers with advisors during the Bay of Pigs invasion, April 1961",
        "CIA / Wikimedia Commons / Public Domain"
    ),
    "reagan-tear-down-wall": (
        "Photograph_of_President_Reagan_giving_a_speech_at_the_Berlin_Wall%2C_Brandenburg_Gate%2C_Federal_Republic_of_Germany_-_NARA_-_198585.jpg",
        "President Reagan delivers his famous speech at the Berlin Wall, June 12, 1987",
        "President Ronald Reagan speaks at the Brandenburg Gate, calling on Gorbachev to 'tear down this wall'",
        "NARA / Wikimedia Commons / Public Domain"
    ),
    "y2k-bug": (
        "Bug_de_l%27an_2000.jpg",
        "A Y2K bug warning screen showing the year 2000 date rollover problem",
        "The Y2K bug — the fear that computers worldwide would crash at midnight on January 1, 2000",
        "Wikimedia Commons / CC BY-SA"
    ),
    "black-death-plague": (
        "Doutielt_1.jpg",
        "Medieval illustration of plague victims being buried",
        "A medieval illustration depicting victims of the Black Death being buried — the plague killed one-third of Europe",
        "Wikimedia Commons / Public Domain"
    ),
    "fall-of-saigon": (
        "Saigon-hubert-van-es.jpg",
        "Evacuees climb a ladder to a helicopter on a Saigon rooftop, April 29, 1975",
        "The iconic photograph of the last helicopter evacuation from a Saigon rooftop as the city fell",
        "Hubert van Es / Wikimedia Commons"
    ),
    "operation-paperclip": (
        "Wernher_von_Braun_1960.jpg",
        "Wernher von Braun, the German rocket scientist recruited through Operation Paperclip",
        "Wernher von Braun — the former Nazi rocket scientist who became a key figure in America's space program",
        "NASA / Wikimedia Commons"
    ),
    "jack-the-ripper": (
        "Jack-the-Ripper-The-Nemesis-of-Neglect-Punch-London-Charivari-cartoon-poem-1888-09-29.jpg",
        "1888 Punch magazine cartoon about Jack the Ripper — The Nemesis of Neglect",
        "'The Nemesis of Neglect' — an 1888 Punch magazine cartoon commenting on the Jack the Ripper murders in Whitechapel",
        "Punch Magazine / Wikimedia Commons / Public Domain"
    ),
    "haitian-revolution": (
        "Toussaint_L%27Ouverture.jpg",
        "Portrait of Toussaint Louverture, leader of the Haitian Revolution",
        "Toussaint Louverture — the former slave who led the Haitian Revolution, the only successful slave revolt in history",
        "Wikimedia Commons / Public Domain"
    ),
    "spanish-armada": (
        "Invincible_Armada.jpg",
        "Painting of the Spanish Armada battle in the English Channel, 1588",
        "The battle between the English fleet and the Spanish Armada in the English Channel, 1588",
        "Wikimedia Commons / Public Domain"
    ),
    "bataan-death-march": (
        "March_of_Death_from_Bataan_to_the_prison_camp_-_Wikimedia_2014.jpg",
        "American and Filipino prisoners during the Bataan Death March, April 1942",
        "American and Filipino prisoners of war during the Bataan Death March, April 1942",
        "U.S. National Archives / Wikimedia Commons"
    ),
    "dust-bowl": (
        "Dust_Bowl_-_Dallas%2C_South_Dakota_1936.jpg",
        "A dust storm approaches the town of Dallas, South Dakota, 1936",
        "A massive dust storm engulfs the town of Dallas, South Dakota, during the Dust Bowl, 1936",
        "NOAA / Wikimedia Commons / Public Domain"
    ),
}


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    content_dir = os.path.join(root, 'content', 'articles')

    updated = 0
    failed = 0

    for slug, (wiki_file, alt, caption, credit) in IMAGE_MAP.items():
        filepath = os.path.join(content_dir, f'{slug}.md')
        if not os.path.exists(filepath):
            print(f"SKIP {slug} - file not found")
            continue

        print(f"Processing {slug}...")
        url = wikimedia_image_url(wiki_file)

        if not url:
            print(f"  FAIL - could not get URL from Wikimedia API")
            failed += 1
            continue

        if not verify_url(url):
            print(f"  FAIL - URL does not load: {url}")
            failed += 1
            continue

        # Read and update the file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        content = re.sub(r'image: ".*?"', f'image: "{url}"', content)
        content = re.sub(r'imagealt: ".*?"', f'imagealt: "{alt}"', content)
        content = re.sub(r'imagecaption: ".*?"', f'imagecaption: "{caption}"', content)
        content = re.sub(r'imagecredit: ".*?"', f'imagecredit: "{credit}"', content)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  OK - updated with {url[:80]}...")
        updated += 1
        time.sleep(0.5)  # Be polite to Wikimedia

    print(f"\nDone: {updated} updated, {failed} failed")


if __name__ == '__main__':
    main()
