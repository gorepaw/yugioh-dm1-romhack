#!/usr/bin/env python3
"""Generate work/duelmonsters-kaizo/drop_config.json (explicit per-pool drop tables).

Goals:
  - every NEW card is droppable from its owner (so all 84 are obtainable, not just
    via the reward grind); strong/fusion cards suppressed, apex/gods at the floor
  - all 50 MAGIC cards droppable from the early opponents (Stage 1 friends) at a very
    low rate -- Raigeki/Dark Hole included (owner request)
  - stock drops kept as the base, with references to retired slots removed
  - Pegasus stays the universal farm (every non-God card)
  - Kaiba: Blue-Eyes farmable (feeds the fusion speedrun), apex at the floor

Rates are a sensible first pass -- easily retuned. Run after apply_new_cards.py.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as cardlib  # noqa: E402
import duelists as D  # noqa: E402
import products  # noqa: E402

rom = open(cardlib.BASE_ROM, "rb").read()
names = cardlib.load_names(rom)
def atk(i): return cardlib.bcd_to_int(cardlib.rd(rom, cardlib.BASE_ATK + 2 * i))
def dfn(i): return cardlib.bcd_to_int(cardlib.rd(rom, cardlib.BASE_DEF + 2 * i))

ROOTP1 = products.data_dir("duelmonsters-kaizo")
ledger = json.load(open(os.path.join(ROOTP1, "new_cards.json")))
retired = {c["id"] - 1 for c in ledger}
by_owner = {}
for c in ledger:
    by_owner.setdefault(c["owner"], []).append(c)

MAGIC = list(range(300, 350))          # card indices 300..349 = #301..#350
GODS = {c["id"] - 1 for c in ledger if c["atk"] == 4000 and c["def"] == 4000}

OWNER_POOL = {"Weevil": 0, "Mai": 1, "Rex": 2, "Mako": 3, "Kaiba": 8, "Mokuba": 9,
              "Puppeteer": 12, "PaniK": 13, "Keith": 14, "Yugi": 5, "Tristan": 10,
              "Joey": 7, "Bakura": 11, "Simon": 16, "Pegasus": 15, "Yami": 4}
FRIEND_POOLS = [5, 10, 7, 11]          # Yugi, Tristan, Joey, Bakura (Stage 1) -> spell drops


def newcard_drop_weight(c):
    a = c["atk"]
    base = (40 if a <= 2000 else 25 if a <= 2600 else 12 if a <= 3000
            else 4 if a <= 3500 else 1)
    if c["zone"] == "F":
        base = max(1, base // 3)       # fusion results/materials suppressed
    if c["id"] - 1 in GODS:
        base = 1
    return base


def main():
    pools = {}
    for owner, pool in OWNER_POOL.items():
        w = D.drop_weights(rom, pool)[:]        # stock weights (list of 365)
        for i in retired:                        # drop references to retired slots
            w[i] = 0
        # add this owner's new cards
        for c in by_owner.get(owner, []):
            w[c["id"] - 1] = max(w[c["id"] - 1], newcard_drop_weight(c))
        pools[pool] = w

    # Pegasus (pool 15): universal farm -- every non-God card gets a floor, toons boosted
    peg = [0] * 365
    for i in range(365):
        if i in GODS:
            continue
        peg[i] = 5
    for c in by_owner["Pegasus"]:
        peg[c["id"] - 1] = 30 if c["atk"] < 2600 else 12
    pools[15] = peg

    # Kaiba (pool 8): Blue-Eyes farmable for the fusion speedrun
    pools[8][0] = 30                              # #1 Blue-Eyes White Dragon

    # spell droppability: all 50 magic at a low floor from the Stage 1 friends
    for pool in FRIEND_POOLS:
        for m in MAGIC:
            pools[pool][m] = max(pools[pool][m], 3)

    # emit explicit pools (drops.py normalizes to 2048)
    cfg = {"pools": {}}
    for pool, w in pools.items():
        cfg["pools"][str(pool)] = {str(i + 1): wt for i, wt in enumerate(w) if wt > 0}
    json.dump(cfg, open(os.path.join(ROOTP1, "drop_config.json"), "w"), indent=1)

    # --- sanity ---
    droppable = set()
    for w in pools.values():
        droppable |= {i for i, wt in enumerate(w) if wt > 0}
    new_missing = [c["name"] for c in ledger if c["id"] - 1 not in droppable]
    magic_missing = [names[m] for m in MAGIC if m not in droppable]
    print(f"wrote drop_config.json ({len(cfg['pools'])} pools)")
    print(f"  new cards droppable somewhere: {84 - len(new_missing)}/84"
          + (f"  MISSING {new_missing}" if new_missing else ""))
    print(f"  all 50 magic droppable: {50 - len(magic_missing)}/50"
          + (f"  MISSING {magic_missing}" if magic_missing else ""))
    for nm, m in (("Raigeki", 336), ("Dark Hole", 335)):
        pcount = sum(1 for w in pools.values() if w[m] > 0)
        print(f"  {names[m]} droppable from {pcount} pool(s)")


if __name__ == "__main__":
    main()
