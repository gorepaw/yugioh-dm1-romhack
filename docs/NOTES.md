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

Bank calling convention: `rst $08` (`CF`) + bank + routine index; each bank starts
with a routine pointer table (bank 5's is at `0x14002`).

**Open question (the important one):** where the card → effect-handler binding lives.
The 16 handlers are bank-5 routines reached through bank 5's routine table (`0x14002`,
handler entries = routine indices 5..20). Far-calls use `rst $08` (`CF`) + routine
index + bank, so **searching for `CF <idx> 05` finds every effect invocation** — the
surrounding code is what decides which effect a played card runs. That decision point
is the next target.

Confirmed separately: no trap / effect-monster category exists (21-type enum has none).

**Far-call convention (decoded):** `rst $08` = `CF <routine_index> <bank>`; each bank
begins with a routine pointer table (bank 5's at `0x14002`; effect handlers are its
routine indices 5..20).
**Effect invocation sites** cluster in **bank 3, `0x00D000`–`0x00D340`** (e.g. three
handlers called in a row at `0x00D01C/26/30`, beside a 7-entry jump table at
`0x00D05E`). The card→effect decision is *there, in code*.

### Assembly assessment — CAN verbs be re-pointed? YES, via a small patch
"Play a card" in bank 3 (`0x00D014`) dispatches by **card category** through a
7-entry jump table at `$505E` (= file `0x00D05E` → handlers `$50CF $50DC $50F0
$5100 $5110 $5120 $5130`), using an index from `$5095`. The 16 **spell** handlers are
then reached from scattered *guarded call sites* (`0xD01C/26/30`, `0xD262`, `0xD28C`,
`0xD291`, `0xD2F8`, `0xD331`) — i.e. the card→verb binding is **hardcoded control
flow**, not a table. That is why the `0x15162` data edit only moved the text.

**Feasible fix — insert a table-driven indirection** (classic romhack technique):
every effect handler is already uniformly callable as `rst $08 <routine_idx> <bank 5>`
(indices 5..20 via bank 5's routine table at `0x14002`). So:
1. Put a new **50-byte table** (magic slot → bank-5 routine index) in genuinely free
   ROM — see the free-space section below (**do not** use bank-13 zero runs).
2. Add a ~20–40 byte stub: read slot → index, issue the `rst $08`.
3. Patch the magic-effect decision point to call the stub.
Result: spell verbs become **freely assignable per magic slot** — what Project 2 wants.

**Remaining work to do it:** pinpoint the exact decision site for "which spell effect".
Fastest route is a BGB breakpoint on one effect handler, then read the caller.

### DESIGN CONSEQUENCE (current, unpatched): "the slot IS the verb"
Because effects are bound in code by card id, you cannot reassign a spell's effect by
editing data. The workable model for both projects is the inverse: **assign card
identities to the existing effect slots.** Whatever card occupies magic slot #337 will
always Raigeki, so name/describe it as the card that should do that. The 50 magic slots
are a fixed palette of verbs to design around. Changing which verb a slot runs is an
*assembly* change (RGBDS is already installed) — a later capability, not a blocker.

## Fusion system (bank 0x3B) — located, format partly decoded
- Bank routine table at `0xEC000` (`$404C $405E $4091 $402B`), then code.
- A large contiguous block of 16-bit **card ids from ~`0xEC155`** (~6,500 entries)
  fills most of the bank. Repeated values (e.g. 207×7, 252×8, 259×10 at `0xED930`)
  look like fusion **results** shared across many partners.
- Exact record grouping (per-material lists vs flat recipe list) still to decode.

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
| Reward pointer table | `0x036F1A` | 17 pointers (one per duelist/pool), 20 bytes apart; file = ptr + `0x30000` |
| Reward card lists | from `0x036F3A` | 17 blocks × 10 × 16-bit card id (award per threshold) |

- Lookup routine ~`0x036EC0` reads the win count from RAM (`$CF70`+) and walks the
  threshold table to pick an index.
- Sanity check — duelist 0 (Weevil): #329, #49 Big Insect, #304 Axe of Despair,
  #52 Hercules Beetle, #305 Laser Cannon Armor, #53 Killer Needle, … (insect-themed ✓).
- **To ease the grind: edit the ten BCD values at `0x036F02`** (e.g. 3,6,9,…,30).
  Reward *cards* can be re-chosen by editing the 17 × 10 id blocks.

## Free space — and a TRAP to avoid
Use `work/scripts/find_freespace.py`. **Zero runs are not automatically free.**

> ⚠️ The zero runs inside bank 13 (`0x034922`, `0x0362CC`, `0x34094`…) are **live
> drop-pool weight data** — cards with 0% drop chance. Writing a patch there would
> silently corrupt the drop tables. Verify a run isn't inside a known table first.

Genuinely free (`0xFF`/`0x00` padding at bank ends), e.g.:
`0x017C00`/`0x017E00` (bank 5), `0x01FC00`–`0x01FE00` (bank 7),
`0x033283` (208 B) and `0x03390C` (332 B) in bank 12.
**Bank 13 is completely full** — packed to `0x37FFF`, no padding at all.

## Cards per win — analysis (NOT yet patched)
Award routine is bank D routine 0 at `$400C` (file `0x3400C`):
```
call $23F7 ; cp 0 ; jr z,skip
call $4027        ; pick the card: PRNG ($2112) x2, then scan the pool's
                  ; cumulative weights until the roll is covered -> card index
rst08 x3          ; add to collection / display
call $6E8E
```
`$4027` (file `0x34027`) is the picker. Awarding 3 cards means running that body
three times — i.e. redirect `$400C` to a looping stub.

**Blockers to solve first:**
1. Bank 13 has **no free space** for the stub, so it must live in another bank
   (fine — `rst $08` switches banks) or replace dead code in bank 13.
2. The caller of `$400C` is **not confirmed**: the only `CF 00 0D` match
   (`0x09F92A`, bank 39) sits in high-entropy data and is very likely a false
   positive. So the invocation path needs verifying.

**Recommended next step:** BGB breakpoint on `0x3400C` (bank 13 `$400C`), win a duel,
and read the call stack / return address. That confirms the caller and the banking
context in minutes, versus guessing statically.

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
