#!/usr/bin/env python3
"""Find loaders that write a card-indexed ROM value into the $CAxx display block.
Reports stores 'ld ($CAxx),a' that have a card-index idiom (ld hl,nn ; add hl,bc)
in the preceding bytes - the nn is the source table (stars / cost / level)."""
import sys

rom = open(sys.argv[1], "rb").read()
n = len(rom)


def idiom_before(j, span=40):
    seg = rom[max(0, j - span):j]
    base = max(0, j - span)
    hits = []
    for k in range(len(seg) - 3):
        if seg[k] == 0x21 and seg[k + 3] in (0x09, 0x19):
            hits.append(seg[k + 1] | (seg[k + 2] << 8))
    return hits


for xx in range(0xA0, 0xD0):
    pat = bytes([0xEA, xx, 0xCA])
    i = 0
    while True:
        j = rom.find(pat, i)
        if j < 0:
            break
        bases = idiom_before(j)
        if bases:
            addrs = ", ".join(f"${b:04X}" for b in bases)
            print(f"$CA{xx:02X} <- store @0x{j:06X}  (idiom base(s): {addrs})")
            print(f"     ctx: {rom[max(0, j - 30):j + 3].hex(' ')}")
        i = j + 1
