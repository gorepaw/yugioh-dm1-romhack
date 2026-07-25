# Duel Monsters MTG — status & rebuild

**Product id:** `duelmonsters-mtg` · **data:** `work/duelmonsters-mtg/` ·
**output:** `build/duelmonsters-mtg-hack.gb` (valid 1 MB, MBC1, checksums OK,
Miyoo-safe). Sibling product is `duelmonsters-kaizo`; tools and `docs/NOTES.md`
are shared, data is never shared.

## Rebuild (three commands, fully reproducible)

```
python mtg_assemble.py                        # creatures+spells+tokens -> cards.json
python mtg_gen.py                             # decks, rewards, equips, drops, starter, fusions
python build.py --product duelmonsters-mtg    # -> build/duelmonsters-mtg-hack.gb
```

Run scripts with the full Python 3.13 interpreter path (see the `python-path`
memory); bare `python` is a broken WindowsApps shim.

## What is DONE (all verified by reading the built ROM back)

| System | State |
|---|---|
| Cards | **300 creatures + 50 spells + 15 tokens = 365**; names 4472/4480, descs 12314/13139 |
| Colours | type byte = colour (White0 Blue1 Black2 Red3 Green4 Colorless5); labels rewritten; terrain tables derived per colour |
| Spells | **all 50 effect slots filled** — 26 equips, 6 lands, 5 burns, 5 heals, Wrath, Terror, seal, Siren's Call, Festival, Marsh Gas, Amnesia, Dance of Many |
| Seal | retargeted to Colorless = artifact-hate (1 byte at `0x0DB42`) |
| Equips | 26 colour-locked, pool 2542/2642 |
| Opponents | 16 named; decks strictly ascending 528 → 2430 avg ATK across the 4/9/3 stages |
| Rewards | 16 × 10 — the 10 best of each deck by `max(ATK,DEF)`, weakest → best |
| Drops | 16 pools, **365/365 cards obtainable**, all Elder Dragons from Yawgmoth |
| Fusions | 2159 rows, same-colour ladder, all 6 capstones reachable, 0 downgrades |
| Starter | 100 cards (90 creatures capped at ATK≤800 and ATK+DEF≤1600, plus 6 lands + 4 spells) |
| Text | duel messages, duelist names, 17 intros, 48 battle lines — **no stock character reference remains** |

## Open / next
- **Playtesting** is the only real unknown left (does the 400:1 scale feel right).
- Already fixed from playtest: spells announcing the DM1 card they replaced, stock
  names on the record page and in dialogue, starter pool too strong.
- The one choice not backed by original data: the starter pool holds **10 magic
  cards** where stock had zero. First thing to revert if the opening deck misbehaves.
- Deliberately untouched: the translation credits at `0xF4900`+.

---

# Duel Monsters MTG — MTG-inspired total conversion

Built on Duel Monsters Kaizo's tools and engine map. This document owns the **design model**;
concrete engine facts live in `docs/NOTES.md`, and the authoring code lives in
`work/scripts/` (the card compiler `cardc.py` plus the colour layer `mtg_colors.py`).

This model is fully implemented in `build/duelmonsters-mtg-hack.gb` — see the status section above.

## The core decision: the type byte becomes COLOR

DM1's per-card **type byte** (`0x2409E`, the 21-value species enum) is repurposed to
hold an MTG **color** instead of a creature species. This is the single highest-leverage
mapping available, for a reason that only became clear once the terrain system was fully
disassembled:

> The terrain (field) ATK/DEF boost is **pre-baked data selected by a field index**, not
> a runtime `base × f(type)`. The loader at `$4312` indexes a 7-entry pointer table by
> the active field (0 = none, 1–6 = the six terrains) and never reads the type byte.
> (Full proof in `docs/NOTES.md` → "How a field is selected at runtime".)

So the association "*this land pumps this card*" is **not a rule in the ROM** — it lives
entirely in *which of the six terrain tables carry a boosted value for each card*, which
the compiler writes. That means:

- We can make **"a Forest pumps your green creatures"** true by construction, with no
  new assembly — it is a compile-time choice about where each card's ×1.3 goes.
- The type byte is **mechanically inert for stats**. Its only live jobs are the on-screen
  **label** (`0x538E`, 21 × 8-byte strings — rewrite to color names) and **seal-by-type**
  (Dragon Capture Jar, verb `$31` — becomes "seal all creatures of color X", which is a
  fine color-hate effect).

In MTG, **color is the primary identity** — far more than creature type. Putting color in
the game's most prominent, already-displayed, terrain-linked byte makes the most iconic
MTG feeling — *your lands empower your color* — fall out of the existing engine for free.
It is also the closest thing this engine can offer to a mana/land system, which it
otherwise entirely lacks.

## The mapping — 6 terrains → 5 colors + colorless (near-perfect fit)

The engine has **6** terrains; MTG has **5** colors + colorless. They line up 1:1, two of
them by literal name. The physical terrain-slot order was recovered from the stock data
(see `docs/NOTES.md`), not guessed:

| Terrain slot | Stock field | Land | Color | Match |
|---|---|---|---|---|
| 1 | Forest | Forest | **Green** | literal |
| 3 | Mountain | Mountain | **Red** | literal |
| 5 | Sea (Umi) | Island | **Blue** | thematic |
| 6 | Dark (Yami) | Swamp | **Black** | thematic (darkness/evil) |
| 4 | Meadow (Sogen) | Plains | **White** | thematic (open fields/order) |
| 2 | Wasteland | Wastes | **Colorless** | thematic (Wastes are real in MTG) |

The 6 field-setting spell verbs (`$03`–`$08`, already in the engine) become **"play a
basic land"** — set the active terrain, i.e. the dominant color, needing zero new code.

## What we gain, and what it costs

**Free wins**
- Land → color pump, exactly as above (the headline mechanic).
- Field spells reskin to basic lands with no assembly.
- Dragon Capture Jar → color-hate lockdown.
- The colorless slot gives artifacts/colorless bodies their own land — legitimate MTG.

**Costs / lossy points (decide before content lock)**
- **Mono-color only.** One byte = one color, so a card is boosted by exactly one land.
  Gold/multicolor identity is not representable. v1: 5 colors + colorless; a gold card
  is assigned its dominant color (or colorless). This is the main compromise — flag it.
- **Creature types (Bear, Goblin, Elf) drop as a mechanic.** No real loss — they were
  already mechanically inert here, and tribal synergy ("other Goblins get +1/+1") needs
  an effect engine we don't have. They live in the name/flavour text.
- **The boost is a flat ×1.3.** Because the boosted number is *stored* (not computed), the
  multiplier is free data — a land could give its color +50%, or a flat +N, per card if we
  wanted. Keep ×1.3 for v1 unless playtesting says otherwise.

## Decisions (owner, alpha)
- **Field frequency: retained from stock.** The land/terrain cadence stays exactly as the
  original game — no change to how or how often the field is set. The color-pump is a
  background swing, not a redesigned system.
- **Alpha = mono-color only.** No gold/multicolor cards in the alpha set. Revisit later.
- **Colors: White, Blue, Black, Red, Green + Colorless.** Full names in the label table,
  with one hardware caveat: the label slots are a hard **8 bytes**. `White/Black/Green`
  (5), `Blue` (4), `Red` (3) fit; **`Colorless` (9) does not** — label that slot
  **`Artifact`** (8, Alpha-accurate, since Alpha's colorless cards are artifacts).
  Alternatives if desired: `Colorles`, `Neutral`.
- **The creative surface for alpha is EQUIPS** (see next section), not the field system.

Still open: exact land/color label wording lock; colorless scope (artifacts only, or also
colorless bodies); whether to keep ×1.3 or retune the land pump after playtest.

## Equips — the primary creative surface (alpha)
The full engine mechanism (the 26-routine template, the `$6BC8` eligibility tables, the
`$1D00` comparator, the shared `$51DB` apply path) is documented in `docs/NOTES.md` →
"Equip combine system". The short version that drives P2 design:

A stock equip's identity = **(which monsters it can attach to) + (name/message)**. Attach
eligibility is an **explicit `$FFFF`-terminated list of monster card ids** (no runtime
"any color" wildcard — same shape as fusion recipes), and the **stat bonus is one uniform
constant** shared by all 26 equips (classic DM1 = +500/+500). That gives two creative tiers.

**Creative tier 1 — data only, no assembly. BUILT & WORKING.** Author `attaches_to:
[colors]` on an equip card in `cards.json`; `mtg_colors.py equips` expands it into that
equip's eligibility list (every monster of those colors) and writes `work/duelmonsters-mtg/equips.json`;
`build.py --product duelmonsters-mtg` compiles it into the ROM. Verified end-to-end: DarkEnergy→Black
and Axe of Despair→Red produce ROM lists equal to exactly those colors' monsters, with the
other 24 equips untouched.

*Budget reality* — the eligibility pool is a **hard 2642 bytes** (`equips.py` refuses to
overflow it). A whole-color equip costs `2·(monsters+1)` bytes; for the bootstrap colors
that is Black 166, White 130, Green 116, Colorless 88, Red 74, Blue 68. Because you're
*swapping* a stock list for a color list, the smart move is to color-lock equips whose
**stock list is already large** (e.g. DarkEnergy carries 162 targets) so the swap frees
space. Locking every one of the 26 equips to a broad color will not fit — narrow with more
specific `attaches_to` sets, or leave most equips on their stock lists.

**Creative tier 2 — small, precedented assembly.** The routines are tiny uniform templates;
in-place rewrites are the same class of change as the cards-per-win and spell-verb patches:
- Swap the id-list-walk predicate for a **compact color gate** (read the target's color byte
  at `$409E`, compare one value) — turns a long id list into a 1-byte "works on Red." One
  shared predicate, reused by all equips.
- Give equips **different amounts / DEF-only / debuffs** by parameterizing the apply payload
  (requires pinning and templating the `+N` constant).

**Hard limits.** Equips are stat modifiers + eligibility only. There is no keyword/ability
engine, so "aura grants flying/first strike/an activated ability" is **not** representable;
"+X/+Y to creatures of color C" is.

## How the compiler changes (see `work/scripts/mtg_colors.py`)
Today `cardc.py` stores all six `field_atk`/`field_def` values per card explicitly and
writes them verbatim. Duel Monsters MTG makes **color the single source of truth**: a card gets a
`color`, and the six terrain values are **derived** — base everywhere except the one slot
matching the card's color, which is `round(base × 1.3)`. `mtg_colors.py` holds:

- `COLORS`, the color→terrain-slot map (grounded in the recovered slot order), and `BOOST`.
- `derive_fields(color, base_atk, base_def)` → the six-long field arrays.
- `recolor_db(db, color_of)` → rewrites a `cards.json` in place so a P2 authoring file only
  has to specify `color` + base stats, never the terrain tables.

The change is fully **contained**: regenerating terrain tables from color touches only the
six terrain ATK/DEF arrays in bank 9 (proven by `mtg_colors.py demo`, which diffs a recolored
build against the base and asserts every changed byte lies inside those tables).
