#!/usr/bin/env python3
"""Classify the 12 stat arrays: which are base ATK/DEF, which are terrain x1.3."""
import sys

rom = open(sys.argv[1], "rb").read()
n = len(rom)
STRIDE = 0x2DC          # 366 words per array
FIRST = 0x024381        # first array (base ATK)
NCARD = 366


def u16le(o):
    return rom[o] | (rom[o + 1] << 8)


def bcd_val(v):
    d = [(v >> 12) & 0xF, (v >> 8) & 0xF, (v >> 4) & 0xF, v & 0xF]
    if any(x > 9 for x in d):
        return None
    return d[0] * 1000 + d[1] * 100 + d[2] * 10 + d[3]


def arr(addr):
    return [bcd_val(u16le(addr + 2 * i)) for i in range(NCARD)]


base_atk = arr(FIRST)
base_def = arr(FIRST + STRIDE)


def classify(vals, ref):
    eq = boost = other = nn = 0
    for v, r in zip(vals, ref):
        if r is None or v is None:
            nn += 1
            continue
        if v == r:
            eq += 1
        elif v == round(r * 1.3):
            boost += 1
        else:
            other += 1
    return eq, boost, other, nn


print(f"base ATK @0x{FIRST:06X}, base DEF @0x{FIRST + STRIDE:06X}")
print(f"valid (non-None) base ATK entries: {sum(1 for x in base_atk if x is not None)}")
print(f"first None in base ATK at index: "
      f"{next((i for i, x in enumerate(base_atk) if x is None), None)}\n")

print("array classification (vs base ATK and base DEF; 'boost' = value == round(base*1.3)):")
for k in range(14):
    a = FIRST + k * STRIDE
    if a + STRIDE > n:
        break
    vals = arr(a)
    ea, ba, oa, _ = classify(vals, base_atk)
    ed, bd, od, _ = classify(vals, base_def)
    kind = "ATK" if (ea + ba) > (ed + bd) else "DEF"
    ref = "ATK" if kind == "ATK" else "DEF"
    eq, bo, ot = (ea, ba, oa) if kind == "ATK" else (ed, bd, od)
    print(f"  array#{k:2d} @0x{a:06X}: looks like {kind:3s}-ref "
          f" base-equal={eq:3d}  x1.3-boost={bo:3d}  other={ot:3d}")
