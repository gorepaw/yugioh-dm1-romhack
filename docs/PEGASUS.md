# Pegasus — deck, drops, rewards (proposal, kaizo)

Duelist 14 / pool 15. **Nothing here is in the ROM yet.**

Identity: **all Toons.** Unlike Yami (additive), Pegasus's entire old deck is cut — his
deck is purely the 18 new Toon monsters, with the weak Toons as the beatable body. His
*drop* table is still additive/expansive (every non-God card). DM1 has zero Toon cards
(verified), so all 18 are new.

## Opponent AI cannot use magic cards (engine fact — verify into NOTES.md later)

Confirmed by code + data:
- **0 of 16 stock opponent decks contain a single magic card** (ids 301–350).
- The magic-activation path (`$56AE` → verb dispatch `$6F49`) is reached **only through
  the player's cursor-driven card menu**: selector `$5095` reads the player's menu
  bitflags at `$CAA5/$CAA6`, indexes the category handler table `$505E`, and only that
  branch fires "play magic". The opponent's turn is a separate path that samples its
  weighted deck and **summons monsters** — no spell-activation branch.

So giving an opponent magic cards yields **dead draws** (it holds cards it never plays).
Making the AI use magic is a **code** change (new assembly), not data — a Project-2
capability, not available now. *(This belongs in docs/NOTES.md; recorded here to avoid
a concurrent edit to that shared file.)*

## Relinquished / Thousand-Eyes — CUT (confirmed)

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

## Deck — 18 cards, ALL TOON (weights /2048)

His entire old deck is cut (per owner). He had **zero** magic cards, and the AI can't
play magic anyway (above), so "keep toons + magic" resolves to a pure all-Toon deck. The
weak Toons are the beatable body: **44% of his draws are sub-1500 ATK "outs"**, and the
three 3000-ATK Toons are just **1.5% each** (4.5% combined). No Gods (those are Yami's).

| wt | % | ATK/DEF | card |
|---:|---:|---|---|
| 191 | 9.33 | 800/1600 | Toon Alligator |
| 183 | 8.94 | 900/1400 | ToonMaskSorcerer |
| 178 | 8.69 | 1400/1500 | Toon Mermaid |
| 173 | 8.45 | 1400/1300 | ToonCannonSoldier |
| 173 | 8.45 | 1300/1400 | Toon Harpie Lady |
| 157 | 7.67 | 1900/900 | Toon Gemini Elf |
| 141 | 6.88 | 2000/1700 | ToonDarkMagGirl |
| 131 | 6.40 | 2100/1600 | Toon Cyber Dragon |
| 115 | 5.62 | 2200/2600 | Manga Ryu-Ran |
| 115 | 5.62 | 2300/0 | ToonGoblinForce |
| 94 | 4.59 | 2400/2000 | RedEyesToonDragon |
| 84 | 4.10 | 2500/1200 | ToonSummonSkull |
| 84 | 4.10 | 2500/2100 | Toon DarkMagician |
| 68 | 3.32 | 2600/2300 | Toon Buster Blader |
| 68 | 3.32 | 2600/2200 | Toon Barrel Dragon |
| 31 | 1.51 | 3000/2500 | BlueEyesToonDrgn |
| 31 | 1.51 | 3000/2500 | ToonBlackLuster |
| 31 | 1.51 | 3000/3000 | ToonAncientGolem |

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
