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
