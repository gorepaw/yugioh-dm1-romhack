# Patches

These are **BPS patches**, not ROMs. Each one contains only the difference
between the original game and the hack, so you need your own copy of the base
ROM to play. No game data is distributed here.

| Patch | Hack |
|---|---|
| `duelmonsters-mtg-*.bps` | **Duel Monsters MTG** — a total conversion to *Magic: The Gathering*; card type becomes colour, so lands boost their own colour |
| *(pending)* | **Duel Monsters Kaizo** — the original game with 85 later-era Yu-Gi-Oh! cards worked into every opponent. Card art is still in progress; its patch is cut once that work is committed. |

A patch is only published when the tree that produced it is committed, so anyone
can rebuild the same ROM from source. `patch.py` refuses to cut one otherwise.

The hex suffix in each filename is the first 8 hex digits of the resulting
ROM's MD5, so you can tell builds apart at a glance.

## Base ROM

These hacks are built on top of **Darrman's English translation**, not on the raw
Japanese game. The base you patch is the *already-translated* ROM:

```
Yu-Gi-Oh! Duel Monsters (Game Boy, 1998), English translation
MD5  dea982111cc284f28ec4c161e921bbcf
size 1,048,576 bytes
```

So there are two steps, and you must supply the game yourself, from your own
cartridge:

1. Apply Darrman's `DM1.ips` to a clean Japanese dump. The patch and its
   instructions are at
   [github.com/Darrman/DM1Translation](https://github.com/Darrman/DM1Translation) —
   it is not redistributed here.
2. Apply one of the `.bps` patches below to the result.

The BPS verifies this by checksum. Applying it to any other dump **fails with an
error** rather than producing a broken ROM. If a patcher rejects your file, the
usual cause is step 1: you are handing it a clean Japanese ROM instead of a
translated one.

That MD5 pins one specific build of the translation. These patches were made
against `DM1Translation` commit `80b23d5` (2021-11-18). If the translation is
ever re-cut, a current `DM1.ips` will produce a ROM with a different MD5 and
these patches will refuse it — correctly, since the addresses they edit may have
moved. In that case the mismatch is a version skew, not a bad download, and the
fix is to build from that commit.

### Credit

The English translation is entirely Darrman's project and its contributors' work,
not ours — hacking and text editing by Darrman, translation by Lazermutt4,
Deltaneos, and Yugipedia contributors, title screen by Graphicus, with prior
documentation by Mantidactyle and Dinoguy1000. The full credits ship with their
repository. These patches contain none of that work: a BPS stores only the
difference against the translated base, so everything in the `.bps` files here is
our own. Play the translation on its own first if you haven't — it is the reason
this game is playable in English at all.

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
