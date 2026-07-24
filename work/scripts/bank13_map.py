#!/usr/bin/env python3
"""Occupancy map of bank $0D, computed from the structures we have decoded.

Runs of 0x00 are NOT free space in this bank: the drop-pool weight arrays are
cumulative, so a card with 0% chance contributes a repeated value (often 0000).
The only safe way to find slack is to account for every known structure and
report what is left over.

Accounted for:
  $4000  far-call routine table (5 entries) + code
  $4072  drop-pool pointer table (17 entries)
  ....   17 x 365 cumulative 16-bit weight arrays (targets of the above)
  $6F02  win-count thresholds (10 x BCD16 + FFFF terminator)
  $6F18  reward pointer table (17 entries)
  ....   17 x 10 reward card ids (targets of the above)

Usage: python bank13_map.py [min_gap]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards  # noqa: E402
import farcall  # noqa: E402

BANK = 0x0D
BASE = BANK * 0x4000
NPOOL = 17
NCARD = 365
NSTEP = 10

DROP_PTRS = 0x4072
THRESHOLDS = 0x6F02
REWARD_PTRS = 0x6F18


def rd16(rom, cpu):
    o = BASE + cpu - 0x4000
    return rom[o] | (rom[o + 1] << 8)


def main(argv):
    rom = open(cards.BASE_ROM, "rb").read()
    min_gap = int(argv[0], 0) if argv else 12
    used = bytearray(0x4000)  # one flag per byte of the bank

    def mark(cpu, length, tag):
        for i in range(length):
            used[cpu - 0x4000 + i] = 1
        regions.append((cpu, cpu + length - 1, tag))

    regions = []
    mark(0x4000, 12, "far-call routine table (5 entries)")
    mark(DROP_PTRS, 2 * NPOOL, "drop-pool pointer table")
    for p in range(NPOOL):
        mark(rd16(rom, DROP_PTRS + 2 * p), 2 * NCARD, f"drop weights pool {p}")
    mark(THRESHOLDS, 2 * NSTEP + 2, "win thresholds + FFFF terminator")
    mark(REWARD_PTRS, 2 * NPOOL, "reward pointer table")
    for p in range(NPOOL):
        mark(rd16(rom, REWARD_PTRS + 2 * p), 2 * NSTEP, f"reward list pool {p}")

    print("known data structures:")
    for lo, hi, tag in sorted(regions):
        print(f"  ${lo:04X}-${hi:04X}  {hi - lo + 1:5d}  {tag}")

    print(f"\nunaccounted-for regions (>= {min_gap} bytes) — code and/or slack:")
    i = 0
    while i < 0x4000:
        if used[i]:
            i += 1
            continue
        j = i
        while j < 0x4000 and not used[j]:
            j += 1
        if j - i >= min_gap:
            lo, hi = 0x4000 + i, 0x4000 + j - 1
            off = BASE + i
            # A gap that begins right after a return/jump cannot be fallen into.
            prev = rom[off - 1]
            ends = {0xC9: "ret", 0xD9: "reti", 0xC3: "jp", 0x18: "jr"}
            after = ends.get(prev, f"0x{prev:02X}")
            body = rom[off:BASE + j]
            fill = "mixed"
            if len(set(body)) == 1:
                fill = f"all 0x{body[0]:02X}"
            print(f"  ${lo:04X}-${hi:04X}  {j - i:5d} bytes  "
                  f"file 0x{off:06X}  prev-byte={after:4s}  {fill}")
        i = j
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
