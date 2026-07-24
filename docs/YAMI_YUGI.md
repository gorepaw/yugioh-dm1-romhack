# Yami Yugi — deck, drops, rewards (proposal v2, kaizo)

Duelist 15 / pool 4. **Nothing here is in the ROM yet.** Rates are tunable; deck and
drop are 365-slot weight arrays that must total 2048, rewards are 10 fixed card ids.

**Design (revised):** this is a **kaizo** — "the last Yu-Gi-Oh game." The deck and drop
tables are **additive**: Yami keeps his old cards (the beatable body that gives you
outs) and the 27 new cards are layered on top as the threat. Broad cuts to the old
cards come later, in the great card-list culling — not here.

- **Deck** = old 27 + new 27 = 54 cards. Old ≈ 56% of draws (defeatable), new ≈ 44%.
  Dark Magician (#35) featured. The three Gods combined are **0.29%** of his draws.
- **Drops** = old 22 + new 27 = 49 cards, additive. Every fusion result is droppable
  (rough grind), but **suppressed well below its stats** so a 2900 fusion is rarer
  than a 2900 vanilla. Gods are an ultra-rare jackpot (~0.15% each).
- **Rewards** (per 10 wins) = the fusion monsters, escalating. **Locked — no changes.**

> Every fusion is obtainable in multiple copies from the drop table, so the fusion
> engine is fully reachable even for a grinder who never fuses.

---

## Deck — 54 cards (old kept + new layered), weights /2048

**Old cards (kept — the beatable body):**

| wt | % | # | card |
|---:|---:|---:|---|
| 114 | 5.57 | 15 | Flame Swordsman |
| 112 | 5.47 | 12 | Swamp Battleguard |
| 111 | 5.42 | 68 | Garoozis |
| 105 | 5.13 | 39 | Curse of Dragon |
| 101 | 4.93 | 14 | Battle Steer |
| 65 | 3.17 | 74 | Giant Rock Soldier |
| 62 | 3.03 | 22 | Summoned Skull |
| 53 | 2.59 | 60 | Great White |
| 51 | 2.49 | 31 | Koumori Dragon |
| 50 | 2.44 | **35** | **Dark Magician** (featured) |
| 39 | 1.90 | 10 | Blackland Fire Dragon |
| 36 | 1.76 | 7 | Winged Dragon |
| 35 | 1.71 | 38 | Gaia the Fierce Knight |
| 35 | 1.71 | 41 | Celtic Guardian |
| 35 | 1.71 | 89 | Catapult Turtle |
| 30 | 1.46 | 6 | Feral Imp |
| 24 | 1.17 | 27 | Beaver Warrior |
| 24 | 1.17 | 46 | Griffore |
| 23 | 1.12 | 2 | Mystical Elf |
| 18 | 0.88 | 25 | Horn Imp |
| 11 | 0.54 | 37 | Gaia the Dragon Champion |
| 8 | 0.39 | 30 | Zombie Warrior |
| 7 | 0.34 | 47 | Torike |
| 7 | 0.34 | 59 | Mammoth Graveyard |
| 7 | 0.34 | 65 | Silver Fang |
| 1 | 0.05 | 48 | Sangan |
| 1 | 0.05 | 217 | Black Skull Dragon |

**New cards (the threat layer):**

| wt | % | ATK/DEF | card |
|---:|---:|---|---|
| 66 | 3.22 | 2000/1700 | Dark Magician Girl |
| 64 | 3.12 | 1900/1700 | Skilled Dark Magician |
| 64 | 3.12 | 1800/1800 | Skilled Blue Magician |
| 64 | 3.12 | 1700/1900 | Skilled White Magician |
| 55 | 2.69 | 2100/2500 | Illusion of Chaos |
| 50 | 2.44 | 2800/1800 | Legendary Knight Timaeus |
| 50 | 2.44 | 2500/2500 | Chronicle Magician |
| 47 | 2.29 | 2800/1800 | Timaeus the United Dragon |
| 44 | 2.15 | 2600/2300 | Buster Blader |
| 41 | 2.00 | 2400/1200 | Timestar Magician |
| 39 | 1.90 | 2600/1700 | DMG the Dragon Knight |
| 39 | 1.90 | 1600/100 | Magician's Rod |
| 36 | 1.76 | 700/2000 | Magician's Robe |
| 36 | 1.76 | 1200/2800 | Buster Dragon |
| 25 | 1.22 | 2800/2300 | Dark Cavalry |
| 25 | 1.22 | 2800/2600 | Dark Magician of Chaos |
| 25 | 1.22 | 2800/2300 | The Dark Magicians |
| 25 | 1.22 | 2800/2500 | Buster Blader Dragon Destroyer |
| 22 | 1.07 | 2800/3200 | Dark Sage |
| 15 | 0.73 | 2900/2400 | Dark Paladin |
| 15 | 0.73 | 2900/2500 | Amulet Dragon |
| 14 | 0.68 | 2900/2400 | Dark Magician Knight |
| 8 | 0.39 | 3000/2500 | Master of Chaos |
| 8 | 0.39 | 3000/2500 | Red-Eyes Dark Dragoon |
| 2 | 0.10 | 4000/4000 | Obelisk the Tormentor |
| 2 | 0.10 | 4000/4000 | Slifer the Sky Dragon |
| 2 | 0.10 | 4000/4000 | The Winged Dragon of Ra |

---

## Drop table — 49 cards (old + new, additive), weights /2048

Old drops kept at roughly stock proportions; new cards added; fusions present but
suppressed; Gods ultra-rare. **All 12 fusion results appear** (verified).

**Non-fusion drops (old + new bodies):**

| wt | % | card | src |
|---:|---:|---|---|
| 267 | 13.04 | Giant Rock Soldier (#74) | old |
| 212 | 10.35 | Great White (#60) | old |
| 152 | 7.42 | Koumori Dragon (#31) | old |
| 120 | 5.86 | Blackland Fire Dragon (#10) | old |
| 118 | 5.76 | Catapult Turtle (#89) | old |
| 74 | 3.61 | Winged Dragon (#7) | old |
| 74 | 3.61 | Celtic Guardian (#41) | old |
| 65 | 3.17 | Mystical Moon (#319, equip) | old |
| 65 | 3.17 | Skilled Dark Magician | new |
| 65 | 3.17 | Skilled Blue Magician | new |
| 65 | 3.17 | Skilled White Magician | new |
| 59 | 2.88 | Dark Magician Girl | new |
| 55 | 2.69 | Mystical Elf (#2) | old |
| 53 | 2.59 | Feral Imp (#6) | old |
| 52 | 2.54 | Illusion of Chaos | new |
| 46 | 2.25 | Magician's Robe | new |
| 46 | 2.25 | Magician's Rod | new |
| 39 | 1.90 | Legendary Knight Timaeus | new |
| 39 | 1.90 | Buster Blader | new |
| 39 | 1.90 | Chronicle Magician | new |
| 38 | 1.86 | Beaver Warrior (#27) | old |
| 38 | 1.86 | Griffore (#46) | old |
| 26 | 1.27 | Dark Magician of Chaos | new |
| 26 | 1.27 | Dark Sage | new |
| 22 | 1.07 | Horn Imp (#25) | old |
| 13 | 0.63 | Dark Magician (#35) | old |
| 7 | 0.34 | Summoned Skull (#22) | old |
| 7 | 0.34 | Final Flame (#345, spell) | old |
| 7 | 0.34 | Swords of Light (#348, spell) | old |
| 6 | 0.29 | Zombie Warrior (#30) | old |
| 5 | 0.24 | Torike / Mammoth Graveyard / Silver Fang | old |
| 1 | 0.05 | Sangan (#48) | old |

**Fusion results (all droppable, suppressed below their stats):**

| wt | % | ATK | card |
|---:|---:|---:|---|
| 16 | 0.78 | 2800 | Timaeus the United Dragon |
| 16 | 0.78 | 1200 | Buster Dragon |
| 14 | 0.68 | 2400 | Timestar Magician |
| 12 | 0.59 | 2800 | Dark Cavalry |
| 12 | 0.59 | 2800 | The Dark Magicians |
| 12 | 0.59 | 2800 | Buster Blader Dragon Destroyer |
| 12 | 0.59 | 2600 | DMG the Dragon Knight |
| 8 | 0.39 | 2900 | Amulet Dragon |
| 8 | 0.39 | 2900 | Dark Paladin |
| 8 | 0.39 | 2900 | Dark Magician Knight |
| 5 | 0.24 | 3000 | Master of Chaos |
| 5 | 0.24 | 3000 | Red-Eyes Dark Dragoon |

**Gods — ultra-rare jackpot:** Obelisk / Slifer / Ra each `wt 3` = **0.15%**; all three
combined ≈ **0.44%** of any single drop.

---

## Rewards — one per 10 wins (LOCKED, no changes)

| Wins | ATK | card | | Wins | ATK | card |
|---:|---:|---|---|---:|---:|---|
| 10 | 1200 | Buster Dragon | | 60 | 2800 | Buster Blader Dragon Destroyer |
| 20 | 2400 | Timestar Magician | | 70 | 2900 | Dark Magician Knight |
| 30 | 2600 | DMG the Dragon Knight | | 80 | 2900 | Amulet Dragon |
| 40 | 2800 | The Dark Magicians | | 90 | 2900 | Dark Paladin |
| 50 | 2800 | Dark Cavalry | | 100 | 3000 | Red-Eyes Dark Dragoon |

Left out of the 10 slots (still droppable): Master of Chaos (3000), Timaeus the United
Dragon (2800). Thresholds (10…100) are a shared table across all 16 duelists.

---

## Open items

- **Slot conflicts (later):** several new fusion cards must occupy #1–#300 and will
  overwrite existing monsters — some of which are the *old* cards still listed in this
  deck/drop. Those overlaps resolve during the card-list culling; this proposal treats
  old and new as coexisting identities for now.
- Rates here are a first pass; tune freely.
