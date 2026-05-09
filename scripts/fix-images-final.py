import json, urllib.request, ssl, time, re, os, sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Map: article_slug -> (wikimedia_file_title, alt, caption, credit)
# These are the EXACT Wikipedia/Wikimedia file page titles
IMAGE_MAP = {
    "berlin-wall-falls": ("Thefalloftheberlinwall1989.JPG", "Crowds at the Brandenburg Gate as the Berlin Wall falls, November 1989", "East and West Germans celebrate at the Brandenburg Gate after the fall of the Berlin Wall", "Wikimedia Commons / Public Domain"),
    "zimmermann-telegram": ("Zimmermann Telegram.jpg", "The decoded Zimmermann Telegram sent to Mexico", "The Zimmermann Telegram — the secret coded message that helped bring America into World War I", "National Archives / Wikimedia Commons"),
    "enigma-code-bletchley-park": ("Enigma (crittografia) - Museo scienza e tecnologia Milano.jpg", "An Enigma cipher machine used by Nazi Germany", "An Enigma cipher machine — the encryption device that Nazi Germany believed was unbreakable", "Wikimedia Commons / CC BY-SA"),
    "chernobyl-disaster": ("VOA Markosian - Chernobyl02.jpg", "Aerial view of the Chernobyl nuclear power plant", "The Chernobyl nuclear power plant in Ukraine, site of the 1986 disaster", "Voice of America / Wikimedia Commons"),
    "milgram-obedience-experiment": ("Milgram experiment v2.svg", "Diagram of the Milgram obedience experiment", "Diagram showing the setup of Milgram's famous obedience experiment", "Wikimedia Commons / CC BY-SA"),
    "stanford-prison-experiment": ("Philip Zimbardo.jpg", "Philip Zimbardo, psychologist who conducted the Stanford Prison Experiment", "Dr. Philip Zimbardo, designer of the Stanford Prison Experiment", "Wikimedia Commons / CC BY-SA"),
    "internet-on-911": ("WTC smoking on 9-11.jpeg", "The World Trade Center towers burning on September 11, 2001", "Smoke pours from the World Trade Center on September 11, 2001", "Wikimedia Commons / Public Domain"),
    "rosalind-franklin-dna": ("ADN animation.gif", "The double helix structure of DNA", "The double helix structure of DNA discovered with Rosalind Franklin's critical X-ray work", "Wikimedia Commons / Public Domain"),
    "hope-diamond": ("The Hope Diamond - SIA.jpg", "The Hope Diamond at the Smithsonian", "The Hope Diamond, a 45.52-carat deep blue diamond at the Smithsonian", "Smithsonian Institution Archives / Wikimedia Commons"),
    "bay-of-pigs-declassified": ("Bay of Pigs - Loss of B-26 aircraft.jpg", "Wreckage from the Bay of Pigs invasion, April 1961", "The aftermath of the failed Bay of Pigs invasion, April 1961", "CIA / Wikimedia Commons"),
    "reagan-tear-down-wall": ("Photograph of President Reagan giving a speech at the Berlin Wall, Brandenburg Gate, Federal Republic of Germany - NARA - 198585.jpg", "President Reagan delivers his Berlin Wall speech, June 12, 1987", "Reagan at the Brandenburg Gate: 'Mr. Gorbachev, tear down this wall!'", "NARA / Wikimedia Commons"),
    "y2k-bug": ("Bug de l'an 2000.jpg", "A Y2K bug warning display", "The Y2K bug — the global fear that computers would crash on January 1, 2000", "Wikimedia Commons / CC BY-SA"),
    "black-death-plague": ("Plague in an Ancient City LACMA AC1997.10.1 (1 of 2).jpg", "Painting depicting plague victims in a medieval city", "The Black Death devastated medieval Europe, killing one-third to one-half of the population", "LACMA / Wikimedia Commons"),
    "fall-of-saigon": ("UH-1 at DAO Compound.jpg", "Helicopter evacuation during the fall of Saigon, April 1975", "A UH-1 helicopter during the evacuation of Saigon, April 1975", "Wikimedia Commons / Public Domain"),
    "operation-paperclip": ("Wernher von Braun crop.jpg", "Wernher von Braun, recruited through Operation Paperclip", "Wernher von Braun — the German rocket scientist who became a key figure in NASA", "NASA / Wikimedia Commons"),
    "jack-the-ripper": ("Jack-the-Ripper-The-Nemesis-of-Neglect-Punch-London-Charivari-cartoon-poem-1888-09-29.jpg", "1888 Punch cartoon about Jack the Ripper", "The Nemesis of Neglect — an 1888 Punch cartoon about the Ripper murders", "Punch Magazine / Public Domain"),
    "haitian-revolution": ("Toussaint Louverture.jpg", "Portrait of Toussaint Louverture", "Toussaint Louverture — the leader of the Haitian Revolution", "Wikimedia Commons / Public Domain"),
    "spanish-armada": ("Invincible Armada.jpg", "Painting of the Spanish Armada battle, 1588", "The battle between the English fleet and the Spanish Armada, 1588", "Wikimedia Commons / Public Domain"),
    "bataan-death-march": ("Bataan Death March.jpg", "Prisoners during the Bataan Death March, 1942", "American and Filipino prisoners during the Bataan Death March", "NARA / Wikimedia Commons"),
    "dust-bowl": ("Dust Bowl - Dallas, South Dakota 1936.jpg", "A dust storm approaches Dallas, South Dakota, 1936", "A massive dust storm engulfs Dallas, South Dakota during the Dust Bowl", "NOAA / Wikimedia Commons"),
}

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

updated = 0
failed = 0

for slug, (wf, alt, cap, cred) in IMAGE_MAP.items():
    fp = f'content/articles/{slug}.md'
    if not os.path.exists(fp):
        print(f"SKIP {slug}")
        continue

    enc = urllib.request.quote(f"File:{wf}")
    api = f'https://en.wikipedia.org/w/api.php?action=query&titles={enc}&prop=imageinfo&iiprop=url&iiurlwidth=1024&format=json'
    req = urllib.request.Request(api, headers={'User-Agent': 'HistoryNewsBot/1.0 (educational history site)'})

    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            data = json.loads(resp.read())
            pages = data['query']['pages']
            for page_key, page in pages.items():
                if 'imageinfo' in page:
                    url = page['imageinfo'][0].get('thumburl') or page['imageinfo'][0].get('url')
                    if url:
                        with open(fp, 'r', encoding='utf-8') as f:
                            content = f.read()
                        content = re.sub(r'image: ".*?"', f'image: "{url}"', content)
                        content = re.sub(r'imagealt: ".*?"', f'imagealt: "{alt}"', content)
                        content = re.sub(r'imagecaption: ".*?"', f'imagecaption: "{cap}"', content)
                        content = re.sub(r'imagecredit: ".*?"', f'imagecredit: "{cred}"', content)
                        with open(fp, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f'OK   {slug}')
                        updated += 1
                    else:
                        print(f'NOURL {slug}')
                        failed += 1
                else:
                    print(f'MISS {slug} - file not found in Wikimedia')
                    failed += 1
    except Exception as e:
        print(f'FAIL {slug}: {e}')
        failed += 1

    time.sleep(6)

print(f"\nDone: {updated} updated, {failed} failed")
