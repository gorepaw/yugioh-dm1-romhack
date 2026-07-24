# Yami Yugi — deck, drops, rewards (proposal)

Planning doc for duelist 15 / pool 4. **Nothing here is in the ROM yet.** Rates are a
first proposal for you to tweak; all three tables are independent 365-slot weight
arrays (deck and drop must total 2048; rewards are 10 fixed card ids).

Design intent:
- **Deck** = all 27 new Project-1 cards. Signature bodies common, apex fusions rare,
  God cards a near-never topdeck.
- **Drops** = the farmable bodies, so beating him builds a Dark Magician deck. The
  apex fusions are *not* drops — they're the rewards. God cards are an ultra-rare
  jackpot drop.
- **Rewards** (per 10 wins) = the fusion monsters, escalating 10 → 100.

> Open question: **Dark Magician (#35) itself is not in any of these tables** — the 27
> new cards are all *around* it. Should the classic Dark Magician be in his deck / a
> drop? It's the centrepiece most of these fuse from. Flagged, not assumed.

---

## Deck (27 cards, weights /2048)

| % | wt | ATK | DEF | type | role | card |
|---:|---:|---:|---:|---|---|---|
| 6.88 | 141 | 2000 | 1700 | Spellcaster | material | Dark Magician Girl |
| 6.74 | 138 | 1900 | 1700 | Spellcaster | | Skilled Dark Magician |
| 6.74 | 138 | 1800 | 1800 | Spellcaster | | Skilled Blue Magician |
| 6.74 | 138 | 1700 | 1900 | Spellcaster | | Skilled White Magician |
| 6.01 | 123 | 2100 | 2500 | Spellcaster | | Illusion of Chaos |
| 5.66 | 116 | 2800 | 1800 | Warrior | | Legendary Knight Timaeus |
| 5.66 | 116 | 2800 | 1800 | Dragon | fusion | Timaeus the United Dragon |
| 5.32 | 109 | 2500 | 2500 | Spellcaster | | Chronicle Magician |
| 4.98 | 102 | 2600 | 2300 | Warrior | material | Buster Blader |
| 4.98 | 102 | 2600 | 1700 | Dragon | fusion | DMG the Dragon Knight |
| 4.59 | 94 | 2400 | 1200 | Spellcaster | fusion | Timestar Magician |
| 4.25 | 87 | 1600 | 100 | Spellcaster | | Magician's Rod |
| 3.91 | 80 | 700 | 2000 | Spellcaster | | Magician's Robe |
| 3.91 | 80 | 1200 | 2800 | Dragon | fusion | Buster Dragon |
| 3.17 | 65 | 2800 | 2300 | Warrior | fusion | Dark Cavalry |
| 3.17 | 65 | 2800 | 2600 | Spellcaster | | Dark Magician of Chaos |
| 3.17 | 65 | 2800 | 2300 | Spellcaster | fusion | The Dark Magicians |
| 3.17 | 65 | 2800 | 2500 | Warrior | fusion | Buster Blader Dragon Destroyer |
| 2.83 | 58 | 2800 | 3200 | Spellcaster | | Dark Sage |
| 2.00 | 41 | 2900 | 2400 | Spellcaster | fusion | Dark Paladin |
| 2.00 | 41 | 2900 | 2500 | Dragon | fusion | Amulet Dragon |
| 1.86 | 38 | 2900 | 2400 | Dragon | fusion | Dark Magician Knight |
| 0.83 | 17 | 3000 | 2500 | Spellcaster | fusion | Master of Chaos |
| 0.83 | 17 | 3000 | 2500 | Warrior | fusion | Red-Eyes Dark Dragoon |
| 0.20 | 4 | 4000 | 4000 | Fiend | god | Obelisk the Tormentor |
| 0.20 | 4 | 4000 | 4000 | Dragon | god | Slifer the Sky Dragon |
| 0.20 | 4 | 4000 | 4000 | Winged Beast | god | The Winged Dragon of Ra |

Combined, the three Gods are **0.6%** of his draws — a real but rare "oh no" moment.

---

## Drop table (16 cards, weights /2048)

Apex fusions deliberately excluded (they're rewards). Gods are the jackpot.

| % | wt | ATK | card |
|---:|---:|---:|---|
| 9.72 | 199 | 1900 | Skilled Dark Magician |
| 9.72 | 199 | 1800 | Skilled Blue Magician |
| 9.72 | 199 | 1700 | Skilled White Magician |
| 8.59 | 176 | 2000 | Dark Magician Girl |
| 8.01 | 164 | 2100 | Illusion of Chaos |
| 7.42 | 152 | 700 | Magician's Robe |
| 7.42 | 152 | 1600 | Magician's Rod |
| 6.88 | 141 | 2500 | Chronicle Magician |
| 6.88 | 141 | 2800 | Legendary Knight Timaeus |
| 6.30 | 129 | 2800 | Timaeus the United Dragon |
| 6.30 | 129 | 2600 | Buster Blader |
| 6.30 | 129 | 1200 | Buster Dragon |
| 5.71 | 117 | 2400 | Timestar Magician |
| 0.34 | 7 | 4000 | Obelisk the Tormentor |
| 0.34 | 7 | 4000 | Slifer the Sky Dragon |
| 0.34 | 7 | 4000 | The Winged Dragon of Ra |

Each God is ~0.29% per drop; all three combined ≈ **1.0%** of any single drop.

---

## Rewards — one per 10 wins (all fusion results, escalating)

| Wins | ATK | card |
|---:|---:|---|
| 10 | 1200 | Buster Dragon |
| 20 | 2400 | Timestar Magician |
| 30 | 2600 | DMG the Dragon Knight |
| 40 | 2800 | The Dark Magicians |
| 50 | 2800 | Dark Cavalry |
| 60 | 2800 | Buster Blader Dragon Destroyer |
| 70 | 2900 | Dark Magician Knight |
| 80 | 2900 | Amulet Dragon |
| 90 | 2900 | Dark Paladin |
| 100 | 3000 | Red-Eyes Dark Dragoon |

There are **12** fusion results; two are left out of the 10 reward slots:
**Master of Chaos (3000)** and **Timaeus the United Dragon (2800)**. Swap any in/out.

Notes on the ladder:
- Buster Dragon at 10 wins is weak on ATK (1200) but has 2800 DEF — a soft first prize.
  If you'd rather the ladder open stronger, promote Timestar Magician to the 10 slot.
- Thresholds (10, 20 … 100) are a **shared table** across all 16 duelists, so changing
  the pace changes it for everyone. Only the ten *cards* are Yami-specific.
