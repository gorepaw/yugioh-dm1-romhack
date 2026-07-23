#!/usr/bin/env python3
"""Whole-ROM multi-stride search for the TYPE field (parallel array or record)."""
import sys

rom = open(sys.argv[1], "rb").read()
n = len(rom)

SPELL = [1, 15, 16, 17, 18, 19, 20]
DRAG = [0, 3, 9, 10]
FIEND = [4, 5, 21]


def all_eq(B, stride, idxs):
    first = rom[B + idxs[0] * stride]
    for i in idxs[1:]:
        if rom[B + i * stride] != first:
            return None
    return first


hits = []
maxidx = max(SPELL + DRAG + FIEND)
for stride in range(1, 13):
    span = maxidx * stride
    for B in range(0, n - span):
        dv = all_eq(B, stride, DRAG)          # cheap 4-check first
        if dv is None:
            continue
        sv = all_eq(B, stride, SPELL)
        if sv is None or sv == dv or max(sv, dv) > 200:
            continue
        fv = all_eq(B, stride, FIEND)
        hits.append((B, stride, sv, dv, fv))

print(f"{len(hits)} hit(s)")
for B, stride, sv, dv, fv in hits[:30]:
    ftxt = f"Fiend={fv}" if fv is not None else "Fiend=mixed"
    print(f"  @0x{B:06X} stride={stride}  Spell={sv} Dragon={dv} {ftxt}")
    if stride <= 4:
        print(f"     bytes[i=0..23]: {[rom[B + i * stride] for i in range(24)]}")
