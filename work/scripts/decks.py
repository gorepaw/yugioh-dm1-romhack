#!/usr/bin/env python3
"""Opponent deck editor (bank 8).

Opponents summon **monsters only** — never magic/equip/field cards. A deck is a
365-entry cumulative 16-bit weight array (total 2048) per pool, reached through
the pointer table at 0x2006C: base = 0x20000 + ptr - 0x4000. Per-card share is
`(cum[i]-cum[i-1])/2048`; the game rolls 0..2047 and summons the bucket's card.

Authoring: work/<product>/deck_config.json holds
    {"decks": [ {"pool": 4, "name": "Yawgmoth", "cards": {"164": 100, ...}} ]}
where cards maps card id -> relative weight (normalized to 2048 on build). It is
applied by build.py. Every card must be a MONSTER (real ATK/DEF), enforced here.

CLI:
  python decks.py show <pool#> [--product p2]     current deck of a pool
  python decks.py verify [--product p2]           deck_config sanity (monsters, pools)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as cardlib   # noqa: E402
import drops              # noqa: E402  (reuse weights_to_cum / cum helpers)
import products           # noqa: E402

DECK_PTRS = 0x2006C
BANK8 = 0x20000
NCARD = 365
POOL_MAP = 0xB734


def deck_base(rom, pool):
    ptr = rom[DECK_PTRS + 2 * pool] | (rom[DECK_PTRS + 2 * pool + 1] << 8)
    return BANK8 + ptr - 0x4000


def is_monster(rom, card_id):
    """A monster has a real base ATK (not the $FFFF that non-monsters carry)."""
    a = rom[cardlib.BASE_ATK + 2 * (card_id - 1)] | (rom[cardlib.BASE_ATK + 2 * (card_id - 1) + 1] << 8)
    return a != 0xFFFF


def apply_config(rom, cfg):
    changed = 0
    for d in cfg.get("decks", []):
        pool = d["pool"]
        nonm = [cid for cid in d["cards"] if not is_monster(rom, int(cid))]
        if nonm:
            raise ValueError(f"deck pool {pool} ({d.get('name','?')}) lists "
                             f"non-monster card(s) {nonm}; opponents summon monsters only")
        weights = [0] * NCARD
        for cid, w in d["cards"].items():
            weights[int(cid) - 1] = w
        cum = drops.weights_to_cum(weights)
        base = deck_base(rom, pool)
        for i, c in enumerate(cum):
            rom[base + 2 * i] = c & 0xFF
            rom[base + 2 * i + 1] = (c >> 8) & 0xFF
        changed += 1
    return changed


def main(argv):
    product, argv = products.pop_arg(argv)
    if not argv:
        print(__doc__)
        return 1
    cmd = argv[0]
    rom = bytearray(open(cardlib.BASE_ROM, "rb").read())
    names = cardlib.load_names(rom)

    if cmd == "show":
        pool = int(argv[1])
        cum = [rom[deck_base(rom, pool) + 2 * i] | (rom[deck_base(rom, pool) + 2 * i + 1] << 8)
               for i in range(NCARD)]
        w = drops.cum_to_weights(cum)
        print(f"pool {pool} deck:")
        for i, wt in sorted(enumerate(w), key=lambda t: -t[1]):
            if wt <= 0:
                break
            print(f"    #{i+1:3d} {names.get(i,'?'):20s} {wt:5d}  ({100*wt/2048:.1f}%)")

    elif cmd == "verify":
        path = products.data_path("deck_config.json", product)
        if not os.path.exists(path):
            print(f"no deck_config.json for {product}")
            return 1
        cfg = json.load(open(path))
        # apply the product's cards.json first so is_monster() sees P2 stats,
        # not the base DM1 card that used to sit in that slot.
        test = bytearray(rom)
        cj = products.data_path("cards.json", product)
        if os.path.exists(cj):
            import cardc
            cardc.apply_config(test, cardc.load_db(cj))
        try:
            n = apply_config(test, cfg)
            print(f"OK: {n} deck(s), all monsters, pools valid")
        except ValueError as e:
            print("FAIL:", e)
            return 1

    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
