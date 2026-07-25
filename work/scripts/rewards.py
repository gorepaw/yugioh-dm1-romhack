#!/usr/bin/env python3
"""Win-count reward editor (bank 13).

Beating a duelist N times awards a card. Layout:
  thresholds   0x036F02 : 10 x 16-bit BCD (10,20,...,100), FFFF-terminated
  pointers     0x036F18 : 17 pointers (one per duelist/pool); file = ptr + 0x30000
  reward lists 0x036F3A : 17 blocks x 10 x 16-bit card id (award per threshold)

Both addresses are read straight out of the code that uses them: $6EBD does
`ld hl,$6F02` to walk the thresholds, and $6E8E does `ld hl,$6F18 / add hl,de`
with DE = 2 * pool to reach the pointer table.

Edits queue to work/reward_config.json and are applied by build.py.

CLI:
  python rewards.py show [duelist#]          thresholds (+ a duelist's rewards)
  python rewards.py set-thresholds a b c ...  up to 10 ascending win counts
  python rewards.py scale <divisor>           divide the stock 10..100 by N
  python rewards.py clear
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards  # noqa: E402

ROOT = cards.ROOT
BASE_ROM = cards.BASE_ROM
import products  # noqa: E402
REWARD_CONFIG = products.data_path("reward_config.json")   # default product (duelmonsters-kaizo)

THRESHOLDS = 0x036F02
PTRS = 0x036F18
NSTEP = 10
NPOOL = 17


def rd16(rom, o):
    return rom[o] | (rom[o + 1] << 8)


def wr16(rom, o, v):
    rom[o] = v & 0xFF
    rom[o + 1] = (v >> 8) & 0xFF


def read_thresholds(rom):
    return [cards.bcd_to_int(rd16(rom, THRESHOLDS + 2 * i)) for i in range(NSTEP)]


def reward_list(rom, pool):
    base = rd16(rom, PTRS + 2 * pool) + 0x30000
    return [rd16(rom, base + 2 * i) for i in range(NSTEP)]


def apply_config(rom, cfg):
    changed = 0
    th = cfg.get("thresholds")
    if th:
        for i, v in enumerate(th[:NSTEP]):
            wr16(rom, THRESHOLDS + 2 * i, cards.int_to_bcd(v))
        changed += len(th[:NSTEP])
    for pool, ids in (cfg.get("rewards") or {}).items():
        base = rd16(rom, PTRS + 2 * int(pool)) + 0x30000
        for i, cid in enumerate(ids[:NSTEP]):
            wr16(rom, base + 2 * i, cid)
        changed += len(ids[:NSTEP])
    return changed


def load_cfg():
    return json.load(open(REWARD_CONFIG)) if os.path.exists(REWARD_CONFIG) else {}


def save_cfg(c):
    os.makedirs(os.path.dirname(REWARD_CONFIG), exist_ok=True)
    json.dump(c, open(REWARD_CONFIG, "w"), indent=2)


def main(argv):
    global REWARD_CONFIG
    product, argv = products.pop_arg(argv)
    REWARD_CONFIG = products.data_path("reward_config.json", product)
    if not argv:
        print(__doc__)
        return 1
    cmd = argv[0]
    rom = bytearray(open(BASE_ROM, "rb").read())
    names = cards.load_names()

    if cmd == "show":
        print("thresholds (wins):", read_thresholds(rom))
        if len(argv) > 1:
            d = int(argv[1])
            pool = rom[0xB734 + d] if d < 16 else d
            print(f"duelist {d} -> pool {pool} rewards:")
            for i, cid in enumerate(reward_list(rom, pool)):
                nm = names.get(cid - 1, "?") if 1 <= cid <= 365 else f"raw 0x{cid:04X}"
                print(f"    {read_thresholds(rom)[i]:4d} wins -> #{cid:3d} {nm}")

    elif cmd == "set-thresholds":
        vals = [int(x) for x in argv[1:]][:NSTEP]
        if vals != sorted(vals) or vals[0] < 1:
            print("thresholds must be ascending and >= 1")
            return 1
        cfg = load_cfg()
        cfg["thresholds"] = vals
        save_cfg(cfg)
        print(f"queued thresholds: {vals}")

    elif cmd == "scale":
        div = float(argv[1])
        vals = [max(1, round(v / div)) for v in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]]
        # keep strictly ascending
        for i in range(1, len(vals)):
            if vals[i] <= vals[i - 1]:
                vals[i] = vals[i - 1] + 1
        cfg = load_cfg()
        cfg["thresholds"] = vals
        save_cfg(cfg)
        print(f"queued thresholds (stock/{div}): {vals}")

    elif cmd == "clear":
        if os.path.exists(REWARD_CONFIG):
            os.remove(REWARD_CONFIG)
        print(f"cleared {os.path.relpath(REWARD_CONFIG, ROOT)}")

    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
