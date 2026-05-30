"""Generate 100 additional This Day in History articles (tdih-MM-DD-02.md)."""
import os

CONTENT_DIR = os.path.join(os.path.dirname(__file__), "..", "content", "articles")

# 100 notable second events for various calendar days
# Format: (monthday, year, title, headline, summary, era, wiki_source)
EVENTS = [
    ("01-01", "1502", "Portuguese Explore Rio de Janeiro", "NEW WORLD HARBOR: Portuguese Explorers Sail Into Guanabara Bay", "On January 1, 1502, Portuguese explorers sailed into Guanabara Bay in present-day Brazil, naming it Rio de Janeiro — River of January — in one of the great misidentifications in exploration history.", "Renaissance", "Rio de Janeiro"),
    ("01-05", "1066", "Death of Edward the Confessor", "CROWN IN CRISIS: Edward the Confessor Dies, Setting the Stage for 1066", "On January 5, 1066, King Edward the Confessor of England died without a clear heir, triggering a succession crisis that would lead to the Norman Conquest.", "Medieval", "Edward the Confessor"),
    ("01-10", "1776", "Thomas Paine Publishes Common Sense", "WORDS LIKE FIRE: Anonymous Pamphlet Ignites a Revolution", "On January 10, 1776, Thomas Paine published Common Sense, a 47-page pamphlet that sold 500,000 copies and transformed a tax dispute into a revolution for independence.", "18th Century", "Common Sense (pamphlet)"),
    ("01-15", "1929", "Birth of Martin Luther King Jr.", "A DREAMER IS BORN: Martin Luther King Jr. Born in Atlanta, Georgia", "On January 15, 1929, Martin Luther King Jr. was born in Atlanta, Georgia. He would grow up to lead the American civil rights movement and become one of the most influential figures of the 20th century.", "Civil Rights Era", "Martin Luther King Jr."),
    ("01-20", "2009", "Barack Obama Inaugurated", "HISTORY MADE: Barack Obama Sworn In as First African American President", "On January 20, 2009, Barack Obama was sworn in as the 44th president of the United States, becoming the first African American to hold the nation's highest office.", "21st Century", "Inauguration of Barack Obama"),
    ("01-27", "1756", "Birth of Mozart", "PRODIGY BORN: Wolfgang Amadeus Mozart Born in Salzburg", "On January 27, 1756, Wolfgang Amadeus Mozart was born in Salzburg, Austria. By age five he was composing music; by his death at 35 he had created over 600 works that would define Western classical music.", "18th Century", "Wolfgang Amadeus Mozart"),
    ("02-01", "1790", "First Supreme Court Session", "ORDER IN THE COURT: U.S. Supreme Court Convenes for the First Time", "On February 1, 1790, the United States Supreme Court held its first session at the Royal Exchange Building in New York City, establishing the judicial branch of the new government.", "18th Century", "Supreme Court of the United States"),
    ("02-04", "1945", "Yalta Conference Opens", "THE BIG THREE MEET: Roosevelt, Churchill, and Stalin Divide the Postwar World", "On February 4, 1945, Roosevelt, Churchill, and Stalin began the Yalta Conference in Crimea, making decisions about postwar Europe that would shape the Cold War.", "World War II", "Yalta Conference"),
    ("02-07", "1812", "Birth of Charles Dickens", "A TALE OF TWO BIRTHS: Charles Dickens Born in Portsmouth, England", "On February 7, 1812, Charles Dickens was born in Portsmouth, England. His novels — Oliver Twist, A Christmas Carol, Great Expectations — would expose Victorian inequality and reshape English literature.", "Victorian Era", "Charles Dickens"),
    ("02-11", "1990", "Nelson Mandela Released from Prison", "FREE AT LAST: Mandela Walks Out of Victor Verster Prison After 27 Years", "On February 11, 1990, Nelson Mandela walked out of Victor Verster Prison after 27 years of imprisonment, beginning South Africa's transition from apartheid to democracy.", "Peace & Cooperation", "Nelson Mandela"),
    ("02-14", "1876", "Bell Files Telephone Patent", "CAN YOU HEAR ME NOW: Alexander Graham Bell Files Patent for the Telephone", "On February 14, 1876, Alexander Graham Bell filed a patent for the telephone — just hours before rival Elisha Gray filed his own design — in one of the closest patent races in history.", "Industrial Age", "Alexander Graham Bell"),
    ("02-17", "1600", "Giordano Bruno Burned at the Stake", "HERESY AND INFINITY: Philosopher Giordano Bruno Executed for Claiming Infinite Worlds", "On February 17, 1600, Giordano Bruno was burned at the stake in Rome for heresy after claiming the universe was infinite and contained countless worlds — ideas that science would later confirm.", "Renaissance", "Giordano Bruno"),
    ("02-20", "1962", "John Glenn Orbits Earth", "GODSPEED, JOHN GLENN: First American Astronaut Orbits the Earth Three Times", "On February 20, 1962, John Glenn became the first American to orbit the Earth, circling the planet three times in the Friendship 7 capsule during a flight that lasted nearly five hours.", "Space Age", "Mercury-Atlas 6"),
    ("02-22", "1732", "Birth of George Washington", "FATHER OF A NATION BORN: George Washington Born in Westmoreland County, Virginia", "On February 22, 1732, George Washington was born in Westmoreland County, Virginia. He would command the Continental Army, preside over the Constitutional Convention, and serve as the first president.", "18th Century", "George Washington"),
    ("02-28", "1953", "Watson and Crick Discover DNA Structure", "THE SECRET OF LIFE: Scientists Discover the Double Helix Structure of DNA", "On February 28, 1953, James Watson and Francis Crick determined the double-helix structure of DNA at Cambridge University, unlocking the molecular basis of heredity.", "Cold War", "Molecular structure of nucleic acids"),
    ("03-03", "1918", "Treaty of Brest-Litovsk", "RUSSIA SURRENDERS: Bolsheviks Sign Separate Peace with Germany, Exiting World War I", "On March 3, 1918, Soviet Russia signed the Treaty of Brest-Litovsk with the Central Powers, ending Russian participation in World War I at the cost of vast territories.", "World War I Era", "Treaty of Brest-Litovsk"),
    ("03-05", "1770", "Boston Massacre", "BLOOD ON THE SNOW: British Soldiers Fire on Boston Crowd, Killing Five", "On March 5, 1770, British soldiers fired into a crowd of colonists in Boston, killing five men. The Boston Massacre became a rallying point for colonial opposition to British rule.", "18th Century", "Boston Massacre"),
    ("03-08", "1917", "February Revolution Begins in Russia", "BREAD AND FREEDOM: Russian Workers March in Petrograd, Beginning the Revolution", "On March 8, 1917 (February 23 in the Russian calendar), women textile workers in Petrograd began a strike for bread that erupted into the February Revolution, toppling the Romanov dynasty.", "World War I Era", "February Revolution"),
    ("03-10", "1876", "Bell Makes First Phone Call", "MR. WATSON, COME HERE: Alexander Graham Bell Makes the First Successful Telephone Call", "On March 10, 1876, Alexander Graham Bell made the first successful telephone call, summoning his assistant Thomas Watson with the words that launched the telecommunications age.", "Industrial Age", "Alexander Graham Bell"),
    ("03-12", "1930", "Gandhi Begins Salt March", "A PINCH OF DEFIANCE: Gandhi Begins 240-Mile March to the Sea to Protest British Salt Tax", "On March 12, 1930, Mohandas Gandhi set out from his ashram with 78 followers on a 240-mile march to the sea to make salt in defiance of the British salt monopoly.", "Colonial Independence", "Salt March"),
    ("03-15", "1917", "Tsar Nicholas II Abdicates", "EMPIRE FALLS: Tsar Nicholas II Abdicates the Russian Throne After 304 Years of Romanov Rule", "On March 15, 1917, Tsar Nicholas II abdicated the Russian throne, ending 304 years of Romanov rule and setting the stage for the Bolshevik Revolution.", "World War I Era", "Nicholas II of Russia"),
    ("03-17", "461", "Death of Saint Patrick", "THE APOSTLE OF IRELAND: Saint Patrick Dies After Transforming a Pagan Island", "On March 17, 461 AD, Saint Patrick, the patron saint of Ireland, died. Captured by Irish raiders as a teenager and enslaved for six years, he returned as a missionary and converted the island to Christianity.", "Ancient World", "Saint Patrick"),
    ("03-20", "1852", "Uncle Tom's Cabin Published", "A BOOK THAT STARTED A WAR: Harriet Beecher Stowe Publishes Uncle Tom's Cabin", "On March 20, 1852, Harriet Beecher Stowe published Uncle Tom's Cabin, an anti-slavery novel that sold 300,000 copies in its first year and inflamed the national debate over slavery.", "19th Century", "Uncle Tom's Cabin"),
    ("03-22", "1765", "Stamp Act Passed", "TAXATION WITHOUT REPRESENTATION: British Parliament Passes the Stamp Act", "On March 22, 1765, the British Parliament passed the Stamp Act, imposing the first direct tax on the American colonies and igniting the protests that would lead to revolution.", "18th Century", "Stamp Act 1765"),
    ("03-25", "1807", "British Abolish Slave Trade", "CHAINS BROKEN: Parliament Votes to Abolish the Atlantic Slave Trade", "On March 25, 1807, the British Parliament passed the Slave Trade Act, abolishing the transatlantic slave trade throughout the British Empire after decades of campaigning by abolitionists.", "19th Century", "Slave Trade Act 1807"),
    ("03-28", "1979", "Three Mile Island Accident", "MELTDOWN: Partial Nuclear Meltdown at Three Mile Island Triggers Nationwide Panic", "On March 28, 1979, a partial nuclear meltdown occurred at Three Mile Island in Pennsylvania, becoming the most serious accident in U.S. commercial nuclear power history.", "Cold War", "Three Mile Island accident"),
    ("03-30", "1867", "United States Purchases Alaska", "SEWARD'S FOLLY: America Buys Alaska from Russia for Two Cents an Acre", "On March 30, 1867, Secretary of State William Seward agreed to purchase Alaska from Russia for $7.2 million — about two cents per acre — in a deal critics called Seward's Folly.", "19th Century", "Alaska Purchase"),
    ("04-02", "1917", "U.S. Enters World War I", "OVER THERE: President Wilson Asks Congress to Declare War on Germany", "On April 2, 1917, President Woodrow Wilson asked Congress to declare war on Germany, bringing the United States into World War I and transforming the global balance of power.", "World War I Era", "United States in World War I"),
    ("04-04", "1968", "Assassination of Martin Luther King Jr.", "DREAM SHATTERED: Martin Luther King Jr. Assassinated in Memphis", "On April 4, 1968, Martin Luther King Jr. was assassinated on the balcony of the Lorraine Motel in Memphis, Tennessee. His death triggered riots across America and galvanized the civil rights movement.", "Civil Rights Era", "Assassination of Martin Luther King Jr."),
    ("04-06", "1917", "U.S. Declares War on Germany", "THE YANKS ARE COMING: Congress Votes to Enter World War I", "On April 6, 1917, the United States Congress voted to declare war on Imperial Germany, bringing American military power into World War I.", "World War I Era", "United States declaration of war on Germany (1917)"),
    ("04-09", "1865", "Lee Surrenders at Appomattox", "THE WAR IS OVER: General Lee Surrenders to Grant at Appomattox Court House", "On April 9, 1865, Confederate General Robert E. Lee surrendered to Union General Ulysses S. Grant at Appomattox Court House, effectively ending the American Civil War.", "Civil War", "Battle of Appomattox Court House"),
    ("04-12", "1861", "Civil War Begins at Fort Sumter", "THE FIRST SHOTS: Confederate Batteries Open Fire on Fort Sumter", "On April 12, 1861, Confederate forces opened fire on Fort Sumter in Charleston Harbor, beginning the American Civil War that would last four years and cost over 600,000 lives.", "Civil War", "Battle of Fort Sumter"),
    ("04-14", "1912", "Titanic Hits Iceberg", "ICEBERG AHEAD: RMS Titanic Strikes Iceberg in the North Atlantic", "On April 14, 1912, the RMS Titanic, the largest ship afloat and considered unsinkable, struck an iceberg in the North Atlantic on her maiden voyage. She sank in less than three hours.", "Early 20th Century", "Sinking of the Titanic"),
    ("04-15", "1947", "Jackie Robinson Breaks Baseball's Color Barrier", "FIRST AT BAT: Jackie Robinson Takes the Field for the Brooklyn Dodgers", "On April 15, 1947, Jackie Robinson started at first base for the Brooklyn Dodgers, becoming the first African American to play in Major League Baseball in the modern era.", "Civil Rights Era", "Jackie Robinson"),
    ("04-18", "1906", "San Francisco Earthquake", "THE EARTH MOVED: Devastating Earthquake Strikes San Francisco at 5:12 AM", "On April 18, 1906, a massive earthquake struck San Francisco at 5:12 AM, followed by fires that burned for three days and destroyed over 80 percent of the city.", "Early 20th Century", "1906 San Francisco earthquake"),
    ("04-20", "1889", "Birth of Adolf Hitler", "DARK BEGINNING: Adolf Hitler Born in Braunau am Inn, Austria", "On April 20, 1889, Adolf Hitler was born in Braunau am Inn, Austria-Hungary. He would rise from failed artist to dictator, launching World War II and the Holocaust.", "Victorian Era", "Adolf Hitler"),
    ("04-22", "1970", "First Earth Day", "A PLANET IN PERIL: 20 Million Americans Participate in the First Earth Day", "On April 22, 1970, an estimated 20 million Americans took part in the first Earth Day, launching the modern environmental movement and leading to creation of the EPA.", "Cold War", "Earth Day"),
    ("04-25", "1859", "Suez Canal Construction Begins", "DIGGING BETWEEN CONTINENTS: Construction Begins on the Suez Canal", "On April 25, 1859, construction began on the Suez Canal in Egypt, a massive engineering project that would connect the Mediterranean and Red Seas and reshape global trade.", "Victorian Era", "Suez Canal"),
    ("04-28", "1789", "Mutiny on the Bounty", "CAST ADRIFT: Fletcher Christian Leads Mutiny Against Captain Bligh on HMS Bounty", "On April 28, 1789, Fletcher Christian led a mutiny against Captain William Bligh aboard HMS Bounty in the South Pacific, setting Bligh and 18 loyalists adrift in an open boat.", "18th Century", "Mutiny on the Bounty"),
    ("04-30", "1803", "Louisiana Purchase Signed", "DOUBLING A NATION: Napoleon Sells Louisiana Territory to the United States", "On April 30, 1803, the United States purchased the Louisiana Territory from France for $15 million, doubling the size of the nation in the largest land deal in history.", "19th Century", "Louisiana Purchase"),
    ("05-01", "1707", "Acts of Union Create Great Britain", "TWO KINGDOMS BECOME ONE: England and Scotland Unite to Form Great Britain", "On May 1, 1707, the Acts of Union took effect, merging the kingdoms of England and Scotland into a single nation — the Kingdom of Great Britain.", "18th Century", "Acts of Union 1707"),
    ("05-05", "1821", "Death of Napoleon", "THE EAGLE FALLS: Napoleon Bonaparte Dies in Exile on Saint Helena", "On May 5, 1821, Napoleon Bonaparte died in exile on the remote island of Saint Helena in the South Atlantic, ending the life of the man who had conquered most of Europe.", "19th Century", "Death of Napoleon"),
    ("05-07", "1945", "Germany Surrenders in World War II", "V-E DAY EVE: Germany Signs Unconditional Surrender at Reims", "On May 7, 1945, German General Alfred Jodl signed the unconditional surrender of all German forces at Allied headquarters in Reims, France, ending World War II in Europe.", "World War II", "German Instrument of Surrender"),
    ("05-10", "1869", "Transcontinental Railroad Completed", "GOLDEN SPIKE: East Meets West as Transcontinental Railroad Completed at Promontory Summit", "On May 10, 1869, the last spike — a golden one — was driven at Promontory Summit, Utah, completing the first transcontinental railroad and connecting America coast to coast.", "19th Century", "First transcontinental railroad"),
    ("05-12", "1820", "Birth of Florence Nightingale", "THE LADY WITH THE LAMP IS BORN: Florence Nightingale Born in Florence, Italy", "On May 12, 1820, Florence Nightingale was born in Florence, Italy. She would revolutionize nursing, pioneer the use of statistics in healthcare, and save thousands of lives during the Crimean War.", "Victorian Era", "Florence Nightingale"),
    ("05-14", "1948", "Israel Declares Independence", "A NATION REBORN: State of Israel Proclaimed in Tel Aviv", "On May 14, 1948, David Ben-Gurion proclaimed the establishment of the State of Israel, creating a Jewish homeland and igniting a conflict with neighboring Arab states that continues to this day.", "Cold War", "Israeli Declaration of Independence"),
    ("05-18", "1980", "Mount St. Helens Erupts", "THE MOUNTAIN EXPLODES: Mount St. Helens Erupts with Force of 500 Atomic Bombs", "On May 18, 1980, Mount St. Helens in Washington State erupted catastrophically, killing 57 people, flattening 230 square miles of forest, and sending an ash cloud around the globe.", "Cold War", "1980 eruption of Mount St. Helens"),
    ("05-20", "1927", "Lindbergh Crosses the Atlantic", "THE LONE EAGLE: Charles Lindbergh Takes Off for Paris in the Spirit of St. Louis", "On May 20, 1927, Charles Lindbergh departed Roosevelt Field in New York in the Spirit of St. Louis, beginning the first solo nonstop transatlantic flight.", "Roaring Twenties", "Charles Lindbergh"),
    ("05-24", "1844", "First Telegraph Message Sent", "WHAT HATH GOD WROUGHT: Samuel Morse Sends First Telegraph Message from Washington to Baltimore", "On May 24, 1844, Samuel Morse sent the first telegraph message — What hath God wrought — from the U.S. Capitol in Washington to Baltimore, launching the age of instant communication.", "19th Century", "Electrical telegraph"),
    ("05-26", "1896", "Dow Jones Industrial Average Debuts", "MEASURING THE MARKET: Charles Dow Publishes the First Dow Jones Industrial Average", "On May 26, 1896, Charles Dow published the first Dow Jones Industrial Average, tracking 12 industrial stocks. It would become the most widely followed stock market index in the world.", "Gilded Age", "Dow Jones Industrial Average"),
    ("05-29", "1453", "Fall of Constantinople", "THE END OF AN EMPIRE: Ottoman Forces Conquer Constantinople After a 53-Day Siege", "On May 29, 1453, Ottoman Sultan Mehmed II conquered Constantinople after a 53-day siege, ending the Byzantine Empire after 1,100 years and reshaping the political map of Europe and Asia.", "Medieval", "Fall of Constantinople"),
    ("05-31", "1859", "Big Ben Rings for the First Time", "BONG: The Great Bell of Westminster Rings for the First Time", "On May 31, 1859, the Great Bell of the clock tower at the Houses of Parliament — known universally as Big Ben — rang for the first time, becoming the most famous clock in the world.", "Victorian Era", "Big Ben"),
    ("06-02", "1953", "Coronation of Elizabeth II", "GOD SAVE THE QUEEN: Elizabeth II Crowned in Westminster Abbey Before Millions", "On June 2, 1953, Queen Elizabeth II was crowned at Westminster Abbey in the first coronation broadcast on television, watched by an estimated 27 million viewers in the UK alone.", "Cold War", "Coronation of Elizabeth II"),
    ("06-05", "1968", "Robert F. Kennedy Assassinated", "ANOTHER KENNEDY FALLS: Robert F. Kennedy Shot After California Primary Victory", "On June 5, 1968, Senator Robert F. Kennedy was shot at the Ambassador Hotel in Los Angeles moments after claiming victory in the California Democratic primary. He died the next day.", "1960s America", "Assassination of Robert F. Kennedy"),
    ("06-06", "1944", "D-Day Normandy Invasion", "THE LONGEST DAY: 156,000 Allied Troops Storm the Beaches of Normandy", "On June 6, 1944, the largest seaborne invasion in history began as 156,000 Allied troops landed on five beaches in Normandy, France, beginning the liberation of Western Europe.", "World War II", "Normandy landings"),
    ("06-10", "1935", "Alcoholics Anonymous Founded", "ONE DAY AT A TIME: Two Alcoholics Found a Movement That Will Save Millions", "On June 10, 1935, Dr. Bob Smith took his last drink, marking the founding date of Alcoholics Anonymous. The twelve-step program he and Bill Wilson created has helped millions worldwide.", "Great Depression", "Alcoholics Anonymous"),
    ("06-12", "1942", "Anne Frank Receives Her Diary", "DEAR KITTY: 13-Year-Old Anne Frank Receives a Red-Checked Diary for Her Birthday", "On June 12, 1942, Anne Frank received a red-and-white checked diary for her 13th birthday. She would fill it over the next two years while hiding from the Nazis, creating one of the most powerful documents of the Holocaust.", "World War II", "The Diary of a Young Girl"),
    ("06-15", "1215", "Magna Carta Sealed", "NO ONE IS ABOVE THE LAW: King John Seals the Magna Carta at Runnymede", "On June 15, 1215, King John of England sealed the Magna Carta at Runnymede, establishing for the first time that the king was subject to the rule of law.", "Medieval", "Magna Carta"),
    ("06-17", "1775", "Battle of Bunker Hill", "DON'T FIRE UNTIL YOU SEE THE WHITES OF THEIR EYES: Americans Hold Bunker Hill", "On June 17, 1775, colonial forces fought the Battle of Bunker Hill (actually fought on Breed's Hill) near Boston. Though the British captured the position, they suffered over 1,000 casualties.", "18th Century", "Battle of Bunker Hill"),
    ("06-18", "1815", "Battle of Waterloo", "NAPOLEON'S FINAL DEFEAT: Wellington and Blucher Crush Napoleon at Waterloo", "On June 18, 1815, the Duke of Wellington and Prussian General Blucher defeated Napoleon at the Battle of Waterloo in Belgium, ending the Napoleonic Wars and reshaping Europe.", "19th Century", "Battle of Waterloo"),
    ("06-20", "1837", "Queen Victoria Ascends the Throne", "A NEW ERA BEGINS: 18-Year-Old Victoria Becomes Queen of the United Kingdom", "On June 20, 1837, 18-year-old Princess Victoria became Queen of the United Kingdom upon the death of her uncle William IV. Her 63-year reign would give its name to an era.", "Victorian Era", "Queen Victoria"),
    ("06-22", "1941", "Operation Barbarossa Begins", "THE GREATEST INVASION: Hitler Launches Operation Barbarossa Against the Soviet Union", "On June 22, 1941, Nazi Germany launched Operation Barbarossa, invading the Soviet Union with over 3 million troops in the largest military operation in history.", "World War II", "Operation Barbarossa"),
    ("06-25", "1950", "Korean War Begins", "CROSSING THE 38TH PARALLEL: North Korea Invades the South, Starting the Korean War", "On June 25, 1950, North Korean forces crossed the 38th parallel and invaded South Korea, beginning a three-year war that would kill over 2.5 million people.", "Cold War", "Korean War"),
    ("06-28", "1914", "Assassination of Archduke Franz Ferdinand", "THE SHOT THAT STARTED A WAR: Archduke Franz Ferdinand Assassinated in Sarajevo", "On June 28, 1914, Archduke Franz Ferdinand of Austria-Hungary was assassinated in Sarajevo by Gavrilo Princip, setting off the chain of events that led to World War I.", "Pre-World War I", "Assassination of Archduke Franz Ferdinand"),
    ("06-30", "1908", "Tunguska Event", "THE SKY EXPLODES: Mysterious Blast Flattens 800 Square Miles of Siberian Forest", "On June 30, 1908, a massive explosion near the Tunguska River in Siberia flattened 800 square miles of forest. The blast — likely caused by an asteroid or comet — remains the largest impact event in recorded history.", "Early 20th Century", "Tunguska event"),
    ("07-01", "1867", "Canadian Confederation", "DOMINION DAY: British North America Act Creates the Dominion of Canada", "On July 1, 1867, the British North America Act took effect, uniting the provinces of Ontario, Quebec, Nova Scotia, and New Brunswick into the Dominion of Canada.", "Victorian Era", "Canadian Confederation"),
    ("07-03", "1863", "Pickett's Charge at Gettysburg", "THE HIGH WATER MARK: 12,500 Confederate Soldiers Charge Across Open Ground at Gettysburg", "On July 3, 1863, approximately 12,500 Confederate soldiers under General George Pickett charged across three-quarters of a mile of open ground at the Battle of Gettysburg. The assault failed catastrophically.", "Civil War", "Pickett's Charge"),
    ("07-05", "1687", "Newton Publishes Principia", "THE UNIVERSE EXPLAINED: Isaac Newton Publishes the Principia Mathematica", "On July 5, 1687, Isaac Newton published Principia Mathematica, laying out the laws of motion and universal gravitation that would govern physics for over two centuries.", "17th Century", "Philosophiæ Naturalis Principia Mathematica"),
    ("07-07", "1937", "Second Sino-Japanese War Begins", "BRIDGE INCIDENT: Fighting at Marco Polo Bridge Triggers Full-Scale War Between China and Japan", "On July 7, 1937, a skirmish at the Marco Polo Bridge near Beijing escalated into the Second Sino-Japanese War, a conflict that merged into World War II and killed millions.", "World War II", "Second Sino-Japanese War"),
    ("07-10", "1925", "Scopes Trial Begins", "MONKEY TRIAL: Tennessee Teacher Tried for Teaching Evolution", "On July 10, 1925, the trial of John Scopes began in Dayton, Tennessee. Scopes was charged with teaching evolution in violation of state law, setting up a clash between science and religion.", "Roaring Twenties", "Scopes Trial"),
    ("07-14", "1789", "Storming of the Bastille", "REVOLUTION: Parisian Mob Storms the Bastille Fortress, Igniting the French Revolution", "On July 14, 1789, a Parisian mob stormed the Bastille, a medieval fortress and political prison, in an act of defiance that became the defining moment of the French Revolution.", "18th Century", "Storming of the Bastille"),
    ("07-16", "1945", "Trinity Nuclear Test", "THE ATOMIC AGE BEGINS: First Nuclear Weapon Detonated in New Mexico Desert", "On July 16, 1945, the United States detonated the first nuclear weapon at the Trinity test site in New Mexico. J. Robert Oppenheimer reportedly quoted the Bhagavad Gita: Now I am become Death, the destroyer of worlds.", "World War II", "Trinity (nuclear test)"),
    ("07-20", "1969", "Apollo 11 Moon Landing", "THE EAGLE HAS LANDED: Armstrong and Aldrin Walk on the Moon", "On July 20, 1969, Apollo 11 astronauts Neil Armstrong and Buzz Aldrin became the first humans to walk on the Moon, fulfilling President Kennedy's challenge and captivating 600 million television viewers.", "Space Age", "Apollo 11"),
    ("07-22", "1934", "FBI Kills John Dillinger", "PUBLIC ENEMY DOWN: FBI Agents Shoot John Dillinger Outside a Chicago Theater", "On July 22, 1934, FBI agents shot and killed bank robber John Dillinger outside the Biograph Theater in Chicago, ending the crime spree of America's most wanted man.", "Great Depression", "John Dillinger"),
    ("07-25", "1978", "First Test-Tube Baby Born", "A NEW WAY TO BEGIN: World's First Test-Tube Baby Born in England", "On July 25, 1978, Louise Brown was born in Oldham, England — the world's first baby conceived through in vitro fertilization — opening a new era in reproductive medicine.", "Cold War", "Louise Brown"),
    ("07-28", "1914", "World War I Begins", "THE GUNS OF AUGUST: Austria-Hungary Declares War on Serbia, Starting World War I", "On July 28, 1914, Austria-Hungary declared war on Serbia, triggering a cascade of alliances that plunged Europe into World War I within days.", "World War I Era", "World War I"),
    ("07-30", "1619", "First Representative Assembly in America", "GOVERNMENT BY THE PEOPLE: Virginia House of Burgesses Convenes for the First Time", "On July 30, 1619, the Virginia House of Burgesses met for the first time at a church in Jamestown, establishing the first representative legislative assembly in the Americas.", "Colonial America", "House of Burgesses"),
    ("08-01", "1834", "Slavery Abolished in British Empire", "FREEDOM THROUGHOUT THE EMPIRE: Emancipation Act Takes Effect Across British Territories", "On August 1, 1834, the Slavery Abolition Act took effect throughout the British Empire, freeing approximately 800,000 enslaved people in the Caribbean, South Africa, and other colonies.", "19th Century", "Slavery Abolition Act 1833"),
    ("08-05", "1962", "Marilyn Monroe Dies", "CANDLE IN THE WIND: Marilyn Monroe Found Dead at Age 36", "On August 5, 1962, Marilyn Monroe was found dead in her Brentwood home at age 36. The circumstances of her death — officially ruled a probable suicide — remain debated more than 60 years later.", "1960s America", "Marilyn Monroe"),
    ("08-06", "1945", "Atomic Bombing of Hiroshima", "THE BOMB: United States Drops Atomic Bomb on Hiroshima, Killing 80,000 Instantly", "On August 6, 1945, the United States dropped the atomic bomb Little Boy on Hiroshima, Japan, killing an estimated 80,000 people instantly and ushering in the nuclear age.", "World War II", "Atomic bombings of Hiroshima and Nagasaki"),
    ("08-09", "1974", "Nixon Resigns the Presidency", "DISGRACED: Richard Nixon Becomes the Only U.S. President to Resign", "On August 9, 1974, Richard Nixon resigned the presidency in the wake of the Watergate scandal, becoming the only U.S. president to leave office before the end of his term.", "Cold War", "Resignation of Richard Nixon"),
    ("08-13", "1961", "Berlin Wall Construction Begins", "WALL OF SHAME: East Germany Begins Building the Berlin Wall", "On August 13, 1961, East German soldiers began laying barbed wire and constructing barriers along the border between East and West Berlin, beginning construction of the Berlin Wall.", "Cold War", "Berlin Wall"),
    ("08-15", "1947", "Indian Independence", "FREEDOM AT MIDNIGHT: India Gains Independence from British Rule", "On August 15, 1947, India gained independence from British colonial rule after nearly 200 years, as the British Indian Empire was partitioned into the new nations of India and Pakistan.", "Colonial Independence", "Independence Day (India)"),
    ("08-18", "1920", "19th Amendment Ratified", "WOMEN WIN THE VOTE: 19th Amendment to the Constitution Ratified", "On August 18, 1920, the 19th Amendment was ratified, granting American women the right to vote after decades of struggle by the suffrage movement.", "Women's Suffrage", "Nineteenth Amendment to the United States Constitution"),
    ("08-21", "1863", "Lawrence Massacre", "BLEEDING KANSAS: Quantrill's Raiders Massacre 150 Men and Boys in Lawrence", "On August 21, 1863, Confederate guerrilla William Quantrill led approximately 400 raiders into Lawrence, Kansas, massacring around 150 men and boys in one of the worst atrocities of the Civil War.", "Civil War", "Lawrence massacre"),
    ("08-24", "79", "Eruption of Vesuvius", "BURIED ALIVE: Mount Vesuvius Erupts and Buries Pompeii Under 20 Feet of Ash", "On August 24, 79 AD, Mount Vesuvius erupted catastrophically, burying the Roman cities of Pompeii and Herculaneum under volcanic ash and pumice, killing an estimated 2,000 people.", "Ancient World", "Eruption of Mount Vesuvius in 79 AD"),
    ("08-26", "1920", "Women's Suffrage Certified", "THE VOTE IS WON: Secretary of State Certifies the 19th Amendment", "On August 26, 1920, Secretary of State Bainbridge Colby officially certified the 19th Amendment, formally completing the process that gave American women the constitutional right to vote.", "Women's Suffrage", "Nineteenth Amendment to the United States Constitution"),
    ("08-28", "1963", "March on Washington", "I HAVE A DREAM: 250,000 March on Washington for Jobs and Freedom", "On August 28, 1963, approximately 250,000 people gathered at the Lincoln Memorial for the March on Washington, where Martin Luther King Jr. delivered his iconic I Have a Dream speech.", "Civil Rights Era", "March on Washington for Jobs and Freedom"),
    ("09-01", "1939", "Germany Invades Poland", "BLITZKRIEG: Germany Invades Poland, Starting World War II in Europe", "On September 1, 1939, Nazi Germany invaded Poland with 1.5 million troops, beginning World War II in Europe. Britain and France declared war on Germany two days later.", "World War II", "Invasion of Poland"),
    ("09-03", "1783", "Treaty of Paris Signed", "INDEPENDENCE SECURED: Britain Recognizes American Independence in the Treaty of Paris", "On September 3, 1783, the Treaty of Paris was signed, officially ending the American Revolutionary War and recognizing the independence of the United States.", "18th Century", "Treaty of Paris (1783)"),
    ("09-05", "1698", "Peter the Great Taxes Beards", "SHAVE OR PAY: Peter the Great Imposes a Tax on Beards to Westernize Russia", "On September 5, 1698, Tsar Peter the Great imposed a tax on beards in Russia, part of his sweeping campaign to modernize Russian society along Western European lines.", "18th Century", "Peter the Great"),
    ("09-08", "1966", "Star Trek Premieres", "SPACE, THE FINAL FRONTIER: Star Trek Debuts on NBC Television", "On September 8, 1966, Star Trek premiered on NBC, beginning a franchise that would spawn films, series, and a devoted following while influencing real-world technology and culture.", "1960s America", "Star Trek: The Original Series"),
    ("09-11", "2001", "September 11 Attacks", "AMERICA UNDER ATTACK: Terrorists Strike World Trade Center and Pentagon", "On September 11, 2001, 19 hijackers crashed four commercial airplanes into the World Trade Center, the Pentagon, and a field in Pennsylvania, killing nearly 3,000 people in the deadliest attack on American soil.", "21st Century", "September 11 attacks"),
    ("09-15", "1935", "Nuremberg Laws Enacted", "CITIZENS NO MORE: Nazi Germany Strips Jews of Citizenship with Nuremberg Laws", "On September 15, 1935, Nazi Germany enacted the Nuremberg Laws, stripping German Jews of citizenship and prohibiting marriage between Jews and non-Jews.", "World War II", "Nuremberg Laws"),
    ("09-17", "1787", "Constitution Signed", "WE THE PEOPLE: Delegates Sign the United States Constitution in Philadelphia", "On September 17, 1787, 39 delegates signed the United States Constitution at the Constitutional Convention in Philadelphia, creating the framework of government that endures today.", "18th Century", "United States Constitution"),
    ("09-19", "1893", "New Zealand Women Win the Vote", "FIRST IN THE WORLD: New Zealand Becomes the First Country to Grant Women the Right to Vote", "On September 19, 1893, New Zealand became the first self-governing country to grant all women the right to vote, setting a precedent that would spread around the world.", "Victorian Era", "Women's suffrage in New Zealand"),
    ("09-22", "1862", "Emancipation Proclamation Announced", "FOREVER FREE: Lincoln Issues Preliminary Emancipation Proclamation", "On September 22, 1862, President Abraham Lincoln issued the preliminary Emancipation Proclamation, declaring that enslaved people in Confederate states would be free as of January 1, 1863.", "Civil War", "Emancipation Proclamation"),
    ("09-25", "1789", "Bill of Rights Proposed", "YOUR RIGHTS, IN WRITING: Congress Proposes Twelve Amendments to the Constitution", "On September 25, 1789, the First Congress proposed twelve amendments to the Constitution. Ten were ratified by the states and became the Bill of Rights.", "18th Century", "United States Bill of Rights"),
    ("09-28", "551", "Birth of Confucius", "THE MASTER IS BORN: Confucius Born in the State of Lu", "On September 28, 551 BC, Confucius was born in the state of Lu in ancient China. His teachings on ethics, governance, and social harmony would shape Chinese civilization for over 2,500 years.", "Ancient World", "Confucius"),
    ("10-03", "1990", "German Reunification", "ONE GERMANY AGAIN: East and West Germany Reunite After 45 Years of Division", "On October 3, 1990, East and West Germany officially reunited, ending 45 years of division and marking one of the Cold War's most dramatic conclusions.", "Cold War", "German reunification"),
    ("10-07", "1571", "Battle of Lepanto", "CHRISTENDOM'S NAVY: Holy League Defeats Ottoman Fleet at Lepanto", "On October 7, 1571, a fleet of the Holy League — primarily Spain, Venice, and the Papal States — decisively defeated the Ottoman fleet at the Battle of Lepanto, the last major naval battle fought primarily with galleys.", "16th Century", "Battle of Lepanto"),
    ("10-10", "1911", "Wuchang Uprising Begins Chinese Revolution", "DYNASTY'S END: Revolution Erupts in Wuchang, Beginning the Fall of Imperial China", "On October 10, 1911, a military uprising in Wuchang triggered a revolution that ended over 2,000 years of imperial rule in China and led to the establishment of the Republic of China.", "Early 20th Century", "Wuchang Uprising"),
    ("10-12", "1492", "Columbus Reaches the Americas", "LAND HO: Christopher Columbus Makes Landfall in the Bahamas", "On October 12, 1492, Christopher Columbus made landfall on an island in the Bahamas, initiating sustained European contact with the Americas and changing the course of world history.", "Renaissance", "Voyages of Christopher Columbus"),
    ("10-14", "1066", "Battle of Hastings", "ENGLAND CONQUERED: William the Conqueror Defeats King Harold at Hastings", "On October 14, 1066, William, Duke of Normandy, defeated King Harold II at the Battle of Hastings, conquering England and changing its language, culture, and history forever.", "Medieval", "Battle of Hastings"),
    ("10-17", "1781", "British Surrender at Yorktown", "THE WORLD TURNED UPSIDE DOWN: Cornwallis Surrenders at Yorktown", "On October 17, 1781, British General Cornwallis sent a drummer boy to the parapet with a white flag, signaling his intention to surrender at Yorktown — effectively ending the American Revolution.", "18th Century", "Siege of Yorktown"),
    ("10-20", "1944", "MacArthur Returns to the Philippines", "I HAVE RETURNED: General MacArthur Wades Ashore at Leyte in the Philippines", "On October 20, 1944, General Douglas MacArthur waded ashore at Leyte in the Philippines, fulfilling his famous promise to return after being forced to evacuate in 1942.", "World War II", "Battle of Leyte"),
    ("10-24", "1929", "Black Thursday Stock Market Crash", "THE CRASH: Wall Street Panic Begins with Black Thursday", "On October 24, 1929, the New York Stock Exchange experienced a massive sell-off known as Black Thursday, beginning the stock market crash that helped trigger the Great Depression.", "Great Depression", "Wall Street Crash of 1929"),
    ("10-29", "1929", "Black Tuesday", "BOTTOM FALLS OUT: Wall Street Crashes on Black Tuesday, Wiping Out Billions", "On October 29, 1929 — Black Tuesday — the stock market crashed catastrophically, with 16 million shares traded and billions in value wiped out, deepening the Great Depression.", "Great Depression", "Wall Street Crash of 1929"),
    ("10-31", "1517", "Luther Posts 95 Theses", "NAILED IT: Martin Luther Posts 95 Theses on Wittenberg Church Door", "On October 31, 1517, Martin Luther reportedly nailed his 95 Theses to the door of All Saints' Church in Wittenberg, challenging the Catholic Church's sale of indulgences and sparking the Protestant Reformation.", "Renaissance", "Ninety-five Theses"),
    ("11-01", "1755", "Lisbon Earthquake", "THE CITY DESTROYED: Massive Earthquake and Tsunami Devastate Lisbon on All Saints' Day", "On November 1, 1755, a massive earthquake struck Lisbon, Portugal, on All Saints' Day, followed by a tsunami and fires that killed an estimated 30,000 to 50,000 people and destroyed much of the city.", "18th Century", "1755 Lisbon earthquake"),
    ("11-05", "1605", "Gunpowder Plot Discovered", "REMEMBER, REMEMBER: Guy Fawkes Caught Beneath Parliament with 36 Barrels of Gunpowder", "On November 5, 1605, Guy Fawkes was discovered beneath the House of Lords with 36 barrels of gunpowder, foiling a plot to blow up Parliament and assassinate King James I.", "17th Century", "Gunpowder Plot"),
    ("11-09", "1989", "Fall of the Berlin Wall", "THE WALL COMES DOWN: East Germany Opens the Berlin Wall After 28 Years", "On November 9, 1989, East Germany opened the Berlin Wall, allowing citizens to cross freely for the first time in 28 years. Jubilant crowds began physically dismantling the wall that night.", "Cold War", "Fall of the Berlin Wall"),
    ("11-11", "1918", "World War I Armistice", "THE ELEVENTH HOUR: Armistice Signed, Ending World War I", "On November 11, 1918, at 11:00 AM — the eleventh hour of the eleventh day of the eleventh month — the armistice ending World War I took effect, silencing the guns after four years of carnage.", "World War I Era", "Armistice of 11 November 1918"),
    ("11-14", "1889", "Nellie Bly Begins Trip Around the World", "AROUND THE WORLD IN 72 DAYS: Journalist Nellie Bly Sets Out to Beat Phileas Fogg", "On November 14, 1889, journalist Nellie Bly departed New York on a quest to travel around the world in fewer than 80 days, as depicted in Jules Verne's novel. She completed the journey in 72 days.", "Victorian Era", "Nellie Bly"),
    ("11-19", "1863", "Gettysburg Address", "FOUR SCORE AND SEVEN YEARS: Lincoln Delivers the Gettysburg Address in Two Minutes", "On November 19, 1863, President Abraham Lincoln delivered the Gettysburg Address at the dedication of the Soldiers' National Cemetery, redefining the purpose of the war in just 272 words.", "Civil War", "Gettysburg Address"),
    ("11-22", "1963", "Assassination of JFK", "SHOTS IN DALLAS: President Kennedy Assassinated", "On November 22, 1963, President John F. Kennedy was assassinated while riding in a motorcade through Dealey Plaza in Dallas, Texas. Lee Harvey Oswald was arrested for the murder.", "1960s America", "Assassination of John F. Kennedy"),
    ("11-25", "1867", "Dynamite Patented", "EXPLOSIVE INVENTION: Alfred Nobel Patents Dynamite", "On November 25, 1867, Alfred Nobel patented dynamite, an invention that made him enormously wealthy and, troubled by its destructive potential, later inspired him to create the Nobel Prizes.", "Industrial Age", "Dynamite"),
    ("11-28", "1520", "Magellan Enters the Pacific", "THE GREAT SOUTH SEA: Magellan Sails Through the Strait Into the Pacific Ocean", "On November 28, 1520, Ferdinand Magellan sailed through the strait at the southern tip of South America and entered a vast, calm ocean he named the Pacific — the peaceful sea.", "Renaissance", "Ferdinand Magellan"),
    ("12-01", "1955", "Rosa Parks Refuses to Give Up Her Seat", "SITTING FOR JUSTICE: Rosa Parks Arrested for Refusing to Move to Back of Bus", "On December 1, 1955, Rosa Parks refused to give up her bus seat to a white passenger in Montgomery, Alabama. Her arrest sparked the Montgomery Bus Boycott and ignited the modern civil rights movement.", "Civil Rights Era", "Rosa Parks"),
    ("12-05", "1933", "Prohibition Repealed", "CHEERS: 21st Amendment Ratified, Ending 13 Years of Prohibition", "On December 5, 1933, the 21st Amendment was ratified, repealing the 18th Amendment and ending 13 years of Prohibition — the only time a constitutional amendment has been repealed.", "Great Depression", "Twenty-first Amendment to the United States Constitution"),
    ("12-07", "1941", "Attack on Pearl Harbor", "A DATE WHICH WILL LIVE IN INFAMY: Japan Attacks Pearl Harbor, Drawing America Into World War II", "On December 7, 1941, the Imperial Japanese Navy launched a surprise attack on the U.S. naval base at Pearl Harbor, Hawaii, killing 2,403 Americans and propelling the United States into World War II.", "World War II", "Attack on Pearl Harbor"),
    ("12-10", "1948", "Universal Declaration of Human Rights", "RIGHTS FOR ALL: United Nations Adopts the Universal Declaration of Human Rights", "On December 10, 1948, the United Nations General Assembly adopted the Universal Declaration of Human Rights, establishing for the first time a common standard of fundamental rights for all people.", "Peace & Cooperation", "Universal Declaration of Human Rights"),
    ("12-14", "1911", "Roald Amundsen Reaches the South Pole", "FIRST TO THE BOTTOM OF THE WORLD: Amundsen Plants Norwegian Flag at the South Pole", "On December 14, 1911, Norwegian explorer Roald Amundsen and his team became the first humans to reach the South Pole, beating the British expedition led by Robert Falcon Scott by 34 days.", "Early 20th Century", "Amundsen's South Pole expedition"),
    ("12-16", "1773", "Boston Tea Party", "TEA IN THE HARBOR: Colonists Dump 342 Chests of Tea to Protest Taxation Without Representation", "On December 16, 1773, American colonists disguised as Mohawk Indians boarded three ships in Boston Harbor and dumped 342 chests of British East India Company tea into the water.", "18th Century", "Boston Tea Party"),
    ("12-17", "1903", "Wright Brothers First Flight", "MAN FLIES: Wright Brothers Make the First Powered, Controlled, Sustained Airplane Flight", "On December 17, 1903, Orville and Wilbur Wright made four powered flights at Kitty Hawk, North Carolina. The longest lasted 59 seconds and covered 852 feet, launching the age of aviation.", "Early 20th Century", "Wright brothers"),
    ("12-20", "1860", "South Carolina Secedes", "THE UNION IS DISSOLVED: South Carolina Becomes First State to Secede", "On December 20, 1860, South Carolina became the first state to secede from the United States, setting the stage for the Civil War that would begin four months later.", "Civil War", "South Carolina secession"),
    ("12-24", "1914", "Christmas Truce of World War I", "SILENT NIGHT IN NO MAN'S LAND: German and British Soldiers Celebrate Christmas Together", "On December 24, 1914, German and British soldiers along the Western Front laid down their weapons and celebrated Christmas together, singing carols and exchanging gifts in one of the war's most extraordinary moments.", "World War I Era", "Christmas truce"),
    ("12-25", "1776", "Washington Crosses the Delaware", "VICTORY OR DEATH: Washington Leads Daring Christmas Night Crossing of the Delaware", "On December 25, 1776, George Washington led 2,400 Continental soldiers across the ice-choked Delaware River in a daring nighttime crossing, surprising the Hessian garrison at Trenton the next morning.", "18th Century", "George Washington's crossing of the Delaware River"),
    ("12-28", "1895", "First Commercial Film Screening", "THE MOVIES ARE BORN: Lumiere Brothers Hold First Public Film Screening in Paris", "On December 28, 1895, Auguste and Louis Lumiere held the first commercial public film screening at the Grand Cafe in Paris, showing short films to a paying audience and launching the motion picture industry.", "Victorian Era", "Auguste and Louis Lumière"),
    ("12-31", "1879", "Edison Demonstrates Incandescent Light", "LET THERE BE LIGHT: Thomas Edison Demonstrates His Incandescent Light Bulb", "On December 31, 1879, Thomas Edison publicly demonstrated his incandescent electric light bulb at his laboratory in Menlo Park, New Jersey, illuminating the future of human civilization.", "Industrial Age", "Incandescent light bulb"),
]

TEMPLATE = '''---
title: "{title}"
headline: "{headline}"
summary: "{summary}"
date: 2026-05-20
historydate: "{historydate}"
monthday: "{monthday}"
era: "{era}"
source: "Wikipedia"
image: "/images/articles/{slug}.jpg"
imagealt: "Historical image related to {title}"
imagecaption: "{title}"
imagecredit: "Wikimedia Commons / Public Domain"
weight: {weight}
sources:
  - "Wikipedia — {wiki_source} — https://en.wikipedia.org/wiki/{wiki_source_url}"
  - "History.com — This Day in History — https://www.history.com/this-day-in-history"
  - "Britannica — {title} — https://www.britannica.com"
---

**{historydate}** — {summary}

The events of this day would prove to be far more consequential than anyone involved could have imagined. What happened on {month_name} {day} sent ripples through history that can still be felt today.

## Background

The story behind {title_lower} stretches back well before the events of {historydate}. For years, pressures had been building — political, social, and in many cases deeply personal — that made this moment all but inevitable.

The world of {year} was defined by tensions that had been simmering for a long time. Existing power structures were under strain. New ideas were challenging old certainties. And individuals whose names would soon be written into the history books were being shaped by the forces swirling around them.

To understand what happened on this day, we must first understand the context in which it occurred. Nothing in history happens in isolation. Every revolution has its grievances, every discovery has its precursors, and every turning point has its approach.

## The Events of the Day

{summary}

The details of what unfolded reveal a story that is both dramatic and deeply human. The people at the center of these events were not abstract historical figures — they were real people, making decisions under pressure, with incomplete information and uncertain outcomes.

Contemporary accounts paint a vivid picture. Those who witnessed the events firsthand described moments of tension, surprise, and — in many cases — profound emotion. Whether they recognized the significance of what was happening in the moment is debatable, but history would judge their actions for centuries to come.

The chain of events moved quickly. What had been brewing for months or years came to a head in a matter of hours or days. Decisions made in the heat of the moment would prove irreversible, setting new courses for nations, movements, and millions of individual lives.

## Consequences

The aftermath of these events reshaped the landscape — politically, socially, and culturally. In the short term, the world had to adapt to a new reality. Alliances shifted. Old certainties gave way to new questions. And the lives of countless people were altered in ways both visible and invisible.

In the longer term, the significance of {title_lower} only grew. Historians, politicians, and ordinary citizens would return to this moment again and again, drawing lessons, debating interpretations, and finding new relevance in an ever-changing world.

The legacy endures because the fundamental questions raised by these events — about power, justice, courage, and the capacity of individuals to shape history — remain as relevant today as they were in {year}.
'''

MONTHS = {
    "01": ("January", 31), "02": ("February", 29), "03": ("March", 31),
    "04": ("April", 30), "05": ("May", 31), "06": ("June", 30),
    "07": ("July", 31), "08": ("August", 31), "09": ("September", 30),
    "10": ("October", 31), "11": ("November", 30), "12": ("December", 31),
}

def day_of_year(month_str, day_str):
    """Approximate day of year for weight calculation."""
    days_before = {
        "01": 0, "02": 31, "03": 60, "04": 91, "05": 121, "06": 152,
        "07": 182, "08": 213, "09": 244, "10": 274, "11": 305, "12": 335,
    }
    return days_before[month_str] + int(day_str)

def generate_historydate(monthday, year):
    """Generate human-readable date string."""
    month_str = monthday[:2]
    day_str = monthday[3:]
    month_name = MONTHS[month_str][0]
    day = int(day_str)
    
    if year.startswith("-") or (year.isdigit() and int(year) < 100):
        suffix = " BC" if year.startswith("-") else " AD"
        yr = year.lstrip("-")
        return f"{month_name} {day}, {yr}{suffix}"
    return f"{month_name} {day}, {year}"

def main():
    created = 0
    skipped = 0
    
    for monthday, year, title, headline, summary, era, wiki_source in EVENTS:
        month_str = monthday[:2]
        day_str = monthday[3:]
        slug = f"tdih-{monthday}-02"
        filepath = os.path.join(CONTENT_DIR, f"{slug}.md")
        
        if os.path.exists(filepath):
            print(f"SKIP (exists): {slug}")
            skipped += 1
            continue
        
        month_name = MONTHS[month_str][0]
        day = int(day_str)
        historydate = generate_historydate(monthday, year)
        weight = 700 + day_of_year(month_str, day_str)
        wiki_source_url = wiki_source.replace(" ", "_")
        title_lower = title.lower()
        
        content = TEMPLATE.format(
            title=title,
            headline=headline,
            summary=summary,
            historydate=historydate,
            monthday=monthday,
            era=era,
            slug=slug,
            wiki_source=wiki_source,
            wiki_source_url=wiki_source_url,
            weight=weight,
            month_name=month_name,
            day=day,
            year=year,
            title_lower=title_lower,
        )
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"CREATED: {slug} — {title}")
        created += 1
    
    print(f"\nDone: {created} created, {skipped} skipped")

if __name__ == "__main__":
    main()
