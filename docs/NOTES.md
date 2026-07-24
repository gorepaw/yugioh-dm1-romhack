# Technical notes — Yu-Gi-Oh! Duel Monsters (GB)

Living document. Record every address, table, and finding here as we discover it.

## ROM identity

| Field | Value |
|---|---|
| Working file | `roms/dm1-english.gb` |
| Patch state | **English** — Darrman `DM1.ips` already applied (562/562 records matched) |
| Size | 1,048,576 bytes (1 MB, 64 × 16 KB banks) |
| MD5 (English) | `DEA982111CC284F28EC4C161E921BBCF` |
| SHA1 (English) | `1BB5F02609592E0E9F6F77ACED78F00EB61AFD3D` |

### Cartridge header (parsed)

| Addr | Field | Value | Meaning |
|---|---|---|---|
| 0x134–0x143 | Title | `YUGIOU` | Internal title |
| 0x143 | CGB flag | `0x00` | DMG (mono Game Boy) |
| 0x146 | SGB flag | `0x03` | Super Game Boy enhanced |
| 0x147 | Cart type | `0x03` | MBC1 + RAM + Battery |
| 0x148 | ROM size | `0x05` | 1 MB / 64 banks |
| 0x149 | RAM size | `0x02` | 8 KB (1 bank) |

Implication: MBC1 mapper. Bank 0 fixed at 0x0000–0x3FFF; switchable bank at
0x4000–0x7FFF. Cartridge SRAM at 0xA000–0xBFFF (battery-backed save).

## Memory map / discovered addresses

_(Fill in as we go.)_

### Card data table — base + terrain stat arrays (Bank 9)
- ATK/DEF are stored as **packed parallel arrays** of 16-bit **BCD little-endian**
  values (3000 → bytes `00 30`, i.e. word `0x3000`). 366 entries per array,
  732 bytes (`0x2DC`) per array. Card index = card number − 1 (index 0 = Blue-Eyes).
- Non-monster cards (Magic/Ritual/Equip/Trap) have no ATK/DEF → stored as `FFFF`.
- **7 ATK/DEF pairs**: 1 base + 6 terrain-boosted (×1.3 for matching monster types),
  one per field (Forest/Wasteland/Mountain/Meadow/Sea/Dark):

  | Pair | ATK array | DEF array |
  |---|---|---|
  | Base (no field) — shown in card list | `0x24381` | `0x2465D` |
  | Terrain 1 | `0x24939` | `0x24C15` |
  | Terrain 2 | `0x24EF1` | `0x251CD` |
  | Terrain 3 | `0x254A9` | `0x25785` |
  | Terrain 4 | `0x25A61` | `0x25D3D` |
  | Terrain 5 | `0x26019` | `0x262F5` |
  | Terrain 6 | `0x265D1` | `0x268AD` |

- To edit a card: change its **base** entry, then propagate to each terrain array by
  that array's per-card factor (1.0 if unboosted, ×1.3 if boosted) so field power
  stays consistent. Handled by `work/scripts/cards.py`.
- Discovery scripts: `work/scripts/card_scan*.py`.

### Card type / species array (Bank 9)
- **1 byte per card at ROM `0x2409E`** (CPU `$409E`), indexed by card id.
- Enum: `00` Dragon, `01` Spellcaster, `02` Zombie, `03` Warrior,
  `04` Beast-Warrior, `05` Beast, `06` Winged Beast, `07` Fiend, `08` Fairy,
  `09` Insect, `0A` Dinosaur, `0B` Reptile, `0C` Fish, `0D` Sea Serpent,
  `0E` Machine, `0F` Thunder, `10` Aqua, `11` Pyro, `12` Rock, `13` Plant,
  `14` Magic (spell/equip). `0xF5` = the last dummy slot (#366).
- Terrain boosts map to species (matches duel text): Mountain→Dragon/WingedBeast/
  Thunder, Forest→Beast/Beast-Warrior/Insect/Plant, Wasteland→Zombie/Dinosaur/Rock,
  Meadow→Warrior/Beast-Warrior, Sea→Fish/SeaSerpent/Thunder/Aqua, Dark→Spellcaster/Fiend.

### KEY TECHNIQUE: find card tables from code
The card-load routine at ROM `0x24068` reads each table with the idiom
`ld hl,$XXXX ; add hl,bc ; ld a,(hl)` (bytes `21 lo hi 09`), where `bc` = card id.
It confirmed type `$409E`, ATK `$4381`, DEF `$465D`. Scan for that idiom with
`work/scripts/card_code_scan.py` to locate any per-card array — far more reliable
than guessing values.

### Card-info RAM block
The loader (0x24000 region) fills RAM `$CD0F–$CD17`: `$CD0F/$CD10` & `$CD11/$CD12`
= card id (two copies), `$CD13/$CD14` = ATK, `$CD15/$CD16` = DEF, `$CD17` = type.

### No guardian-star / deck-cost / level system in DM1 (confirmed by the player)
This first game has **no points (deck cost) system and no Guardian Star system** —
those were introduced in later titles (Dark Duel Stories onward). There are no such
tables to find; the earlier hunt came up empty because the data doesn't exist.
A DM1 card = **name + ATK + DEF + type/species + description text**. The editor
covers ATK/DEF/type (`cards.py`) and description text (`descriptions.py`), so it is
complete for this game's card model.

### Card description / lore text — EDITABLE (`descriptions.py`)
- Fixed **36-byte records** (2 lines × 18 tiles), consecutive from ROM `0xF033A`
  (card #N at `0xF033A + 36*N`). Pointer table at `0xF0060` (pointer value + `0xEC000`
  = file offset), but fixed width means edits are in-place — pointers never change.
- Ligature squashes (`il li ll l! 's 't`) auto-applied to fit more per line.

## Card drop system (Bank D) — EDITABLE (`drops.py`)
- 16 duelists → pool index via the map at `0xB734` (16 bytes).
- Pool pointer table at `0x34072` (CPU `$4072`): 17 pointers; pool file offset =
  pointer + `0x30000`.
- Each pool = **365 entries of 16-bit cumulative weights**, total **2048**. Per-card
  weight = `cum[i] - cum[i-1]`; after a win the game rolls 0..2047 and awards the card
  whose cumulative bucket contains the roll. Pools are themed (~20–36 cards each; e.g.
  pool 0 = insects/Weevil). `drops.py` rewrites pools keeping total 2048 & monotonic.

## Spell / magic effect system (P1.0a) — THE DESIGN SPACE

**Magic cards are card #301–350** (contiguous; type byte `0x14`).

> **TESTED 2026-07-23 — the `0x15162` table is FLAVOUR TEXT ONLY.**
> Experiment: card #343 Sparks (slot 42) had its id changed `0x21`(33, weakest burn)
> → `0x1B`(27, Raigeki). In-game the *message* became Raigeki's, but the *effect*
> stayed Sparks' (no monsters destroyed). So this table selects the duel message and
> **not** the effect handler. **Spell effects are bound elsewhere — positionally, by
> card id.** Finding that real binding is the open question.

| Thing | Location | Notes |
|---|---|---|
| Magic slot → **message** id (NOT effect) | **`0x15162`, 50 bytes** | index = card# − 301. Flavour text only — proven by experiment |
| Effect-handler pointer table | `0x1400C` (CPU `$400C`, bank 5) | **16 handlers**: `$500C $501F $5032 $508A $509A $50AD $50BD $50DD $512C $5148 $5194 $51DB $5204 $5049 $5059 $50CD` |
| Current message id (RAM) | `$CF47` | every effect handler writes it |
| Message pointer table | `0x14980` (CPU `$4980`, bank 5) | indexed by `$CF47`; → strings at `0x15400`+ |
| Petit Moth evolution stages | `0x15118` (4 bytes) | → messages 10–13 |
| Swords of Revealing Light state | `0x15146` (2 bytes) | active / expired messages |

**Effect id values seen** (`0x10`–`0x28` = 16–40): `16` generic equip, `17` Elegant
Egotist, `18` Stop Defence, `19` Dragon Capture Jar, `20-25` the six field terrains
(Forest/Wasteland/Mountain/Sogen/Umi/Yami), `26` Dark Hole, `27` Raigeki, `28-32`
heals (5 magnitudes), `33-37` burns (5 magnitudes), `38` Swords, `39` Spellbinding
Circle, `40` Dark-Piercing Light.

**Engine verb vocabulary (~16 handlers):** equip/power-up, set field terrain,
destroy-all, destroy-enemy-side, heal (several magnitudes), burn (several magnitudes),
skip-enemy-attacks (Swords), power-down-all-enemies (Spellbinding Circle), reveal
(Dark-Piercing Light), force-attack (Stop Defence), seal-by-type (Dragon Capture Jar),
transform (Elegant Egotist), plus fusion and Petit Moth evolution as special cases.
*This is the complete set of "verbs" available for card design in both projects.*

Bank calling convention: `rst $08` (`CF`) + `sel` + bank — see the fully decoded
description below; each bank starts with a routine pointer table at `$4002`
(bank 5's is at `0x14002`).

**Open question (the important one):** where the card → effect-handler binding lives.
The 16 handlers are bank-5 routines reached through bank 5's routine table (`0x14002`,
handler entries = routine indices 5..20). Far-calls use `rst $08` (`CF`) + routine
index + bank, so **searching for `CF <idx> 05` finds every effect invocation** — the
surrounding code is what decides which effect a played card runs. That decision point
is the next target.

Confirmed separately: no trap / effect-monster category exists (21-type enum has none).

**Far-call convention — FULLY DECODED** (handler disassembled at bank 0 `$1033`;
tooling: `work/scripts/farcall.py`, `work/scripts/dis.py`):

```
rst $08          ; CF
db  <sel>        ; sel = 2*index + 3   (ALWAYS ODD — a strong search filter)
db  <bank>       ; destination bank number
```

The handler reads a 16-bit LE target from the **destination** bank at
`$4000 + sel - 1`, so each bank is laid out:

```
$4000  db <this bank's own number>   ; the handler reads it to save the caller's bank
$4001  db $00
$4002  dw routine_0                  ; sel = 3
$4004  dw routine_1                  ; sel = 5   ...  sel = 2*i + 3
```

It builds a fake stack frame returning to `$1071`, which restores the caller's bank,
so far calls **nest freely** (bank 13's `$400C` issues three of them itself).
Note `sel` is *not* bounds-checked against the table — it can address any byte pair
in `$4002..$40FF`.

> ⚠️ Earlier notes had this as `CF <index> <bank>`. That is wrong and made every
> call-site search miss. The award routine's real call site is `CF 03 0D`, not
> `CF 00 0D`.
## Spell verbs (bank 3) — ALREADY DATA-DRIVEN, no patch needed
Tool: `work/scripts/spells.py` (`list` / `verbs` / `set` / `verify`).

> ⚠️ **Retraction.** Earlier notes here claimed the card→effect binding was
> "hardcoded control flow", that `0x00D000`–`0x00D340` was the decision site, and that
> a table-driven indirection had to be *added*. All three are wrong.
> `0x00D014` is the **menu-slot** dispatcher — `$5095` reads cursor bitflags from
> `$CAA5`/`$CAA6`, not card ids. And the `0x15162` experiment only moved the text
> because that table only ever selects the **message**: `$5148` writes it to `$CF47`
> and returns. Message and effect are simply two independent tables.

The binding is a **one-byte-per-card lookup** that already exists:

| Structure | CPU | File | Notes |
|---|---|---|---|
| Verb jump table | `$6F82` | `0x00EF82` | **53 entries** (`$00`–`$34`) → bank 3 routines |
| Verb table A | base `$6EF2` | magic block `0x00F01E` | play onto field |
| Verb table B | base `$6F62` | magic block `0x00F08E` | equip / combine |

Both bases are **negative offsets**: the dispatcher computes `base + card_id`, so table
A's first real entry is `$6EF2 + 300 = $701E`. The notional first 300 entries overlap
the jump table and the dispatcher code itself and are never read, because ids below 300
are short-circuited. Only ids 300–364 (cards **#301–365**) are live — 65 bytes each.

Dispatchers, both ending in `x2 → index $6F82 → jp hl`:
- `$6FEE` **play path** — card from `$CDF2/$CDF3`; id < 300 → verb `$2F` outright
- `$705F` **fuse path** — card from `$CECD/$CECE`; id < 300 → try a fusion (far-call
  bank `$3B` idx 2), returning verb `$01` if it fused, else `$02`

Two tables exist because *playing* an equip card is generic (verb `$2F`) while
*combining* it with a monster needs per-equip logic, so table B gives each equip its own
verb `$15`–`$2E`. Swords of Light, Spellbinding Circle and Dark-Piercing Light are `$00`
(a bare `ret`) in table B — they cannot be combined.

### The complete verb vocabulary (what card design can use)
`$00` nothing · `$01` summon fusion result · `$02` summon fusion material ·
`$03`–`$08` field (Forest, Wasteland, Mountain, Sogen, Umi, Yami) ·
`$09`–`$0D` heal ×5 magnitudes · `$0E`–`$12` burn ×5 magnitudes ·
`$13` Dark Hole · `$14` Raigeki · `$15`–`$2E` per-equip combine ·
`$2F` generic play/summon · `$30` Stop Defence · `$31` Dragon Capture Jar ·
`$32` Swords of Light · `$33` Dark-Piercing Light · `$34` Spellbinding Circle ·
`$35` Elegant Egotist.

**Reassigning a spell is a one-byte edit.** Making Sparks (#343) cast Raigeki is
`0x00F048: 0x0E → 0x14`, and nothing else changes — note the message table is separate,
so the card would still *say* "Sparks". Verified as a 1-byte diff.

### DESIGN CONSEQUENCE — the slot is NOT the verb
The earlier "assign card identities to fixed effect slots" workaround is unnecessary.
Any of the 65 cards from #301 up can be given any of the 53 verbs freely, in either
table, independently of its name, art and lore. For Project 2 the real limits are the
**53 available verbs** and the fact that new verbs need new assembly — not the binding.

## Fusion system (bank 0x3B) — FULLY DECODED
Tool: `work/scripts/fusions.py` (`extract` / `verify` / `list` / `find` / `stats`).
Round-trips byte-identically.

Not grouped and not variable-length — **three parallel arrays of 2159 16-bit entries**:

| Array | CPU | File | Meaning |
|---|---|---|---|
| material A | `$4155` | `0x0EC155` | 0-based card index |
| material B | `$5233` | `0x0ED233` | 0-based card index |
| result | `$6311` | `0x0EE311` | 0-based card index (ends `0x0EF3EF`) |

Recipe *i* is `A[i] + B[i] -> result[i]`. Values are **card index = card number − 1**;
`$016D` (365) is the "empty slot" sentinel used in RAM and never appears in the tables.
Observed range is 1..299, i.e. monsters #2..#300 only — Magic starts at #301 and never
fuses. Sanity checks: *Baby Dragon + Time Wizard → Thousand Dragon*, *Gaia the Fierce
Knight + Curse of Dragon → Gaia the Dragon Champion*.

Resolution (`$4091`, bank routine index 2):
- inputs in RAM at `$CECB/$CECC` and `$CECD/$CECE`; result to `$CECF/$CED0`;
  returns `0` on success, `1` on no fusion (`$400A`/`$402B` reset all three to 365)
- `$40E2` **linear-scans** array A for a match and calls `$411F` on each hit to test
  array B at the same index — first match wins
- on failure the pair is swapped (`$4070`) and rescanned, so recipes are
  order-insensitive even though each is stored in one direction only
- `$4145` maps the matched index to the result via the array at `$6311`

> ⚠️ The count **2159 is a hardcoded immediate `$086E` in three places** — `$40E4`,
> `$4112`, `$4122`. The array length is fixed unless all three are patched. To retire
> a recipe, point it at an unreachable material pair rather than shortening the array;
> `fusions.py` refuses to compile any other row count.

Stock content: 2159 recipes, **0 duplicate pairs**, 52 distinct results, 263 distinct
materials. Most-produced: Flame Swordsman (418), Zombie Warrior (318),
CharubinFireKnight (168) — so a handful of results absorb most of the table.

## The opponent roster — 16 duelists, FULLY MAPPED
Tool: `work/scripts/duelists.py` (`list` / `deck <n>` / `rewards <n>`).

Everything about an opponent hangs off one **pool id** from the 16-byte map at `0xB734`,
which selects their deck, drop table and reward list together.

| Structure | Address | Format |
|---|---|---|
| Duelist names | `0x5457` | 16 × **fixed 8 bytes**, space-padded (followed by UI strings `LinkDuel`, `Duelled`, `Name`) |
| Duelist → pool | `0xB734` | 16 bytes |
| Deck pointers | `0x2006C` (bank 8) | 17 × 16-bit → 365 × cumulative weights, total 2048 |
| Drop pointers | `0x34072` (bank 13) | 17 × 16-bit, same shape |
| Reward pointers | `0x036F18` (bank 13) | 17 × 16-bit → 10 card ids |

| # | Duelist | Pool | Deck cards | Drop cards | Deck file |
|---|---|---|---|---|---|
| 0 | Weevil | 0 | 13 | 17 | `0x02008E` |
| 1 | Mai | 1 | 39 | 36 | `0x020368` |
| 2 | Rex | 2 | 18 | 16 | `0x020642` |
| 3 | Mako | 3 | 29 | 32 | `0x02091C` |
| 4 | Kaiba | 8 | 61 | 33 | `0x0214B0` |
| 5 | Mokuba | 9 | 101 | 100 | `0x02178A` |
| 6 | Puppeter | 12 | 66 | 36 | `0x022018` |
| 7 | PaniK | 13 | 38 | 31 | `0x0222F2` |
| 8 | Keith | 14 | 56 | 28 | `0x0225CC` |
| 9 | Yugi | 5 | 33 | 46 | `0x020ED0` |
| 10 | Tristan | 10 | **3** | 29 | `0x021A64` |
| 11 | Joey | 7 | 28 | 40 | `0x0211D6` |
| 12 | Bakura | 11 | 10 | 49 | `0x021D3E` |
| 13 | Simon | 16 | 19 | 24 | `0x022B80` |
| 14 | Pegasus | 15 | 49 | 29 | `0x0228A6` |
| 15 | YamiYugi | 4 | 27 | 22 | `0x020BF6` |

- **17 pool slots, 16 duelists — pool 6 is referenced by nobody.** Its deck pointer is a
  44-byte stub (real decks are 730 bytes) and drop pools 6 and 7 share one pointer, so
  slot 6 is a free deck + drop table. The *roster size* is still fixed at 16 by the name
  table and `0xB734`.
- Duelist index is **not** pool index: Kaiba is duelist 4 / pool 8, YamiYugi is 15 / 4.
- Deck sizes vary enormously — Tristan is 3 cards (Kuriboh, Skull Servant, Dark Plant,
  33% each), Mokuba is 101. "Deck size" means distinct cards with a non-zero share.
- Names are **fixed 8 bytes**, so renaming an opponent is in-place and free — unlike
  card names there is no shared pool to repack.

## Opponent decks (bank 8) — SAME FORMAT AS DROP POOLS
- Deck tables are **monotonic cumulative weight arrays** (values run past 365, so they
  are weights, not card ids). Opponent decks are **probability distributions the game
  samples**, not fixed 40-card lists.
- Seen at `0x20486`, `0x206E0`, `0x223E0`, `0x228FC` (bank 8 = `0x20000`).
- **Implication:** `drops.py`'s transform logic (flatten / uniform / weighted / boost,
  preserving the running total) applies directly to decks — one toolset retunes both
  what opponents play and what they drop.

## Win-count reward system (bank 13) — LOCATED & STRUCTURED
Beating a duelist 10/20/…/100 times awards a specific card.

| Part | Address | Format |
|---|---|---|
| **Thresholds** | **`0x036F02`** | 10 × 16-bit **BCD** (`10,20,…,100`), `FFFF`-terminated |
| Reward pointer table | **`0x036F18`** | 17 pointers (one per duelist/pool), 20 bytes apart; file = ptr + `0x30000` |
| Reward card lists | from `0x036F3A` | 17 blocks × 10 × 16-bit card id (award per threshold) |

- Both addresses are read straight out of the code: `$6EBD` does `ld hl,$6F02` to walk
  the thresholds, `$6E8E` does `ld hl,$6F18 / add hl,de` with `DE = 2 * pool`.
  (`0x036F1A` was wrong — it read pool *N+1*'s list for pool *N*. Fixed 2026-07-23.)
- Lookup routine `$6EBD` (`0x036EBD`) reads a 16-bit BCD win count from
  `$CF70 + 2*duelist` and walks the threshold table. It is a **pure comparison** —
  it never increments anything, and the reward fires only when the win count is
  **exactly** equal to a threshold. So running the award routine twice on the same
  win hands out the milestone card twice.
- Win counts are incremented by the BCD adder at `0x002867` (caps at 9999); the
  17 × 2-byte zero table at `0x002823` is their initialiser — **not** free space.
- Sanity check — duelist 0 (Weevil): #329, #49 Big Insect, #304 Axe of Despair,
  #52 Hercules Beetle, #305 Laser Cannon Armor, #53 Killer Needle, … (insect-themed ✓).
- **To ease the grind: edit the ten BCD values at `0x036F02`** (e.g. 3,6,9,…,30).
  Reward *cards* can be re-chosen by editing the 17 × 10 id blocks.

## Free space — and a TRAP to avoid
Use `work/scripts/find_freespace.py`. **Zero runs are not automatically free.**

> ⚠️ The zero runs inside bank 13 (`0x034922`, `0x0362CC`, `0x34094`…) are **live
> drop-pool weight data** — cards with 0% drop chance. Writing a patch there would
> silently corrupt the drop tables. Verify a run isn't inside a known table first.

Two more traps found the same way, both of which *look* like padding:

> ⚠️ `0x002823` (68 bytes of `0x00`, bank 0, right after a `ret`) is the **win-counter
> initialiser table** — read by `ld de,$2823` / `ld de,$2845` at `0x0027FF`/`0x002810`.
> ⚠️ Bank 13's tail (`~$71CD`–`$7FFF`) and bank 4's `0xFF` runs are **graphics**;
> blank tiles scan as free space. Classify 64-byte blocks by `%00/FF` first.

**Method that actually works:** account for every known structure in a bank and report
what's left over — `work/scripts/bank13_map.py` does this for bank 13. Its result:

| Range | Contents |
|---|---|
| `$4000-$400B` | far-call routine table (5 entries) |
| `$400C-$4071` | award routine + drop picker (102 bytes, exactly packed) |
| `$4072-$4093` | drop-pool pointer table |
| `$4094-$6E33` | 16 × 730-byte cumulative weight arrays (duelists 6 and 7 **share** a pool) |
| `$6E34-$6F01` | code (`$6E34`, `$6E68`, `$6E8E`, `$6EBD`) |
| `$6F02-$708D` | thresholds + reward pointer table + reward lists |
| `$708E-~$71CC` | code, then a 9-entry string table at `$7173` |
| `~$71CD-$7FFF` | graphics |

So **bank 13 genuinely has no free space** — but it did not need any (below).

## Cards per win — SOLVED & PATCHED
`work/scripts/grind.py`, config `work/grind_config.json` (`{"cards_per_win": 3}`;
set it to 1 for stock). Applied by `build.py`.

Call site: **bank 4 `$4110` (file `0x010110`)** = `CF 03 0D`, the *only* far call to
bank 13 index 0. Found by searching for the correct `sel` once the convention was
decoded — the previously-suspected `0x09F92A` was indeed a false positive.

The trick is that `$400C-$4071` is one **contiguous 102-byte block holding only the
award routine and its picker**. Verified: the sole reference into it from inside
bank 13 is the award routine's own `call $4027`, and the sole reference from outside
is table entry 0. So the whole block can be re-laid-out in place, and no free space,
no stub, and no second bank are involved.

A counted loop costs 6 bytes. It is funded from inside the picker without changing
what the picker does:

```
ld a,$00 / ld [$CE9D],a / ld a,$FF / ld [$CE9E],a      (10 bytes)
ld hl,$CE9D / xor a / ld [hl+],a / ld [hl],$FF         ( 7 bytes)   x2  = -6
cp $00  ->  and a   (identical flags)                  in both routines = -2
```

New layout — award `$400C-$402C` (33 B), picker `$402D-$4070` (68 B), 1 byte spare:

```
$400C  push af / push bc / call $23F7 / and a / jr z,$402A
$4014  ld b,<cards_per_win>          ; <-- the tunable byte, file 0x034015
$4016  push bc / call $402D / rst08 $11,$01 / rst08 $41,$01 / rst08 $29,$02
$4023  pop bc / dec b / jr nz,$4016
$4027  call $6E8E                    ; milestone reward — OUTSIDE the loop
$402A  pop bc / pop af / ret
```

**`call $6E8E` must stay outside the loop.** `$6EBD` fires on an *exact* win-count
match and never increments, so looping the whole routine would award three copies of
the milestone card on wins 10, 20, 30…

Verified against the built ROM: the patch changes only `$400C-$4071`; the far-call
table, drop pointer table, all 16 weight arrays, and the whole reward system are
byte-identical to the base.

## P1.1 — the card compiler (DONE)
`work/scripts/cardc.py`. One source of truth, `work/cards.json` (gitignored — it
contains Darrman's translated names and lore), regenerating all four card structures.
`python cardc.py verify` extracts from the pristine ROM, compiles straight back, and
requires byte-identity. It passes, and `build.py` with `cards.json` present reproduces
MD5 `dea982111cc284f28ec4c161e921bbcf` — the base ROM exactly.

| Structure | Address | Format |
|---|---|---|
| Name pointers | `0x440F` | 365 × 16-bit CPU addr **+ a 366th end sentinel** (`$8000`) |
| Name pool | `$6E80`–`$7FFF` (bank 1, file == CPU) | **4480 bytes, 100% full** |
| Type | `0x2409E` | 365 × 1 byte |
| ATK / DEF | 7 pairs (see `cards.py TABLES`) | 365 × BCD16 LE each; Magic = `$FFFF` |
| Description pointers | `0xF0060` | 365 × 16-bit CPU addr (**no** sentinel) |
| Description pool | `$433A`–`$768D` (bank `$3C`, file = `0xEC000`+CPU) | **13139 bytes, 100% full** |

**Strings have no terminator** — `0x00` is a *space*. A record's length is the gap to
the next pointer, which is why both pools must be repacked and re-pointed together.

> ⚠️ Descriptions are **not** fixed 36-byte records. Cards 76 and 121 are 35 bytes and
> card 175 is 37, so `0xF033A + 36*index` is wrong from card #77 onward and lands on
> top of the neighbouring record. `descriptions.py` used to do exactly that; it now
> reads the pointer table and refuses any in-place edit that changes a record's length.

**Text codec** (`cardtext.py`): built from `text.tbl` rather than hardcoded, and
longest-match-first, because six bytes are ligatures (`il li ll l! 's 't`) that squash
two glyphs into one tile. All 365 names and all 365 descriptions survive
decode → encode byte-identically, so `cards.json` can hold readable text and still
round-trip. A per-record raw-hex fallback exists but is currently unused (0 records).

### The constraint Project 1 has to plan around
**Both pools are exactly full — 0 free bytes.** Renaming is a zero-sum budget:
swapping *Skull Servant* (12 B, `ll` is one tile) for *Buster Blader* (13 B) is
rejected with "over by 1" until a byte is freed elsewhere. Verified that a
budget-neutral swap works end to end and leaves every other card untouched.
Growing the roster's total name length at all requires relocating a pool and
re-pointing its reader — not yet investigated.

Card count is **365**, not 366; index 365 in the name pointer table is the end
sentinel. `cards.py NCARD` was 366 and `load_names()` read Darrman's script file
instead of the ROM; both are fixed, so names now come from whatever ROM is loaded.

### Card lore / description text (bonus find)
- Bank `0x3C`: description pointer table at `$F0060`, strings from `$F033A`
  (card #0 Blue-Eyes description @ `$F033A`). Editable later via `text_tool.py`.

### Card-info DISPLAY routine (bank 1) — mapped for a future debugger session
- **Type-name label table @ `0x538E`**, 8 bytes/entry, 21 entries in type-enum order:
  `Dragon, Magician (=Spellcaster), Zombie, Warrior, BWarrior, Beast, WinBeast,
  Fiend, Fairy, Insect, Dinosaur, Reptile, Fish, SSerpent, Machine, Thunder, Aqua,
  Pyro, Rock, Plant, Magic`. (Confirms the type enum independently.)
- Type-name draw routine @ `0x5366`: reads the type byte, `hl = $538E + type*8`,
  copies 8 chars to the RAM display buffer.
- Nibble->tile table @ `0x535D` = `[01..10]`; routine @ `0x532C` splits a **BCD byte
  into its two decimal digits** and maps each to a digit tile — this is the **ATK/DEF
  number renderer** (BCD -> on-screen digits), NOT guardian stars (which don't exist here).

### Text encoding
- English text uses a custom byte→tile map: `reference/DM1Translation/Insertion/text.tbl`.
  `0x00`=space, `0x01–0x0A`=`0–9`, `0x0B–0x24`=`A–Z`, `0x25–0x3E`=`a–z`, then punctuation.
  Space-saving ligatures: `0x4E`=il `0x4F`=li `0x50`=ll `0x51`=l! `0x52`='s `0x53`='t.
  Control codes: `0xB0`=[Line] `0xB1`=[Page] `0xB2`=[Pause] `0xB3`=[Input] `0xB4`=[Exit]
  `0xB5`=[CardNum] `0xB6`=[CardName].
- Strings are reached via 16-bit little-endian pointer tables. Use
  `work/scripts/text_tool.py` to encode/decode/search this text directly.

### Card names
- Pointer table begins ~`0x440F` (entry 0 = card #0). Name strings were relocated to
  free space at `0x6E80` (`#JMP($6E80,$7FFF)`, `#HDR($-0)`).
- Card #0 `BlueEyes W.Dragon` string @ `0x6E80`; card #1 `Mystical Elf` follows.

### Duel messages
- Pointer table ~`0x14980`; strings relocated to `0x15400` (`#JMP($15400,$17FFF)`,
  `#HDR($10000)`). `It's your turn.` @ `0x15400`.

### Drop tables
- Location: TBD

### Opponent decks / AI
- Location: TBD

## Change log (our edits)
| ROM offset | Change | Note |
|---|---|---|
| `0x1540D` | `0x44`(`.`) → `0x3F`(`!`) | Duel-start line 'It's your turn.' → 'It's your turn!' (pipeline test) |

## Open questions
- Exact clean-ROM hash Darrman's DM1.ips targets (confirm patch applies cleanly).
- Where the card database lives and its per-card record size.
