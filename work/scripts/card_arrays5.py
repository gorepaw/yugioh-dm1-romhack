#!/usr/bin/env python3
"""Brute-force bank resolution: for every table-base load (ld hl,nn / ld de,nn
with nn in $4000-$7FFF, or fixed nn<$4000), try ALL banks and keep regions that
look like a data-like per-card array. Surfaces arrays in switched banks."""
import sys
from collections import Counter

rom = open(sys.argv[1], "rb").read()
n = len(rom)
HEAD = 350
OPCODES = {0xCD, 0xC9, 0x20, 0x28, 0xFE, 0x21, 0x18, 0xC3, 0xEA,
           0xF5, 0xC5, 0xE5, 0xD5, 0xF1, 0xC1, 0xE1, 0xD1, 0x00, 0x11, 0x01}


def data_like(off):
    if off < 0 or off + HEAD > n:
        return None
    head = rom[off:off + HEAD]
    if sum(1 for b in head[:160] if b in OPCODES) / 160 > 0.10:
        return None
    mx, distinct = max(head), len(set(head))
    modal = Counter(head).most_common(1)[0][1]
    if mx > 0x63 or not (5 <= distinct <= 40) or modal > HEAD * 0.5:
        return None
    return mx, distinct, modal


# table-base loads: 21=ld hl,nn  11=ld de,nn
bases = set()
for i in range(n - 2):
    if rom[i] in (0x21, 0x11):
        bases.add(rom[i + 1] | (rom[i + 2] << 8))

hits = {}
for addr in bases:
    if addr < 0x4000:
        cand = [addr]
    else:
        cand = [b * 0x4000 + (addr - 0x4000) for b in range(64)]
    for off in cand:
        p = data_like(off)
        if p:
            hits.setdefault(off, (addr, off // 0x4000, *p))

print(f"{len(hits)} data-like per-card array candidate(s) across all banks:\n")
for off in sorted(hits):
    addr, bank, mx, distinct, modal = hits[off]
    note = "  <-- TYPE" if off == 0x2409E else ""
    print(f"  0x{off:06X} (bank {bank:2d}, ${addr:04X}) max=0x{mx:02X} "
          f"distinct={distinct} modal={modal}{note}")
    print(f"     first 30: {list(rom[off:off + 30])}")
