#!/usr/bin/env python3
"""Find per-card array accesses: the idiom  ld hl,$4xxx ; add hl,bc  (21 lo hi 09).

Each hit is code indexing a Bank-9 per-card table by card id. Maps the target
CPU address ($4000-$7FFF) to a ROM file offset (addr - 0x4000 + 0x24000) and
shows the following load opcode so we can tell what it reads.
"""
import sys

rom = open(sys.argv[1], "rb").read()
n = len(rom)

LOAD = {0x7E: "ld a,(hl)", 0x2A: "ldi a,(hl)", 0x5E: "ld e,(hl)",
        0x56: "ld d,(hl)", 0x46: "ld b,(hl)", 0x4E: "ld c,(hl)",
        0x66: "ld h,(hl)", 0x6E: "ld l,(hl)"}

seen = {}
for i in range(n - 4):
    if rom[i] == 0x21 and rom[i + 3] in (0x09, 0x19):  # ld hl,nn ; add hl,bc/de
        addr = rom[i + 1] | (rom[i + 2] << 8)
        if 0x4000 <= addr <= 0x7FFF:
            nxt = rom[i + 4]
            reg = "bc" if rom[i + 3] == 0x09 else "de"
            seen.setdefault(addr, []).append((i, reg, nxt))

print(f"{len(seen)} distinct Bank-9 per-card table address(es) indexed by code:\n")
for addr in sorted(seen):
    refs = seen[addr]
    file_off = addr - 0x4000 + 0x24000
    loads = {LOAD.get(nxt, f"op {nxt:02X}") for _, _, nxt in refs}
    where = ", ".join(f"@0x{i:05X}" for i, _, _ in refs[:4])
    print(f"  $%04X -> ROM 0x%06X   x%d refs  next:{sorted(loads)}  {where}"
          % (addr, file_off, len(refs)))
