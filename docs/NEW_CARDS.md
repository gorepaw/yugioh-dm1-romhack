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

## Apprentice Illusion Magician

| | |
|---|---|
| **In-game name** | `AprnticeIlusnMagc` — 17 tiles |
| **ATK / DEF** | 2000 / 1700 |
| **Type** | Spellcaster |
| **Flavour** | `Novice of the dark` (18) / `magician's craft.` (16) |
| **Slot zone** | either — no fusion involvement yet |

*Not representable:* Level 6, DARK.

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
| **Type** | Spellcaster |
| **Flavour** | `The magician rides` (18) / `armed for war.` (14) |
| **Slot zone** | **#1–#300 required** — it is a Fusion result |

Fusion: *Dark Magician + 1 Warrior monster*. Same as Amulet Dragon — no "any monster
of type X" rule exists, so this becomes one explicit row per Warrior we allow.

*Not representable:* Level 8, DARK, Fusion/Effect subtype, the effect text.

---

## Dark Eradicator Warlock

| | |
|---|---|
| **In-game name** | `EradicatorWarlock` — 17 tiles |
| **ATK / DEF** | 2500 / 2100 |
| **Type** | Spellcaster |
| **Flavour** | `Burns all it finds` (17) / `to bitter ash.` (14) |
| **Slot zone** | either — no fusion involvement yet |

Name note: the full name is 23 characters. `DarkEradicWarlock` (17) is the alternative
if you'd rather keep "Dark" than "Warlock" intact.

*Not representable:* Level 7, DARK.

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

## Dark Magician Girl the Magician's Apprentice

| | |
|---|---|
| **In-game name** | `DMGirl:Aprentice` — 16 tiles |
| **ATK / DEF** | 2000 / 1700 |
| **Type** | Spellcaster |
| **Flavour** | `Still learning the` (17) / `dark master's art.` (17) |
| **Slot zone** | either — no fusion involvement yet |

Name note: full name is 44 characters. Alternative: `DMGirlMagAprntce` (16).

*Not representable:* Level 6, DARK.

---

## ⚠ Stat collisions

DM1 has no effects, so **two cards with the same type and the same ATK/DEF are
mechanically identical** — only name, art and flavour differ. Three entries currently
collide:

| Card | Stats | Type |
|---|---|---|
| Apprentice Illusion Magician | 2000 / 1700 | Spellcaster |
| Dark Magician Girl | 2000 / 1700 | Spellcaster |
| Dark Magician Girl the Magician's Apprentice | 2000 / 1700 | Spellcaster |

That is faithful to the real cards, and is fine if they're intended as
same-card-different-art. If they should feel distinct in play, the only lever the
engine offers is nudging ATK/DEF apart.

---

## Running budget

| | |
|---|---|
| Cards recorded | 8 |
| Name tiles used by new cards | 130 |
| Fusion-zone (#1–#300) slots required | 4 |
| Free-zone (#351–365) eligible | 4 |

The name pool is zero-slack, so every new name must be paid for by retiring an
existing card's name of equal or greater length. That accounting starts once the
retirement list exists. Note the fusion-zone requirement already exceeds nothing yet,
but four of eight cards cannot use the free tail — they must displace existing
monsters in #1–#300.
