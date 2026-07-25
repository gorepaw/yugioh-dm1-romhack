# Project 2 — MTG card conversion (multi-set)

Master creature pool: `work/p2/creatures.json`. Sets: LEB (89), ARN (43), ATQ (33), DRK (59), FEM (54), LEG (44) = **322 creatures**.
Engine/model rationale in `docs/PROJECT2.md`. Nothing here is in a ROM yet.

## Conversion rules (creatures)

- **Stats: 400:1**, capped +4000 (Elder Dragon apex tier); ATK-only keyword liberty
  (flying+300, first+200, trample/rampage+150, banding+100, fear/unblockable+200,
  landwalk+100; cap +400), power≥1 non-Walls; DEF never bumped. **Walls → 0 ATK.**
- **Color → type byte** (mono/colorless; gold skipped **except the 5 Elder Dragons**,
  placed under their shard-center color at a fixed **4000/4000** apex).
- **Stars = mana cost** (informational); accented names folded; `*/*` fixed; names >18 compacted.
- **Dedup across sets; core/reprints skipped.** LEB → ARN → ATQ → DRK → FEM → curated LEG backfill.

## White — 57 creatures

| Card (in-game) | Set | P/T | ★ | ATK | DEF | note |
|---|---|---|---|--:|--:|---|
| Arcades Sabboth | LEG | 7/7 | 8 | 4000 | 4000 | Elder Dragon — apex |
| Akron Legionnaire | LEG | 8/4 | 8 | 3200 | 1600 |  |
| PersonalIncarnatn | LEB | 6/6 | 6 | 2400 | 2400 |  |
| Serra Angel | LEB | 4/4 | 5 | 1900 | 1600 | flying+300 |
| Righteous Avengers | LEG | 3/1 | 5 | 1400 | 400 |  |
| Moorish Cavalry | ARN | 3/3 | 4 | 1350 | 1200 | trample+150 |
| Petra Sphinx | LEG | 3/4 | 5 | 1200 | 1600 |  |
| Northern Paladin | LEB | 3/3 | 4 | 1200 | 1200 |  |
| Angry Mob | DRK | 3/3 | 4 | 1200 | 1200 |  [was */*] |
| Ivory Guardians | LEG | 3/3 | 6 | 1200 | 1200 |  |
| White Knight | LEB | 2/2 | 2 | 1200 | 800 | first+200,evasion+200 |
| Thunder Spirit | LEG | 2/2 | 3 | 1200 | 800 |  |
| War Elephant | ARN | 2/2 | 4 | 1050 | 800 | trample+150,banding+100 |
| Order of Leitbur | FEM | 2/1 | 2 | 1000 | 400 |  |
| Icatian Phalanx | FEM | 2/4 | 5 | 900 | 1600 |  |
| Knights of Thorn | DRK | 2/2 | 4 | 900 | 800 |  |
| Hand of Justice | FEM | 2/6 | 6 | 800 | 2400 |  |
| Veteran Bodyguard | LEB | 2/5 | 5 | 800 | 2000 |  |
| KeepersOfTheFaith | LEG | 2/3 | 3 | 800 | 1200 |  |
| Pearled Unicorn | LEB | 2/2 | 3 | 800 | 800 |  |
| ArgivinBlacksmith | ATQ | 2/2 | 3 | 800 | 800 |  |
| Farrel's Zealot | FEM | 2/2 | 3 | 800 | 800 |  |
| Enchanted Being | LEG | 2/2 | 3 | 800 | 800 |  |
| Mesa Pegasus | LEB | 1/1 | 2 | 800 | 400 | flying+300,banding+100 |
| Savannah Lions | LEB | 2/1 | 1 | 800 | 400 |  |
| Pikemen | DRK | 1/1 | 2 | 700 | 400 |  |
| Icatian Infantry | FEM | 1/1 | 1 | 700 | 400 |  |
| IcatianSkirmishrs | FEM | 1/1 | 4 | 700 | 400 |  |
| Osai Vultures | LEG | 1/1 | 2 | 700 | 400 |  |
| Icatian Scout | FEM | 1/1 | 1 | 600 | 400 |  |
| Amrou Kithkin | LEG | 1/1 | 2 | 600 | 400 |  |
| Tundra Wolves | LEG | 1/1 | 1 | 600 | 400 |  |
| Benalish Hero | LEB | 1/1 | 1 | 500 | 400 | banding+100 |
| Martyrs of Korlis | ATQ | 1/6 | 5 | 400 | 2400 |  |
| Farrelite Priest | FEM | 1/3 | 3 | 400 | 1200 |  |
| RepentntBlacksmith | ARN | 1/2 | 2 | 400 | 800 |  |
| Squire | DRK | 1/2 | 2 | 400 | 800 |  |
| Icatian Lieutenant | FEM | 1/2 | 2 | 400 | 800 |  |
| D'Avenant Archer | LEG | 1/2 | 3 | 400 | 800 |  |
| Samite Healer | LEB | 1/1 | 2 | 400 | 400 |  |
| King Suleiman | ARN | 1/1 | 2 | 400 | 400 |  |
| ArgivianArchaeolg | ATQ | 1/1 | 3 | 400 | 400 |  |
| Exorcist | DRK | 1/1 | 2 | 400 | 400 |  |
| Miracle Worker | DRK | 1/1 | 1 | 400 | 400 |  |
| Preacher | DRK | 1/1 | 3 | 400 | 400 |  |
| Witch Hunter | DRK | 1/1 | 4 | 400 | 400 |  |
| Icatian Javelineers | FEM | 1/1 | 1 | 400 | 400 |  |
| Icatian Priest | FEM | 1/1 | 1 | 400 | 400 |  |
| ClergyHolyNimbus | LEG | 1/1 | 1 | 400 | 400 |  |
| Wall of Swords | LEB | 3/5 | 4 | 0 | 2000 | [wall] |
| Elder Land Wurm | LEG | 5/5 | 7 | 0 | 2000 | [wall] |
| Wall of Light | LEG | 1/5 | 3 | 0 | 2000 | [wall] |
| Combat Medic | FEM | 0/2 | 3 | 0 | 800 |  |
| IcatianMoneychngr | FEM | 0/2 | 1 | 0 | 800 |  |
| Abu Ja'far | ARN | 0/1 | 1 | 0 | 400 |  |
| Camel | ARN | 0/1 | 1 | 0 | 400 |  |
| Wall of Caltrops | LEG | 2/1 | 2 | 0 | 400 | [wall] |

## Blue — 52 creatures

| Card (in-game) | Set | P/T | ★ | ATK | DEF | note |
|---|---|---|---|--:|--:|---|
| Leviathan | DRK | 10/10 | 9 | 4000 | 4000 | capped to apex |
| Chromium | LEG | 7/7 | 8 | 4000 | 4000 | Elder Dragon — apex |
| Elder Spawn | LEG | 6/6 | 7 | 2600 | 2400 |  |
| Deep Spawn | FEM | 6/6 | 8 | 2550 | 2400 |  |
| IslandFishJascnus | ARN | 6/8 | 7 | 2400 | 3200 |  |
| Mahamoti Djinn | LEB | 5/6 | 6 | 2400 | 2400 | flying+300,evasion+200 |
| Serendib Djinn | ARN | 5/6 | 4 | 2300 | 2400 | flying+300 |
| Sea Serpent | LEB | 5/5 | 6 | 2000 | 2000 |  |
| Water Elemental | LEB | 5/4 | 5 | 2000 | 1600 |  |
| Air Elemental | LEB | 4/4 | 5 | 1900 | 1600 | flying+300 |
| Phantasmal Forces | LEB | 4/1 | 4 | 1900 | 400 | flying+300 |
| Giant Shark | DRK | 4/4 | 6 | 1750 | 1600 |  |
| Pirate Ship | LEB | 4/3 | 5 | 1600 | 1200 |  |
| Dandan | ARN | 4/1 | 2 | 1600 | 400 |  |
| Serendib Efreet | ARN | 3/4 | 3 | 1500 | 1600 | flying+300 |
| Phantom Monster | LEB | 3/3 | 4 | 1500 | 1200 | flying+300 |
| Segovian Leviathan | LEG | 3/3 | 5 | 1400 | 1200 |  |
| Homarid Warrior | FEM | 3/3 | 5 | 1200 | 1200 |  |
| Vodalian Knights | FEM | 2/2 | 3 | 1200 | 800 |  |
| Ghost Ship | DRK | 2/4 | 4 | 1100 | 1600 |  |
| Azure Drake | LEG | 2/4 | 4 | 1100 | 1600 |  |
| Lord of Atlantis | LEB | 2/2 | 2 | 1100 | 800 | evasion+200,walk+100 |
| River Merfolk | FEM | 2/1 | 2 | 1000 | 400 |  |
| Old Man of the Sea | ARN | 2/3 | 3 | 800 | 1200 |  |
| Homarid | FEM | 2/2 | 3 | 800 | 800 |  |
| Brine Hag | LEG | 2/2 | 4 | 800 | 800 |  |
| Psionic Entity | LEG | 2/2 | 5 | 800 | 800 |  |
| Homarid Shaman | FEM | 2/1 | 4 | 800 | 400 |  |
| Flying Men | ARN | 1/1 | 1 | 700 | 400 | flying+300 |
| Zephyr Falcon | LEG | 1/1 | 2 | 700 | 400 |  |
| Devouring Deep | LEG | 1/2 | 3 | 600 | 800 |  |
| Sage of Lat-Nam | ATQ | 1/2 | 2 | 400 | 800 |  |
| Merfolk Assassin | DRK | 1/2 | 2 | 400 | 800 |  |
| Vodalian Soldiers | FEM | 1/2 | 2 | 400 | 800 |  |
| MerfolkPearlTridnt | LEB | 1/1 | 1 | 400 | 400 |  |
| Prodigal Sorcerer | LEB | 1/1 | 3 | 400 | 400 |  |
| Giant Tortoise | ARN | 1/1 | 2 | 400 | 400 |  |
| Sindbad | ARN | 1/1 | 2 | 400 | 400 |  |
| Drowned | DRK | 1/1 | 2 | 400 | 400 |  |
| Electric Eel | DRK | 1/1 | 1 | 400 | 400 |  |
| Water Wurm | DRK | 1/1 | 1 | 400 | 400 |  |
| Svyelunite Priest | FEM | 1/1 | 2 | 400 | 400 |  |
| Vodalian Mage | FEM | 1/1 | 3 | 400 | 400 |  |
| Wall of Air | LEB | 1/5 | 3 | 0 | 2000 | [wall] |
| Wall of Water | LEB | 0/5 | 3 | 0 | 2000 | [wall] |
| Wall of Wonder | LEG | 1/5 | 4 | 0 | 2000 | [wall] |
| VodalianWarMachine | FEM | 0/4 | 3 | 0 | 1600 | [wall] |
| Merchant Ship | ARN | 0/2 | 1 | 0 | 800 |  |
| Time Elemental | LEG | 0/2 | 3 | 0 | 800 |  |
| Apprentice Wizard | DRK | 0/1 | 3 | 0 | 400 |  |
| Seasinger | FEM | 0/1 | 3 | 0 | 400 |  |
| Wall of Vapor | LEG | 0/1 | 4 | 0 | 400 | [wall] |

## Black — 59 creatures

| Card (in-game) | Set | P/T | ★ | ATK | DEF | note |
|---|---|---|---|--:|--:|---|
| Nicol Bolas | LEG | 7/7 | 8 | 4000 | 4000 | Elder Dragon — apex |
| Lord of the Pit | LEB | 7/7 | 7 | 3200 | 2800 | flying+300,trample+150 |
| Cosmic Horror | LEG | 7/7 | 6 | 3000 | 2800 |  |
| Yawgmoth Demon | ATQ | 6/6 | 6 | 2800 | 2400 |  |
| Mold Demon | LEG | 6/6 | 7 | 2400 | 2400 |  |
| Nightmare | LEB | 5/5 | 6 | 2400 | 2000 | flying+300,evasion+200 [was */*] |
| Ebon Praetor | FEM | 5/5 | 6 | 2350 | 2000 |  |
| Demonic Hordes | LEB | 5/5 | 6 | 2000 | 2000 |  |
| Juzam Djinn | ARN | 5/5 | 4 | 2000 | 2000 |  |
| Sengir Vampire | LEB | 4/4 | 5 | 2000 | 1600 | flying+300,evasion+200 |
| Nameless Race | DRK | 4/4 | 4 | 1600 | 1600 |  [was */*] |
| Derelor | FEM | 4/4 | 4 | 1600 | 1600 |  |
| Bog Wraith | LEB | 3/3 | 4 | 1500 | 1200 | evasion+200,walk+100 |
| Junun Efreet | ARN | 3/3 | 3 | 1500 | 1200 | flying+300 |
| Fallen Angel | LEG | 3/3 | 5 | 1500 | 1200 |  |
| Eater of the Dead | DRK | 3/4 | 5 | 1200 | 1600 |  |
| Black Knight | LEB | 2/2 | 2 | 1200 | 800 | first+200,evasion+200 |
| Hasran Ogress | ARN | 3/2 | 2 | 1200 | 800 |  |
| Zombie Master | LEB | 2/3 | 3 | 1100 | 1200 | evasion+200,walk+100 |
| Hypnotic Specter | LEB | 2/2 | 3 | 1100 | 800 | flying+300 |
| OrderOfTheEbonHand | FEM | 2/1 | 2 | 1000 | 400 |  |
| Guardian Beast | ARN | 2/4 | 4 | 800 | 1600 |  |
| Erg Raiders | ARN | 2/3 | 2 | 800 | 1200 |  |
| The Fallen | DRK | 2/3 | 4 | 800 | 1200 |  |
| Plague Rats | LEB | 2/2 | 3 | 800 | 800 | [was */*] |
| Scathe Zombies | LEB | 2/2 | 3 | 800 | 800 |  |
| Scavenging Ghoul | LEB | 2/2 | 4 | 800 | 800 |  |
| Murk Dwellers | DRK | 2/2 | 4 | 800 | 800 |  |
| Mindstab Thrull | FEM | 2/2 | 3 | 800 | 800 |  |
| Necrite | FEM | 2/2 | 3 | 800 | 800 |  |
| Thrull Champion | FEM | 2/2 | 5 | 800 | 800 |  |
| Bog Imp | DRK | 1/1 | 2 | 800 | 400 |  |
| Rag Man | DRK | 2/1 | 4 | 800 | 400 |  |
| StoneThrowngDevils | ARN | 1/1 | 1 | 600 | 400 | first+200 |
| Bog Rats | DRK | 1/1 | 1 | 600 | 400 |  |
| Marsh Goblins | DRK | 1/1 | 2 | 600 | 400 |  |
| Cuombajj Witches | ARN | 1/3 | 2 | 400 | 1200 |  |
| Uncle Istvan | DRK | 1/3 | 4 | 400 | 1200 |  |
| Armor Thrull | FEM | 1/3 | 3 | 400 | 1200 |  |
| Priest of Yawgmoth | ATQ | 1/2 | 2 | 400 | 800 |  |
| Basal Thrull | FEM | 1/2 | 2 | 400 | 800 |  |
| Drudge Skeletons | LEB | 1/1 | 2 | 400 | 400 |  |
| Nether Shadow | LEB | 1/1 | 2 | 400 | 400 |  |
| Nettling Imp | LEB | 1/1 | 3 | 400 | 400 |  |
| Royal Assassin | LEB | 1/1 | 3 | 400 | 400 |  |
| El-Hajjaj | ARN | 1/1 | 3 | 400 | 400 |  |
| Khabal Ghoul | ARN | 1/1 | 3 | 400 | 400 |  |
| Sorceress Queen | ARN | 1/1 | 3 | 400 | 400 |  |
| Phyrexian Gremlins | ATQ | 1/1 | 3 | 400 | 400 |  |
| Xenic Poltergeist | ATQ | 1/1 | 3 | 400 | 400 |  |
| Grave Robbers | DRK | 1/1 | 3 | 400 | 400 |  |
| InitiatesEbonHand | FEM | 1/1 | 1 | 400 | 400 |  |
| Thrull Wizard | FEM | 1/1 | 3 | 400 | 400 |  |
| Hell's Caretaker | LEG | 1/1 | 4 | 400 | 400 |  |
| Wall of Bone | LEB | 1/4 | 3 | 0 | 1600 | [wall] |
| Frozen Shade | LEB | 0/1 | 3 | 0 | 400 |  |
| Will-o'-the-Wisp | LEB | 0/1 | 1 | 0 | 400 |  |
| Banshee | DRK | 0/1 | 4 | 0 | 400 |  |
| FrankensteinMonstr | DRK | 0/1 | 2 | 0 | 400 |  |

## Red — 62 creatures

| Card (in-game) | Set | P/T | ★ | ATK | DEF | note |
|---|---|---|---|--:|--:|---|
| Vaevictis Asmadi | LEG | 7/7 | 8 | 4000 | 4000 | Elder Dragon — apex |
| Orgg | FEM | 6/6 | 5 | 2550 | 2400 |  |
| Ball Lightning | DRK | 6/1 | 3 | 2550 | 400 |  |
| Mijae Djinn | ARN | 6/3 | 3 | 2400 | 1200 |  |
| Shivan Dragon | LEB | 5/5 | 6 | 2300 | 2000 | flying+300 |
| Fire Elemental | LEB | 5/4 | 5 | 2000 | 1600 |  |
| TwoHeadGiantForiys | LEB | 4/4 | 5 | 1750 | 1600 | trample+150 |
| Frost Giant | LEG | 4/4 | 6 | 1750 | 1600 |  |
| Earth Elemental | LEB | 4/5 | 5 | 1600 | 2000 |  |
| Stone Giant | LEB | 3/4 | 4 | 1500 | 1600 | flying+300 |
| Roc of Kher Ridges | LEB | 3/3 | 4 | 1500 | 1200 | flying+300 |
| Firestorm Phoenix | LEG | 3/2 | 6 | 1500 | 800 |  |
| Goblin Rock Sled | DRK | 3/1 | 2 | 1350 | 400 |  |
| Ydwen Efreet | ARN | 3/6 | 3 | 1200 | 2400 |  |
| Hill Giant | LEB | 3/3 | 4 | 1200 | 1200 |  |
| Keldon Warlord | LEB | 3/3 | 4 | 1200 | 1200 | [was */*] |
| Tempest Efreet | LEG | 3/3 | 4 | 1200 | 1200 |  |
| Brassclaw Orcs | FEM | 3/2 | 3 | 1200 | 800 |  |
| Goblin Flotilla | FEM | 2/2 | 3 | 1200 | 800 |  |
| Dragon Whelp | LEB | 2/3 | 4 | 1100 | 1200 | flying+300 |
| Granite Gargoyle | LEB | 2/2 | 3 | 1100 | 800 | flying+300 |
| Orcish Veteran | FEM | 2/2 | 3 | 1000 | 800 |  |
| Goblin King | LEB | 2/2 | 3 | 900 | 800 | walk+100 |
| Desert Nomads | ARN | 2/2 | 3 | 900 | 800 | walk+100 |
| Hurloon Minotaur | LEB | 2/3 | 3 | 800 | 1200 |  |
| Gray Ogre | LEB | 2/2 | 3 | 800 | 800 |  |
| Ironclaw Orcs | LEB | 2/2 | 2 | 800 | 800 |  |
| Sedge Troll | LEB | 2/2 | 3 | 800 | 800 |  |
| Uthden Troll | LEB | 2/2 | 3 | 800 | 800 |  |
| Brothers of Fire | DRK | 2/2 | 3 | 800 | 800 |  |
| Goblin Hero | DRK | 2/2 | 3 | 800 | 800 |  |
| Orc General | DRK | 2/2 | 3 | 800 | 800 |  |
| SistersOfTheFlame | DRK | 2/2 | 3 | 800 | 800 |  |
| Dwarven Soldier | FEM | 2/1 | 2 | 800 | 400 |  |
| Bird Maiden | ARN | 1/2 | 3 | 700 | 800 | flying+300 |
| Fire Drake | DRK | 1/2 | 3 | 700 | 800 |  |
| GoblnBalloonBrigade | LEB | 1/1 | 1 | 700 | 400 | flying+300 |
| Cave People | DRK | 1/4 | 3 | 600 | 1600 |  |
| Dwarven Warriors | LEB | 1/1 | 3 | 600 | 400 | evasion+200 |
| GoblinsOfTheFlarg | DRK | 1/1 | 1 | 600 | 400 |  |
| Orcish Artillery | LEB | 1/3 | 3 | 400 | 1200 |  |
| Atog | ATQ | 1/2 | 2 | 400 | 800 |  |
| Dwarven Lieutenant | FEM | 1/2 | 2 | 400 | 800 |  |
| DwarvenDemolitnTeam | LEB | 1/1 | 3 | 400 | 400 |  |
| Mons'sGoblinRaidrs | LEB | 1/1 | 1 | 400 | 400 |  |
| Aladdin | ARN | 1/1 | 4 | 400 | 400 |  |
| Ali Baba | ARN | 1/1 | 1 | 400 | 400 |  |
| Hurr Jackal | ARN | 1/1 | 1 | 400 | 400 |  |
| Kird Ape | ARN | 1/1 | 1 | 400 | 400 |  |
| DwarvnWeaponsmith | ATQ | 1/1 | 2 | 400 | 400 |  |
| Goblin Artisans | ATQ | 1/1 | 1 | 400 | 400 |  |
| Orcish Mechanics | ATQ | 1/1 | 3 | 400 | 400 |  |
| Goblin Digging Team | DRK | 1/1 | 1 | 400 | 400 |  |
| Goblin Wizard | DRK | 1/1 | 4 | 400 | 400 |  |
| Orcish Captain | FEM | 1/1 | 1 | 400 | 400 |  |
| Orcish Spy | FEM | 1/1 | 1 | 400 | 400 |  |
| Wall of Stone | LEB | 0/8 | 3 | 0 | 3200 | [wall] |
| Wall of Fire | LEB | 0/5 | 3 | 0 | 2000 | [wall] |
| Rukh Egg | ARN | 0/3 | 4 | 0 | 1200 |  |
| Dwarven Armorer | FEM | 0/2 | 1 | 0 | 800 |  |
| Goblin Chirurgeon | FEM | 0/2 | 1 | 0 | 800 |  |
| Ali from Cairo | ARN | 0/1 | 4 | 0 | 400 |  |

## Green — 62 creatures

| Card (in-game) | Set | P/T | ★ | ATK | DEF | note |
|---|---|---|---|--:|--:|---|
| Palladia-Mors | LEG | 7/7 | 8 | 4000 | 4000 | Elder Dragon — apex |
| Force of Nature | LEB | 8/8 | 6 | 3350 | 3200 | trample+150 |
| Craw Giant | LEG | 6/4 | 7 | 2700 | 1600 |  |
| Gaea's Liege | LEB | 6/6 | 6 | 2400 | 2400 | [was */*] |
| Craw Wurm | LEB | 6/4 | 6 | 2400 | 1600 |  |
| Feral Thallid | FEM | 6/3 | 6 | 2400 | 1200 |  |
| Erhnam Djinn | ARN | 4/5 | 4 | 1900 | 2000 | evasion+200,walk+100 |
| Wormwood Treefolk | DRK | 4/4 | 5 | 1800 | 1600 |  |
| Durkwood Boars | LEG | 4/4 | 5 | 1600 | 1600 |  |
| Elven Riders | LEG | 3/3 | 5 | 1600 | 1200 |  |
| Ifh-Biff Efreet | ARN | 3/3 | 4 | 1500 | 1200 | flying+300 |
| War Mammoth | LEB | 3/3 | 4 | 1350 | 1200 | trample+150 |
| Ironroot Treefolk | LEB | 3/5 | 5 | 1200 | 2000 |  |
| Argothian Treefolk | ATQ | 3/5 | 5 | 1200 | 2000 |  |
| Gaea's Avenger | ATQ | 3/3 | 3 | 1200 | 1200 |  [was */*] |
| Cockatrice | LEB | 2/4 | 5 | 1100 | 1600 | flying+300 |
| Giant Spider | LEB | 2/4 | 4 | 1100 | 1600 | flying+300 |
| Spitting Slug | DRK | 2/4 | 3 | 1000 | 1600 |  |
| Land Leeches | DRK | 2/2 | 3 | 1000 | 800 |  |
| Scarwood Bandits | DRK | 2/2 | 4 | 1000 | 800 |  |
| Elvish Archers | LEB | 2/1 | 2 | 1000 | 400 | first+200 |
| Argothian Pixies | ATQ | 2/1 | 2 | 1000 | 400 |  |
| Thicket Basilisk | LEB | 2/4 | 5 | 800 | 1600 |  |
| PeopleOfTheWoods | DRK | 2/4 | 2 | 800 | 1600 |  [was */*] |
| Lurker | DRK | 2/3 | 3 | 800 | 1200 |  |
| Fungusaur | LEB | 2/2 | 4 | 800 | 800 |  |
| Grizzly Bears | LEB | 2/2 | 2 | 800 | 800 |  |
| Ghazban Ogre | ARN | 2/2 | 1 | 800 | 800 |  |
| Niall Silvain | DRK | 2/2 | 3 | 800 | 800 |  |
| Scarwood Goblins | DRK | 2/2 | 2 | 800 | 800 |  |
| Tracker | DRK | 2/2 | 3 | 800 | 800 |  |
| Thallid Devourer | FEM | 2/2 | 3 | 800 | 800 |  |
| Thorn Thallid | FEM | 2/2 | 3 | 800 | 800 |  |
| Scryb Sprites | LEB | 1/1 | 1 | 700 | 400 | flying+300 |
| Shanodin Dryads | LEB | 1/1 | 1 | 700 | 400 | evasion+200,walk+100 |
| Scarwood Hag | DRK | 1/1 | 2 | 600 | 400 |  |
| Timber Wolves | LEB | 1/1 | 1 | 500 | 400 | banding+100 |
| Marsh Viper | DRK | 1/2 | 4 | 400 | 800 |  |
| Thelonite Monk | FEM | 1/2 | 4 | 400 | 800 |  |
| Ley Druid | LEB | 1/1 | 3 | 400 | 400 |  |
| Llanowar Elves | LEB | 1/1 | 1 | 400 | 400 |  |
| Nafs Asp | ARN | 1/1 | 1 | 400 | 400 |  |
| Wyluli Wolf | ARN | 1/1 | 2 | 400 | 400 |  |
| Citanul Druid | ATQ | 1/1 | 2 | 400 | 400 |  |
| ElvesOfDeepShadow | DRK | 1/1 | 1 | 400 | 400 |  |
| Savaen Elves | DRK | 1/1 | 1 | 400 | 400 |  |
| Scavenger Folk | DRK | 1/1 | 1 | 400 | 400 |  |
| Whippoorwill | DRK | 1/1 | 1 | 400 | 400 |  |
| Elvish Hunter | FEM | 1/1 | 2 | 400 | 400 |  |
| Elvish Scout | FEM | 1/1 | 1 | 400 | 400 |  |
| Thallid | FEM | 1/1 | 1 | 400 | 400 |  |
| Thelonite Druid | FEM | 1/1 | 3 | 400 | 400 |  |
| Wall of Ice | LEB | 0/7 | 3 | 0 | 2800 | [wall] |
| Carnivorous Plant | DRK | 4/5 | 4 | 0 | 2000 | [wall] |
| Wall of Brambles | LEB | 2/3 | 3 | 0 | 1200 | [wall] |
| Wall of Wood | LEB | 0/3 | 1 | 0 | 1200 | [wall] |
| Singing Tree | ARN | 0/3 | 4 | 0 | 1200 |  |
| VerduranEnchantrss | LEB | 0/2 | 3 | 0 | 800 |  |
| Elvish Farmer | FEM | 0/2 | 2 | 0 | 800 |  |
| Birds of Paradise | LEB | 0/1 | 1 | 0 | 400 |  |
| Spore Flower | FEM | 0/1 | 2 | 0 | 400 |  |
| Killer Bees | LEG | 0/1 | 3 | 0 | 400 |  |

## Colorless — 30 creatures

| Card (in-game) | Set | P/T | ★ | ATK | DEF | note |
|---|---|---|---|--:|--:|---|
| Colossus of Sardia | ATQ | 9/9 | 9 | 3750 | 3600 |  |
| Juggernaut | LEB | 5/3 | 4 | 2200 | 1200 | evasion+200 |
| Mishra'sWarMachine | ATQ | 5/5 | 7 | 2100 | 2000 |  |
| Urza's Avenger | ATQ | 4/4 | 6 | 2000 | 1600 |  |
| Bronze Horse | LEG | 4/4 | 7 | 1750 | 1600 |  |
| Obsianus Golem | LEB | 4/6 | 6 | 1600 | 2400 |  |
| Su-Chi | ATQ | 4/4 | 4 | 1600 | 1600 |  |
| Diabolic Machine | DRK | 4/4 | 7 | 1600 | 1600 |  |
| Shapeshifter | ATQ | 4/3 | 6 | 1600 | 1200 |  [was */*] |
| Primal Clay | ATQ | 3/3 | 4 | 1200 | 1200 | [wall] [was */*] |
| Coal Golem | DRK | 3/3 | 5 | 1200 | 1200 |  |
| Marble Priest | LEG | 3/3 | 5 | 1200 | 1200 |  |
| Clay Statue | ATQ | 3/1 | 4 | 1200 | 400 |  |
| Grapeshot Catapult | ATQ | 2/3 | 4 | 1100 | 1200 |  |
| Scarecrow | DRK | 2/2 | 5 | 1100 | 800 |  |
| Dancing Scimitar | ARN | 1/5 | 4 | 800 | 2000 | flying+300,evasion+200 |
| Onulet | ATQ | 2/2 | 3 | 800 | 800 |  |
| Tetravus | ATQ | 1/1 | 6 | 700 | 400 |  |
| Battering Ram | ATQ | 1/1 | 2 | 500 | 400 |  |
| Yotian Soldier | ATQ | 1/4 | 3 | 400 | 1600 |  |
| Brass Man | ARN | 1/3 | 1 | 400 | 1200 |  |
| Dragon Engine | ATQ | 1/3 | 3 | 400 | 1200 |  |
| Triskelion | ATQ | 1/1 | 6 | 400 | 400 |  |
| Sentinel | LEG | 1/1 | 4 | 400 | 400 |  |
| Living Wall | LEB | 0/6 | 4 | 0 | 2400 | [wall] |
| Clockwork Beast | LEB | 0/4 | 6 | 0 | 1600 |  |
| Clockwork Avian | ATQ | 0/4 | 5 | 0 | 1600 |  |
| Wall of Spears | ATQ | 2/3 | 3 | 0 | 1200 | [wall] |
| Ornithopter | ATQ | 0/2 | 0 | 0 | 800 |  |
| Necropolis | DRK | 0/1 | 5 | 0 | 400 | [wall] |

## Compacted in-game names

- Dwarven Demolition Team → **DwarvenDemolitnTeam** [LEB]
- Goblin Balloon Brigade → **GoblnBalloonBrigade** [LEB]
- Merfolk of the Pearl Trident → **MerfolkPearlTridnt** [LEB]
- Mons's Goblin Raiders → **Mons'sGoblinRaidrs** [LEB]
- Personal Incarnation → **PersonalIncarnatn** [LEB]
- Two-Headed Giant of Foriys → **TwoHeadGiantForiys** [LEB]
- Verduran Enchantress → **VerduranEnchantrss** [LEB]
- Island Fish Jasconius → **IslandFishJascnus** [ARN]
- Repentant Blacksmith → **RepentntBlacksmith** [ARN]
- Stone-Throwing Devils → **StoneThrowngDevils** [ARN]
- Argivian Archaeologist → **ArgivianArchaeolg** [ATQ]
- Argivian Blacksmith → **ArgivinBlacksmith** [ATQ]
- Dwarven Weaponsmith → **DwarvnWeaponsmith** [ATQ]
- Mishra's War Machine → **Mishra'sWarMachine** [ATQ]
- Elves of Deep Shadow → **ElvesOfDeepShadow** [DRK]
- Frankenstein's Monster → **FrankensteinMonstr** [DRK]
- Goblins of the Flarg → **GoblinsOfTheFlarg** [DRK]
- People of the Woods → **PeopleOfTheWoods** [DRK]
- Sisters of the Flame → **SistersOfTheFlame** [DRK]
- Icatian Moneychanger → **IcatianMoneychngr** [FEM]
- Icatian Skirmishers → **IcatianSkirmishrs** [FEM]
- Initiates of the Ebon Hand → **InitiatesEbonHand** [FEM]
- Order of the Ebon Hand → **OrderOfTheEbonHand** [FEM]
- Vodalian War Machine → **VodalianWarMachine** [FEM]
- Clergy of the Holy Nimbus → **ClergyHolyNimbus** [LEG]
- Keepers of the Faith → **KeepersOfTheFaith** [LEG]

## Running capacity — POOL FULL
| | used | free |
|---|--:|--:|
| Creatures | 322 | — |
| Noncreatures (fields/equips/burn/wipe/heal/seal) | ~25 | — |
| Total cards (365 slots) | ~347 | ~18 |
| **Name pool (4480 tiles)** | ~4166 + ~250 noncreature | ~64 |

---
# Noncreatures — the rundown

200 noncreatures. The engine's spell vocabulary is a **fixed ~10 effect families** (the
53 verbs, but most are field/heal/burn/equip variants — see `docs/NOTES.md`). A
noncreature is convertible **only if it maps onto one of those families**; new effect
types need assembly, and the ROM cannot grow. Most of MTG's noncreature identity —
mana, countermagic, card draw, tutors, land/permanent destruction, persistent global
enchantments — has **no engine primitive** and simply cannot come across.

## Maps cleanly today (data-only)

**Basic lands → field verbs `$03`–`$08` (5 of 5).** Plains/Island/Swamp/Mountain/Forest
*are* the color fields. This is the land→color pump already designed. Wasteland is the
6th field = colorless. Clean and iconic.

**Stat-buff auras → equip slots `$15`–`$2E`.** 26 slots exist; only auras that *add*
combat stats map (the equip apply path only adds; ability grants and debuffs don't). The
curated list so far (**11 of 26 slots**):

| Aura | set | color | effect | as equip |
|---|---|---|---|---|
| Holy Strength | LEB | White | +1/+2 | +400 / +800 |
| Holy Armor | LEB | White | +0/+2 | +0 / +800 |
| Blessing | LEB | White | +1/+1 (activated) | +400 / +400 |
| Unholy Strength | LEB | Black | +2/+1 | +800 / +400 |
| Firebreathing | LEB | Red | +1/+0 (activated) | +400 / +0 |
| Web | LEB | Green | +0/+2 | +0 / +800 |
| Aspect of Wolf | LEB | Green | +X/+Y (Forest count) | ~+800/+800 |
| Unstable Mutation | ARN | Blue | +3/+3 | +1200/+1200 |
| Coral Helm | ATQ | Colorless | +3/+3 (artifact) | +1200/+1200 |
| Tawnos's Weaponry | ATQ | Colorless | +2/+2 (artifact) | +800/+800 |
| Thrull Retainer | FEM | Black | +1/+1 | +400/+400 |

Ability-granting auras (Flight, the protection Wards, Regeneration, Control Magic, Fear)
and debuffs (Weakness) don't map. The equip zone stays mostly *unfilled* by these sets:
either leave slots on DM1's gear, or (a liberty) reskin ability auras and pump *spells*
(Giant Growth, Berserk) as flat stat equips. Color-locking uses `p2colors.py equips`.

**Wrath of God → Dark Hole `$13` (destroy all monsters).** Exact, iconic, one card.

**Burn → burn verbs `$0E`–`$12` (5 of 5, a perfect fit):** Lightning Bolt (3),
Psionic Blast (4), Fireball (X), Disintegrate (X), Drain Life (X). Five real damage
spells for five burn magnitudes.

**Color-hate → Dragon Capture Jar `$31`, sealed color = COLORLESS (decided).** The seal
target is a single hardcoded immediate — `$5B41 cp $00` (file **`0x0DB42`**), which compares
the monster's type byte (= color in P2) against `$00`. Changing that one byte to the
**Colorless** enum value makes the seal hit all colorless/artifact creatures: an
**artifact-hate** card (a lock, not literal destruction — "artifact destruction *kind of*"),
reskinned from Shatter / Crumble / Disenchant. Only one sealed color is possible (it's one
routine, and the verb table is full 54/54), so Colorless is the pick. **Cost: a 1-byte
edit**, applied once we finalize the color→type-byte enum.

## Maps with a compromise / tier-2 assembly

- **Targeted destruction (Terror, Tunnel)** → no single-target verb; Raigeki `$14`
  ("destroy all **enemy** monsters") is the closest, so Terror becomes heavy-handed.
- **Life gain** → heal verbs `$09`–`$0D` exist, but Beta's only clean spell is Healing
  Salve; the rest is passive/triggered artifacts (Ivory Cup, Crystal Rod) that don't map.
  Heal slots would be filled with invented/reskinned cards, not source-faithful ones.
- **Earthquake / Hurricane** (damage all non-flyers / flyers) → partial: no flying in
  DM1, so Earthquake ≈ mass damage (Dark-Hole-ish), Hurricane ≈ nothing.
- **"Skip your attacks / must attack" (Siren's Call, Falter)** → loosely Swords of
  Revealing Light `$32` / Stop Defence `$30`.

## Cannot come across (no primitive; listed so they're not attempted)

- **Mana (14):** Black Lotus, the five Moxen, Sol Ring, Dark Ritual, Channel, Fastbond,
  Mana Flare… — DM1 has no resource system. Dead.
- **Counterspells (7):** Counterspell, Power Sink, Spell Blast, the Elemental Blasts'
  counter mode… — no stack.
- **Draw / tutor / bounce / recursion (7+):** Ancestral Recall, Braingeyser, Timetwister,
  Demonic Tutor, Regrowth, Raise Dead, Unsummon — no draw/hand/graveyard interaction.
- **Nonbasic/dual lands (10):** Tundra, Underground Sea, Badlands… — only 6 fields exist.
- **Permanent/global enchantments & artifacts (bulk of the rest):** Armageddon, Balance,
  The Abyss, Nether Void, Winter Orb, Howling Mine, Black Vise, Bad Moon, Icy
  Manipulator, land destruction (Stone Rain/Sinkhole/Ice Storm), Disenchant/Shatter
  (no artifacts/enchantments exist on the field to destroy) — all rely on persistent
  board state the engine doesn't track.

## Bottom line
From 200 noncreatures, a **source-faithful** alpha yields only: **6 fields** (lands),
**7 stat-buff equips**, **5 burns**, **1 board wipe (Wrath)**, **1 color-hate seal**, and
**1 heal** (Healing Salve) — ~20 real slots of the 50 in the #301–350 spell zone. The
equip zone stays half-empty unless we take liberties (reskin ability auras and pump spells
as flat stat gear). The other ~165 noncreatures are MTG's resource/interaction layer —
mana, counters, draw, tutors, land/permanent destruction, global enchantments — which this
engine fundamentally does not model. The conversion's spell identity therefore comes from
**a handful of equips + burn + the land/color system**, not MTG's spell suite.
