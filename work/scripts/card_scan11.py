#!/usr/bin/env python3
"""Strict wide-stride search: SPELL, DRAG, FIEND each internally equal & all distinct.

Covers per-card record layouts up to 48 bytes. Near-zero false positives.
"""
import sys

rom = open(sys.argv[1], "rb").read()
n = len(rom)

SPELL = [1, 15, 16, 17, 18, 19, 20]
DRAG = [0, 3, 9, 10]
FIEND = [4, 5, 21]
MAXI = max(SPELL + DRAG + FIEND)


def eq(B, s, idxs):
    f = rom[B + idxs[0] * s]
    for i in idxs[1:]:
        if rom[B + i * s] != f:
            return None
    return f


hits = []
for s in range(1, 49):
    span = MAXI * s
    end = n - span
    B = 0
    while B < end:
        dv = eq(B, s, DRAG)
        if dv is not None:
            sv = eq(B, s, SPELL)
            if sv is not None and sv != dv:
                fv = eq(B, s, FIEND)
                if fv is not None and fv != sv and fv != dv:
                    hits.append((B, s, sv, dv, fv))
        B += 1

print(f"{len(hits)} strict 3-distinct hit(s)")
for B, s, sv, dv, fv in hits:
    print(f"  @0x{B:06X} stride={s}  Spell={sv} Dragon={dv} Fiend={fv}")
    print(f"     type[i=0..23] = {[rom[B + i * s] for i in range(24)]}")
