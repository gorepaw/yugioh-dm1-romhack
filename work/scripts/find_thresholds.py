#!/usr/bin/env python3
"""Hunt the win-count reward thresholds (10,20,...,100) in several encodings."""
import sys

rom = open(sys.argv[1], "rb").read()

vals = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]


def bcd(v):
    return int(f"{v:04d}", 16)


patterns = {
    "byte 10,20,..(5+)": bytes(vals[:5]),
    "byte 10,20,..(all)": bytes(vals),
    "u16LE 10,20,..(5+)": b"".join(v.to_bytes(2, "little") for v in vals[:5]),
    "BCD16LE 10,20,..(5+)": b"".join(bcd(v).to_bytes(2, "little") for v in vals[:5]),
    "byte BCD 0x10,0x20..": bytes([0x10, 0x20, 0x30, 0x40, 0x50]),
}

for name, pat in patterns.items():
    hits, i = [], 0
    while True:
        j = rom.find(pat, i)
        if j < 0:
            break
        hits.append(j)
        i = j + 1
    print(f"{name:24s} [{pat.hex(' ')}] -> {len(hits)} hit(s)")
    for j in hits[:6]:
        print(f"    @0x{j:06X} bank {j // 0x4000:2d}: {rom[j:j + 24].hex(' ')}")
