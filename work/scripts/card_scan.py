#!/usr/bin/env python3
"""Locate the card-stats table by anchoring on known ATK values.

Card order (from Darrman's cardname.txt): #0 Blue-Eyes (3000/2500),
#1 Mystical Elf (800/2000), #2 Hitotsu-Me Giant (1200/1000).

We look for three ATK values [3000, 800, 1200] appearing at a fixed stride S.
A hit pins down the table position, the per-card record size (S), and the
number encoding all at once. Then we dump aligned rows so DEF/type/etc. become
visible as columns that repeat.
"""
import sys

rom = open(sys.argv[1], "rb").read()
n = len(rom)

ATK_SEQ = [3000, 800, 1200]      # card #0, #1, #2 ATK
DEF_SEQ = [2500, 2000, 1000]     # their DEF, for column-spotting


def u16le(o):
    return rom[o] | (rom[o + 1] << 8)


def u16be(o):
    return (rom[o] << 8) | rom[o + 1]


def find_table(reader):
    pos0 = [a for a in range(n - 1) if reader(a) == ATK_SEQ[0]]
    pos1 = {a for a in range(n - 1) if reader(a) == ATK_SEQ[1]}
    pos2 = {a for a in range(n - 1) if reader(a) == ATK_SEQ[2]}
    hits = []
    for a in pos0:
        for S in range(2, 129):
            if (a + S) in pos1 and (a + 2 * S) in pos2:
                hits.append((a, S))
    return hits


for reader, label in ((u16le, "little-endian"), (u16be, "big-endian")):
    hits = find_table(reader)
    print(f"=== ATK read as {label}: {len(hits)} hit(s) ===")
    for a, S in hits:
        print(f"  card#0 ATK field @ 0x{a:06X}, record stride = {S} bytes")
        print(f"  aligned rows (each row = one card's {S} bytes, starting at ATK field):")
        for i in range(6):
            row = rom[a + i * S: a + i * S + S]
            print(f"    card#{i} @0x{a + i * S:06X}: {row.hex(' ')}")
        # where does DEF sit? scan columns for the DEF sequence
        for col in range(0, S - 1):
            vals = [reader(a + i * S + col) for i in range(3)]
            if vals == DEF_SEQ:
                print(f"  -> DEF field is at +{col} bytes from ATK (col matches {DEF_SEQ})")
        print()
