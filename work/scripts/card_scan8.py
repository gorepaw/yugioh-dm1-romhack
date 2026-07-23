#!/usr/bin/env python3
"""Find TYPE data at any stride (parallel array OR packed record), + diagnostics."""
import sys
from collections import Counter

rom = open(sys.argv[1], "rb").read()
n = len(rom)

SPELL = [1, 15, 16, 17, 18, 19, 20]   # Spellcasters
DRAG = [0, 3, 9, 10]                   # Dragons
FIEND = [4, 5, 21]                     # Fiends
REGION = range(0x18000, 0x30000)


def modal(B, stride, idxs):
    c = Counter(rom[B + i * stride] for i in idxs if B + i * stride < n)
    v, cnt = c.most_common(1)[0]
    return v, cnt, len(idxs)


print("=== strict multi-stride search ===")
hits = []
for stride in range(1, 25):
    for B in REGION:
        if B + 21 * stride >= n:
            continue
        sv, sc, sn = modal(B, stride, SPELL)
        dv, dc, dn = modal(B, stride, DRAG)
        if sc == sn and dc == dn and sv != dv and max(sv, dv) < 64:
            fv, fc, fn = modal(B, stride, FIEND)
            hits.append((B, stride, sv, dv, fv, fc == fn and fv not in (sv, dv)))
print(f"{len(hits)} strict hit(s)")
for B, stride, sv, dv, fv, fok in hits[:20]:
    print(f"  @0x{B:06X} stride={stride} Spell={sv} Dragon={dv} Fiend={fv} fiend_ok={fok}")

print("\n=== tolerant best (stride 1 & 2): maximize group agreement ===")
for stride in (1, 2):
    best = None
    for B in REGION:
        if B + 21 * stride >= n:
            continue
        sv, sc, _ = modal(B, stride, SPELL)
        dv, dc, _ = modal(B, stride, DRAG)
        score = sc + dc + (2 if sv != dv else 0)
        if best is None or score > best[0]:
            best = (score, B, stride, sv, sc, dv, dc)
    _, B, st, sv, sc, dv, dc = best
    print(f"  stride={st}: best @0x{B:06X}  Spell modal={sv} ({sc}/{len(SPELL)})  "
          f"Dragon modal={dv} ({dc}/{len(DRAG)})")
