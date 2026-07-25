#!/usr/bin/env python3
"""Generate Duel Monsters MTG drop pools into work/duelmonsters-mtg/drop_config.json.

Rules:
  1. Every opponent drops the cards from **their own deck** — commons frequent,
     bombs rare (weight falls with power), so grinding a duelist builds their
     archetype.
  2. **All five Elder Dragons** additionally drop from Yawgmoth's pool — he is
     the only source of the 4000/4000 apex cards.
  3. **Full coverage**: every card not already dropped by rule 1/2 is assigned to
     an appropriate pool, matched by **colour** and by **power tier** (weak cards
     from early opponents of that colour, strong cards from late ones). Unlike
     decks, drop pools DO include non-monsters — spells/equips/fields are only
     obtainable this way.

Weight curve: w = round(BASE / (1 + value/500)) where value = max(ATK, DEF), so a
400-power common is ~5x as likely as a 4000-power bomb, and nothing is unreachable.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import products  # noqa: E402

NCARD = 365
BASE = 100
SPELL_VALUE = 1400          # non-monsters have no stats; treat as upper-mid tier


def value(card):
    if card["atk"] is None:
        return SPELL_VALUE
    return max(card["atk"], card["def"])


def weight(card):
    return max(3, round(BASE / (1 + value(card) / 500.0)))


def main():
    cards = json.load(open(products.data_path("cards.json", "duelmonsters-mtg"), encoding="utf-8"))["cards"]
    info = {c["id"]: c for c in cards}
    cfg = json.load(open(products.data_path("deck_config.json", "duelmonsters-mtg"), encoding="utf-8"))

    # pool -> deck name, and the tier order (by deck average ATK) per colour
    decks = {d["pool"]: d for d in cfg["decks"]}
    atk = {c["id"]: (c["atk"] or 0) for c in cards}

    def deck_avg(d):
        t = sum(d["cards"].values())
        return sum(atk[int(i)] * w for i, w in d["cards"].items()) / t

    # colour identity of each opponent pool (for leftover assignment)
    POOL_COLORS = {
        5: ["Blue"], 10: ["Red"], 7: ["Red"], 11: ["Green"],            # stage 1
        0: ["White"], 1: ["Black", "Colorless"], 2: ["Colorless"], 3: ["Blue"],
        8: ["Green", "White", "Blue"], 9: ["White", "Blue", "Black"],
        12: ["Red", "Green", "White"], 13: ["Black", "Red", "Green"],
        14: ["Blue", "Black", "Red"],                                    # stage 2
        16: ["Red", "Colorless"], 15: ["White", "Colorless"], 4: ["Black", "Colorless"],
    }
    tier = {p: deck_avg(decks[p]) for p in POOL_COLORS}

    pools = {p: {} for p in POOL_COLORS}

    # --- rule 1: your own deck drops from you ---
    for p, d in decks.items():
        for cid in d["cards"]:
            pools[p][int(cid)] = weight(info[int(cid)])

    # --- rule 2: all Elder Dragons drop from Yawgmoth (pool 4) ---
    for c in cards:
        if c["name"] in ("Arcades Sabboth", "Chromium", "Nicol Bolas",
                         "Palladia-Mors", "Vaevictis Asmadi"):
            pools[4][c["id"]] = weight(c)

    # --- rule 3: everything else, by colour then power tier ---
    covered = {cid for pl in pools.values() for cid in pl}
    leftovers = [c for c in cards if c["id"] not in covered]
    by_color = {}
    for p, cols in POOL_COLORS.items():
        for col in cols:
            by_color.setdefault(col, []).append(p)
    for col in by_color:
        by_color[col].sort(key=lambda p: tier[p])        # weakest opponent first

    for c in leftovers:
        opts = by_color.get(c["color"]) or sorted(POOL_COLORS, key=lambda p: tier[p])
        # place by power: weak cards early in the ladder, strong cards late
        v = value(c)
        frac = min(0.999, max(0.0, (v - 400) / 3600.0))
        pools[opts[int(frac * len(opts))]][c["id"]] = weight(c)

    out = {"pools": {str(p): {str(k): v for k, v in sorted(d.items())}
                     for p, d in pools.items()}}
    path = products.data_path("drop_config.json", "duelmonsters-mtg")
    json.dump(out, open(path, "w", encoding="utf-8"), indent=1)

    covered = {cid for pl in pools.values() for cid in pl}
    print(f"wrote {path}")
    print(f"  pools: {len(pools)}   cards covered: {len(covered)}/{NCARD}")
    missing = [c["id"] for c in cards if c["id"] not in covered]
    if missing:
        print(f"  MISSING: {missing}")
    for p in sorted(pools, key=lambda p: tier[p]):
        print(f"    pool {p:2} {decks[p]['name'][:28]:28} {len(pools[p]):3} droppable")
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
