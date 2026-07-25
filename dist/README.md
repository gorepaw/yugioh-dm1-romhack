# Patches

These are **BPS patches**, not ROMs. Each one contains only the difference
between the original game and the hack, so you need your own copy of the base
ROM to play. No game data is distributed here.

| Patch | Hack |
|---|---|
| `duelmonsters-kaizo-*.bps` | **Duel Monsters Kaizo** — the original game with 85 later-era Yu-Gi-Oh! cards worked into every opponent |
| `duelmonsters-mtg-*.bps` | **Duel Monsters MTG** — a total conversion to *Magic: The Gathering*; card type becomes colour, so lands boost their own colour |

The hex suffix in each filename is the first 8 hex digits of the resulting
ROM's MD5, so you can tell builds apart at a glance.

## Base ROM

You must supply this yourself, from your own cartridge:

```
Yu-Gi-Oh! Duel Monsters (Game Boy, 1998), English translation
MD5  dea982111cc284f28ec4c161e921bbcf
size 1,048,576 bytes
```

The patch verifies this by checksum. Applying it to any other dump **fails with
an error** rather than producing a broken ROM — if a patcher rejects your file,
you have the wrong base, not a bad patch.

## Applying

Use [Flips](https://github.com/Alcaro/Flips) (Windows/Linux), a browser patcher,
or this repo's own tooling:

```
python work/scripts/patch.py verify --product duelmonsters-mtg
```

Flips: *Apply Patch* → pick the `.bps` → pick your base ROM → choose an output
name. That output is yours alone; don't redistribute it.

## Playing

Any Game Boy emulator runs the result. The target device is a **Miyoo Mini
Plus on stock software**, so both hacks stay within the original 1 MB / 64-bank
MBC1 layout with a valid header checksum — no ROM expansion, nothing that needs
a modern emulator.

`<product>.md5` records the expected base and result hashes for both hacks, so
a mismatch is diagnosable without re-running the build.
