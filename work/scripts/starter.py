#!/usr/bin/env python3
"""Starter pool editor — the 100 cards the player begins with.

Table at **0x26AC**: exactly **100 x 16-bit card ids**, immediately followed by
code (`push af/bc/de/hl` at 0x2774), so the list is a **hard 100 entries** and
cannot grow. Stock is 100 monsters (avg ATK 942, range 300-3200).

Authoring: work/<product>/starter_config.json = {"cards": [id, ...]} (exactly
100). Applied by build.py.

CLI:
  python starter.py show [--product duelmonsters-mtg]     the current/base pool
  python starter.py verify [--product duelmonsters-mtg]   config sanity (length, valid ids)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as cardlib  # noqa: E402
import products          # noqa: E402

TABLE = 0x26AC
NCARDS = 100


def read_pool(rom):
    """-> card NUMBERS (1..365). The ROM stores 0-based indices; see apply_config."""
    return [(rom[TABLE + 2 * i] | (rom[TABLE + 2 * i + 1] << 8)) + 1
            for i in range(NCARDS)]


def apply_config(rom, cfg):
    ids = cfg.get("cards", [])
    if len(ids) != NCARDS:
        raise ValueError(f"starter pool must be exactly {NCARDS} cards, got {len(ids)}")
    bad = [c for c in ids if not 1 <= c <= 365]
    if bad:
        raise ValueError(f"invalid card ids in starter pool: {bad[:8]}")
    for i, cid in enumerate(ids):
        v = cid - 1                       # the table stores 0-based card INDICES
        rom[TABLE + 2 * i] = v & 0xFF
        rom[TABLE + 2 * i + 1] = (v >> 8) & 0xFF
    return len(ids)


def main(argv):
    product, argv = products.pop_arg(argv)
    if not argv:
        print(__doc__)
        return 1
    cmd = argv[0]
    rom = bytearray(open(cardlib.BASE_ROM, "rb").read())

    if cmd == "show":
        path = products.data_path("cards.json", product)
        names = {}
        if os.path.exists(path):
            for c in json.load(open(path, encoding="utf-8"))["cards"]:
                names[c["id"]] = c["name"]
        else:
            names = {i + 1: n for i, n in cardlib.load_names(rom).items()}
        for i, cid in enumerate(read_pool(rom)):
            print(f"  [{i:3d}] #{cid:3d} {names.get(cid, '?')}")

    elif cmd == "verify":
        p = products.data_path("starter_config.json", product)
        if not os.path.exists(p):
            print(f"no starter_config.json for {product}")
            return 1
        try:
            n = apply_config(bytearray(rom), json.load(open(p, encoding="utf-8")))
            print(f"OK: {n} starter cards, all ids valid")
        except ValueError as e:
            print("FAIL:", e)
            return 1
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
