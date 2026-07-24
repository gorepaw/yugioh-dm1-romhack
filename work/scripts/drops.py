#!/usr/bin/env python3
"""Card drop-pool editor (Bank D).

17 pools, each a 365-entry cumulative 16-bit weight table (total 2048), indexed
by card id. 16 duelists map to pools via the table at 0xB734. After a win the
game rolls 0..2047 and awards the card whose cumulative bucket it lands in.

Edits are queued to work/drop_config.json and applied by build.py. Every
transform keeps a pool's total at 2048 and its cumulative array monotonic.

Modes (per pool or default for all):
  none      leave the pool unchanged
  flatten   cards the pool already drops become equally likely
  uniform   ALL 365 cards equally likely (any card from this duelist)
  weighted  all cards droppable, but the pool's original cards ~10x more likely

CLI:
  python drops.py duelists                         duelist -> pool map
  python drops.py show <duelist#>                  a duelist's droppable cards
  python drops.py pools                            one-line summary per pool
  python drops.py set-mode <pool#|all> <mode>
  python drops.py boost <pool#> <card#> <weight>
  python drops.py clear
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards  # noqa: E402

ROOT = cards.ROOT
BASE_ROM = cards.BASE_ROM
import products  # noqa: E402
DROP_CONFIG = products.data_path("drop_config.json")   # default product (p1)
PTRTAB = 0x34072
NPOOL = 17
NCARD = 365
TOTAL = 2048
DMAP = 0xB734


def pool_bases(rom):
    return [(rom[PTRTAB + 2 * i] | (rom[PTRTAB + 2 * i + 1] << 8)) + 0x30000
            for i in range(NPOOL)]


def read_cumulative(rom, base):
    return [rom[base + 2 * i] | (rom[base + 2 * i + 1] << 8) for i in range(NCARD)]


def cum_to_weights(cum):
    out, prev = [], 0
    for c in cum:
        out.append(c - prev)
        prev = c
    return out


def weights_to_cum(weights, total=TOTAL):
    """Scale weights to a monotonic cumulative array summing exactly to total."""
    s = sum(weights)
    if s <= 0:
        weights = [1] * len(weights)
        s = len(weights)
    scaled = [w * total // s for w in weights]
    rem = total - sum(scaled)
    order = [i for i, w in enumerate(weights) if w > 0] or list(range(len(weights)))
    k = 0
    while rem > 0:
        scaled[order[k % len(order)]] += 1
        rem -= 1
        k += 1
    cum, acc = [], 0
    for w in scaled:
        acc += w
        cum.append(acc)
    return cum


def base_weights(mode, orig):
    if mode == "flatten":
        return [1 if w > 0 else 0 for w in orig]
    if mode == "uniform":
        return [1] * len(orig)
    if mode == "weighted":
        return [10 if w > 0 else 1 for w in orig]
    return None  # none / unknown -> unchanged


def apply_config(rom, cfg):
    bases = pool_bases(rom)
    default = cfg.get("default_mode", "none")
    pool_modes = cfg.get("pool_modes", {})
    boosts = cfg.get("boosts", [])
    changed = 0
    for pi in range(NPOOL):
        mode = pool_modes.get(str(pi), default)
        orig = cum_to_weights(read_cumulative(rom, bases[pi]))
        bw = base_weights(mode, orig)
        weights = orig[:] if bw is None else bw
        touched = bw is not None
        for b in boosts:
            if b["pool"] == pi:
                weights[b["card"] - 1] = b["weight"]
                touched = True
        if touched:
            cum = weights_to_cum(weights)
            for i, c in enumerate(cum):
                rom[bases[pi] + 2 * i] = c & 0xFF
                rom[bases[pi] + 2 * i + 1] = (c >> 8) & 0xFF
            changed += 1
    return changed


def load_cfg():
    if os.path.exists(DROP_CONFIG):
        return json.load(open(DROP_CONFIG))
    return {"default_mode": "none", "pool_modes": {}, "boosts": []}


def save_cfg(c):
    os.makedirs(os.path.dirname(DROP_CONFIG), exist_ok=True)
    json.dump(c, open(DROP_CONFIG, "w"), indent=2)


def main(argv):
    global DROP_CONFIG
    product, argv = products.pop_arg(argv)
    DROP_CONFIG = products.data_path("drop_config.json", product)
    if not argv:
        print(__doc__)
        return 1
    cmd = argv[0]
    rom = bytearray(open(BASE_ROM, "rb").read())
    names = cards.load_names()
    bases = pool_bases(rom)
    dmap = [rom[DMAP + i] for i in range(16)]

    if cmd == "duelists":
        for d in range(16):
            print(f"  duelist {d:2d} -> pool {dmap[d]}")

    elif cmd == "pools":
        for pi in range(NPOOL):
            w = cum_to_weights(read_cumulative(rom, bases[pi]))
            drops = sum(1 for x in w if x > 0)
            print(f"  pool {pi:2d} @0x{bases[pi]:05X}: {drops} droppable cards")

    elif cmd == "show":
        d = int(argv[1])
        pi = dmap[d] if d < 16 else d
        w = cum_to_weights(read_cumulative(rom, bases[pi]))
        print(f"duelist {d} -> pool {pi}:")
        for i, wt in sorted(enumerate(w), key=lambda t: -t[1]):
            if wt <= 0:
                break
            print(f"    #{i + 1:3d} {names.get(i, '?'):20s} {wt:5d}  ({100 * wt / TOTAL:.1f}%)")

    elif cmd == "set-mode":
        pool, mode = argv[1], argv[2]
        cfg = load_cfg()
        if pool == "all":
            cfg["default_mode"] = mode
        else:
            cfg["pool_modes"][str(int(pool))] = mode
        save_cfg(cfg)
        print(f"set mode {mode} for pool {pool}")

    elif cmd == "boost":
        pool, card, weight = int(argv[1]), int(argv[2]), int(argv[3])
        cfg = load_cfg()
        cfg["boosts"] = [b for b in cfg["boosts"]
                         if not (b["pool"] == pool and b["card"] == card)]
        cfg["boosts"].append({"pool": pool, "card": card, "weight": weight})
        save_cfg(cfg)
        print(f"boost pool {pool} card #{card} ({names.get(card - 1, '?')}) -> weight {weight}")

    elif cmd == "clear":
        if os.path.exists(DROP_CONFIG):
            os.remove(DROP_CONFIG)
        print(f"cleared {os.path.relpath(DROP_CONFIG, ROOT)}")

    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
