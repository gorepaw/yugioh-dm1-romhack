#!/usr/bin/env python3
"""Duel Monsters MTG — the COLOR layer on top of the P1.1 card compiler.

Design rationale and the full mapping live in `docs/MTG.md`; the engine
proof that this is safe (the terrain boost is a pre-baked table selected by
field index, and the type byte is inert for stats) lives in `docs/NOTES.md`.

The one idea: DM1's per-card *type byte* is reinterpreted as an MTG *color*, and
the six terrain ATK/DEF tables are **derived** from that color instead of being
authored by hand. A card whose color is C is pumped only by C's land:

    field_atk[slot(C)] = round(base_atk * BOOST)   # and DEF likewise
    every other terrain slot = base                # unboosted

So "a Forest pumps your green creatures" is true by construction, with no new
assembly — it is purely which of the six tables carries the ×1.3.

This is a Duel Monsters MTG tool: it defaults to `--product duelmonsters-mtg` and routes its output
through `products.py` into `work/duelmonsters-mtg/`, so it plugs into `build.py --product duelmonsters-mtg`.

CLI:
  python mtg_colors.py map                 print the grounded color/land/slot table
  python mtg_colors.py sample <card#> ...  show a card's per-land stats, colored
  python mtg_colors.py recolor             colorize work/duelmonsters-mtg/cards.json + derive its
                                         terrain tables in place (default product duelmonsters-mtg)
  python mtg_colors.py equips              generate work/duelmonsters-mtg/equips.json from each equip
                                         card's `attaches_to: [colors]` authoring
  python mtg_colors.py demo                containment proof: recolor stock, compile,
                                         assert diffs live only in the 6 terrain tables
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cardc            # noqa: E402
import cards as cardlib  # noqa: E402
import products         # noqa: E402

BOOST = 1.3

# Colors, and which 0-based terrain slot (index into field_atk/field_def, i.e.
# ROM terrain tables 1..6) each color's land occupies. The slot order was
# recovered empirically from the stock data — see docs/NOTES.md.
COLORS = ["White", "Blue", "Black", "Red", "Green", "Colorless"]

COLOR_SLOT = {          # color -> terrain slot 0..5
    "Green":     0,     # slot 1  Forest
    "Colorless": 1,     # slot 2  Wasteland  -> Wastes
    "Red":       2,     # slot 3  Mountain
    "White":     3,     # slot 4  Meadow     -> Plains
    "Blue":      4,     # slot 5  Sea        -> Island
    "Black":     5,     # slot 6  Dark       -> Swamp
}
COLOR_LAND = {"Green": "Forest", "Red": "Mountain", "Blue": "Island",
              "Black": "Swamp", "White": "Plains", "Colorless": "Wastes"}

# Demo only: a plausible stock-species -> color assignment, used by `demo` and
# `sample` to exercise the derivation against real cards. Real P2 content will
# set `color` per card by hand; this is not the shipping mapping.
TYPE_COLOR = {
    "Beast": "Green", "Beast-Warrior": "Green", "Insect": "Green", "Plant": "Green",
    "Zombie": "Colorless", "Dinosaur": "Colorless", "Rock": "Colorless",
    "Machine": "Colorless",
    "Dragon": "Red", "Winged Beast": "Red", "Thunder": "Red", "Pyro": "Red",
    "Warrior": "White", "Fairy": "White",
    "Fish": "Blue", "Sea Serpent": "Blue", "Aqua": "Blue", "Reptile": "Blue",
    "Fiend": "Black", "Spellcaster": "Black",
    # "Magic" -> no color (non-monster, stats stay $FFFF)
}


def derive_fields(color, base_atk, base_def):
    """Return (field_atk[6], field_def[6]) for a mono-color card.

    Non-monster cards (base is None) keep None in every slot, so the compiler
    writes the $FFFF they carry today. An unknown/None color leaves every slot
    at base (colorless-with-no-land), which is a safe no-boost default."""
    def col(base):
        if base is None:
            return [None] * 6
        vals = [base] * 6
        slot = COLOR_SLOT.get(color)
        if slot is not None:
            vals[slot] = round(base * BOOST)
        return vals
    return col(base_atk), col(base_def)


def recolor_card(card, color):
    """Set a card's six terrain tables from `color`, in place. Leaves the type
    byte (`card['type']`) untouched — colors get their own byte/label later."""
    fa, fd = derive_fields(color, card["atk"], card["def"])
    card["field_atk"], card["field_def"] = fa, fd
    return card


def recolor_db(db, color_of):
    """Rewrite every card's terrain tables from a `color_of(card) -> color`
    function. `db` is a cardc extract dict; mutated in place and returned."""
    for c in db["cards"]:
        recolor_card(c, color_of(c))
    return db


# --- terrain-table byte ranges (for the containment proof) ---------------
def _terrain_ranges():
    """(start, end) file ranges of the six terrain ATK/DEF arrays (not base)."""
    span = 2 * (cardc.NCARD + 1)          # 366 entries * 2 bytes = 732 = 0x2DC
    r = []
    for a, d in cardlib.TABLES[1:]:       # [0] is the base table — excluded
        r.append((a, a + span))
        r.append((d, d + span))
    return r


def _in_terrain(off, ranges):
    return any(lo <= off < hi for lo, hi in ranges)


# --- CLI -----------------------------------------------------------------
def cmd_map():
    print(f"BOOST = x{BOOST}\n")
    print(f"{'color':10} {'land':9} {'terrain slot':13} {'ROM ATK tbl':11} DEF tbl")
    for color in ["Green", "Red", "Blue", "Black", "White", "Colorless"]:
        slot = COLOR_SLOT[color]
        a, d = cardlib.TABLES[slot + 1]   # +1: skip the base table
        print(f"{color:10} {COLOR_LAND[color]:9} slot {slot+1} (idx {slot})   "
              f"0x{a:05X}      0x{d:05X}")


def cmd_sample(nums):
    rom = bytearray(open(cardlib.BASE_ROM, "rb").read())
    db = cardc.extract(rom)["cards"]
    for n in nums:
        c = db[int(n) - 1]
        color = TYPE_COLOR.get(c["type"])
        fa, _ = derive_fields(color, c["atk"], c["def"])
        print(f"#{c['id']} {c['name']}  [{c['type']} -> {color}]  base ATK {c['atk']}")
        if c["atk"] is None:
            print("    (non-monster - no stats)")
            continue
        for color2 in ["Green", "Red", "Blue", "Black", "White", "Colorless"]:
            slot = COLOR_SLOT[color2]
            mark = "  <-- its land" if color2 == color else ""
            print(f"    {COLOR_LAND[color2]:8} ({color2:9}) ATK {fa[slot]}{mark}")


def cmd_recolor(product):
    """Colorize a product's cards.json in place: give every monster a `color`
    (kept if already set, else bootstrapped from its stock species) and derive
    the six terrain tables from it. Non-monsters (atk None) are left untouched.
    cards.json is gitignored and product-scoped, so this is safe to re-run."""
    path = products.data_path("cards.json", product)
    db = json.load(open(path, encoding="utf-8"))
    changed = colored = 0
    for c in db["cards"]:
        if c["atk"] is None:                 # non-monster: no color, no fields
            continue
        color = c.get("color") or TYPE_COLOR.get(c["type"])
        if color is None:
            continue                         # unmapped species -> leave as-is
        if c.get("color") != color:
            c["color"] = color
            changed += 1
        c["field_atk"], c["field_def"] = derive_fields(color, c["atk"], c["def"])
        colored += 1
    with open(path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=1, ensure_ascii=False)
    print(f"recolored {colored} monsters in {os.path.relpath(path, products.ROOT)}")
    print(f"  colors newly assigned/changed: {changed}")
    print(f"  build it: python build.py --product {product}   -> "
          f"{os.path.relpath(products.build_path(product), products.ROOT)}")
    return 0


def cmd_equips(product):
    """Generate work/<product>/equips.json from color-locked authoring.

    An equip card in cards.json may carry `attaches_to`: a list of colors. Its
    eligibility list becomes every monster of those colors. Equips without
    `attaches_to` keep their stock list. Enforces the pool budget."""
    import equips
    base = bytearray(open(cardlib.BASE_ROM, "rb").read())
    db_e = equips.extract(base)                       # stock lists = starting point
    cards = json.load(open(products.data_path("cards.json", product),
                            encoding="utf-8"))["cards"]

    # Tokens are filler bodies, not real creatures — never equip targets. Leaving
    # them in would also bloat every Colorless list past the 2642-byte pool.
    color_of = {c["id"]: c.get("color") for c in cards
                if c["atk"] is not None and not c.get("token")}
    card_to_idx = {e["card"]: e["index"] for e in db_e["equips"] if e["card"]}

    locked = 0
    locked_idx = set()
    for c in cards:
        at = c.get("attaches_to")
        if not at:
            continue
        idx = card_to_idx.get(c["id"])
        if idx is None:
            print(f"  warn: #{c['id']} {c['name']} has attaches_to but is not an "
                  f"equip slot ($15-$2E); skipped")
            continue
        colors = set(at)
        targets = sorted(n for n, col in color_of.items() if col in colors)
        db_e["equips"][idx]["targets"] = targets
        db_e["equips"][idx]["attaches_to"] = list(at)   # record intent
        locked += 1
        locked_idx.add(idx)
        print(f"  #{c['id']} {c['name']:20} -> {'/'.join(at):20} "
              f"{len(targets)} monsters")
    # Any equip slot we did NOT color-lock is a dead slot in this product (the
    # card there is not an equip), so empty its eligibility list to reclaim pool.
    for e in db_e["equips"]:
        if e["index"] not in locked_idx:
            e["targets"] = []

    tot = sum(2 * (len(e["targets"]) + 1) for e in db_e["equips"])
    out = products.data_path("equips.json", product)
    rel = os.path.relpath(out, products.ROOT)
    if tot > equips.BUDGET:
        # Do NOT write an over-budget file — it would only crash the next build.
        print(f"OVER BUDGET by {tot - equips.BUDGET} (pool {tot}/{equips.BUDGET}); "
              f"NOT written. Narrow some attaches_to sets, or lock equips whose "
              f"stock list is large (e.g. DarkEnergy has 162) so the swap frees space.")
        return 1
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(db_e, fh, indent=1, ensure_ascii=False)
    print(f"wrote {rel}: {locked} color-locked equip(s); "
          f"pool {tot}/{equips.BUDGET} bytes ({equips.BUDGET - tot} free)")
    return 0


def cmd_demo():
    print("Containment proof: recolor every stock card by species->color, derive")
    print("all six terrain tables from that color, compile, and check what moved.\n")
    base = bytes(open(cardlib.BASE_ROM, "rb").read())
    db = cardc.extract(bytearray(base))

    def color_of(c):
        return TYPE_COLOR.get(c["type"])   # None for Magic -> stays $FFFF
    recolor_db(db, color_of)

    rebuilt = bytearray(base)
    cardc.compile_into(rebuilt, db)

    diffs = [i for i in range(len(base)) if base[i] != rebuilt[i]]
    ranges = _terrain_ranges()
    stray = [i for i in diffs if not _in_terrain(i, ranges)]

    print(f"total bytes changed : {len(diffs)}")
    print(f"inside the 6 terrain tables : {len(diffs) - len(stray)}")
    print(f"anywhere else (should be 0) : {len(stray)}")
    if stray:
        print("  FAIL — stray writes at:", [hex(x) for x in stray[:12]])
        return 1
    print("\nCONTAINED - the color model touches only the six terrain ATK/DEF")
    print("arrays. Names, descriptions, type bytes and base stats are untouched.")
    print("(Diff count is nonzero and expected: derived mono-color boosts differ")
    print(" from stock's multi-terrain boosts, e.g. Beast-Warrior/Thunder.)")
    return 0


def pop_product(argv, default="duelmonsters-mtg"):
    """Like products.pop_arg but defaults to duelmonsters-mtg — this is a Duel Monsters MTG tool."""
    argv = list(argv)
    if "--product" in argv:
        i = argv.index("--product")
        p = products.check(argv[i + 1])
        del argv[i:i + 2]
        return p, argv
    return default, argv


def main(argv):
    product, argv = pop_product(argv)
    if not argv:
        print(__doc__)
        return 1
    cmd = argv[0]
    if cmd == "map":
        cmd_map()
    elif cmd == "sample":
        cmd_sample(argv[1:] or ["1"])
    elif cmd == "recolor":
        return cmd_recolor(product)
    elif cmd == "equips":
        return cmd_equips(product)
    elif cmd == "demo":
        return cmd_demo()
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
