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
| **In-game name** | `IllusionMagician` — 15 tiles |
| **ATK / DEF** | 2000 / 1700 |
| **Type** | Spellcaster |
| **Flavour** | `Novice of the dark` (18) / `magician's craft.` (16) |
| **Slot zone** | either — no fusion involvement yet |

Name note: the full "Apprentice Illusion Magician" is 28 characters and cannot fit.
`IllusionMagician` keeps the recognisable half and is the cheapest option at 15 tiles.
Alternatives if you'd rather keep "Apprentice": `ApprenticeMagicn` (16) or
`AprnticeIlusnMagc` (17). Flag a preference and it changes here, not in the ROM.

*Not representable:* Level 6, DARK.

---

## Running budget

| | |
|---|---|
| Cards recorded | 2 |
| Name tiles used by new cards | 28 |
| Fusion-zone (#1–#300) slots required | 1 |
| Free-zone (#351–365) eligible | 1 |

The name pool is zero-slack, so every new name must be paid for by retiring an
existing card's name of equal or greater length. That accounting starts once the
retirement list exists.
