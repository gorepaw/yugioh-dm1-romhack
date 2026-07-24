#!/usr/bin/env python3
"""Find every 'ld ($XXXX),a' store to a given address, with preceding context.

Usage: python find_stores.py <rom> <addr-hex>
e.g.   python find_stores.py rom.gb 0xCF47      # spell-effect message id
Each hit is (usually) an effect handler setting its message id.
"""
import sys

rom = open(sys.argv[1], "rb").read()
addr = int(sys.argv[2], 0)
pat = bytes([0xEA, addr & 0xFF, (addr >> 8) & 0xFF])

hits, i = [], 0
while True:
    j = rom.find(pat, i)
    if j < 0:
        break
    hits.append(j)
    i = j + 1

print(f"{len(hits)} store(s) to ${addr:04X}:\n")
for j in hits:
    bank = j // 0x4000
    # the immediately preceding 'ld a,$nn' (3E nn) is the value stored, if present
    val = None
    for k in range(2, 8):
        if j - k >= 0 and rom[j - k] == 0x3E:
            val = rom[j - k + 1]
            break
    vs = f"value=0x{val:02X} ({val})" if val is not None else "value=<computed>"
    print(f"  @0x{j:06X} (bank {bank:2d})  {vs}")
    print(f"     before: {rom[max(0, j - 14):j].hex(' ')}")
