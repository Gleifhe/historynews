import json, urllib.request, ssl, time, re, os

ctx = ssl.create_default_context()

IMAGE_MAP = {
    "berlin-wall-falls": ("West_and_East_Germans_at_the_Brandenburg_Gate_in_1989.jpg", "Crowds gather at the Brandenburg Gate as the Berlin Wall falls, November 1989", "East and West Germans celebrate at the Brandenburg Gate after the fall of the Berlin Wall", "Wikimedia Commons / Public Domain"),
    "zimmermann-telegram": ("Zimmermann_Telegram_as_Received_by_the_German_Ambassador_to_Mexico_-_NARA_-_302025.jpg", "The decoded Zimmermann Telegram", "The Zimmermann Telegram that helped draw America into World War I", "National Archives / Wikimedia Commons"),
    "enigma-code-bletchley-park": ("Enigma-plugboard.jpg", "The plugboard of a German Enigma cipher machine", "The plugboard of an Enigma machine", "Wikimedia Commons / Public Domain"),
    "chernobyl-disaster": ("Chernobyl_nuclear_power_plant.jpg", "The Chernobyl Nuclear Power Plant", "The Chernobyl Nuclear Power Plant in Ukraine", "Wikimedia Commons / Public Domain"),
    "milgram-obedience-experiment": ("Milgram_experiment_v2.svg", "Diagram of the Milgram obedience experiment", "Diagram showing the setup of Milgram's obedience experiment", "Wikimedia Commons / CC BY-SA"),
    "stanford-prison-experiment": ("Philip_Zimbardo.jpg", "Philip Zimbardo, psychologist who conducted the Stanford Prison Experiment", "Dr. Philip Zimbardo at Stanford University", "Wikimedia Commons / CC BY-SA"),
    "internet-on-911": ("WTC_smoking_on_9-11.jpeg", "The World Trade Center towers burning on September 11, 2001", "Smoke pours from the World Trade Center towers on September 11, 2001", "Wikimedia Commons / Public Domain"),
    "rosalind-franklin-dna": ("DNA_simple2.svg", "The double helix structure of DNA", "The double helix structure of DNA", "Wikimedia Commons / Public Domain"),
    "hope-diamond": ("Hope_Diamond.jpg", "The Hope Diamond at the Smithsonian", "The Hope Diamond on display at the Smithsonian National Museum of Natural History", "Wikimedia Commons / Public Domain"),
    "bay-of-pigs-declassified": ("Bay_of_Pigs_CIA_map.png", "CIA map of the Bay of Pigs invasion, April 1961", "CIA operational map of the Bay of Pigs invasion", "CIA / Wikimedia Commons"),
    "reagan-tear-down-wall": ("Photograph_of_President_Reagan_giving_a_speech_at_the_Berlin_Wall,_Brandenburg_Gate,_Federal_Republic_of_Germany_-_NARA_-_198585.jpg", "President Reagan at the Berlin Wall, June 12, 1987", "President Ronald Reagan delivers his famous speech at the Brandenburg Gate", "NARA / Wikimedia Commons"),
    "y2k-bug": ("Bug_de_l'an_2000.jpg", "A Y2K bug warning screen", "The Y2K bug - the fear that computers would crash at midnight on January 1, 2000", "Wikimedia Commons / CC BY-SA"),
    "black-death-plague": ("Plague_in_Ashod.jpg", "Painting depicting the plague", "The devastating effects of the plague on medieval European communities", "Wikimedia Commons / Public Domain"),
    "fall-of-saigon": ("Saigon-hubert-van-es.jpg", "Helicopter evacuation from a Saigon rooftop, April 1975", "The iconic photograph of the last helicopter evacuation from Saigon", "Hubert van Es / Wikimedia Commons"),
    "operation-paperclip": ("Wernher_von_Braun_1960.jpg", "Wernher von Braun, recruited through Operation Paperclip", "Wernher von Braun, the German rocket scientist who became a key figure in the American space program", "NASA / Wikimedia Commons"),
    "jack-the-ripper": ("Jack-the-Ripper-The-Nemesis-of-Neglect-Punch-London-Charivari-cartoon-poem-1888-09-29.jpg", "1888 Punch magazine cartoon about Jack the Ripper", "The Nemesis of Neglect - an 1888 Punch cartoon about the Ripper murders", "Punch Magazine / Public Domain"),
    "haitian-revolution": ("Toussaint_L'Ouverture.jpg", "Portrait of Toussaint Louverture, leader of the Haitian Revolution", "Toussaint Louverture, the former slave who led the Haitian Revolution", "Wikimedia Commons / Public Domain"),
    "spanish-armada": ("Invincible_Armada.jpg", "The Spanish Armada in the English Channel, 1588", "The battle between the English fleet and the Spanish Armada, 1588", "Wikimedia Commons / Public Domain"),
    "bataan-death-march": ("March_of_Death_from_Bataan_to_the_prison_camp_-_Wikimedia_2014.jpg", "Prisoners during the Bataan Death March, April 1942", "American and Filipino prisoners during the Bataan Death March", "U.S. National Archives / Wikimedia Commons"),
    "dust-bowl": ("Dust_Bowl_-_Dallas,_South_Dakota_1936.jpg", "A dust storm approaches Dallas, South Dakota, 1936", "A massive dust storm engulfs Dallas, South Dakota during the Dust Bowl, 1936", "NOAA / Wikimedia Commons"),
}

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

for slug, (wf, alt, cap, cred) in IMAGE_MAP.items():
    fp = f'content/articles/{slug}.md'
    if not os.path.exists(fp):
        print(f"SKIP {slug}")
        continue

    enc = urllib.request.quote(wf.replace(' ', '_'))
    api = f'https://en.wikipedia.org/w/api.php?action=query&titles=File:{enc}&prop=imageinfo&iiprop=url&iiurlwidth=1024&format=json'
    req = urllib.request.Request(api, headers={'User-Agent': 'HistoryNewsBot/1.0 (history site image updater)'})

    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            data = json.loads(resp.read())
            pages = data['query']['pages']
            for pid, p in pages.items():
                if pid != '-1' and 'imageinfo' in p:
                    url = p['imageinfo'][0].get('thumburl') or p['imageinfo'][0].get('url')
                    with open(fp, 'r', encoding='utf-8') as f:
                        content = f.read()
                    content = re.sub(r'image: ".*?"', f'image: "{url}"', content)
                    content = re.sub(r'imagealt: ".*?"', f'imagealt: "{alt}"', content)
                    content = re.sub(r'imagecaption: ".*?"', f'imagecaption: "{cap}"', content)
                    content = re.sub(r'imagecredit: ".*?"', f'imagecredit: "{cred}"', content)
                    with open(fp, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f'OK   {slug} -> {url[:80]}...')
                else:
                    print(f'MISS {slug}')
    except Exception as e:
        print(f'FAIL {slug}: {e}')

    time.sleep(5)

print("\nDone.")
