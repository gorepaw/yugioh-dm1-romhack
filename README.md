# Yu-Gi-Oh! Duel Monsters (GB, 1998) — Romhack

A romhack of the first Game Boy Yu-Gi-Oh! game (**Yu-Gi-Oh! Duel Monsters**, Japan-only, 1998),
built on top of **Darrman's English translation** as the base.

> **No ROM is included or distributed here.** This repository contains only original
> tooling and reverse-engineering documentation. You must supply your own legally
> obtained copy of the game. Darrman's translation patch is available separately from
> [its own repository](https://github.com/Darrman/DM1Translation). Emulator and
> assembler binaries are likewise not redistributed — see the setup notes below.

## Goal

Improve the game across four layers:

1. **Text** — card names, dialogue, menu wording
2. **Data** — card ATK/DEF, types, drop rates, deck contents
3. **Graphics** — title screen, sprites, card art, font
4. **Logic** — duel rules, opponent AI, new features (assembly)

## Project layout

| Folder | Tracked in git? | What it holds |
|---|---|---|
| `roms/` | ❌ (copyright) | `dm1-english.gb` — the English-patched ROM (our base / source of truth) |
| `reference/` | ❌ (external) | Darrman's translation repo, disassembly, other people's work |
| `tools/` | ❌ (large) | RGBDS, BGB emulator, flips, mgbdis |
| `work/` | ✅ | Our own edits, scripts, and patches |
| `build/` | ❌ (derived) | Built/patched ROMs we produce |
| `docs/` | ✅ | Research notes, memory map, addresses we discover |

Only **our own work** (`work/`, `docs/`, this README) is committed. ROMs are never committed.

## The base ROM

Our base is **already the English translation** (Darrman's `DM1.ips` applied — verified: all
562 patch records already matched, so there is no patching step).

- **File:** `roms/dm1-english.gb`  (English-patched; internal header title is still `YUGIOU`)
- **Hardware:** MBC1+RAM+Battery · 1 MB (64 banks) · SGB-enhanced
- **MD5:** `DEA982111CC284F28EC4C161E921BBCF`  ← this is the *English* ROM
- **SHA1:** `1BB5F02609592E0E9F6F77ACED78F00EB61AFD3D`

We hack this English base directly (fine for all four layers) and do not keep a clean Japanese
ROM. If your ROM's MD5 differs from the above, addresses in this repo may not line up.

## Rebuilding from scratch

External dependencies aren't committed. To reconstruct the working tree:

```
# Base translation (provides DM1.ips + text extract/insert scripts + graphics)
git clone https://github.com/Darrman/DM1Translation.git reference/DM1Translation
```

Toolchain (in `tools/`, not committed): Python 3, RGBDS (assembler), BGB (emulator/debugger),
mgbdis (disassembler).

## Build flow

```
roms/dm1-english.gb  --our edits-->  build/dm1-hack.gb   (our romhack)
```

`roms/dm1-english.gb` stays pristine; we always build our hack into `build/`.

### Hard build invariants (target hardware: Miyoo Mini Plus / OnionOS)

Builds must stay drop-in replaceable for the base ROM, because handhelds are fussy
about romhacks. `build.py` preserves all of these, and they should not be broken
without a very good reason:

| Invariant | Value | Why |
|---|---|---|
| File size | **1,048,576 bytes** (64 banks) | growing the ROM is the #1 cause of hacks failing on handhelds |
| Cart type `0x147` | `0x03` MBC1+RAM+BATTERY | changing the mapper breaks core compatibility |
| ROM-size byte `0x148` | `0x05` | must agree with the real file size |
| RAM-size byte `0x149` | `0x02` (8 KB) | keeps existing `.sav` files compatible |
| Header checksum `0x14D` | recomputed each build | **real hardware refuses to boot on a mismatch** |
| Global checksum `0x14E–F` | recomputed each build | cosmetic, but cheap to keep correct |

Everything is patched **in place inside existing banks**. Relocations (e.g. the verb
jump table, or the card-name pool if it ever overflows) move data into free space
*within* the existing 64 banks — they never append. Adding a bank would require
changing `0x148`, which is exactly the change that breaks handheld compatibility.

## Editing

Edits are queued as data (JSON / the `EDITS` list) and applied by `build.py`.
Scripts are in `work/scripts/` (run with your Python 3).

**The card compiler** (`cardc.py`) is the main way to edit cards. It extracts every
card's complete model — name, type, ATK/DEF across all seven terrain tables, and lore —
into `work/cards.json`, then recompiles all of it back into the ROM, repacking and
re-pointing the name and description pools:

```
python cardc.py extract              # -> work/cards.json (the source of truth)
python cardc.py verify               # extract -> recompile -> must be byte-identical
python cardc.py show 1 24
python cardc.py budget               # name / description pool usage
```

Edit `work/cards.json`, then `python build.py`. `verify` is the safety net: it proves
the compiler reproduces the base ROM exactly, so any diff in your build is a change
you made rather than a decoding bug.

> **Both text pools are 100% full** (names 4480 B, descriptions 13139 B). Renaming is
> a zero-sum budget — a longer name has to be paid for by a shorter one somewhere, and
> the compiler refuses to build if the total overflows.

`work/cards.json` is gitignored: it holds the translated card text, which isn't ours
to redistribute. Regenerate it with `cardc.py extract`.

The narrower editors below still work and are applied *after* the compiler, so they
can tweak individual cards on top of it.

**Card stats & type** — `cards.py` → `work/card_edits.json`:
```
python cards.py find dragon                          # search by name
python cards.py show 1 22                             # decode ATK/DEF/type
python cards.py types                                 # list the 21-type enum
python cards.py set 1 --atk 3000 --def 2500 --type Dragon
```

**Card descriptions** — `descriptions.py` → `work/desc_edits.json` (2 lines × 18 tiles):
```
python descriptions.py show 1
python descriptions.py set 1 "line one (<=18)" "line two (<=18)"
```

**Text / names / dialogue** — `text_tool.py` (search) + the `EDITS` list in `build.py`:
```
python text_tool.py reference/DM1Translation/Insertion/text.tbl roms/dm1-english.gb search "your turn."
```

**Card artwork** — `cardart.py` → `work/<product>/art/NNN.png` (needs Pillow):
```
python cardart.py extract                             # all 365 -> work/duelmonsters-kaizo/art_src/
python cardart.py preview mypic.png --out opts.png    # every dither/fit, with sizes
python cardart.py import 24 mypic.png --dither bayer4 # -> work/duelmonsters-kaizo/art/024.png
python cardart.py budget                              # per-bank space report
```
Each card is a 64×80 four-shade picture with the frame baked in (art box 52×68).
`import` converts any image you supply and prints the compressed size against the
card's slot; `build.py` writes in place when it fits and repacks the bank when it
doesn't. Cards with no PNG keep their stock picture byte for byte.

> Dithering costs space. `--dither bayer4` (the default) and `bayer8` compress far
> better than `fs`; `none` is smallest. Watch the byte count `import` prints.

Full reference — format, per-bank budget, which cards share a bank, and the
traps — is in **[docs/CARDART.md](docs/CARDART.md)**.

**Screens and font** — `screens.py` → `work/<product>/screens/<name>.png`:
```
python screens.py list                                # every screen + its budget
python screens.py extract                             # -> work/<product>/screens_src/
python screens.py import title mypic.png              # 160x144, any image
python screens.py import arena00 face.png             # a duel backdrop, 160x88
python screens.py font extract | font import f.png    # the 128-glyph font, 128x64
```
The title screen, the boot splashes, the character portraits and the duel
backdrops are repaintable pictures; the menus are tilemaps of **font glyphs**,
so restyling the font restyles every menu and every line of dialogue at once.

> The game runs an **inverted palette** (BGP `$1B`: colour 0 is black, 3 is
> white). `screens.py` handles it — every PNG it reads or writes is in screen
> colours. Note this also means `cardart.py`'s extracts are negatives.

Full reference — the four graphics formats, the duel/dialogue screen, per-screen
budgets and the traps — is in **[docs/SCREENS.md](docs/SCREENS.md)**.

**Cards awarded per won duel** — `grind.py` → `work/grind_config.json`:
```
python grind.py show
python grind.py set 3                                 # 1 = stock
```

**Win-count reward thresholds / cards** — `rewards.py` → `work/reward_config.json`:
```
python rewards.py show 0                              # thresholds + duelist 0's rewards
python rewards.py set-thresholds 10 20 30 40 50 60 70 80 90 100
```

Then build, and undo by removing the relevant JSON entry / `EDITS` line:
```
python build.py                                       # -> build/dm1-hack.gb
```

### Reverse-engineering tools

The game calls across banks with `rst $08` followed by two inline parameter bytes,
which desyncs ordinary disassemblers. These understand it:

```
python farcall.py table 0x0D          # decode a bank's routine pointer table
python farcall.py calls 0x0D 0        # every call site targeting bank 13 routine 0
python dis.py 0x03400C 33             # disassemble, resolving far calls
python dis.py 0x03400C 33 --rom ../../build/dm1-hack.gb
python bank13_map.py                  # account for every byte of bank 13
python find_freespace.py ../../roms/dm1-english.gb
```

Note `find_freespace.py` reports *candidates*, not free space: runs of `0x00`/`0xFF`
in this ROM are frequently live cumulative-weight data, pointer-table initialisers,
or blank graphics tiles. Always confirm against a bank map before writing a patch.

DM1 cards have no deck cost, Guardian Stars, or levels (those are later-game systems),
so name + ATK + DEF + type + description is the complete, editable card model.
