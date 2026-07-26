# Card artwork — format, tooling, and how to replace it

**Status: solved and working.** The format is fully decoded, the codec round-trips
all 365 pictures byte-identically, replacement art can be imported from any image
file, and `build.py` packs it into the ROM. Nothing here is speculative — every
claim below was verified against the ROM.

This document is the handoff. `docs/NOTES.md` has the same format decode in its
"Card artwork" section for consistency with the rest of the reverse-engineering
notes; this file adds the workflow, the budget planning, and the traps.

---

## 1. What a card picture is

| | |
|---|---|
| Size | **64 × 80 pixels** |
| Colours | 4, stored as colour indices 0–3 |
| Palette | **BGP `$1B` — inverted: colour 0 is BLACK, colour 3 is WHITE** (see §5a) |
| Frame | **baked into the picture**, outer 6 px on all sides |
| Usable art box | **x 6–57, y 6–73 → 52 × 68 px** |
| Storage | 1280 bytes GB 2bpp (80 tiles), LZSS-compressed |
| Count | 365 (card #1 … #365) |

There is one picture per card and it is used everywhere the card is shown. There
is no separate thumbnail, no palette per card, and no per-card tilemap.

---

## 2. Where it lives in the ROM

| Structure | File offset | Format |
|---|---|---|
| Art **bank** table | `0x0018F0` | 365 bytes, card index (= card # − 1) → ROM bank |
| Art **pointer** table | `0x040028` | 365 × 16-bit LE CPU address; table ends at CPU `$4302` |
| Picture streams | banks `$10`–`$1F`, `$21`–`$2C` | 13 per bank (bank `$11` has 14) |

The pointer table lives *inside* bank `$10` at CPU `$4028`, which is why bank
`$10`'s own art starts at `$4304` instead of `$4002` like every other art bank.

**File offset of a card's stream** = `bank * 0x4000 + (cpu_addr - 0x4000)`.

### The loader chain (all in bank 0)

```
$18B1  call $18B8      ; set up
       call $1AFD      ; decompress
$18B8  call $1AAF      ; init LZSS ring at $C000, output cursor $C412, page counter $FF86=$80
       ld a,$10 / call $109F        ; bank-switch to $10
       bc = [$CD0C/$CD0D]           ; <- the card id
       d  = [$CD0B]                 ; 0 = card art table, 1 = the other set (sec. 8)
       call $4002                   ; bank $10 lookup: bc = id -> bc = art pointer
       call $1ADE                   ; $FF80/81 = source pointer
       ld a,$01 / call $1AF9        ; $CD0E = 1  (method: compressed)
       ld bc,$0500 / call $1AF0     ; $FF84/85 = 1280 = output byte count
       hl = $18F0 + card id / call $109F   ; bank-switch to the art bank
$1AFD  $CD0E == 1 ? $1B23 (LZSS) : $1B0E (raw 10 x 128-byte copy of the same 1280 B)
```

`$4002` in bank `$10` is **not** the usual far-call routine table — it is a plain
lookup routine, `d`=0 → pointer table `$4028`, `d`=1 → a second table at `$7E84`.

> The raw path at `$1B0E` is real and works: set `$CD0E` to anything but 1 and the
> game copies 1280 uncompressed bytes instead. The shipped data never uses it, but
> it is an escape hatch if compression ever becomes the binding constraint.

---

## 3. The codec — Okumura LZSS (`work/scripts/gblzss.py`)

Recovered from `$1B23` plus `$1B92` (source fetch) and `$1BA5` (output store).

| Parameter | Value |
|---|---|
| Ring buffer | `$C000`–`$C3FF`, 1024 bytes |
| Prefill | `$C000`–`$C3DD` (990 bytes) = `$20`; the last 34 bytes are never read |
| Initial write cursor | `$C3DE` (= N − F = 1024 − 34, the textbook value) |
| Flag byte | 8 tokens, **LSB first**; `1` = literal, `0` = back-reference |
| Literal | 1 byte |
| Reference | 2 bytes `lo hi`: `len = (hi & $1F) + 3` (3–34), `pos = ((hi >> 5) & 3) << 8 \| lo` (0–1023) |
| Unused | bit 7 of `hi` |
| Terminator | **none** — the decoder stops the instant the output counter hits 0, mid-token if need be |

Output does **not** go into the ring. `$1BA5` streams it via `$C412` in 128-byte
pages (`$FF86` counts down from `$80`) through `$17DB` into the VRAM queue.

Because the ring is only a sliding window over `(990 × $20) ++ output`, this is
plain LZ77 with a 1024-byte window, and that is how `gblzss.compress` encodes it.

**Our encoder beats Konami's**: 392,393 vs 394,001 bytes across all 365 cards
(−0.4 %). It is larger on 12 cards, by at most 4 bytes, and all 12 still fit.

---

## 4. Tile order — the trap

The 80 tiles are stored as **8 × 16 vertical PAIRS**, not row-major:

```
tile 2t     = TOP half of a column
tile 2t + 1 = BOTTOM half of that column
pairs run left -> right across a 16-pixel band, then band by band
layout is 8 tiles wide x 10 tall
```

A plain row-major dump looks like scrambled noise and will send you chasing
imaginary compression bugs. If you ever need to re-derive an arrangement, score
candidates by **seam roughness ÷ interior roughness** — the true layout came out
at 0.90 (seams *smoother* than tile interiors) while every other arrangement,
including all the plausible ones, scored ≥ 1.12. Whole-image gradient energy does
**not** separate them; only the seam ratio does.

`cardart.to_pixels()` / `cardart.to_raw()` handle this; don't re-implement it.

---

## 5. The frame

All 365 pictures share a rounded frame in the outer 6 pixels. Stored **colour
index** on the left, what the player actually sees on the right:

| | stored | displayed (BGP `$1B`) |
|---|---|---|
| col 0 (col 63 = 1) | 2 | light grey |
| cols 1–3 (60–62) | **0** | **black** |
| col 4 (59) — inner rounded line | 1 | dark grey |
| col 5 (58) — bevel | 2 | light grey |

…and the same top and bottom (row 0 = colour 2, row 4 = inner line, row 79 =
colour 1). So it reads on screen as a **black border ring with a grey bevel**
around a white art box — which is the same black-on-white convention every menu
frame in the game uses.

### 5a. The palette is inverted — this bites when you author by hand

DM1 runs **BGP = `$1B`**: stored colour **0 displays as BLACK** and **3 as
WHITE**. Only the three boot logos use the normal `$E4`, and card art is never
on screen during those. (Proof and the full palette table are in
[SCREENS.md](SCREENS.md) §0.)

`cardart.py` handles it: **every PNG it reads or writes is in screen colours —
what the player sees.** `import` converts a source image so that bright stays
bright, `extract` writes a picture that looks like the card, and `load_png`
undoes it on the way back in. You only need to care about stored indices if you
are reading raw bytes.

> This was wrong until 2026-07-24: the tool assumed colour 0 was the lightest,
> so extracts came out as negatives *and* `import` wrote inverted pictures into
> the ROM. Fixed. No replacement art existed yet, so nothing needed migrating —
> but any 64 × 80 PNG authored before that date is a negative and must be
> inverted before use.

`cardart.frame_template()` derives it by taking the **modal value across a sample
of the roster**, so a single card whose art bleeds into the border cannot corrupt
it. Don't copy it from one card.

`import` re-stamps this frame by default. `--frame none` skips it and lets the
picture bleed to all four edges (the art then gets the full 64 × 80 canvas
instead of the 52 × 68 box) — visually inconsistent with the rest of the game,
so use it deliberately.

---

## 6. THE SPACE BUDGET — read this before picking cards

This is the only real constraint, and it is **per bank**, not per card.

```
python cardart.py budget            # stock
python cardart.py budget --product duelmonsters-mtg   # with your replacements costed in
```

| Fact | Value |
|---|---|
| Uncompressed picture | 1280 bytes |
| **Worst case compressed** (incompressible noise) | **1440 bytes** |
| Typical stock picture | ~1080 bytes |
| Typical in-place slot | ~1150–1250 bytes |
| Bank capacity ÷ cards (most banks) | **1260 bytes/card** |
| Bank capacity ÷ cards (bank `$11`, the tightest) | **1170 bytes/card** |
| Total spare after a tight repack | **63,925 bytes** |

### Which cards share a bank

Cards are grouped 13 per bank in card-number order, so **replacing #1–#13 all at
once spends one bank's budget**, and replacing #1, #50, #200 spends three
different banks' budgets. Spreading replacements across banks is free; clustering
them is what runs you out of room.

| Bank | Cards | | Bank | Cards |
|---|---|---|---|---|
| `$10` | #1–13 (15,612 B — the pointer table eats the first 772) | | `$21` | #210–222 |
| `$11` | #14–27 (**14 cards — tightest bank**) | | `$22` | #223–235 |
| `$12` | #28–40 | | `$23` | #236–248 |
| `$13` | #41–53 | | `$24` | #249–261 |
| `$14` | #54–66 | | `$25` | #262–274 |
| `$15` | #67–79 | | `$26` | #275–287 |
| `$16` | #80–92 | | `$27` | #288–300 |
| `$17` | #93–105 | | `$28` | #301–313 |
| `$18` | #106–118 | | `$29` | #314–326 |
| `$19` | #119–131 | | `$2A` | #327–339 |
| `$1A` | #132–144 | | `$2B` | #340–352 |
| `$1B` | #145–157 | | `$2C` | #353–365 |
| `$1C` | #158–170 | | | |
| `$1D` | #171–183 | | | |
| `$1E` | #184–195 **and #199** | | | |
| `$1F` | #196–198 **and #200–209** | | | |

> ⚠ Banks `$1E`/`$1F` interleave — card #199 lives with `$1E` while #196–198 live
> with `$1F`. `cardart.py budget` prints the exact set for those two rather than a
> range. Nothing else in the roster is out of order.

### What costs bytes

**Dithering, overwhelmingly.** Flat regions compress to almost nothing; dither
noise compresses to nothing at all.

| Setting | Typical size | Notes |
|---|---|---|
| `--dither none` | smallest | hard 4-level posterise, banding on gradients |
| `--dither bayer4` (default) | small | regular pattern, compresses well, matches the stock art's look |
| `--dither bayer8` | small | finer pattern, slightly better tonality |
| `--dither fs` | **largest** | Floyd–Steinberg; best detail, worst compression |

Busy, high-frequency source images cost more than clean ones regardless of dither.
`import` prints the compressed size every time — watch it.

---

## 7. How a replacement gets into the ROM

### Workflow

```bash
# 0. one-time: Pillow must be installed for the interpreter you use
#    C:\Users\lando\AppData\Local\Programs\Python\Python313\python.exe -m pip install Pillow

# 1. see the stock art (optional, for reference/comparison)
python cardart.py extract                     # all 365 -> work/duelmonsters-kaizo/art_src/NNN.png
python cardart.py extract --cards 1,5,10-20
python cardart.py show 1 24 89 --out sheet.png

# 2. try conversion settings on your image
python cardart.py preview mypic.png --out opts.png   # 10 variants + byte counts

# 3. commit one
python cardart.py import 24 mypic.png --dither bayer4 --fit cover
#    -> work/duelmonsters-kaizo/art/024.png            (the build reads this)
#    -> work/duelmonsters-kaizo/art/_preview_024.png   (4x zoom for eyeballing; ignored by the build)

# 4. check you still fit, then build
python cardart.py budget
python build.py                               # -> build/duelmonsters-kaizo-hack.gb
```

Add `--product duelmonsters-mtg` to any of these to work on Duel Monsters MTG instead.

### The contract with `build.py`

`work/<product>/art/NNN.png` — one **64 × 80** PNG per card you want to redraw,
in the four GB shades. `NNN` is the card number (leading zeros optional; anything
after the digits is ignored, so `024-blue-eyes.png` works). Files starting with
`_` are skipped. **Cards with no PNG keep their stock picture byte for byte.**

You can hand-author these PNGs in any pixel editor instead of using `import` —
each pixel is snapped to the nearest of the four GB greys, so exact RGB values
don't matter. **Draw what you want to see** (§5a): dark pixels come out dark in
game. Start from an `extract` if you want the frame for free.

### In place vs repack

`cardart.apply_config` is two-tier:

1. **In place** when the new stream fits the card's existing slot. A build that
   changes two cards then touches exactly two records — no pointers move, nothing
   else in the ROM shifts.
2. **Repack the whole bank** when it doesn't. All 13 (or 14) cards in that bank
   are re-laid-out tightly and their pointer-table entries rewritten. This
   reclaims the ~82 bytes of unread padding Konami's compressor left after every
   record, which is where the ~2 KB/bank of headroom comes from.
3. **Hard error** if the bank still overflows, naming every card in the bank and
   the byte overage. Nothing is written. Fix by re-importing the busiest card(s)
   with a flatter dither.

Bank assignment never changes — a card always stays in the bank it was born in.

---

## 8. Traps and things not to assume

- **Row-major tile order is wrong.** See section 4. This is the single biggest
  time sink in this investigation.
- **Colour index is not brightness.** BGP is inverted; stored colour 0 is black.
  See §5a. Anything that converts between an image and stored bytes has to go
  through the palette, or it silently produces negatives.
- **Bank `$20` is NOT free.** It holds 16 KB of data in exactly this art format —
  its first bytes decode to the same frame top-left as card #1 — yet the bank
  table never selects it. Something else may read it. `ART_BANKS` in `cardart.py`
  deliberately excludes it. Don't claim that 16 KB until you have found what, if
  anything, points there.
- **The ~82 bytes after each record are not padding you can rely on.** They are
  the tail of a stream Konami's compressor emitted for a larger buffer than the
  game reads. Harmless, reclaimable by repacking, but don't write anything there
  by hand — the pointer arithmetic in `slots()` treats a card's slot as running to
  the next card's pointer, and hand-edits would desync that.
- **The picture count is 365, not 366**, like every other card table in this ROM.
- **Never grow the ROM.** All the build invariants in `README.md` still apply;
  everything here happens inside the existing 64 banks.

---

## 9. Not done / open

- ~~**The second image set.**~~ **SOLVED** — it is the 18 duelist portraits
  behind the duel text window. The tiles resisted every arrangement because they
  are a *tileset*, not a bitmap: a 20 × 11 tilemap in bank `$06` (`$4229`)
  arranges them. Decoded and editable — see [SCREENS.md](SCREENS.md) §3.
- **What reads bank `$20`.** See above. Still open.
- ~~**Other graphics**~~ — the title screen, the boot splashes, the character
  portraits, every menu tilemap and the font are all decoded and editable now:
  [SCREENS.md](SCREENS.md), `work/scripts/screens.py`.

---

## 12. Source art style changes the settings (Duel Monsters MTG)

Kaizo's `--fit cover --dither bayer8` is tuned for Yu-Gi-Oh! art: clean, high
contrast line work that survives four shades. **Magic art from 1993 does not.**
It is painterly, dark and busy, and the same settings produced grey soup on
about half the first batch — one card came out a featureless rectangle.

What the measurements said, converting 365 pictures:

| Lever | Verdict |
|---|---|
| `--dither fs` | **The big win.** Dragon Whelp went from a flat grey slab to a legible dragon. fs compresses worst, but there was 63 KB of bank headroom, and after replacing all 365 pictures *every bank still fits* — detail was the right thing to spend it on. |
| `--contrast 1.4 --gamma 1.15 --sharpen 0.9` | Consistent improvement on painted sources. |
| `--zoom` (added for this) | **Do not automate it.** See below. |
| `--dither none` | The rescue for genuinely dark art — posterising beats dithering when the tonal range is too narrow to dither. |

### The zoom trap

`--zoom` crops in on the subject before fitting, and by eye it rescues busy
illustrations. The obvious next step — score each crop and keep the best — is
wrong, and measurably so.

Any structure metric rises as you crop, because you are magnifying local
contrast. So "pick the highest-scoring crop" always picks the tightest one.
Calibrated against thirteen hand-judged cards, the score gain from zooming had
**no relationship** to whether the picture looked better: the two best-composed
cards in the batch both "improved" 10–13% while losing their subject — figures
cropped off at the neck. Zoom is a per-card rescue a human chooses, not an
objective to maximise.

The same metric *is* a good **detector**, though, which is how it is used now:
standard deviation after 2×2 block-averaging (average first, or Floyd–Steinberg
noise reads as detail and scores mush as excellent). Genuine mush scored 21
against a floor of 40 across every legible card, so anything under 34 is
reported for hand work instead of shipped silently.

### Per-card overrides

`work/duelmonsters-mtg/art_tuning.json`, keyed by card number, each with the
reason recorded. Keys beginning `_` are notes, not settings:

```json
{"8": {"_card": "Demonic Hordes", "_why": "dark, formless; fs spread a narrow
        tonal range into noise", "contrast": 2.5, "gamma": 0.7, "dither": "none"}}
```

One card out of 365 needed this. `mtg_art_convert.py` also steps a bank's
biggest pictures down (`fs → bayer8 → bayer4 → none`) if the bank overflows, so
one busy picture is flattened rather than thirteen — it did not have to fire.

## 10. File map

| File | What it is |
|---|---|
| `work/scripts/gblzss.py` | The codec. `decompress(src, off, out_len)` / `compress(data)`. Run it directly for a 200-case round-trip self-test. Used by any future compressed-graphics work, not just cards. |
| `work/scripts/cardart.py` | Everything else: ROM structure, tile↔pixel, frame, image conversion, CLI, and `apply_config` for the build. |
| `work/scripts/build.py` | Calls `cardart.apply_config` when `work/<product>/art/` exists. |
| `work/<product>/art/NNN.png` | **Your replacement pictures.** Committed. |
| `work/<product>/art/_preview_NNN.png` | 4× zoom written by `import`. Gitignored. |
| `work/<product>/art_src/NNN.png` | Stock art dumped by `extract`. Gitignored (Konami's pixel art). |
| `docs/NOTES.md` § Card artwork | The same format decode, in the main notes. |

## 11. Verification

```
python gblzss.py            # 200/200 randomised codec round-trips
python cardart.py verify    # 365/365: decode -> pixels -> 2bpp -> re-encode -> decode
```

`verify` is the safety net that proves the tooling reproduces the ROM's own data,
so any difference in your build is a change you made rather than a decoding bug.
Both pass at the time of writing.

Additionally checked end to end: after a build with replacements, all 365 pictures
still decode from the built ROM, every pointer and bank entry is in range, the
replaced cards match their PNGs pixel-for-pixel, untouched cards are byte-identical,
the file is still 1,048,576 bytes, and the bank-overflow path fails cleanly with
nothing written.
