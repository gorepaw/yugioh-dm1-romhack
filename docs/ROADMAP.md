# Project roadmap — Yu-Gi-Oh! Duel Monsters (GB) romhack

## Vision — two products

**Project 1 — "Modernized DM1" (the foundation).** Cut the many uselessly weak
cards and replace them with stronger cards from later in the series that never
appeared in the original (e.g. drop Skull Servant, add Buster Blader). This forces
a **full rebalance** and is best done as a **full rewrite** of the card system.
Its real purpose: build the toolset and engine knowledge needed for Project 2.

**Project 2 — MTG-inspired total conversion.** A full Magic: The Gathering–style
overhaul, built on Project 1's tools and knowledge.

## Guiding principle — keep the art, rewrite the data
Character art and card art are retained. Project 1 rewrites the *data* around the
existing art (or reuses a card's art for a thematically similar replacement).
Art edits are a later, separate layer.

## Architecture — a card COMPILER (single source of truth)
Stop byte-patching. Author one master definition of all 366 card slots (name, ATK,
DEF, type, description, spell-effect id, fusion role, drop/deck/reward membership)
and **compile** it into every ROM table. This is Project 1's headline deliverable
and becomes the authoring tool for Project 2.

```
master card data (JSON/CSV)  ->  compiler  ->  ROM tables
   (names, stats, types, descriptions, drops, decks, rewards, fusions)
```

The tools built so far (cards.py, descriptions.py, drops.py, text_tool.py, build.py)
are the seeds of this compiler.

## The make-or-break unknown — engine expressiveness
Before rewriting cards we must know exactly what the engine can express. This is the
"game knowledge" Project 1 exists to produce and the gating constraint for Project 2:

- **Card categories** the engine supports (monster / spell subtypes / ritual / fusion).
- **Spell-effect roster** — DM1 spells appear to be a FIXED set of hardcoded effects
  (field terrains, Dark Hole, Raigeki, Swords of Revealing Light, equips, direct-damage
  burns, healing, Stop Defense, Spellbinding Circle, Elegant Egotist, Dragon Capture
  Jar, …; ~44 messages seen in `dueltext.txt`). How is an effect bound to a card? Can we
  reassign an effect to a different card / add copies?
- **Fusion** system (bank `0x3B`) — recipes and how they resolve.
- **Verify the player's belief:** no traps, no monster effects (confirm in code).

**Implication:** an added card (Buster Blader, etc.) is a vanilla stats+type body
UNLESS it reuses an existing spell effect or a fusion role. So card curation must be
effect-aware — which is exactly why we map the engine first.

## Phased plan — Project 1
- **P1.0 — Engine map.** Spell-effect roster + how effects bind to cards; categories;
  fusion; opponent decklists (bank 8) + starter deck (`0x26AC`); win-count reward
  tables + cards-per-win; confirm no traps/effects. → produces the design space.
- **P1.1 — Compiler.** Master card table → all ROM tables, round-trip verified
  (rebuild the untouched ROM byte-for-byte from extracted data first).
- **P1.2 — Curate + rebalance.** Cut weak cards, slot in later cards, retune stats,
  regenerate drops/decks/rewards; iterate with BGB playtesting.

## Known systems (mapped so far) — see docs/NOTES.md
Text encoding; card names; ATK/DEF (BCD, base + 6 terrain tables); type array + enum;
card descriptions; drop pools (17 × cumulative weights); duelist→pool map.

## Open questions
1. Card curation: do you have a target list of cuts/adds, or should we build a rubric
   (e.g. "cut the bottom-N by usefulness; add these later vanillas")?
2. Keep the 366 card slots and repopulate in place (simplest, all tables sized for it)?
3. For swapped cards: reuse the existing art, or plan art edits for key ones?
