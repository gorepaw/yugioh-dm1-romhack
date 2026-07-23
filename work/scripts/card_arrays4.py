#!/usr/bin/env python3
"""Per-card array finder v4: map idiom access to accessing-code bank, profile the
first 350 cards (skip padding tail), and keep data-like (non-code) regions."""
import sys
from collections import Counter

rom = open(sys.argv[1], "rb").read()
n = len(rom)
HEAD = 350
OPCODES = {0xCD, 0xC9, 0x20, 0x28, 0xFE, 0x21, 0x18, 0xC3, 0xEA,
           0xF5, 0xC5, 0xE5, 0xD5, 0xF1, 0xC1, 0xE1, 0xD1, 0x00}


def code_frac(off, m=160):
    seg = rom[off:off + m]
    return sum(1 for b in seg if b in OPCODES) / max(1, len(seg))


def looks_percard(off):
    if off < 0 or off + HEAD > n:
        return None
    head = rom[off:off + HEAD]
    mx, distinct = max(head), len(set(head))
    modal = Counter(head).most_common(1)[0][1]
    if code_frac(off) > 0.12:            # too code-like
        return None
    if mx > 0x63 or distinct < 4 or modal > HEAD * 0.55:
        return None
    return mx, distinct, modal


seen = {}
for i in range(n - 4):
    if rom[i] == 0x21 and rom[i + 3] in (0x09, 0x19):
        addr = rom[i + 1] | (rom[i + 2] << 8)
        off = addr if addr < 0x4000 else (i // 0x4000) * 0x4000 + (addr - 0x4000)
        p = looks_percard(off)
        if p:
            seen.setdefault(off, (i, addr, *p))

print(f"{len(seen)} data-like per-card array candidate(s):\n")
for off in sorted(seen):
    i, addr, mx, distinct, modal = seen[off]
    tag = ""
    if off == 0x2409E:
        tag = "  <-- known TYPE array (sanity check OK)"
    print(f"  data@0x{off:06X} (code@0x{i:06X} ld hl,${addr:04X}) "
          f"max=0x{mx:02X} distinct={distinct} modal={modal}{tag}")
    print(f"     first 30: {list(rom[off:off + 30])}")
