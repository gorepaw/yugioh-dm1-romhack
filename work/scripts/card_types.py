#!/usr/bin/env python3
"""Decode the type enum: group cards by their type byte (ROM 0x2409E)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards  # noqa: E402

rom = open(cards.BASE_ROM, "rb").read()
names = cards.load_names()
TYPE = 0x2409E

groups = {}
for i in range(366):
    v = rom[TYPE + i]
    groups.setdefault(v, []).append(f"#{i + 1} {names.get(i, '?')}")

print(f"{len(groups)} distinct type bytes:\n")
for v in sorted(groups):
    sample = groups[v][:7]
    print(f"  0x{v:02X} ({len(groups[v]):3d} cards): {', '.join(sample)}")
