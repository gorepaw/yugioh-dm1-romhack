#!/usr/bin/env python3
"""Find genuine free space: long runs of 0x00 or 0xFF, reported per bank.

Usage: python find_freespace.py <rom> [minlen]
Free space at the END of a bank is safest (padding), so runs are annotated with
how far they sit from the bank boundary.
"""
import sys

rom = open(sys.argv[1], "rb").read()
minlen = int(sys.argv[2], 0) if len(sys.argv) > 2 else 96
n = len(rom)

runs = []
i = 0
while i < n:
    b = rom[i]
    if b in (0x00, 0xFF):
        j = i
        while j < n and rom[j] == b:
            j += 1
        if j - i >= minlen:
            runs.append((i, j - i, b))
        i = j
    else:
        i += 1

print(f"{len(runs)} free-space run(s) >= {minlen} bytes:\n")
for off, ln, b in runs:
    bank = off // 0x4000
    bank_end = (bank + 1) * 0x4000
    tail = "  <== runs to END of bank (padding, safest)" if off + ln >= bank_end else ""
    cpu = off if bank == 0 else 0x4000 + (off % 0x4000)
    print(f"  0x{off:06X} bank {bank:2d} (cpu ${cpu:04X})  {ln:5d} bytes of 0x{b:02X}{tail}")
