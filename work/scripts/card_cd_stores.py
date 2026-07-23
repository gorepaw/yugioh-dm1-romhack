#!/usr/bin/env python3
"""Show every store to $CD11 / $CD12 with preceding context (find the loader)."""
import sys

rom = open(sys.argv[1], "rb").read()
n = len(rom)

for xx, label in ((0x11, "$CD11"), (0x12, "$CD12")):
    pat = bytes([0xEA, xx, 0xCD])
    print(f"=== stores to {label} ===")
    i = 0
    while True:
        j = rom.find(pat, i)
        if j < 0:
            break
        before = rom[max(0, j - 28):j]
        print(f"  @0x{j:06X}: ...{before.hex(' ')} | EA {xx:02X} CD")
        i = j + 1
    print()
