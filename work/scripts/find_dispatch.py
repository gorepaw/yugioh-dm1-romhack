#!/usr/bin/env python3
"""Find jump-table dispatchers: ld hl,$xxxx ; add hl,bc/de ; ... ; jp hl (E9).

A dispatcher indexed by an effect id is how a fixed roster of spell effects gets
bound to handlers. Reports the table address, the accessing code offset, and the
table's own bank-resolved file offset (assuming code reads its own bank).
"""
import sys

rom = open(sys.argv[1], "rb").read()
n = len(rom)

hits = []
for i in range(n - 20):
    if rom[i] == 0x21 and rom[i + 3] in (0x09, 0x19):
        window = rom[i + 4:i + 18]
        if 0xE9 in window:                      # jp hl within a few instrs
            addr = rom[i + 1] | (rom[i + 2] << 8)
            if 0x4000 <= addr <= 0x7FFF:
                data = (i // 0x4000) * 0x4000 + (addr - 0x4000)
            else:
                data = addr
            hits.append((i, addr, data, window.index(0xE9)))

print(f"{len(hits)} jump-table dispatcher(s):\n")
for code, addr, data, dist in hits:
    bank = code // 0x4000
    print(f"  code@0x{code:06X} (bank {bank:2d})  ld hl,${addr:04X} ; add hl "
          f"-> table @0x{data:06X}   (jp hl +{dist})")
    print(f"     table bytes: {rom[data:data + 16].hex(' ')}")
