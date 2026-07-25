# work/duelmonsters-mtg — Duel Monsters MTG data (MTG-inspired total conversion)

All of Duel Monsters MTG's card data lives here and **nowhere else**. The Duel Monsters Kaizo
data is in `work/duelmonsters-kaizo/`. The two never share a file: they are different
games occupying the same 366 card slots, so one `cards.json` cannot represent both.

Build this product with:

```
python scripts/build.py --product duelmonsters-mtg     # -> build/duelmonsters-mtg-hack.gb
```

Every data tool takes `--product duelmonsters-mtg` and writes here, e.g.:

```
python scripts/cardc.py   extract --product duelmonsters-mtg   # -> work/duelmonsters-mtg/cards.json
python scripts/fusions.py extract --product duelmonsters-mtg   # -> work/duelmonsters-mtg/fusions.json
python scripts/drops.py   --product duelmonsters-mtg ...
```

`cards.json` / `fusions.json` are gitignored (regenerable, hold translated text);
config JSONs written by the editors are tracked as design intent.

Shared with Duel Monsters Kaizo (do not fork these): the reverse-engineering notes in
`docs/NOTES.md` and every tool in `work/scripts/`.
