# work/p2 — Project 2 data (MTG-inspired total conversion)

All of Project 2's card data lives here and **nowhere else**. Project 1's data is
in `work/p1/`. The two never share a file: they are different games occupying the
same 366 card slots, so one `cards.json` cannot represent both.

Build this product with:

```
python scripts/build.py --product p2     # -> build/p2-hack.gb
```

Every data tool takes `--product p2` and writes here, e.g.:

```
python scripts/cardc.py   extract --product p2   # -> work/p2/cards.json
python scripts/fusions.py extract --product p2   # -> work/p2/fusions.json
python scripts/drops.py   --product p2 ...
```

`cards.json` / `fusions.json` are gitignored (regenerable, hold translated text);
config JSONs written by the editors are tracked as design intent.

Shared with Project 1 (do not fork these): the reverse-engineering notes in
`docs/NOTES.md` and every tool in `work/scripts/`.
