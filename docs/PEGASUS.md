# Pegasus — deck, drops, rewards (proposal, kaizo)

Duelist 14 / pool 15. **Nothing here is in the ROM yet.** Same additive kaizo treatment
as Yami: old cards kept as the beatable body, new Toon monsters layered on.

Identity: **Toons.** DM1 has zero Toon cards (verified), so all 18 are new.

## Relinquished / Thousand-Eyes — CUT (recommended)

The chain in the real game:

```
Relinquished (Ritual, L1, DARK Spellcaster, 0/0)   — absorbs a monster
Thousand-Eyes Idol (L1 Normal, 0/0)                — fusion material only
   Relinquished + Thousand-Eyes Idol  ->  Thousand-Eyes Restrict (Fusion, L1, 0/0)
```

Thousand-Eyes Restrict is the iconic Pegasus fusion — it absorbs one of your monsters
and freezes the field. **None of the three is in DM1** (confirmed), and all three are
**0 ATK / 0 DEF**: their entire value is the absorb/lock *effect*, which this engine
cannot represent. As plain vanilla 0/0 monsters they'd be the worst cards in the game.

**Recommendation: cut them, make Pegasus all-Toon.** There's also no ritual mechanic
in DM1, so Relinquished couldn't even be summoned normally. Nothing of value is lost.

## Toon roster — 18 monsters (all new)

| in-game name | tiles | ATK/DEF | type | dupes an existing card? |
|---|---:|---|---|---|
| Toon Alligator | 13 | 800/1600 | Reptile | |
| Toon Mermaid | 12 | 1400/1500 | Aqua | |
| ToonSummonSkull | 14 | 2500/1200 | Fiend | = Summoned Skull |
| Manga Ryu-Ran | 13 | 2200/2600 | Dragon | |
| Toon Gemini Elf | 15 | 1900/900 | Spellcaster | |
| ToonMaskSorcerer | 16 | 900/1400 | Spellcaster | = Masked Sorcerer |
| ToonCannonSoldier | 17 | 1400/1300 | Machine | |
| BlueEyesToonDrgn | 16 | 3000/2500 | Dragon | = Blue-Eyes |
| RedEyesToonDragon | 17 | 2400/2000 | Dragon | = Red-Eyes / Thousand Dragon |
| Toon DarkMagician | 17 | 2500/2100 | Spellcaster | = Dark Magician |
| ToonDarkMagGirl | 15 | 2000/1700 | Spellcaster | = (Yami's) Dark Magician Girl |
| ToonGoblinForce | 14 | 2300/0 | Warrior | |
| Toon Harpie Lady | 16 | 1300/1400 | Winged Beast | = Harpie Lady |
| Toon Cyber Dragon | 17 | 2100/1600 | Machine | |
| Toon Barrel Dragon | 18 | 2600/2200 | Machine | |
| ToonBlackLuster | 15 | 3000/2500 | Warrior | = Black Luster Soldier |
| Toon Buster Blader | 18 | 2600/2300 | Warrior | = (Yami's) Buster Blader |
| ToonAncientGolem | 16 | 3000/3000 | Machine | |

**279 name tiles.** 7 duplicate an existing card's stats (inherent to a no-effects
engine — the Toon is mechanically its base card, distinguished only by name/art). That's
fine as same-card-different-art; nudge stats/type on any you want to feel distinct.
Toon Ancient Gear Golem (3000/3000) is a brand-new stat line — the beefiest wall added
so far. *Parrot Dragon (2000/1300 Dragon)* is an archetype Toon with no "Toon" in its
name — omitted; add if wanted.

## Deck — 67 cards (old 49 + 18 Toons), weights /2048

Additive. Old ≈ **76%**, Toons ≈ **24%** (his old deck is large, so Toons dilute more
than Yami's did). If you want Pegasus to feel more Toon-dominant, say so and I'll shift
the split. Top of curve is his old fiends/warriors (Gatekeeper, Kojikocy, Ansatsu ~4.5%);
Toon threat tier runs 0.6–2.0%, with the three 3000-ATK Toons at 0.59% each.

Full weighted list lives in the eventual `work/p1/drop_config.json` + deck config; this
doc records the design, not the raw array.

## Drop table — every card except the Gods

Per your call: Pegasus drops **all 362 non-God cards**. Scheme: a flat baseline (~5–6
weight each, ≈0.27%) with his Toons boosted so the theme still reads, renormalized to
2048. The three God cards are **weight 0** — only Yami drops those. This makes Pegasus
the universal farm: grind him long enough and almost anything can appear.

## Rewards — best 10 Toons by ATK (10 → 100 wins)

| Wins | ATK | Toon | | Wins | ATK | Toon |
|---:|---:|---|---|---:|---:|---|
| 10 | 2200 | Manga Ryu-Ran | | 60 | 2600 | Toon Barrel Dragon |
| 20 | 2300 | ToonGoblinForce | | 70 | 2600 | Toon Buster Blader |
| 30 | 2400 | RedEyesToonDragon | | 80 | 3000 | BlueEyesToonDrgn |
| 40 | 2500 | ToonSummonSkull | | 90 | 3000 | ToonBlackLuster |
| 50 | 2500 | Toon DarkMagician | | 100 | 3000 | ToonAncientGolem |

The 8 Toons below 2200 ATK (Alligator, Mermaid, Gemini Elf, Mask Sorcerer, Cannon
Soldier, Harpie Lady, Cyber Dragon, DM Girl) are not rewards but are all deck cards and
all droppable.

## Running budget across the roster (⚠ the pool is shared)

| | new cards | name tiles | notes |
|---|---:|---:|---|
| Yami | 27 | 420 | 14 need fusion-zone (#1–#300) |
| Pegasus | 18 | 279 | none are fusion pieces |
| **total (2 of 16 duelists)** | **45** | **699** | of 365 slots / 4480 tiles |

Two duelists have already claimed **45 of the 365 card slots** and 699 of 4480 name
tiles. At this pace the pool overflows well before duelist 16. The resolution: **only
the marquee opponents (Yami, Pegasus, Kaiba…) get big themed sets; the early duelists
mostly keep their stock decks** with light additions. The great culling frees old slots,
but it can't create more than 365. This is the constraint to steer by from here on.
