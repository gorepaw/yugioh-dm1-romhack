#!/usr/bin/env python3
"""Map the card-stat region: which arrays are ATK vs DEF, how long, where."""
import sys

rom = open(sys.argv[1], "rb").read()
n = len(rom)

ATK = [3000, 800, 1200, 1200, 1000, 1300, 1400, 800, None, 1500, 1750, 1800,
       1200, 1800, 1800, 500, 200, 200, 200, 200, 1000, 2500, 1400]
DEF = [2500, 2000, 1000, 700, 500, 1400, 1200, 600, None, 800, 2030, 1500,
       1400, 1300, 1600, 400, 300, 300, 300, 300, 1000, 1200, 700]


def u16le(o):
    return rom[o] | (rom[o + 1] << 8)


def bcd_val(v):
    d = [(v >> 12) & 0xF, (v >> 8) & 0xF, (v >> 4) & 0xF, v & 0xF]
    if any(x > 9 for x in d):
        return None
    return d[0] * 1000 + d[1] * 100 + d[2] * 10 + d[3]


def runlen(base):
    """How many consecutive valid-BCD words starting at base."""
    c = 0
    while base + 2 * c + 1 < n and bcd_val(u16le(base + 2 * c)) is not None:
        c += 1
    return c


def matchcount(base, seq):
    c = 0
    for i, want in enumerate(seq):
        if want is None:
            continue
        if bcd_val(u16le(base + 2 * i)) == want:
            c += 1
    return c


print("=== decode candidate bases (spaced 0x5B8=1464) ===")
for b in [0x024381, 0x024939, 0x024EF1, 0x0254A9, 0x025A61, 0x026019]:
    vals = [bcd_val(u16le(b + 2 * i)) for i in range(23)]
    print(f"0x{b:06X}: ATK={matchcount(b, ATK):2d}/22 DEF={matchcount(b, DEF):2d}/22 "
          f"run={runlen(b):4d}  first10={vals[:10]}")

print("\n=== full-ROM search: DEF array (DEF[0..22] as BCD-LE, stride 2) ===")
d0 = 0x2500  # bcd of 2500
for o in range(n - 1):
    if u16le(o) == d0 and matchcount(o, DEF) >= 18:
        print(f"  DEF array @0x{o:06X}  DEF={matchcount(o, DEF)}/22 run={runlen(o)}")

print("\n=== what surrounds the ATK array at 0x026019? (words before/after) ===")
base = 0x026019
print("  16 words BEFORE:", [f"{u16le(base-2*(i+1)):04X}" for i in range(16)][::-1])
print("  entries 360..368:", [bcd_val(u16le(base + 2 * i)) for i in range(360, 369)])
