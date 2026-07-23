#!/usr/bin/env python3
"""Find the card-stats table via a tolerant, multi-encoding ATK-sequence match.

We know cards #0..#22 in order (from cardname.txt) and their ATK/DEF. We look
for the (start offset, stride, encoding) where the most ATK values line up.
A long distinctive sequence beats coincidence; tolerant matching survives a few
wrong reference values. Then we locate the DEF column and dump records.
"""
import sys

rom = open(sys.argv[1], "rb").read()
n = len(rom)

#            #0    #1   #2    #3    #4    #5    #6   #7  #8   #9   #10   #11
ATK = [3000, 800, 1200, 1200, 1000, 1300, 1400, 800, None, 1500, 1750, 1800,
       1200, 1800, 1800, 500, 200, 200, 200, 200, 1000, 2500, 1400]
DEF = [2500, 2000, 1000, 700, 500, 1400, 1200, 600, None, 800, 2030, 1500,
       1400, 1300, 1600, 400, 300, 300, 300, 300, 1000, 1200, 700]
N = len(ATK)


def u16le(o):
    return (rom[o] | (rom[o + 1] << 8)) if o + 1 < n else -1


def u16be(o):
    return ((rom[o] << 8) | rom[o + 1]) if o + 1 < n else -1


def bcd(v):
    return int(f"{v:04d}", 16)


ENCS = {
    "raw_LE": (u16le, lambda v: v),
    "raw_BE": (u16be, lambda v: v),
    "bcd_LE": (u16le, bcd),
    "bcd_BE": (u16be, bcd),
}


def score(reader, enc, o, S, seq):
    m = tot = 0
    for i in range(N):
        if seq[i] is None:
            continue
        if o + i * S + 1 >= n:
            return -1, 0
        tot += 1
        if reader(o + i * S) == enc(seq[i]):
            m += 1
    return m, tot


hits = []
for ename, (reader, enc) in ENCS.items():
    t0 = enc(ATK[0])
    for o in (p for p in range(n - 1) if reader(p) == t0):
        for S in range(2, 65):
            m, tot = score(reader, enc, o, S, ATK)
            if m >= 16:
                hits.append((m, tot, ename, o, S))

hits.sort(reverse=True)
print(f"top ATK matches (>=16 of {sum(1 for a in ATK if a is not None)}):")
for m, tot, ename, o, S in hits[:8]:
    print(f"  [{ename}] ATK#0 @0x{o:06X} stride={S}  ATK={m}/{tot}")

if hits:
    m, tot, ename, o, S = hits[0]
    reader, enc = ENCS[ename]
    print(f"\nBEST: {ename}  ATK#0 field @0x{o:06X}  record stride={S}")
    # find DEF column relative to ATK field
    best_d = None
    for d in range(-16, S + 16):
        dm = sum(1 for i in range(N)
                 if DEF[i] is not None and reader(o + i * S + d) == enc(DEF[i]))
        if best_d is None or dm > best_d[0]:
            best_d = (dm, d)
    print(f"DEF column: +{best_d[1]} from ATK  (DEF matches {best_d[0]})")
    rec_start = o + min(0, best_d[1])
    print(f"\nfirst 8 records (stride {S}, from 0x{o:06X}):")
    for i in range(8):
        base = o + i * S
        print(f"  card#{i} @0x{base:06X}: {rom[base:base + S].hex(' ')}")
