#!/usr/bin/env python3
"""Hex-dump a ROM region (rows of 24 bytes)."""
import sys

rom = open(sys.argv[1], "rb").read()
base = int(sys.argv[2], 0)
length = int(sys.argv[3], 0)
for off in range(0, length, 24):
    chunk = rom[base + off:base + off + 24]
    print(f"0x{base + off:06X}: " + " ".join(f"{b:02X}" for b in chunk))
