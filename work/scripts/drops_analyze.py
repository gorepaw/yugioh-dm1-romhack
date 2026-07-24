#!/usr/bin/env python3
"""Confirm the drop-pool format: 17 pools of 365 cumulative 16-bit weights."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards  # noqa: E402

rom = open(cards.BASE_ROM, "rb").read()
names = cards.load_names()

PTRTAB = 0x34072
NPOOL = 17
NCARD = 365
DMAP = 0xB734


def u16(o):
    return rom[o] | (rom[o + 1] << 8)


ptrs = [u16(PTRTAB + 2 * i) for i in range(NPOOL)]
bases = [p + 0x30000 for p in ptrs]           # bank D: file = cpu + 0x30000
dmap = [rom[DMAP + i] for i in range(16)]

print("pool pointers:", [f"${p:04X}" for p in ptrs])
print("duelist->pool map (duelist 0..15):", dmap)
print()

for pi in (0, 1, 3, 15):
    base = bases[pi]
    cum = [u16(base + 2 * i) for i in range(NCARD)]
    mono = all(cum[i] <= cum[i + 1] for i in range(NCARD - 1))
    total = cum[-1]
    drops, prev = [], 0
    for i in range(NCARD):
        w = cum[i] - prev
        prev = cum[i]
        if w > 0:
            drops.append((i + 1, w))
    print(f"POOL {pi} @0x{base:05X}: monotonic={mono} total={total} "
          f"droppable_cards={len(drops)}")
    for cardnum, w in drops[:10]:
        pct = 100 * w / total if total else 0
        print(f"    #{cardnum:3d} {names.get(cardnum - 1, '?'):20s} weight {w:4d} ({pct:.1f}%)")
    print()
