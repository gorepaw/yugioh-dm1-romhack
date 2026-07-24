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

## Editing

Edits are queued as data (JSON / the `EDITS` list) and applied by `build.py`.
Scripts are in `work/scripts/` (run with your Python 3).

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

Then build, and undo by removing the relevant JSON entry / `EDITS` line:
```
python build.py                                       # -> build/dm1-hack.gb
```

DM1 cards have no deck cost, Guardian Stars, or levels (those are later-game systems),
so name + ATK + DEF + type + description is the complete, editable card model.
