#!/usr/bin/env python3
"""Find card-indexed loads that feed the card-info RAM slots $CD11/$CD12
(the two bytes the ATK/DEF/type loader leaves untouched -> cost/level/stars)."""
import sys

rom = open(sys.argv[1], "rb").read()
n = len(rom)

# any store 'ld ($CDxx),a' = EA xx CD, for xx in a small window of the info block
SLOTS = {0x11: "$CD11", 0x12: "$CD12", 0x18: "$CD18", 0x19: "$CD19"}


def find_store_after(i, span=20):
    seg = rom[i:i + span]
    for k in range(len(seg) - 2):
        if seg[k] == 0xEA and seg[k + 2] == 0xCD and seg[k + 1] in SLOTS:
            return SLOTS[seg[k + 1]], k
    return None, None


print("card-indexed loads (ld hl,nn; add hl,bc/de) feeding a $CD1x info slot:")
for i in range(n - 4):
    if rom[i] == 0x21 and rom[i + 3] in (0x09, 0x19):
        slot, k = find_store_after(i + 4, 22)
        if slot:
            addr = rom[i + 1] | (rom[i + 2] << 8)
            print(f"  @0x{i:06X}: ld hl,${addr:04X} ; add hl ; ... ld ({slot}),a")
            print(f"       bytes: {rom[i:i + 4 + k + 3].hex(' ')}")
