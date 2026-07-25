# Screens — title, dialogue, menus, duel field, font

**Status: solved and working.** Every screen in the game that isn't card art is
located, decoded, extractable to PNG and replaceable from PNG; `build.py` packs
the replacements back in. `screens.py verify` passes 28/28 and a build with a
replaced title screen, a replaced duel backdrop and a re-imported font was
checked byte for byte against the base ROM.

This is the companion to `docs/CARDART.md`. Card art is one format used 365
times; screens are **four** formats used a few dozen times, so the useful thing
to hold in your head is which format a given screen uses.

---

## 0. The one thing that will confuse you first: the palette is inverted

DM1 runs with **BGP = `$1B`**, not the usual `$E4`:

| stored colour | under `$E4` (normal) | under **`$1B`** (what DM1 uses) |
|---|---|---|
| 0 | white | **black** |
| 1 | light grey | dark grey |
| 2 | dark grey | light grey |
| 3 | black | **white** |

So in every tile in this document, **colour 0 is ink and colour 3 is paper.**
Proof, not inference: rendering the title screen's tiles + tilemap under `$1B`
matches Darrman's own `reference/DM1Translation/Graphics/titleEN.png` on
23,004 of 23,040 pixels; under `$E4` it matches 6.

The only exceptions are the three boot logos (KONAMI, KCE Shinjuku, copyright),
which run `$E4`.

| routine (bank 0) | BGP | OBP0 | OBP1 | used by |
|---|---|---|---|---|
| `$0FF0` | `$1B` | `$1B` | `$1B` | |
| `$0FFF` | `$1B` | `$E4` | `$1B` | menus (trunk, deck, trade) |
| `$100E` | `$1B` | `$D2` | `$1B` | title, portraits, cast, ruins |
| `$101D` / `$24AF` | `$00` | `$00` | `$00` | blank the screen before a load |
| `$2495` | `$E4` | `$E4` | `$E4` | the three boot logos |
| `$24BA` | fade `$00`→`$40`→`$90`→`$E4` | | | boot logo fade-in |
| `$257F` | fade `$FF`→`$AB`→`$5B`→`$1B` | | | fade into the game palette |

`screens.py` stores each screen's BGP and does the conversion, so **every PNG it
reads or writes is in screen colours — what the player sees.** You never have to
think about raw colour indices unless you are hand-editing bytes.

> ⚠ This applies to card art too. Card pictures are shown under `$1B`, so the
> PNGs `cardart.py extract` writes are inverted relative to the screen (its
> `SHADES` table assumes 0 = lightest). The card-art *tooling* is unaffected —
> it round-trips the same indices either way — but if you author a replacement
> by eye from an extract, you are drawing a negative. Invert before importing,
> or import from a source image and let `cardart.py` do the conversion.

---

## 1. The four formats

| # | Format | Count | Where | Editable as |
|---|---|---|---|---|
| 1 | **Static screen** — raw tiles + 20×18 tilemap | 21 | banks `$0A`/`$0B`/`$0C` | a 160×144 PNG (picture screens) or a 360-byte tilemap (layout screens) |
| 2 | **Duel backdrop** — LZSS 192-tile set + 20×11 tilemap | 18 | banks `$2E`–`$30`, maps in bank `$06` | a 160×88 PNG |
| 3 | **Font** — 128 glyphs, 1 bit per pixel | 1 | `0x0080D9` | a 128×64 PNG |
| 4 | **Window frames** — small raw tile blocks | 3 | banks `$06`/`$0A`/`$0C` | raw tiles (rarely worth touching) |

Everything below is reachable from one tool:

```bash
python screens.py list      # every screen, its addresses, its budget
python screens.py budget
python screens.py extract   # all of it -> work/<product>/screens_src/*.png
python screens.py verify
```

---

## 2. Static screens — the title screen and its 20 siblings

### The loader, which is the same code 21 times

```
$xxxx  push af/bc/de/hl
       ld de,$9000 / ld hl,<tiles>  / ld b,$80 / ld c,$10   ; 128 tiles -> ids $00-$7F
       ld de,$8800                  / ld b,$80 / ld c,$10   ; 128 tiles -> ids $80-$FF
       ld de,$9800 / ld hl,<map>    / ld b,$12 / ld c,$14   ; 20x18, +12 per row
```

Tile addressing is **signed** (LCDC bit 4 = 0), so `$9000` holds ids `$00`–`$7F`
and `$8800` holds `$80`–`$FF`; on disk the tiles are simply 256 consecutive
16-byte tiles in id order. The map blit adds 12 to the destination after each
row of 20, because the BG map is 32 tiles wide.

`screens.py` finds these by scanning for the map blit
(`06 12 0E 14 2A 12 13 0D 20 FA`) and walking backwards over the tile blits, so
**the addresses come out of the ROM, not out of a table that can go stale.**

### The 21 screens

| name | bank | tiles | map | kind | cap | far call |
|---|---|---|---|---|---|---|
| `trunk` | `$0A` | `0x0283CC` | `0x02846C` | layout | 10 | `CF 05 0A` |
| `trunk-trade` | `$0A` | `0x0283CC` | `0x02860E` | layout | 10 | `CF 13 0A` |
| `deck` | `$0A` | `0x0287B0` | `0x028850` | layout | 10 | `CF 07 0A` |
| `trade-review` | `$0A` | `0x0287B0` | `0x0289F2` | layout | 10 | `CF 09 0A` |
| `duel-prep` | `$0A` | `0x028B94` | `0x028CA4` | layout | 17 | `CF 0B 0A` |
| `trade-prep` | `$0A` | `0x028B94` | `0x028E46` | layout | 17 | `CF 0D 0A` |
| `link-menu` | `$0A` | `0x02805A` | `0x028FFB` | layout | 50 | `CF 11 0A` |
| `duel-field` | `$0A` | `0x0291AA` | `0x0292BA` | layout | 17 | `CF 0F 0A` |
| **`title`** | `$0A` | **`0x02946C`** | **`0x02A46C`** | **picture** | **256** | `CF 15 0A` |
| `duel-field-jp` | `$0A` | `0x02A60B` | `0x02A6AB` | layout | 10 | `CF 17 0A` (never called) |
| `ruins` | `$0A` | `0x02A85A` | `0x02B85A` | picture | 256 | `CF 19 0A` |
| `konami` | `$0B` | `0x02C051` | `0x02C361` | picture | 49 | `CF 03 0B` |
| `kce-shinjuku` | `$0B` | `0x02C510` | `0x02CA20` | picture | 81 | `CF 05 0B` |
| `copyright` | `$0B` | `0x02CBCF` | `0x02D5AF` | picture | 158 | `CF 07 0B` |
| `cast` | `$0B` | `0x02D75E` | `0x02E75E` | picture | 256 | `CF 09 0B` |
| `simon` | `$0C` | `0x030055` | `0x030FF5` | picture | 250 | `CF 03 0C` |
| `pegasus` | `$0C` | `0x0311A4` | `0x0321A4` | picture | 256 | `CF 05 0C` |
| `yami-yugi` | `$0C` | `0x032353` | `0x033353` | picture | 256 | `CF 07 0C` |
| `name-lower` | `$0C` | `0x0334F5` | `0x0335C5` | layout | 13 | `CF 09 0C` |
| `name-upper` | `$0C` | — | `0x033751` | layout | 0 | `CF 0B 0C` |
| `records` | `$0C` | `0x0334F5` | `0x0338F0` | layout | 13 | `CF 0D 0C` |

`duel-field-jp` is dead weight: it is the untranslated Japanese duel layout and
its far-call table entry has no call site anywhere in the ROM. Its ~4 KB of
bank `$0A` is therefore reclaimable if you ever need space there.

### PICTURE vs LAYOUT — the distinction that matters

A **picture screen** is drawn entirely from its own tile blob. Repaint it from
any image:

```bash
python screens.py import title mypic.png --dither bayer4
python build.py
```

A **layout screen** owns only a window-frame tile set (9–17 tiles) and spells
everything else out of **font glyphs**, so there is no picture to replace —
`import` refuses these and tells you so. Their content is the 360-byte tilemap,
where a byte below `$80` is a *character code* from
`reference/DM1Translation/Insertion/text.tbl` and a byte at `$80`/`$D0` and
above is a frame tile. That is how Darrman translated the menus: he rewrote the
tilemaps as text (`reference/DM1Translation/Insertion/script/tilemaps.txt`).

`screens.py` classifies automatically — a screen is a picture when ≥90 % of its
360 cells point inside its own blob and it owns ≥32 tiles — and merges the font,
the digit tiles and the window frame into layout-screen extracts so they come
out readable instead of as blank boxes.

The two window-frame vocabularies:

```
menus (ids $80-$89, from the 128-tile blobs in bank $0A)
   $80 blank   $82 ┌  $83 ─  $84 ┐
               $85 │         $86 │
               $87 └  $88 ─  $89 ┘

dialogue/name entry (ids $D0-$FF, 48 tiles from 0x02805A -> VRAM $8D00)
   $D2 ┌  $D3 ─  $D4 ┐    $D5 │  $D6 │    $D7 └  $D8 ─  $D9 ┘
```

### THE SPACE BUDGET

There is no free space and no relocation: a screen's tiles are written back
**in place**, so the only limit is **distinct tiles**.

```
python screens.py budget
```

| Fact | Value |
|---|---|
| Screen | 20 × 18 = **360 cells** |
| Tiles a full-page loader copies | 256 |
| Bytes per tile | 16 |
| So: **at least 104 of the 360 cells must repeat** | always |
| Stock title screen | 248 distinct of 256 |
| Tightest picture screens | `konami` 49/49, `kce-shinjuku` 81/81 — **full** |

The `cap` column is not always 256. Several loaders copy 256 tiles from a blob
that is shorter than 4096 bytes, so the copy runs straight over the tilemap and
into VRAM as tiles nothing references (`copyright`'s real blob is 158 tiles;
`simon`'s is 250). `screens.py` computes the cap as *the smaller of* what the
loader copies and the room before the next structure, which is what keeps an
import from clobbering the map that sits right behind it.

If an import needs more than the cap it fails loudly and writes nothing.
Flatten the source (`--dither none`, less detail, larger flat areas) — the fix
is always fewer *unique* 8×8 blocks, not a smaller file.

### A trap: `copyright` is not what its name suggests

`0x02CBCF` starts with **a 2 bpp copy of the whole font** (128 tiles), and only
tiles `$80`–`$9D` are logo art. Darrman replaced the Japanese splash graphic
with font tiles + a text tilemap. That is why it decodes as legible text rather
than as a picture.

---

## 3. The dialogue screen — duelist portrait + text window

This is the screen the game spends the most time on, and it is two independent
pieces stacked:

```
rows 0-10   20x11 tilemap  ->  the duelist's portrait   (bank $06 table)
rows 11-17  20x7  tilemap  ->  the text window          (bank $06 $419D)
```

### The 18 portraits (a.k.a. duel backdrops)

Same codec as card art — Okumura LZSS, `work/scripts/gblzss.py` — but a
different geometry, which is why they resisted decoding for so long:

| | |
|---|---|
| Payload | **3072 bytes = 192 tiles** (`ld bc,$0C00` at `$1A89`) |
| VRAM | ids `$00`–`$7F` → `$9000`, ids `$80`–`$BF` → `$8800` |
| Bank table | `0x001A9D`, 18 bytes, banks `$2E`/`$2F`/`$30`, six each |
| Pointer table | bank `$10` CPU `$7E84` (the `d`=1 path of the shared loader `$4002`) |
| Tilemaps | bank `$06` CPU `$4229`, 18 × 16-bit pointer → 20 × 11 = 220 bytes each, packed back to back from `$424D` |
| Selected by | `$CD50`, the game-state byte |

> **The tiles are NOT a picture.** `docs/CARDART.md` recorded this set as
> undecoded because no tile arrangement scored well. That was correct and the
> reason is now known: it is a **tileset**, not a bitmap. Ruled out and recorded
> so nobody repeats it — every (width × height) factor pair of 192 in row,
> column, 2-tall-pair, 4-tall-pair and every band-height order (best seam score
> 1.54 vs card art's 0.90); linear 2 bpp bitmaps at six widths; separated
> bitplanes; 1 bpp. All noise. The tilemap in bank `$06` is the missing half.

Loader chain (bank 0), for reference:

```
$187B  set image: d = set (0 = card art, 1 = backdrop), bc = index
$188A  dispatch through the 2-entry table at $18AD -> $18B1 (card art) / $1A5E
$1A5E  call $1A65 (set up) then $1AFD (decompress)
$1A65  bank in $10, look up the pointer, output length $0C00, bank in $2E/$2F/$30
```

Both are driven by the cutscene/script interpreter in bank `$07` (`$400C`
reads three script bytes: set, index low, index high).

### The text window

16 tiles at **bank `$06` `$405E` (`0x01805E`)** → VRAM `$8BB0` = ids
`$BB`–`$CA`, blitted *after* the backdrop, which is why a backdrop may only use
ids `$00`–`$BA`. Only 13 of the 16 are real:

| id | piece | id | piece |
|---|---|---|---|
| `$BB` | paper (solid) | `$C2` | left edge |
| `$BC` | ink (solid) | `$C3` | right edge |
| `$BD` | horizontal rule | `$C4` | top-right corner |
| `$C0` | bottom-right corner | `$C5` | top-left corner |
| `$C1` | bottom-left corner | `$C6`–`$CA` | junk |

Its map is 140 bytes at **bank `$06` `$419D` (`0x01819D`)**:

```
C5 BD x18 C4
C2 BB x18 C3     <- six rows of paper; the text engine writes glyph ids in here
...
C1 BD x18 C0
```

Two more pieces of the same screen, for completeness:

* **digits** — bank `$02` `$4059` renders font glyphs `$01`–`$0A` into ids
  `$C6`–`$CF` (VRAM `$8C60`), which is what the LP and ATK/DEF counters use.
* **the duelist's name** — bank `$06` `$535B` points the VRAM write cursor at
  `$8D00` (ids `$D0`+) and renders the name string glyph by glyph, because the
  backdrop has just overwritten the font's normal home at `$9000`.

### Editing one

```bash
python screens.py extract arena00        # -> work/<p>/screens_src/arena00.png (160x144)
python screens.py import arena00 face.png --dither bayer4
python build.py
```

Import takes a **160×88** image (the portrait area only — the text window
belongs to the engine, not to the backdrop). Budget:

| | |
|---|---|
| Distinct tiles | ≤ **187** (`$00`–`$BA`) |
| Cells | 20 × 11 = 220, so ≥ 33 must repeat |
| Bank capacity | 16,382 bytes for six backdrops |
| Stock use | `$2E` 14,535 · `$2F` 13,782 · `$30` **15,681** (only 701 spare) |

A backdrop that outgrows its slot repacks its whole bank and rewrites the six
pointers, exactly like card art; overflow is a hard error that writes nothing.

> ⚠ **Bank `$30` — backdrops 12–17 — is the binding constraint.** It has
> **701 bytes spare of 16,382**, and a busy replacement runs 300–500 bytes over
> the stock stream it displaces, so that bank cannot absorb even two of them.
> `$2E` has 1,847 spare and `$2F` has 2,600. **Spread replacements across the
> three banks rather than clustering them**, and use `--dither none` on anything
> destined for `$30`. `screens.py budget` prints the headroom and flags any bank
> under 1 KB, so check it before you plan a batch — this is the one number that
> decides whether a set of replacements is possible at all.

> Curiosity, harmless but don't "fix" it: Konami's streams are each ~14–25 bytes
> *shorter* than the game decodes, so every backdrop reads a few bytes of its
> neighbour to fill tiles `$B8`–`$BF`, which no tilemap references. Our packer
> encodes all 3072 bytes honestly, so replacements are slightly larger than
> stock — the bank repack absorbs it.

---

## 4. The font

| | |
|---|---|
| Location | **`0x0080D9`** (bank `$02` CPU `$40D9`) |
| Format | **1 bit per pixel**, 8 bytes per glyph, **128 glyphs** = 1024 bytes |
| Polarity | bit set = paper (colour 3), bit clear = ink (colour 0) |
| Encoding | `reference/DM1Translation/Insertion/text.tbl` — `$00` space, `$01`–`$0A` `0`–`9`, `$0B`–`$24` `A`–`Z`, `$25`–`$3E` `a`–`z`, then punctuation and the space-saving ligatures `$4E` il … `$53` 't |

The loader at bank `$02` `$40B4` writes each byte **twice**, once into each
bitplane, so a glyph is pure black on pure white with no greys — which also
means a 1 bpp font costs half what a 2 bpp one would.

Two entry points use it:

* `$403E` — blit all 128 glyphs to VRAM `$9000` (ids `$00`–`$7F`). This is why
  a menu tilemap can just contain text: cell byte = character code = tile id.
* `$4074` — render one glyph. **Codes ≥ `$7D` take a different path** (`$4096`):
  they are read as ready-made 2 bpp tiles, 16 bytes each, from
  **bank `$02` `$44C1` (`0x0084C1`)**. That is where the few glyphs that need
  grey live.

```bash
python screens.py font extract          # -> screens_src/font.png, 128x64, 16 x 8 glyphs
#   edit it in any pixel editor - only pure black and pure white survive
python screens.py font import myfont.png
```

Restyling the font restyles **every menu, every card name, every line of
dialogue** at once, and costs nothing: it is a fixed 1024-byte slot.

---

## 5. How a replacement gets into the ROM

### The contract with `build.py`

```
work/<product>/screens/<name>.png     one per screen you want to change
        <name>  = any name from `screens.py list`
        160x144 for a static picture screen
        160x88  for arena00 .. arena17
        128x64  for `font`
```

Files starting with `_` are skipped (that is where `import` puts its 3× zoom
previews). **A screen with no PNG keeps its stock graphics byte for byte.** An
unrecognised filename is a hard error rather than a silent no-op.

`build.py` calls `screens.apply_config` right after the card-art step. Static
screens are written in place (tiles then map, no pointer moves); backdrops go
through the bank-repack path.

### Workflow

```bash
python screens.py list                                # what exists, and its budget
python screens.py extract                             # see the stock art
python screens.py import title mypic.png --dither bayer4 --fit cover
python screens.py budget
python build.py
```

`import` options: `--dither bayer4|none`, `--fit cover|contain|stretch`,
`--contrast N`, `--invert`. It prints the distinct-tile count against the cap
every time — watch that number, it is the only thing that can fail.

---

## 6. Traps

- **The palette is inverted.** Section 0. Everything else follows from it.
- **Three menus share one tile blob** (`0x0283CC` serves `trunk` and
  `trunk-trade`; `0x0287B0` serves `deck` and `trade-review`; `0x028B94` serves
  `duel-prep` and `trade-prep`). Changing the frame changes all of them.
- **Loaders copy past the end of their data.** A 256-tile copy from a 158-tile
  blob is normal and harmless — the surplus lands in VRAM as tiles no tilemap
  references. It does mean the naive "tiles are 4096 bytes" assumption will
  overwrite the tilemap sitting right behind them. Use the computed cap.
- **The 192-tile backdrops are a tileset, not a bitmap.** Section 3.
- **`copyright`'s tile blob is mostly font.** Section 2.
- **Darrman's `tilemaps.txt` offsets are not the map starts** — he jumped into
  the middle of each map to skip leading blank rows: name entry is `0x0335C5`
  here but `$33601` there (+60 = three rows in), the copyright splash `0x02D5AF`
  vs `$2D5AF`+0. Use the offsets in this document.
- **Never grow the ROM.** Everything here is in place or repacked inside its
  existing bank; the file stays 1,048,576 bytes.

---

## 7. Not done / open

- **The overworld/campaign map**, if there is one distinct from `ruins` and the
  menus, has not been separately identified. Every *full-screen* static blit in
  the ROM is accounted for above (31 raw tile blits, 21 map blits, both scans
  exhaustive), so anything left is drawn incrementally through the VRAM queue.
- **Sprites.** Twelve-tile blits to VRAM `$8000` from bank `$01` (`0x0062FB`,
  `0x006665`, `0x0068E4`, `0x006ADD`, `0x006CD6`) and a 128-tile page from
  bank `$02` `$4C78` are the OAM tiles — cursors and the sparkle on the boot
  screens. Located, not decoded, not exposed by the tool.
- **What reads bank `$20`** — still open from `docs/CARDART.md`.

---

## 8. File map

| File | What it is |
|---|---|
| `work/scripts/screens.py` | Everything: loader parsing, tile↔pixel, packer, image conversion, CLI, `apply_config` for the build |
| `work/scripts/gblzss.py` | The LZSS codec, shared with card art |
| `work/<product>/screens/<name>.png` | **Your replacements.** Committed |
| `work/<product>/screens/_preview_*.png` | 3× zoom written by `import`. Gitignored |
| `work/<product>/screens_src/*.png` | Stock screens dumped by `extract`. Gitignored (Konami's art) |
| `docs/CARDART.md` | The card-picture format — same codec, different geometry |

## 9. Verification

```
python screens.py verify        # 28/28: pixels -> tiles + map -> pixels, plus
                                # the codec round-trip on all 18 backdrops and
                                # the 1bpp font round-trip
python gblzss.py                # 200/200 codec round-trips
```

Checked end to end on a real build: after importing a replacement title screen,
a replacement `arena03` and a re-imported font, the built ROM's title screen
matches its PNG pixel for pixel, `arena03` matches its PNG, the other five
backdrops in the repacked bank `$2E` still decompress byte-identically, the font
is byte-identical, no other screen's tilemap changed, and the file is still
1,048,576 bytes.
