# Project 1 — build pipeline

How `build/p1-hack.gb` is produced from the tracked sources. Run scripts with the full
Python path (`C:\Users\lando\AppData\Local\Programs\Python\Python313\python.exe`), from
`work/scripts/`, always `--product p1`.

## Status

Project 1 is a **complete, valid, playable ROM** as of 2026-07-24. Full build passes:
hardware invariants (1 MB / MBC1+RAM+BAT / valid header checksum, Miyoo-safe), the
marquee fusion chain present, and every changed byte inside a known data table (zero
stray writes). **Next step: playtest** — the deck/drop weights and some type-partner
fusion recipes are unplaytested first-pass numbers.

## Sources of truth (tracked)

| File | What |
|---|---|
| `work/p1/new_cards.json` | the 84 new cards: name, ATK, DEF, type, 2-line flavour, and `id` (assigned slot). **The master ledger.** |
| `work/p1/patches.json` | 34 starter-pool remaps (verified byte patches) so the player doesn't start with new cards/gods |
| `work/p1/deck_config.json` | 16 opponent decks — `{card_id: weight}` per pool |
| `work/p1/reward_config.json` | 16 reward lists — `{pool: [10 card_ids]}` |
| `work/p1/drop_config.json` | 17 drop pools — explicit `{card_id: weight}` |
| `docs/*.md` | the design docs behind all of the above |

**Derived / gitignored** (regenerated, never committed): `work/p1/cards.json`,
`work/p1/fusions.json` (bulk card data), and the working files `docs/DECKLISTS.md`,
`docs/RECALC.md`, `docs/ASSIGNMENT.md` (bulk translated names).

## Rebuild from a clean checkout

```
cd work/scripts
python cardc.py extract --product p1          # stock 365-card db -> work/p1/cards.json
python apply_new_cards.py --product p1        # overlay the 84 new cards (needs new_cards.json)
python gen_fusions.py                          # regenerate fusions.json (needs new_cards.json)
python build.py --product p1                   # -> build/p1-hack.gb
```

That is sufficient: the deck/reward/drop **configs are already tracked**, so the build
needs only `cards.json` + `fusions.json` regenerated (both come from the tracked
`new_cards.json`). `build.py` reads every `work/p1/*.json` and applies it.

## Regenerating the configs (only if the design changes)

The deck/reward/drop generators read the pruned deck list `docs/DECKLISTS.md` (a local
working file, gitignored), so they only run where that file exists:

```
python gen_decks_rewards.py                    # deck_config.json + reward_config.json
python gen_drops.py                            # drop_config.json
```

Then commit the regenerated (tracked) configs.

## How the 84 slots were chosen (one-time, already done)

Recorded here so it isn't lost. `new_cards.json` already holds the results.

1. **Cull pool** = monsters that are weak, DEF < 1500 (owner: high-DEF is protected),
   and used in no deck/reward/fusion of the new design. 133 such slots; DM1 is densely
   packed, so most weak cards are load-bearing deck filler — see `docs/CULLING.md`.
2. **Retire the 84 longest-named** of those (name-pool budget: the new names cost more
   tiles than short-named junk frees, so we retire the longest junk). Final name pool
   4475/4480.
3. **Assign** fusion cards (21) to #1–300 slots (fusion can't reach above #300), the
   rest anywhere. Names were de-spaced + `Magician`→`Magicn` to fit the pool.
4. **Starter fix**: 34 starter-monster entries pointed at retired slots → remapped to
   weak kept monsters (patches.json). Excludes Exodia (Simon's reward chase) and Cocoon.

## Verify a build

```
python -c "..."   # see the Phase-4 check: invariants + marquee fusion + zero stray writes
```
Key asserts: size 1048576, `0x147==3`, `0x148==5`, `0x149==2`, header checksum valid,
all diffs inside {card tables, decks, drops, rewards, fusions, starter, checksums}.
