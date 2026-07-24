#!/usr/bin/env python3
"""Decode the starter-deck / starter-pool table at 0x26AC (16-bit card ids)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards  # noqa: E402

rom = open(cards.BASE_ROM, "rb").read()
names = cards.load_names()
base = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0x26AC
count = int(sys.argv[2], 0) if len(sys.argv) > 2 else 120

print(f"table @0x{base:05X}:")
for i in range(count):
    v = rom[base + 2 * i] | (rom[base + 2 * i + 1] << 8)
    if not (1 <= v <= 365):
        print(f"  [{i:3d}] raw 0x{v:04X}  <- not a card id (end of table?)")
        break
    t = rom[cards.TYPE_ARRAY + (v - 1)]
    tag = "  <== MAGIC" if t == 0x14 else ""
    print(f"  [{i:3d}] #{v:3d} {names.get(v - 1, '?'):20s} {cards.type_name(t):13s}{tag}")
