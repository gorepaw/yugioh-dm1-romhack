#!/usr/bin/env python3
"""Build our romhack: apply byte edits to the pristine English base ROM.

Reads roms/dm1-english.gb, applies every edit in EDITS (verifying the current
byte first, so a shifted address can never silently corrupt the ROM), fixes the
Game Boy header + global checksums, and writes build/dm1-hack.gb.

Add new changes by appending to EDITS. This is our whole build step for
byte-level (text / data) edits.
"""
import hashlib
import json
import os

import cards

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.path.join(ROOT, "roms", "dm1-english.gb")
OUT = os.path.join(ROOT, "build", "dm1-hack.gb")

# (offset, expected_old_byte, new_byte, description)
EDITS = [
    (0x01540D, 0x44, 0x3F, "Duel-start message: 'It's your turn.' -> 'It's your turn!'"),
]


def header_checksum(rom):
    c = 0
    for b in rom[0x134:0x14D]:
        c = (c - b - 1) & 0xFF
    return c


def global_checksum(rom):
    return (sum(rom) - rom[0x14E] - rom[0x14F]) & 0xFFFF


def main():
    rom = bytearray(open(BASE, "rb").read())
    print(f"base: {BASE} ({len(rom)} bytes)")

    for off, old, new, desc in EDITS:
        cur = rom[off]
        if cur != old:
            print(f"ABORT @0x{off:06X}: expected 0x{old:02X}, found 0x{cur:02X} - {desc}")
            return 1
        rom[off] = new
        print(f"  @0x{off:06X}: 0x{old:02X} -> 0x{new:02X}   {desc}")

    # --- card stat edits (work/card_edits.json, applied via cards.py) ---
    card_edits_path = os.path.join(ROOT, "work", "card_edits.json")
    card_edit_count = 0
    if os.path.exists(card_edits_path):
        for e in json.load(open(card_edits_path)):
            summary = cards.apply_card_stat(rom, e["card"] - 1,
                                            e.get("atk"), e.get("def"), e.get("type"))
            print(f"  card #{e['card']} {e.get('name', '')}: {summary}")
            card_edit_count += 1

    rom[0x14D] = header_checksum(rom)
    gc = global_checksum(rom)
    rom[0x14E], rom[0x14F] = (gc >> 8) & 0xFF, gc & 0xFF

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "wb").write(rom)
    print(f"wrote: {OUT}")
    print(f"  applied {len(EDITS)} byte edit(s) + {card_edit_count} card edit(s)")
    print(f"  MD5:  {hashlib.md5(bytes(rom)).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
