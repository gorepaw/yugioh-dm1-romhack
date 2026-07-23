#!/usr/bin/env python3
"""Find candidate per-card byte arrays: 366 consecutive small-valued bytes that
are referenced by the card-index idiom (ld hl,nn ; add hl,bc/de).

Reports the target of every such idiom (bank-0 targets map directly to file
offset; $4000-$7FFF are shown as bank-9 guesses) and whether the pointed-to
region looks like a categorical per-card array (small max, several distinct
values) - candidates for type/star/cost/level.
"""
import sys
from collections import Counter

rom = open(sys.argv[1], "rb").read()
n = len(rom)
NCARD = 366

# collect idiom targets
targets = set()
for i in range(n - 4):
    if rom[i] == 0x21 and rom[i + 3] in (0x09, 0x19):
        targets.add(rom[i + 1] | (rom[i + 2] << 8))


def profile(off):
    if off + NCARD > n:
        return None
    win = rom[off:off + NCARD]
    return max(win), len(set(win)), Counter(win).most_common(1)[0][1]


print("candidate per-card arrays (referenced by idiom, look categorical):")
for addr in sorted(targets):
    for label, off in ((("bank0", addr) if addr < 0x4000
                        else ("bank9?", addr - 0x4000 + 0x24000)),):
        p = profile(off)
        if not p:
            continue
        mx, distinct, modal = p
        # categorical per-card array: modest max, several distinct, not dominated
        if mx < 0x30 and 5 <= distinct <= 40 and modal < NCARD * 0.6:
            print(f"  $%04X -> %s ROM 0x%06X  max=0x%02X distinct=%d modal=%d  "
                  "first16=%s" % (addr, label, off, mx, distinct, modal,
                                  list(rom[off:off + 16])))
