# Project 1 — new card list

Cards to add to the pool. **Nothing here is in the ROM yet** — this is the design
sheet. Entries are appended as they're chosen; flavour text is written to fit the
engine and does not need approval.

## What the engine can and cannot represent

DM1 has **no attributes, no levels, no card effects, and no traps**. A card is
exactly five things: name, type, ATK, DEF, flavour text. Everything else on a modern
card is recorded below under *Not representable* purely for reference.

| Field | Limit |
|---|---|
| Name | shares a 4480-byte pool with all 365 cards; longest stock name is **18 tiles** |
| Flavour | **2 lines × 18 tiles**; line 1 is padded to 18 so line 2 starts its own row |
| Type | one of the 21-value enum only (no attributes) |
| ATK / DEF | BCD, 0–9999 |

Ligatures `il li ll l! 's 't` each cost **one tile**, so some names are cheaper than
their letter count — `IllusionMagician` is 16 characters but 15 tiles.

**Slot zoning matters.** Fusion only reaches cards **#1–#300**, so any card that is a
fusion result *or* a fusion material must occupy that range, which means overwriting
an existing monster. Cards #351–365 are free and unreferenced but fusion-blind.
Spells live at #301–350.

Tile counts below are measured with the real encoder, not estimated.

**Removed (owner decisions).** First cull — three exact stat-clones of the existing
Dark Magician (2500/2100 Spellcaster): *Dark Eradicator Warlock*, *Magician of Black
Magic*, *Magician of Chaos*. Second cull — six redundant within-set duplicates:
*Apprentice Illusion Magician*, *DMG the Magician's Apprentice*, *Dark Magician of
Destruction*, *Magician of Dark Chaos*, *Magician of Dark Illusion*, and *Timaeus the
United Magical Dragon* (its fusion-result role passed to Timaeus the United Dragon).
Two cards were **retyped to Warrior** to break their remaining collisions: Dark
Cavalry and Red-Eyes Dark Dragoon.

---

## Amulet Dragon

| | |
|---|---|
| **In-game name** | `Amulet Dragon` — 13 tiles |
| **ATK / DEF** | 2900 / 2500 |
| **Type** | Dragon |
| **Flavour** | `Dragon born of the` (18) / `Magician's power.` (16) |
| **Slot zone** | **#1–#300 required** — it is a Fusion result |

Fusion: *Dark Magician + 1 Dragon monster*. The engine has no "any monster of type X"
rule — every recipe is an explicit pair — so this becomes one row per Dragon we want
to allow, i.e. Dark Magician + each chosen Dragon. That is cheap: there are 736 spare
rows currently pointing at Flame Swordsman and Zombie Warrior.

*Not representable:* Level 8, DARK, Fusion/Effect subtype, the effect text.

---

## Chronicle Magician

| | |
|---|---|
| **In-game name** | `Chronicle Magician` — 18 tiles (at the ceiling) |
| **ATK / DEF** | 2500 / 2500 |
| **Type** | Spellcaster |
| **Flavour** | `Keeper of the ages` (18) / `and their secrets.` (18) |
| **Slot zone** | either — no fusion involvement yet |

*Not representable:* Level 7, DARK.

---

## Dark Cavalry

| | |
|---|---|
| **In-game name** | `Dark Cavalry` — 12 tiles |
| **ATK / DEF** | 2800 / 2300 |
| **Type** | **Warrior** (retyped from Spellcaster to break its collision with The Dark Magicians) |
| **Flavour** | `The magician rides` (18) / `armed for war.` (14) |
| **Slot zone** | **#1–#300 required** — it is a Fusion result |

Fusion: *Dark Magician + 1 Warrior monster*. Same as Amulet Dragon — no "any monster
of type X" rule exists, so this becomes one explicit row per Warrior we allow.

*Not representable:* Level 8, DARK, Fusion/Effect subtype, the effect text.

---

## Dark Magician Girl

| | |
|---|---|
| **In-game name** | `Dark Magician Girl` — 18 tiles (at the ceiling) |
| **ATK / DEF** | 2000 / 1700 |
| **Type** | Spellcaster |
| **Flavour** | `The magician's own` (17) / `bright pupil.` (12) |
| **Slot zone** | **#1–#300 required** — it is a Fusion *material* |

Material for Dark Magician Girl the Dragon Knight, so it must sit in the fusion zone.

*Not representable:* Level 6, DARK.

---

## Dark Magician Girl the Dragon Knight

| | |
|---|---|
| **In-game name** | `DMGirl:DrgnKnight` — 17 tiles |
| **ATK / DEF** | 2600 / 1700 |
| **Type** | Dragon |
| **Flavour** | `Rides a dragon in` (17) / `her master's name.` (17) |
| **Slot zone** | **#1–#300 required** — it is a Fusion result |

Fusion: *Dark Magician Girl + 1 Dragon monster* — one row per allowed Dragon.
Name note: full name is 36 characters. The colon-and-dropped-vowels style matches the
stock `Gaia:DrgnChampion`. Alternative: `MagGirlDrgnKnight` (17).

*Not representable:* Level 7, DARK, Fusion/Effect subtype, the effect text.

---

## Dark Magician of Chaos

| | |
|---|---|
| **In-game name** | `DarkMagicianChaos` — 17 tiles |
| **ATK / DEF** | 2800 / 2600 |
| **Type** | Spellcaster |
| **Flavour** | `Chaos remade the` (16) / `master magician.` (16) |
| **Slot zone** | either |

*Not representable:* Level 8, DARK.

---

## Dark Magician the Knight of Dragon Magic

| | |
|---|---|
| **In-game name** | `DarkMagicianKnight` — 18 tiles |
| **ATK / DEF** | 2900 / 2400 |
| **Type** | Dragon |
| **Flavour** | `Dragon and mage` (15) / `joined as one.` (14) |
| **Slot zone** | **#1–#300 required** — Fusion result |

Fusion: *Dark Magician + 1 Level 7+ Dragon or Warrior*. No levels exist, so the
"Level 7 or higher" gate is unrepresentable — pick the partner list by hand.

*Not representable:* Level 8, DARK, Fusion/Effect subtype, the level condition.

---

## Dark Paladin

| | |
|---|---|
| **In-game name** | `Dark Paladin` — 12 tiles |
| **ATK / DEF** | 2900 / 2400 |
| **Type** | Spellcaster |
| **Flavour** | `Mage and blade in` (17) / `a single hand.` (14) |
| **Slot zone** | **#1–#300 required** — Fusion result |

Fusion: *Dark Magician + Buster Blader*. The only recipe so far that is a clean
two-card pair with no type/level wildcard — it maps to the engine exactly as printed,
one row. **Buster Blader must therefore also be added, in #1–#300.**

*Not representable:* Level 8, DARK, Fusion/Effect subtype.

---

## Dark Sage

| | |
|---|---|
| **In-game name** | `Dark Sage` — 9 tiles |
| **ATK / DEF** | 2800 / 3200 |
| **Type** | Spellcaster |
| **Flavour** | `Ancient wisdom in` (17) / `a frail body.` (12) |
| **Slot zone** | either |

Highest DEF of any card recorded so far, and the only one whose DEF exceeds its ATK
by a wide margin — it will play very differently from the rest of the Spellcasters.

*Not representable:* Level 9, DARK.

---

## Illusion of Chaos

| | |
|---|---|
| **In-game name** | `Illusion of Chaos` — 16 tiles |
| **ATK / DEF** | 2100 / 2500 |
| **Type** | Spellcaster |
| **Flavour** | `A mirage born of` (16) / `the chaos void.` (15) |
| **Slot zone** | either |

*Not representable:* Level 7, DARK.

---

## Magician's Robe

| | |
|---|---|
| **In-game name** | `Magician's Robe` — 14 tiles |
| **ATK / DEF** | 700 / 2000 |
| **Type** | Spellcaster |
| **Flavour** | `Cloth that guards` (17) / `its wearer well.` (15) |
| **Slot zone** | either |

*Not representable:* Level 2, DARK.

---

## Magician's Rod

| | |
|---|---|
| **In-game name** | `Magician's Rod` — 13 tiles |
| **ATK / DEF** | 1600 / 100 |
| **Type** | Spellcaster |
| **Flavour** | `A rod that strikes` (18) / `but cannot shield.` (18) |
| **Slot zone** | either |

*Not representable:* Level 3, DARK.

---

## Master of Chaos

| | |
|---|---|
| **In-game name** | `Master of Chaos` — 15 tiles |
| **ATK / DEF** | 3000 / 2500 |
| **Type** | Spellcaster |
| **Flavour** | `Chaos itself bows` (17) / `to his command.` (15) |
| **Slot zone** | **#1–#300 required** — Fusion result |

Fusion: *Dark Magician + 1 "Chaos" or "Black Luster Soldier" Ritual Monster*. There
are no rituals in this engine; the partner list is chosen by hand. Black Luster
Soldier already exists as #364 — but that slot is **outside the fusion zone**, so
using it as a material means moving it into #1–#300.

*Not representable:* Level 8, DARK, Fusion/Effect subtype, ritual condition.

---

## Red-Eyes Dark Dragoon

| | |
|---|---|
| **In-game name** | `RedEyesDarkDragoon` — 18 tiles |
| **ATK / DEF** | 3000 / 2500 |
| **Type** | **Warrior** (retyped from Spellcaster to break its collision with Master of Chaos) |
| **Flavour** | `Mage astride the` (16) / `black dragon.` (13) |
| **Slot zone** | **#1–#300 required** — Fusion result |

Fusion: *Dark Magician + Red-Eyes Black Dragon* (or any Dragon effect monster).
Red-Eyes already exists as **#82**, comfortably inside the fusion zone, so the
headline recipe maps directly with no relocation.

> ⚠ **New collision from the retype.** As a Warrior 3000/2500 it now exactly matches
> the existing **Black Luster Soldier (#364)**. Since BLS is already flagged for
> relocation/retirement (it sits outside the fusion zone), this may be moot — but if
> both survive, nudge one stat (e.g. Dragoon to 3000/2400) to keep them distinct.

*Not representable:* Level 8, DARK, Fusion/Effect subtype.

---

## The Dark Magicians

| | |
|---|---|
| **In-game name** | `The Dark Magicians` — 18 tiles |
| **ATK / DEF** | 2800 / 2300 |
| **Type** | Spellcaster |
| **Flavour** | `Master and pupil` (15) / `cast as one.` (12) |
| **Slot zone** | **#1–#300 required** — Fusion result |

Fusion: *Dark Magician or Dark Magician Girl + 1 Spellcaster*. Two wildcards, so this
expands to a hand-picked list against both.

*Not representable:* Level 8, DARK, Fusion/Effect subtype.

---

## The Egyptian God cards

All three are **4000 / 4000** with no effects. The engine has no Divine-Beast type, so
each takes a different existing type — which is not merely cosmetic: **the terrain
tables give ±30% by type**, so the type choice is the only thing that makes them play
differently from one another.

| Card | In-game name | ATK/DEF | Type | Flavour |
|---|---|---|---|---|
| Obelisk the Tormentor | `ObeliskTormentor` (15) | 4000/4000 | Fiend | `The god of the` (14) / `tormenting fist.` (16) |
| Slifer the Sky Dragon | `SliferSkyDragon` (14) | 4000/4000 | Dragon | `The sky serpent` (15) / `of the storm god.` (17) |
| The Winged Dragon of Ra | `WingedDragonOfRa` (16) | 4000/4000 | Winged Beast | `The sun god sealed` (18) / `in golden wings.` (16) |

At 4000 these become the strongest cards in the game by a wide margin — the current
apex is Perfect Great Moth at 3500, and Yami Yugi's best is Black Skull Dragon at
3200. On matching terrain a God card reaches **5200**.

*Not representable:* Level 10, DIVINE, Divine-Beast type, all effects.

---

## Buster Blader

| | |
|---|---|
| **In-game name** | `Buster Blader` — 13 tiles |
| **ATK / DEF** | 2600 / 2300 |
| **Type** | Warrior |
| **Flavour** | `Trained to slay` (15) / `the great dragons.` (18) |
| **Slot zone** | **#1–#300 required** — Fusion *material* |

The keystone the whole Dark Magician fusion line has been waiting on: material for
**Dark Paladin** (Dark Magician + Buster Blader), **Buster Blader the Dragon Destroyer
Swordsman**, and **Buster Dragon**. Must live in the fusion zone.

*Not representable:* Level 7, EARTH.

---

## Buster Blader, the Dragon Destroyer Swordsman

| | |
|---|---|
| **In-game name** | `BusterBladeDrgnDst` — 18 tiles |
| **ATK / DEF** | 2800 / 2500 |
| **Type** | Warrior |
| **Flavour** | `Sworn to end every` (18) / `winged dragon.` (14) |
| **Slot zone** | **#1–#300 required** — Fusion result |

Fusion: *Buster Blader + 1 Dragon* — a hand-picked partner list.
Name alternatives: `BladerDrgnDestroyr` (18), `BusterDragonSlayer` (18).

*Not representable:* Level 8, LIGHT, Fusion/Effect subtype.

---

## Buster Dragon

| | |
|---|---|
| **In-game name** | `Buster Dragon` — 13 tiles |
| **ATK / DEF** | 1200 / 2800 |
| **Type** | Dragon |
| **Flavour** | `The sword itself` (16) / `reborn as a beast.` (18) |
| **Slot zone** | **#1–#300 required** — Fusion result |

Fusion: *a Warrior + a Dragon*. A defensive body (2800 DEF), unusual in this set.

*Not representable:* Level 8, DARK, Fusion/Effect subtype.

---

## Legendary Knight Timaeus

| | |
|---|---|
| **In-game name** | `LegndKnghtTimaeus` — 17 tiles |
| **ATK / DEF** | 2800 / 1800 |
| **Type** | Warrior |
| **Flavour** | `Sworn knight of` (15) / `the eye of time.` (16) |
| **Slot zone** | either |

Name alternatives: `Knight Timaeus` (14), `Timaeus the Knight` (18). Warrior 2800/1800,
so it shares stats with Timaeus the United Dragon (Dragon 2800/1800) but the type
differs — they play differently on terrain, not a hard collision.

*Not representable:* Level 8, LIGHT.

---

## Timaeus the United Dragon

| | |
|---|---|
| **In-game name** | `TimaeusUnitedDragn` — 18 tiles |
| **ATK / DEF** | 2800 / 1800 |
| **Type** | Dragon |
| **Flavour** | `The knight who` (14) / `sealed the dragon.` (18) |
| **Slot zone** | **#1–#300 required** — Fusion result |

Now the Timaeus fusion **result** (inherited from the cut *Timaeus the United Magical
Dragon*). Its former recipe *Timaeus the United Dragon + Dark Magician* was
self-referential once the Magical form was cut, so the recipe is **open** — the
natural fit is *Legendary Knight Timaeus + Dark Magician* (knight unites with the
mage's power), a clean two-card pair. Flag if you'd prefer a different pairing.
Name alternatives: `Timaeus the Dragon` (18), `TimaeusUnitdDragon` (18).

*Not representable:* Level 8, LIGHT, Fusion subtype.

---

## Timestar Magician

| | |
|---|---|
| **In-game name** | `Timestar Magician` — 17 tiles |
| **ATK / DEF** | 2400 / 1200 |
| **Type** | Spellcaster |
| **Flavour** | `Turns back the` (14) / `duel's very clock.` (17) |
| **Slot zone** | **#1–#300 required** — Fusion result |

Originally an Xyz ("Rank 4", 2 Level-4 Spellcasters). No Xyz or ranks exist, so it's
treated as a fusion of two Spellcasters — a hand-picked partner list.

*Not representable:* Rank 4 / Xyz, DARK, Fusion/Effect subtype.

---

## Skilled Blue Magician

| | |
|---|---|
| **In-game name** | `SkilledBlueMagicin` — 17 tiles |
| **ATK / DEF** | 1800 / 1800 |
| **Type** | Spellcaster |
| **Flavour** | `Adept in the art` (16) / `of blue magic.` (14) |
| **Slot zone** | either |

*Not representable:* Level 4, LIGHT, spell-counter effect.

---

## Skilled Dark Magician

| | |
|---|---|
| **In-game name** | `SkilledDarkMagicin` — 17 tiles |
| **ATK / DEF** | 1900 / 1700 |
| **Type** | Spellcaster |
| **Flavour** | `Adept in the art` (16) / `of dark magic.` (14) |
| **Slot zone** | either |

*Not representable:* Level 4, DARK, spell-counter effect.

---

## Skilled White Magician

| | |
|---|---|
| **In-game name** | `SkilledWhiteMagicn` — 17 tiles |
| **ATK / DEF** | 1700 / 1900 |
| **Type** | Spellcaster |
| **Flavour** | `Adept in the art` (16) / `of white magic.` (15) |
| **Slot zone** | either |

*Not representable:* Level 4, LIGHT, spell-counter effect.

---

## ⚠ Stat collisions

DM1 has no effects, so **two cards with the same type and the same ATK/DEF are
mechanically identical** — only name, art and flavour differ. After the second cull
(6 cards) and two retypes (Dark Cavalry → Warrior, Red-Eyes Dark Dragoon → Warrior),
**every within-set hard collision is resolved.** The remaining near-collisions differ
only by type, which the terrain tables (±30%) make matter:

| Stats | Cards (differ by type) |
|---|---|
| 2900/2400 | DarkMagicianKnight [Dragon] · Dark Paladin [Spellcaster] |
| 2800/1800 | TimaeusUnitedDragn [Dragon] · LegndKnghtTimaeus [Warrior] |
| 4000/4000 | Obelisk [Fiend] · Slifer [Dragon] · Ra [Winged Beast] — intentional |

One collision now exists **against an existing ROM card**: retyping Red-Eyes Dark
Dragoon to Warrior 3000/2500 makes it match **Black Luster Soldier (#364)**. BLS is
already flagged for relocation/retirement (it's outside the fusion zone), so this is
likely moot — but noted on the Dragoon entry.

---

## Running budget

| | |
|---|---|
| Cards recorded | **27** |
| Name tiles required | **420** |
| Fusion-zone (#1–#300) slots required | **14** |
| Free-zone (#351–365) eligible | 13 (15 slots exist) |

### ⚠ The name pool does not balance

The pool is 4480 tiles with **zero free**, stock average 12.3 tiles/card. Adding 27
cards by overwriting 27 existing ones does **not** pay for itself:

| | Tiles |
|---|---|
| Cost of the 27 new names | 420 |
| Freed by retiring 27 *average* cards | 332 |

To break even purely by name length you'd retire **at least 24 cards from the
longest-named end** — and the real retirement list is chosen for weakness, not name
length, so it will free less and fall short. This remains the binding constraint and
points at the pending **name-pool relocation** task: bank 1's pool ends exactly at
`$7FFF`, so growing it means finding 4480+ contiguous free bytes in another bank and
re-pointing the reader.

### Fusion-zone pressure

**14 of 27 cards must live in #1–#300** (fusion can't reach above #300), displacing 14
existing monsters from the fusion range; the free tail #351–365 can't hold any of
them. The 13 non-fusion cards fit the 15-slot tail with 2 to spare — so this batch no
longer forces an extra displacement beyond the 14. **Net: at least 14 existing
monsters retired to seat this roster.** Related: Black Luster Soldier (#364) is outside
the fusion zone, so using it as a Master of Chaos material means relocating it too.

The retirement list is the next thing to build.
