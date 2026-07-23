#!/usr/bin/env python3
"""Broader hunt for the card-stats table.

Two strategies:
  A) Proximity: find Blue-Eyes' distinctive ATK+DEF pair (3000 & 2500) close
     together under several encodings, regardless of card ordering.
  B) Triple anchor: ATK of cards #0,#1,#2 (3000,800,1200) at a fixed stride,
     under raw / ÷10 (16-bit) and ÷100 / ÷50 (single-byte) encodings.
"""
import sys

rom = open(sys.argv[1], "rb").read()
n = len(rom)


def u16le(o):
    return rom[o] | (rom[o + 1] << 8)


def u16be(o):
    return (rom[o] << 8) | rom[o + 1]


def positions(reader, value, size):
    return [o for o in range(n - size + 1) if reader(o) == value]


# --- Strategy A: Blue-Eyes ATK/DEF proximity -----------------------------
print("=== A) Blue-Eyes 3000/2500 proximity ===")
schemes = [
    ("16-bit LE raw", u16le, 2, 3000, 2500),
    ("16-bit BE raw", u16be, 2, 3000, 2500),
    ("16-bit LE /10", u16le, 2, 300, 250),
    ("16-bit BE /10", u16be, 2, 300, 250),
    ("byte /100", lambda o: rom[o], 1, 30, 25),
    ("byte /50", lambda o: rom[o], 1, 60, 50),
    ("byte /10", lambda o: rom[o], 1, None, None),  # 3000/10=300 > 255 -> skip
]
for label, reader, size, atk, dfn in schemes:
    if atk is None:
        continue
    pa = positions(reader, atk, size)
    pd = set(positions(reader, dfn, size))
    near = []
    for a in pa:
        for delta in range(-16, 17):
            if delta == 0:
                continue
            if (a + delta) in pd:
                near.append((a, delta))
                break
    tag = f"atk_hits={len(pa):5d} def_hits={len(pd):5d} near_pairs={len(near)}"
    print(f"  {label:16s} {tag}")
    for a, delta in near[:8]:
        print(f"      ATK@0x{a:06X}  DEF at {delta:+d}")


# --- Strategy B: triple ATK anchor at fixed stride -----------------------
print("\n=== B) ATK sequence [card0,card1,card2] at fixed stride ===")
anchor_schemes = [
    ("16-bit LE raw", u16le, [3000, 800, 1200]),
    ("16-bit BE raw", u16be, [3000, 800, 1200]),
    ("16-bit LE /10", u16le, [300, 80, 120]),
    ("byte /100", lambda o: rom[o], [30, 8, 12]),
    ("byte /50", lambda o: rom[o], [60, 16, 24]),
]
for label, reader, seq in anchor_schemes:
    p0 = positions(reader, seq[0], 2)
    s1 = set(positions(reader, seq[1], 2))
    s2 = set(positions(reader, seq[2], 2))
    hits = []
    for a in p0:
        for S in range(1, 129):
            if (a + S) in s1 and (a + 2 * S) in s2:
                hits.append((a, S))
    print(f"  {label:16s} hits={len(hits)}")
    for a, S in hits[:8]:
        print(f"      ATK@0x{a:06X} stride={S}")
