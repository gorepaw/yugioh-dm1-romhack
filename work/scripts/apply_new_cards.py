#!/usr/bin/env python3
"""Overlay the new-card ledger onto a fresh stock extract to produce cards.json.

Pipeline:  stock ROM --extract--> 365 cards  --overlay work/<product>/new_cards.json-->
           work/<product>/cards.json   (the compiler's input)

Each ledger entry has a slot `id` (the retired card it replaces), name, type, atk,
def, and 2-line flavour. Terrain (field) values are derived: a card gets ATK/DEF x1.3
on the one terrain that boosts its type (per docs/NOTES.md), matching how stock cards
are stored so field power stays consistent.

cards.json is regenerable (gitignored), so this is safe to re-run whenever the ledger
changes.

Usage: python apply_new_cards.py [--product p1]
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cardc  # noqa: E402
import cards as cardlib  # noqa: E402
import products  # noqa: E402

# terrain field index (0=Forest,1=Wasteland,2=Mountain,3=Meadow,4=Sea,5=Dark) boosted per type
BOOST = {
    "Beast": [0], "Insect": [0], "Plant": [0], "Beast-Warrior": [0, 3],
    "Zombie": [1], "Dinosaur": [1], "Rock": [1],
    "Dragon": [2], "Winged Beast": [2], "Thunder": [2, 4],
    "Warrior": [3],
    "Aqua": [4], "Fish": [4], "Sea Serpent": [4],
    "Fiend": [5], "Spellcaster": [5],
    "Fairy": [], "Reptile": [], "Machine": [], "Pyro": [],
}


def terrain_values(base, boosted_idxs):
    """6 terrain values: base, x1.3 on each boosted slot."""
    return [round(base * 1.3) if k in boosted_idxs else base for k in range(6)]


def main(argv):
    product, _ = products.pop_arg(argv)
    rom = bytearray(open(cardlib.BASE_ROM, "rb").read())
    db = cardc.extract(rom)               # fresh stock 365-card database
    cards = db["cards"]

    ledger_path = products.data_path("new_cards.json", product)
    ledger = json.load(open(ledger_path, encoding="utf-8"))

    applied = 0
    for e in ledger:
        if "id" not in e:
            raise SystemExit(f"ledger entry {e['name']!r} has no slot id (run assign first)")
        i = e["id"] - 1
        boost = BOOST.get(e["type"], [])
        c = cards[i]
        c["name"] = e["name"]
        c["type"] = e["type"]
        c["atk"] = e["atk"]
        c["def"] = e["def"]
        c["field_atk"] = terrain_values(e["atk"], boost)
        c["field_def"] = terrain_values(e["def"], boost)
        c["desc"] = [e["l1"], e["l2"]]
        c.pop("name_raw", None)
        c.pop("desc_raw", None)
        applied += 1

    out = products.data_path("cards.json", product)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=1, ensure_ascii=False)

    # sanity: compile into a scratch ROM to confirm the pools fit
    scratch = bytearray(open(cardlib.BASE_ROM, "rb").read())
    s = cardc.compile_into(scratch, db)
    print(f"overlaid {applied} new cards -> {os.path.relpath(out, cardlib.ROOT)}")
    print(f"  name pool : {s['names']:5d} / {s['name_budget']} "
          f"({s['name_budget'] - s['names']} free)")
    print(f"  desc pool : {s['descs']:5d} / {s['desc_budget']} "
          f"({s['desc_budget'] - s['descs']} free)")
    if s["names"] > s["name_budget"] or s["descs"] > s["desc_budget"]:
        print("  *** OVER BUDGET ***")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
