#!/usr/bin/env python3
"""Find the TYPE array by categorical signature + known-group cohesion."""
import sys
from collections import Counter

rom = open(sys.argv[1], "rb").read()
n = len(rom)

SPELL = [1, 15, 16, 17, 18, 19, 20]
DRAG = [0, 3, 9, 10]
FIEND = [4, 5, 21]
NCARD = 366


def modal(win, idxs):
    c = Counter(win[i] for i in idxs)
    v, cnt = c.most_common(1)[0]
    return v, cnt


best = []
for B in range(0x4000, 0x30000):
    win = rom[B:B + NCARD]
    if len(win) < NCARD:
        break
    if max(win) >= 48:
        continue
    distinct = len(set(win))
    if not (8 <= distinct <= 40):
        continue
    sv, sc = modal(win, SPELL)
    dv, dc = modal(win, DRAG)
    fv, fc = modal(win, FIEND)
    if len({sv, dv, fv}) < 3:
        continue
    best.append((sc + dc + fc, B, distinct, max(win), (sv, sc), (dv, dc), (fv, fc)))

best.sort(reverse=True)
print("top candidate TYPE arrays (score out of 14 = 7 Spell + 4 Dragon + 3 Fiend):")
for score, B, distinct, mx, (sv, sc), (dv, dc), (fv, fc) in best[:12]:
    print(f"  @0x{B:06X} score={score}/14 distinct={distinct} max={mx}  "
          f"Spell={sv}({sc}/7) Dragon={dv}({dc}/4) Fiend={fv}({fc}/3)")
    print(f"     first 24: {list(rom[B:B + 24])}")
