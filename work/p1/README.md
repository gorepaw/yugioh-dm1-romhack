# work/p1 — Project 1 data ("Modernized DM1")

All of Project 1's card data lives here and **nowhere else**. Project 2's data is
in `work/p2/`. The two never share a file: they are different games occupying the
same 366 card slots.

Build this product with:

```
python scripts/build.py                 # product p1 is the default
python scripts/build.py --product p1     # explicit
```

Output: `build/p1-hack.gb`.

Files that may appear here (each tool writes its own, all with `--product p1`):

| File | Written by | Tracked? |
|---|---|---|
| `cards.json` | `cardc.py extract` | no — extracted game text (gitignored) |
| `fusions.json` | `fusions.py extract` | no — extracted table data (gitignored) |
| `card_edits.json` | `cards.py set` | yes — our design |
| `desc_edits.json` | `descriptions.py set` | yes |
| `drop_config.json` | `drops.py` | yes |
| `reward_config.json` | `rewards.py` | yes |
| `grind_config.json` | `grind.py` | yes |
| `spell_config.json` | `spells.py` | yes |

`cards.json` / `fusions.json` are regenerable from the ROM and hold Darrman's
translated text, so they are gitignored like the ROM itself.
