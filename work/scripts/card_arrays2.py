#!/usr/bin/env python3
"""Find star/cost/level arrays by value-range signature over 366-long runs,
and flag which are referenced by the card-index idiom (in any bank)."""
import sys

rom = open(sys.argv[1], "rb").read()
n = len(rom)
NCARD = 366

# idiom targets (CPU addresses used as ld hl,nn ; add hl,bc/de)
targets = set()
for i in range(n - 4):
    if rom[i] == 0x21 and rom[i + 3] in (0x09, 0x19):
        targets.add(rom[i + 1] | (rom[i + 2] << 8))


def cpu_of(off):
    return off if off < 0x4000 else 0x4000 + (off % 0x4000)


def referenced(off):
    return cpu_of(off) in targets


def runs(pred, minlen=NCARD):
    out, start = [], None
    for i in range(n + 1):
        ok = i < n and pred(rom[i])
        if ok and start is None:
            start = i
        elif not ok and start is not None:
            if i - start >= minlen:
                out.append((start, i - start))
            start = None
    return out


def report(title, pred):
    print(f"=== {title} ===")
    for s, ln in runs(pred):
        ref = " <== idiom-referenced!" if referenced(s) else ""
        print(f"  0x{s:06X} len={ln} (cpu ${cpu_of(s):04X}){ref}")
    print()


report("star-like (bytes 0..9)", lambda b: b <= 9)
report("level-like (bytes 1..12)", lambda b: 1 <= b <= 12)
report("packed nibbles both 0..9 (BCD / 2 stars)", lambda b: (b & 0xF) <= 9 and (b >> 4) <= 9)
