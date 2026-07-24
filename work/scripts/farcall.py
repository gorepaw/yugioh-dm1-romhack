#!/usr/bin/env python3
"""Far-call (`rst $08`) tooling.

The game's cross-bank call convention, decoded from the handler at bank 0 $1033:

    rst $08          ; CF
    db  <sel>        ; sel = 2*index + 3
    db  <bank>       ; destination bank number

The handler reads a 16-bit little-endian target address from the DESTINATION
bank at ($4000 + sel - 1), banks in, and jumps there. Each bank therefore
begins with:

    $4000  db <bank number>     ; the handler reads this to save the caller's bank
    $4001  db $00
    $4002  dw routine_0         ; sel = 3
    $4004  dw routine_1         ; sel = 5
    ...                         ; sel = 2*i + 3

On `ret` the routine lands on a trampoline at $1071 that restores the caller's
bank, so far calls nest freely.

CLI:
  python farcall.py table <bank>              decode a bank's routine table
  python farcall.py calls <bank> [index]      find every call site (CF sel bank)
  python farcall.py at <file_offset>          decode the far call at an offset
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards  # noqa: E402

BASE_ROM = cards.BASE_ROM
BANKSIZE = 0x4000


def bank_base(bank):
    return bank * BANKSIZE


def to_file(bank, cpu):
    return bank_base(bank) + (cpu - 0x4000 if bank else cpu)


def to_cpu(off):
    bank = off // BANKSIZE
    return bank, (off % BANKSIZE) + (0x4000 if bank else 0)


def rd16(rom, o):
    return rom[o] | (rom[o + 1] << 8)


def sel_to_index(sel):
    return (sel - 3) // 2


def index_to_sel(index):
    return 2 * index + 3


def read_table(rom, bank):
    """Decode a bank's routine pointer table.

    The table ends where the first routine begins, so the entry with the
    lowest target address bounds it.
    """
    base = bank_base(bank)
    entries, limit = [], 0x4000 + BANKSIZE
    for i in range(256):
        addr = 0x4002 + 2 * i
        if addr + 1 >= limit:
            break
        tgt = rd16(rom, base + 2 + 2 * i)
        if not (0x4000 <= tgt < 0x8000):
            break
        entries.append((i, index_to_sel(i), tgt))
        limit = min(limit, tgt)
    return entries


def find_calls(rom, bank, index=None):
    """Every `CF <sel> <bank>` in the ROM. sel is always odd, which makes this
    a far stronger filter than a bare two-byte search."""
    hits = []
    want = index_to_sel(index) if index is not None else None
    for off in range(len(rom) - 2):
        if rom[off] != 0xCF or rom[off + 2] != bank:
            continue
        sel = rom[off + 1]
        if sel < 3 or sel % 2 == 0:
            continue
        if want is not None and sel != want:
            continue
        hits.append((off, sel))
    return hits


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    rom = open(BASE_ROM, "rb").read()
    cmd = argv[0]

    if cmd == "table":
        bank = int(argv[1], 0)
        idb = rom[bank_base(bank)]
        print(f"bank ${bank:02X}: id byte @$4000 = 0x{idb:02X}"
              f"{'  (OK)' if idb == bank else '  <-- MISMATCH, not a table bank'}")
        for i, sel, tgt in read_table(rom, bank):
            print(f"  index {i:3d}  sel 0x{sel:02X}  -> ${tgt:04X} "
                  f"(file 0x{to_file(bank, tgt):06X})   call: CF {sel:02X} {bank:02X}")

    elif cmd == "calls":
        bank = int(argv[1], 0)
        index = int(argv[2], 0) if len(argv) > 2 else None
        for off, sel in find_calls(rom, bank, index):
            b, cpu = to_cpu(off)
            tab = read_table(rom, bank)
            tgt = next((t for i, s, t in tab if s == sel), None)
            tgts = f"${tgt:04X}" if tgt else "?"
            print(f"  0x{off:06X}  bank {b:2d} ${cpu:04X}  -> "
                  f"bank ${bank:02X} index {sel_to_index(sel)} {tgts}")

    elif cmd == "at":
        off = int(argv[1], 0)
        if rom[off] != 0xCF:
            print(f"0x{off:06X} is 0x{rom[off]:02X}, not CF (rst $08)")
            return 1
        sel, bank = rom[off + 1], rom[off + 2]
        tab = read_table(rom, bank)
        tgt = next((t for i, s, t in tab if s == sel), None)
        print(f"0x{off:06X}: rst $08 / db ${sel:02X},${bank:02X}"
              f" -> bank ${bank:02X} index {sel_to_index(sel)}"
              f" {'$%04X' % tgt if tgt else '(no such entry)'}")

    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
