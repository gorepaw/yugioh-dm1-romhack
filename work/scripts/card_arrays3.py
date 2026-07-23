#!/usr/bin/env python3
"""Locate per-card arrays by mapping each idiom access to the ACCESSING CODE's
bank (code usually reads data from its own bank), then profiling the target."""
import sys
from collections import Counter

rom = open(sys.argv[1], "rb").read()
n = len(rom)
NCARD = 366


def profile(off):
    if off < 0 or off + NCARD > n:
        return None
    win = rom[off:off + NCARD]
    return max(win), len(set(win)), Counter(win).most_common(1)[0][1]


seen = {}
for i in range(n - 4):
    if rom[i] == 0x21 and rom[i + 3] in (0x09, 0x19):
        addr = rom[i + 1] | (rom[i + 2] << 8)
        if addr < 0x4000:
            off = addr                                   # fixed bank 0
        else:
            off = (i // 0x4000) * 0x4000 + (addr - 0x4000)  # code's own bank
        p = profile(off)
        if not p:
            continue
        mx, distinct, modal = p
        if mx < 0x30 and 4 <= distinct <= 40 and modal < NCARD * 0.6:
            seen.setdefault(off, (i, addr, mx, distinct, modal))

print(f"{len(seen)} candidate per-card array(s) (small categorical values):\n")
for off in sorted(seen):
    i, addr, mx, distinct, modal = seen[off]
    print(f"  data@0x{off:06X}  (code@0x{i:06X} ld hl,${addr:04X})  "
          f"max=0x{mx:02X} distinct={distinct} modal={modal}")
    print(f"     first 30: {list(rom[off:off + 30])}")
