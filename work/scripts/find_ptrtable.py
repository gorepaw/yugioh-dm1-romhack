#!/usr/bin/env python3
"""Find pointer tables: runs of consecutive 16-bit LE values inside [lo,hi].

Usage: python find_ptrtable.py <rom> <lo> <hi> [minlen]
A run of many pointers into a handler address range is a dispatch table.
"""
import sys

rom = open(sys.argv[1], "rb").read()
lo = int(sys.argv[2], 0)
hi = int(sys.argv[3], 0)
minlen = int(sys.argv[4], 0) if len(sys.argv) > 4 else 6
n = len(rom)

i = 0
runs = []
while i < n - 1:
    j, vals = i, []
    while j < n - 1:
        v = rom[j] | (rom[j + 1] << 8)
        if lo <= v <= hi:
            vals.append(v)
            j += 2
        else:
            break
    if len(vals) >= minlen:
        runs.append((i, vals))
        i = j
    else:
        i += 1

print(f"{len(runs)} pointer-table run(s) with >= {minlen} entries in "
      f"[${lo:04X},${hi:04X}]:\n")
for off, vals in runs:
    print(f"  @0x{off:06X} bank {off // 0x4000}: {len(vals)} entries")
    print("     " + " ".join(f"${v:04X}" for v in vals[:20]) +
          (" ..." if len(vals) > 20 else ""))
