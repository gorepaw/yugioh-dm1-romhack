#!/usr/bin/env python3
"""Find the per-card TYPE (species) array by structural signature.

Known types (0-based card index):
  Spellcaster: 1 (Mystical Elf), 15 (Time Wizard), 16-20 (Exodia + pieces)
  Dragon:      0 (Blue-Eyes), 3 (Baby Dragon), 9, 10
  Fiend:       4 (Ryu-Kishin), 5 (Feral Imp), 21 (Summoned Skull)
A per-card byte array is the TYPE array if each group is internally equal and
the groups differ from each other. Then dump neighbours (star/cost/level live
in adjacent parallel arrays).
"""
import sys

rom = open(sys.argv[1], "rb").read()
n = len(rom)

SPELL = [1, 15, 16, 17, 18, 19, 20]
DRAG = [0, 3, 9, 10]
FIEND = [4, 5, 21]
NCARD = 366


def group_val(B, idxs):
    vals = {rom[B + i] for i in idxs}
    return next(iter(vals)) if len(vals) == 1 else None


print("=== scanning for the TYPE array ===")
cands = []
for B in range(0x1C000, 0x2E000):
    if B + NCARD > n:
        break
    sv = group_val(B, SPELL)
    dv = group_val(B, DRAG)
    fv = group_val(B, FIEND)
    if None in (sv, dv, fv):
        continue
    if len({sv, dv, fv}) == 3 and max(sv, dv, fv) < 40:
        cands.append((B, sv, dv, fv))

print(f"{len(cands)} candidate(s)")
for B, sv, dv, fv in cands:
    print(f"\n  TYPE array @0x{B:06X}: Spellcaster={sv} Dragon={dv} Fiend={fv}")
    print(f"    first 24 type bytes: {list(rom[B:B + 24])}")
    # distinct values across the whole array -> number of species/categories
    vals = list(rom[B:B + NCARD])
    distinct = sorted(set(vals))
    print(f"    distinct byte values in array: {distinct}")
    # neighbouring arrays (candidates for star/cost/level/category)
    for off in (-NCARD * 2, -NCARD, NCARD, NCARD * 2, NCARD * 3):
        a = B + off
        if 0 <= a and a + 24 <= n:
            print(f"    neighbour @0x{a:06X} (B{off:+d}): {list(rom[a:a + 16])}")
