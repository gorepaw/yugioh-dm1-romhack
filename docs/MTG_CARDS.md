# Duel Monsters MTG — MTG card conversion (multi-set)

Final roster in `work/duelmonsters-mtg/cards.json`: **300 creatures + 50 spells + 15 tokens = 365**.
Creature sources: LEB (82), DRK (59), FEM (54), ARN (37), LEG (36), ATQ (32).
(22 creatures were retired to free effect slots — see Bottom line.)
Engine/model rationale in `docs/MTG.md`; opponents in `docs/MTG_DECKS.md`.

## Conversion rules (creatures)

- **Stats: 400:1**, capped at **4000** (Elder Dragon apex); ATK-only keyword liberty
  (flying+300, first+200, trample/rampage+150, banding+100, fear/unblockable+200,
  landwalk+100; cap +400), power≥1 non-Walls only; DEF never bumped.
- **Walls → 0 ATK** (pure blockers). **Colour → the type byte.**
- **Stars = mana cost** (informational); accented names ASCII-folded; `*/*` given a
  fixed body; names >18 tiles compacted; 0/0 copy creatures cut.
- Gold cards skipped **except the 5 Elder Dragons**, placed under their shard-centre
  colour at a fixed 4000/4000.
- Sets: LEB → ARN → ATQ → DRK → FEM → curated LEG backfill; core sets/reprints skipped.

## White — 53 creatures

| # | Card | Set | ATK | DEF |
|--:|---|---|--:|--:|
| 298 | Arcades Sabboth | LEG | 4000 | 4000 |
| 265 | Akron Legionnaire | LEG | 3200 | 1600 |
| 43 | PersonalIncarnatn | LEB | 2400 | 2400 |
| 59 | Serra Angel | LEB | 1900 | 1600 |
| 273 | Righteous Avengers | LEG | 1400 | 400 |
| 108 | Moorish Cavalry | ARN | 1350 | 1200 |
| 272 | Petra Sphinx | LEG | 1200 | 1600 |
| 39 | Northern Paladin | LEB | 1200 | 1200 |
| 152 | Angry Mob | DRK | 1200 | 1200 |
| 269 | Ivory Guardians | LEG | 1200 | 1200 |
| 80 | White Knight | LEB | 1200 | 800 |
| 274 | Thunder Spirit | LEG | 1200 | 800 |
| 118 | War Elephant | ARN | 1050 | 800 |
| 247 | Order of Leitbur | FEM | 1000 | 400 |
| 237 | Icatian Phalanx | FEM | 900 | 1600 |
| 178 | Knights of Thorn | DRK | 900 | 800 |
| 229 | Hand of Justice | FEM | 800 | 2400 |
| 68 | Veteran Bodyguard | LEB | 800 | 2000 |
| 270 | KeepersOfTheFaith | LEG | 800 | 1200 |
| 42 | Pearled Unicorn | LEB | 800 | 800 |
| 121 | ArgivinBlacksmith | ATQ | 800 | 800 |
| 225 | Farrel's Zealot | FEM | 800 | 800 |
| 268 | Enchanted Being | LEG | 800 | 800 |
| 36 | Mesa Pegasus | LEB | 800 | 400 |
| 52 | Savannah Lions | LEB | 800 | 400 |
| 192 | Pikemen | DRK | 700 | 400 |
| 233 | Icatian Infantry | FEM | 700 | 400 |
| 240 | IcatianSkirmishrs | FEM | 700 | 400 |
| 271 | Osai Vultures | LEG | 700 | 400 |
| 239 | Icatian Scout | FEM | 600 | 400 |
| 2 | Benalish Hero | LEB | 500 | 400 |
| 134 | Martyrs of Korlis | ATQ | 400 | 2400 |
| 224 | Farrelite Priest | FEM | 400 | 1200 |
| 110 | RepentntBlacksmith | ARN | 400 | 800 |
| 203 | Squire | DRK | 400 | 800 |
| 235 | Icatian Lieutenant | FEM | 400 | 800 |
| 266 | D'Avenant Archer | LEG | 400 | 800 |
| 51 | Samite Healer | LEB | 400 | 400 |
| 105 | King Suleiman | ARN | 400 | 400 |
| 120 | ArgivianArchaeolg | ATQ | 400 | 400 |
| 167 | Exorcist | DRK | 400 | 400 |
| 185 | Miracle Worker | DRK | 400 | 400 |
| 193 | Preacher | DRK | 400 | 400 |
| 209 | Witch Hunter | DRK | 400 | 400 |
| 234 | Icatian Javelineers | FEM | 400 | 400 |
| 238 | Icatian Priest | FEM | 400 | 400 |
| 75 | Wall of Swords | LEB | 0 | 2000 |
| 267 | Elder Land Wurm | LEG | 0 | 2000 |
| 275 | Wall of Light | LEG | 0 | 2000 |
| 214 | Combat Medic | FEM | 0 | 800 |
| 236 | IcatianMoneychngr | FEM | 0 | 800 |
| 83 | Abu Ja'far | ARN | 0 | 400 |
| 87 | Camel | ARN | 0 | 400 |

## Blue — 51 creatures

| # | Card | Set | ATK | DEF |
|--:|---|---|--:|--:|
| 180 | Leviathan | DRK | 4000 | 4000 |
| 297 | Chromium | LEG | 4000 | 4000 |
| 279 | Elder Spawn | LEG | 2600 | 2400 |
| 215 | Deep Spawn | FEM | 2550 | 2400 |
| 101 | IslandFishJascnus | ARN | 2400 | 3200 |
| 34 | Mahamoti Djinn | LEB | 2400 | 2400 |
| 112 | Serendib Djinn | ARN | 2300 | 2400 |
| 56 | Sea Serpent | LEB | 2000 | 2000 |
| 79 | Water Elemental | LEB | 2000 | 1600 |
| 1 | Air Elemental | LEB | 1900 | 1600 |
| 44 | Phantasmal Forces | LEB | 1900 | 400 |
| 171 | Giant Shark | DRK | 1750 | 1600 |
| 46 | Pirate Ship | LEB | 1600 | 1200 |
| 90 | Dandan | ARN | 1600 | 400 |
| 113 | Serendib Efreet | ARN | 1500 | 1600 |
| 45 | Phantom Monster | LEB | 1500 | 1200 |
| 281 | Segovian Leviathan | LEG | 1400 | 1200 |
| 232 | Homarid Warrior | FEM | 1200 | 1200 |
| 261 | Vodalian Knights | FEM | 1200 | 800 |
| 170 | Ghost Ship | DRK | 1100 | 1600 |
| 276 | Azure Drake | LEG | 1100 | 1600 |
| 32 | Lord of Atlantis | LEB | 1100 | 800 |
| 250 | River Merfolk | FEM | 1000 | 400 |
| 109 | Old Man of the Sea | ARN | 800 | 1200 |
| 230 | Homarid | FEM | 800 | 800 |
| 277 | Brine Hag | LEG | 800 | 800 |
| 280 | Psionic Entity | LEG | 800 | 800 |
| 231 | Homarid Shaman | FEM | 800 | 400 |
| 95 | Flying Men | ARN | 700 | 400 |
| 284 | Zephyr Falcon | LEG | 700 | 400 |
| 278 | Devouring Deep | LEG | 600 | 800 |
| 142 | Sage of Lat-Nam | ATQ | 400 | 800 |
| 184 | Merfolk Assassin | DRK | 400 | 800 |
| 263 | Vodalian Soldiers | FEM | 400 | 800 |
| 35 | MerfolkPearlTridnt | LEB | 400 | 400 |
| 48 | Prodigal Sorcerer | LEB | 400 | 400 |
| 97 | Giant Tortoise | ARN | 400 | 400 |
| 114 | Sindbad | ARN | 400 | 400 |
| 163 | Drowned | DRK | 400 | 400 |
| 165 | Electric Eel | DRK | 400 | 400 |
| 207 | Water Wurm | DRK | 400 | 400 |
| 253 | Svyelunite Priest | FEM | 400 | 400 |
| 262 | Vodalian Mage | FEM | 400 | 400 |
| 69 | Wall of Air | LEB | 0 | 2000 |
| 76 | Wall of Water | LEB | 0 | 2000 |
| 283 | Wall of Wonder | LEG | 0 | 2000 |
| 264 | VodalianWarMachine | FEM | 0 | 1600 |
| 106 | Merchant Ship | ARN | 0 | 800 |
| 282 | Time Elemental | LEG | 0 | 800 |
| 153 | Apprentice Wizard | DRK | 0 | 400 |
| 251 | Seasinger | FEM | 0 | 400 |

## Black — 54 creatures

| # | Card | Set | ATK | DEF |
|--:|---|---|--:|--:|
| 296 | Nicol Bolas | LEG | 4000 | 4000 |
| 33 | Lord of the Pit | LEB | 3200 | 2800 |
| 293 | Cosmic Horror | LEG | 3000 | 2800 |
| 150 | Yawgmoth Demon | ATQ | 2800 | 2400 |
| 295 | Mold Demon | LEG | 2400 | 2400 |
| 38 | Nightmare | LEB | 2400 | 2000 |
| 220 | Ebon Praetor | FEM | 2350 | 2000 |
| 8 | Demonic Hordes | LEB | 2000 | 2000 |
| 103 | Juzam Djinn | ARN | 2000 | 2000 |
| 58 | Sengir Vampire | LEB | 2000 | 1600 |
| 187 | Nameless Race | DRK | 1600 | 1600 |
| 216 | Derelor | FEM | 1600 | 1600 |
| 4 | Bog Wraith | LEB | 1500 | 1200 |
| 102 | Junun Efreet | ARN | 1500 | 1200 |
| 294 | Fallen Angel | LEG | 1500 | 1200 |
| 164 | Eater of the Dead | DRK | 1200 | 1600 |
| 3 | Black Knight | LEB | 1200 | 800 |
| 99 | Hasran Ogress | ARN | 1200 | 800 |
| 82 | Zombie Master | LEB | 1100 | 1200 |
| 26 | Hypnotic Specter | LEB | 1100 | 800 |
| 248 | OrderOfTheEbonHand | FEM | 1000 | 400 |
| 98 | Guardian Beast | ARN | 800 | 1600 |
| 93 | Erg Raiders | ARN | 800 | 1200 |
| 204 | The Fallen | DRK | 800 | 1200 |
| 47 | Plague Rats | LEB | 800 | 800 |
| 53 | Scathe Zombies | LEB | 800 | 800 |
| 54 | Scavenging Ghoul | LEB | 800 | 800 |
| 186 | Murk Dwellers | DRK | 800 | 800 |
| 242 | Mindstab Thrull | FEM | 800 | 800 |
| 243 | Necrite | FEM | 800 | 800 |
| 259 | Thrull Champion | FEM | 800 | 800 |
| 156 | Bog Imp | DRK | 800 | 400 |
| 194 | Rag Man | DRK | 800 | 400 |
| 117 | StoneThrowngDevils | ARN | 600 | 400 |
| 157 | Bog Rats | DRK | 600 | 400 |
| 182 | Marsh Goblins | DRK | 600 | 400 |
| 88 | Cuombajj Witches | ARN | 400 | 1200 |
| 206 | Uncle Istvan | DRK | 400 | 1200 |
| 211 | Armor Thrull | FEM | 400 | 1200 |
| 140 | Priest of Yawgmoth | ATQ | 400 | 800 |
| 212 | Basal Thrull | FEM | 400 | 800 |
| 50 | Royal Assassin | LEB | 400 | 400 |
| 92 | El-Hajjaj | ARN | 400 | 400 |
| 104 | Khabal Ghoul | ARN | 400 | 400 |
| 116 | Sorceress Queen | ARN | 400 | 400 |
| 139 | Phyrexian Gremlins | ATQ | 400 | 400 |
| 149 | Xenic Poltergeist | ATQ | 400 | 400 |
| 177 | Grave Robbers | DRK | 400 | 400 |
| 241 | InitiatesEbonHand | FEM | 400 | 400 |
| 260 | Thrull Wizard | FEM | 400 | 400 |
| 70 | Wall of Bone | LEB | 0 | 1600 |
| 81 | Will-o'-the-Wisp | LEB | 0 | 400 |
| 155 | Banshee | DRK | 0 | 400 |
| 169 | FrankensteinMonstr | DRK | 0 | 400 |

## Red — 56 creatures

| # | Card | Set | ATK | DEF |
|--:|---|---|--:|--:|
| 300 | Vaevictis Asmadi | LEG | 4000 | 4000 |
| 249 | Orgg | FEM | 2550 | 2400 |
| 154 | Ball Lightning | DRK | 2550 | 400 |
| 107 | Mijae Djinn | ARN | 2400 | 1200 |
| 61 | Shivan Dragon | LEB | 2300 | 2000 |
| 14 | Fire Elemental | LEB | 2000 | 1600 |
| 65 | TwoHeadGiantForiys | LEB | 1750 | 1600 |
| 292 | Frost Giant | LEG | 1750 | 1600 |
| 12 | Earth Elemental | LEB | 1600 | 2000 |
| 62 | Stone Giant | LEB | 1500 | 1600 |
| 49 | Roc of Kher Ridges | LEB | 1500 | 1200 |
| 291 | Firestorm Phoenix | LEG | 1500 | 800 |
| 174 | Goblin Rock Sled | DRK | 1350 | 400 |
| 119 | Ydwen Efreet | ARN | 1200 | 2400 |
| 24 | Hill Giant | LEB | 1200 | 1200 |
| 30 | Keldon Warlord | LEB | 1200 | 1200 |
| 213 | Brassclaw Orcs | FEM | 1200 | 800 |
| 228 | Goblin Flotilla | FEM | 1200 | 800 |
| 9 | Dragon Whelp | LEB | 1100 | 1200 |
| 21 | Granite Gargoyle | LEB | 1100 | 800 |
| 246 | Orcish Veteran | FEM | 1000 | 800 |
| 20 | Goblin King | LEB | 900 | 800 |
| 91 | Desert Nomads | ARN | 900 | 800 |
| 25 | Hurloon Minotaur | LEB | 800 | 1200 |
| 22 | Gray Ogre | LEB | 800 | 800 |
| 27 | Ironclaw Orcs | LEB | 800 | 800 |
| 57 | Sedge Troll | LEB | 800 | 800 |
| 66 | Uthden Troll | LEB | 800 | 800 |
| 158 | Brothers of Fire | DRK | 800 | 800 |
| 173 | Goblin Hero | DRK | 800 | 800 |
| 190 | Orc General | DRK | 800 | 800 |
| 201 | SistersOfTheFlame | DRK | 800 | 800 |
| 219 | Dwarven Soldier | FEM | 800 | 400 |
| 85 | Bird Maiden | ARN | 700 | 800 |
| 168 | Fire Drake | DRK | 700 | 800 |
| 19 | GoblnBalloonBrigade | LEB | 700 | 400 |
| 160 | Cave People | DRK | 600 | 1600 |
| 11 | Dwarven Warriors | LEB | 600 | 400 |
| 175 | GoblinsOfTheFlarg | DRK | 600 | 400 |
| 41 | Orcish Artillery | LEB | 400 | 1200 |
| 124 | Atog | ATQ | 400 | 800 |
| 218 | Dwarven Lieutenant | FEM | 400 | 800 |
| 10 | DwarvenDemolitnTeam | LEB | 400 | 400 |
| 37 | Mons'sGoblinRaidrs | LEB | 400 | 400 |
| 84 | Ali Baba | ARN | 400 | 400 |
| 132 | Goblin Artisans | ATQ | 400 | 400 |
| 137 | Orcish Mechanics | ATQ | 400 | 400 |
| 172 | Goblin Digging Team | DRK | 400 | 400 |
| 176 | Goblin Wizard | DRK | 400 | 400 |
| 244 | Orcish Captain | FEM | 400 | 400 |
| 245 | Orcish Spy | FEM | 400 | 400 |
| 74 | Wall of Stone | LEB | 0 | 3200 |
| 72 | Wall of Fire | LEB | 0 | 2000 |
| 111 | Rukh Egg | ARN | 0 | 1200 |
| 217 | Dwarven Armorer | FEM | 0 | 800 |
| 227 | Goblin Chirurgeon | FEM | 0 | 800 |

## Green — 56 creatures

| # | Card | Set | ATK | DEF |
|--:|---|---|--:|--:|
| 299 | Palladia-Mors | LEG | 4000 | 4000 |
| 15 | Force of Nature | LEB | 3350 | 3200 |
| 288 | Craw Giant | LEG | 2700 | 1600 |
| 17 | Gaea's Liege | LEB | 2400 | 2400 |
| 7 | Craw Wurm | LEB | 2400 | 1600 |
| 226 | Feral Thallid | FEM | 2400 | 1200 |
| 94 | Erhnam Djinn | ARN | 1900 | 2000 |
| 210 | Wormwood Treefolk | DRK | 1800 | 1600 |
| 289 | Durkwood Boars | LEG | 1600 | 1600 |
| 290 | Elven Riders | LEG | 1600 | 1200 |
| 100 | Ifh-Biff Efreet | ARN | 1500 | 1200 |
| 78 | War Mammoth | LEB | 1350 | 1200 |
| 28 | Ironroot Treefolk | LEB | 1200 | 2000 |
| 123 | Argothian Treefolk | ATQ | 1200 | 2000 |
| 131 | Gaea's Avenger | ATQ | 1200 | 1200 |
| 6 | Cockatrice | LEB | 1100 | 1600 |
| 18 | Giant Spider | LEB | 1100 | 1600 |
| 202 | Spitting Slug | DRK | 1000 | 1600 |
| 179 | Land Leeches | DRK | 1000 | 800 |
| 197 | Scarwood Bandits | DRK | 1000 | 800 |
| 13 | Elvish Archers | LEB | 1000 | 400 |
| 122 | Argothian Pixies | ATQ | 1000 | 400 |
| 63 | Thicket Basilisk | LEB | 800 | 1600 |
| 191 | PeopleOfTheWoods | DRK | 800 | 1600 |
| 181 | Lurker | DRK | 800 | 1200 |
| 16 | Fungusaur | LEB | 800 | 800 |
| 23 | Grizzly Bears | LEB | 800 | 800 |
| 96 | Ghazban Ogre | ARN | 800 | 800 |
| 189 | Niall Silvain | DRK | 800 | 800 |
| 198 | Scarwood Goblins | DRK | 800 | 800 |
| 205 | Tracker | DRK | 800 | 800 |
| 255 | Thallid Devourer | FEM | 800 | 800 |
| 258 | Thorn Thallid | FEM | 800 | 800 |
| 55 | Scryb Sprites | LEB | 700 | 400 |
| 60 | Shanodin Dryads | LEB | 700 | 400 |
| 199 | Scarwood Hag | DRK | 600 | 400 |
| 64 | Timber Wolves | LEB | 500 | 400 |
| 183 | Marsh Viper | DRK | 400 | 800 |
| 257 | Thelonite Monk | FEM | 400 | 800 |
| 126 | Citanul Druid | ATQ | 400 | 400 |
| 166 | ElvesOfDeepShadow | DRK | 400 | 400 |
| 195 | Savaen Elves | DRK | 400 | 400 |
| 200 | Scavenger Folk | DRK | 400 | 400 |
| 208 | Whippoorwill | DRK | 400 | 400 |
| 222 | Elvish Hunter | FEM | 400 | 400 |
| 223 | Elvish Scout | FEM | 400 | 400 |
| 254 | Thallid | FEM | 400 | 400 |
| 256 | Thelonite Druid | FEM | 400 | 400 |
| 73 | Wall of Ice | LEB | 0 | 2800 |
| 159 | Carnivorous Plant | DRK | 0 | 2000 |
| 71 | Wall of Brambles | LEB | 0 | 1200 |
| 77 | Wall of Wood | LEB | 0 | 1200 |
| 115 | Singing Tree | ARN | 0 | 1200 |
| 67 | VerduranEnchantrss | LEB | 0 | 800 |
| 221 | Elvish Farmer | FEM | 0 | 800 |
| 252 | Spore Flower | FEM | 0 | 400 |

## Colorless — 30 creatures

| # | Card | Set | ATK | DEF |
|--:|---|---|--:|--:|
| 129 | Colossus of Sardia | ATQ | 3750 | 3600 |
| 29 | Juggernaut | LEB | 2200 | 1200 |
| 135 | Mishra'sWarMachine | ATQ | 2100 | 2000 |
| 147 | Urza's Avenger | ATQ | 2000 | 1600 |
| 285 | Bronze Horse | LEG | 1750 | 1600 |
| 40 | Obsianus Golem | LEB | 1600 | 2400 |
| 144 | Su-Chi | ATQ | 1600 | 1600 |
| 162 | Diabolic Machine | DRK | 1600 | 1600 |
| 143 | Shapeshifter | ATQ | 1600 | 1200 |
| 141 | Primal Clay | ATQ | 1200 | 1200 |
| 161 | Coal Golem | DRK | 1200 | 1200 |
| 286 | Marble Priest | LEG | 1200 | 1200 |
| 127 | Clay Statue | ATQ | 1200 | 400 |
| 133 | Grapeshot Catapult | ATQ | 1100 | 1200 |
| 196 | Scarecrow | DRK | 1100 | 800 |
| 89 | Dancing Scimitar | ARN | 800 | 2000 |
| 136 | Onulet | ATQ | 800 | 800 |
| 145 | Tetravus | ATQ | 700 | 400 |
| 125 | Battering Ram | ATQ | 500 | 400 |
| 151 | Yotian Soldier | ATQ | 400 | 1600 |
| 86 | Brass Man | ARN | 400 | 1200 |
| 130 | Dragon Engine | ATQ | 400 | 1200 |
| 146 | Triskelion | ATQ | 400 | 400 |
| 287 | Sentinel | LEG | 400 | 400 |
| 31 | Living Wall | LEB | 0 | 2400 |
| 5 | Clockwork Beast | LEB | 0 | 1600 |
| 128 | Clockwork Avian | ATQ | 0 | 1600 |
| 148 | Wall of Spears | ATQ | 0 | 1200 |
| 138 | Ornithopter | ATQ | 0 | 800 |
| 188 | Necropolis | DRK | 0 | 400 |

## Retired creatures (22)

Cut to free effect slots — all vanilla bodies ≤1200 power appearing in no opponent deck:

- Aladdin
- Ali from Cairo
- Amrou Kithkin
- Birds of Paradise
- ClergyHolyNimbus
- Drudge Skeletons
- DwarvnWeaponsmith
- Frozen Shade
- Hell's Caretaker
- Hurr Jackal
- Killer Bees
- Kird Ape
- Ley Druid
- Llanowar Elves
- Nafs Asp
- Nether Shadow
- Nettling Imp
- Tempest Efreet
- Tundra Wolves
- Wall of Caltrops
- Wall of Vapor
- Wyluli Wolf

## Bottom line — every effect slot is now filled (50/50)

The first pass left 24 of the engine's 50 effect-capable slots occupied by
overflow creatures and filler tokens, which made the game spell-starved. They are
now all real spells. Where the source sets had no exact analogue, the closest MTG
card was chosen and reskinned onto the existing verb — the verb is what actually
runs, so the card only has to *read* right.

| Engine effect | MTG card | Note |
|---|---|---|
| field ×6 (`$03`–`$08`) | Forest, Wastes, Mountain, Plains, Island, Swamp | the land/colour system |
| equip ×26 (`$15`–`$2E`) | Holy Strength, Holy Armor, Blessing, Unholy Strength, Firebreathing, Web, Aspect of Wolf, Unstable Mutation, Coral Helm, Tawnos's Weaponry, Thrull Retainer, **Giant Growth, Berserk, Cocoon, Divine Transformation, Infinite Authority, Giant Strength, The Brute, Rapid Fire, Burrowing, Fishliver Oil, Elven Lyre, Zelyon Sword, Spirit Shield, Living Armor, Ashnod's Transmogrant** | all 26 filled, colour-locked |
| burn ×5 (`$0E`–`$12`) | Lightning Bolt, Psionic Blast, Fireball, Disintegrate, Drain Life | exact fits |
| heal ×5 (`$09`–`$0D`) | Healing Salve, **Balm of Restoration, Dark Heart of the Wood, Fountain of Youth, Ivory Cup** | real life-gain cards |
| Dark Hole (`$13`) | Wrath of God | exact |
| Raigeki (`$14`) | Terror | destroys the foe's side |
| seal by colour (`$31`) | Shatter | retargeted to Colorless = artifact-hate |
| Stop Defence (`$30`) | **Siren's Call** | "creatures must attack" — near-exact |
| Swords of Light (`$32`) | **Festival** | "creatures can't attack this turn" |
| Spellbinding Circle (`$34`) | **Marsh Gas** | "all creatures get −2/−0" |
| Dark-Piercing Light (`$33`) | **Amnesia** | reveals the opponent's hand |
| transform (`$35`) | **Dance of Many** | creates a copy of a creature |

**Cost:** 22 creature slots. Cut per the rule "underutilized Legends cards in
overrepresented colours" — all 22 were vanilla bodies of ≤1200 power that appeared
in **no** opponent deck (8 Legends, 7 Beta, 6 Arabian Nights, 1 Antiquities).
Colours after the cut are tighter than before: R56 G56 B54 W53 U51 C30 = **exactly
300 creatures**, which now fills the fusion-reachable zone #1–300 precisely.

Final layout: **300 creatures + 50 spells + 15 tokens = 365**, name pool
4472/4480, description pool 12314/13139.
