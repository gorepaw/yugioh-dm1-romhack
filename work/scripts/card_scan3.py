#!/usr/bin/env python3
"""Test BCD encoding for ATK/DEF, and dump context around raw 3000 hits."""
import sys

rom = open(sys.argv[1], "rb").read()
n = len(rom)


def u16le(o):
    return rom[o] | (rom[o + 1] << 8)


def u16be(o):
    return (rom[o] << 8) | rom[o + 1]


def positions(reader, value):
    return [o for o in range(n - 1) if reader(o) == value]


# --- BCD: 3000 -> 0x3000, 800 -> 0x0800, 1200 -> 0x1200 ------------------
print("=== BCD triple-anchor [0x3000,0x0800,0x1200] ===")
for reader, label in ((u16le, "LE"), (u16be, "BE")):
    p0 = positions(reader, 0x3000)
    s1 = set(positions(reader, 0x0800))
    s2 = set(positions(reader, 0x1200))
    hits = []
    for a in p0:
        for S in range(1, 129):
            if (a + S) in s1 and (a + 2 * S) in s2:
                hits.append((a, S))
    print(f"  {label}: 0x3000 count={len(p0)}  triple-hits={len(hits)}")
    for a, S in hits[:8]:
        print(f"     ATK@0x{a:06X} stride={S}")

print("\n=== BCD Blue-Eyes pair (0x3000 near 0x2500) ===")
for reader, label in ((u16le, "LE"), (u16be, "BE")):
    pa = positions(reader, 0x3000)
    pd = set(positions(reader, 0x2500))
    for a in pa:
        for d in range(-16, 17):
            if d and (a + d) in pd:
                print(f"  {label}: ATK(0x3000)@0x{a:06X}  DEF(0x2500) at {d:+d}")

# --- Dump context around every raw 3000 occurrence ----------------------
print("\n=== context around raw u16le==3000 and u16be==3000 ===")
for reader, label in ((u16le, "LE"), (u16be, "BE")):
    for a in positions(reader, 3000):
        lo = max(0, a - 12)
        print(f"  {label} @0x{a:06X}: {rom[lo:a + 14].hex(' ')}")
