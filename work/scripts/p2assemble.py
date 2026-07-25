#!/usr/bin/env python3
"""Assemble work/p2/cards.json (dm1-cards/1) from the P2 design pool.

Slots the 322-creature master pool + the mappable noncreatures + short filler
into the 365 card slots, choosing noncreature slots that already carry the right
base verb (so effects work with NO rebinding — see docs/NOTES.md verb map):

  #301-311  equips (verbs $15-$1F)        <- our 11 stat-buff auras
  #329      Dragon Capture Jar ($31)      <- Colorless seal (artifact-hate)
  #330-335  fields ($03-$08)              <- the 6 basic lands
  #336      Dark Hole ($13)               <- Wrath of God
  #337      Raigeki  ($14)                <- Terror
  #338      heal 1   ($09)                <- Healing Salve
  #343-347  burns    ($0E-$12)            <- our 5 burns

Everything else in #301-365 holds overflow creatures (verbs are ignored for
monsters) or tiny token filler. Colours -> the type byte (White0 Blue1 Black2
Red3 Green4 Colorless5); terrain tables are derived from colour via p2colors.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as cardlib      # noqa: E402
import p2colors             # noqa: E402
import p2desc               # noqa: E402
import products             # noqa: E402

COLOR_BYTE = {"White": 0, "Blue": 1, "Black": 2, "Red": 3, "Green": 4, "Colorless": 5}
NCARD = 365

# noncreatures: (name, color, verb-kind) placed at fixed slots below
EQUIPS = [  # #301-311, in equip-index order; each color-locks to its own colour
    ("Holy Strength", "White"), ("Holy Armor", "White"), ("Blessing", "White"),
    ("Unholy Strength", "Black"), ("Firebreathing", "Red"), ("Web", "Green"),
    ("Aspect of Wolf", "Green"), ("Unstable Mutation", "Blue"),
    ("Coral Helm", "Colorless"), ("Tawnos Weaponry", "Colorless"),
    ("Thrull Retainer", "Black"),
]
LANDS = [  # #330-335, matching field verbs $03-$08 -> Forest/Waste/Mtn/Sogen/Umi/Yami
    ("Forest", "Green"), ("Wastes", "Colorless"), ("Mountain", "Red"),
    ("Plains", "White"), ("Island", "Blue"), ("Swamp", "Black"),
]
BURNS = [  # #343-347, burn 1..5 (small -> large)
    ("Lightning Bolt", "Red"), ("Psionic Blast", "Blue"), ("Fireball", "Red"),
    ("Disintegrate", "Red"), ("Drain Life", "Black"),
]
FILLER = ["Rat", "Bat", "Elf", "Orc", "Imp", "Ape", "Eel", "Cat", "Bee",
          "Fox", "Goo", "Elk", "Owl", "Ram", "Hen", "Sow", "Cub"]  # 17 tiny tokens


def creature_card(cid, cr):
    color = cr["color"]
    fa, fd = p2colors.derive_fields(color, cr["atk"], cr["def"])
    return {"id": cid, "name": cr.get("shortname", cr["name"]), "color": color,
            "type": str(COLOR_BYTE[color]), "atk": cr["atk"], "def": cr["def"],
            "field_atk": fa, "field_def": fd,
            "desc": p2desc.for_creature(cr["name"], color)}


def spell_card(cid, name, color, tag, attaches=None):
    c = {"id": cid, "name": name, "color": color, "type": str(COLOR_BYTE[color]),
         "atk": None, "def": None, "field_atk": [None] * 6, "field_def": [None] * 6,
         "desc": p2desc.SPELL.get(name, [tag, color])}
    if attaches:
        c["attaches_to"] = attaches
    return c


def main():
    pool = json.load(open(products.data_path("creatures.json", "p2"), encoding="utf-8"))
    if len(pool) != 322:
        print(f"warning: expected 322 creatures, got {len(pool)}")

    slots = [None] * NCARD           # index = id-1
    cr = iter(pool)

    def put(cid, card):
        slots[cid - 1] = card

    def next_creature(cid):
        put(cid, creature_card(cid, next(cr)))

    # #1-300 creatures
    for cid in range(1, 301):
        next_creature(cid)
    # #301-311 equips (color-locked)
    for k, (nm, col) in enumerate(EQUIPS):
        put(301 + k, spell_card(301 + k, nm, col, "Equip", attaches=[col]))
    # #312-328 overflow creatures (17)
    for cid in range(312, 329):
        next_creature(cid)
    # #329 seal
    put(329, spell_card(329, "Shatter", "Colorless", "Seal artifacts"))
    # #330-335 lands
    for k, (nm, col) in enumerate(LANDS):
        put(330 + k, spell_card(330 + k, nm, col, "Field"))
    # #336 Wrath, #337 Terror, #338 Healing Salve
    put(336, spell_card(336, "Wrath of God", "White", "Destroy all"))
    put(337, spell_card(337, "Terror", "Black", "Destroy foes"))
    put(338, spell_card(338, "Healing Salve", "White", "Gain life"))
    # #339-342 overflow creatures (4)
    for cid in range(339, 343):
        next_creature(cid)
    # #343-347 burns
    for k, (nm, col) in enumerate(BURNS):
        put(343 + k, spell_card(343 + k, nm, col, "Burn"))
    # #348 overflow creature (the 322nd)
    next_creature(348)
    # #349-350 + #351-365 filler tokens (17)
    fill = iter(FILLER)
    for cid in list(range(349, 351)) + list(range(351, 366)):
        nm = next(fill)
        c = {"id": cid, "name": nm, "color": "Colorless", "type": str(COLOR_BYTE["Colorless"]),
             "atk": 400, "def": 400,
             "field_atk": p2colors.derive_fields("Colorless", 400, 400)[0],
             "field_def": p2colors.derive_fields("Colorless", 400, 400)[1],
             "desc": p2desc.FILLER}
        put(cid, c)

    # sanity: every slot filled, creatures exhausted
    assert all(s is not None for s in slots), "unfilled slot!"
    leftover = list(cr)
    if leftover:
        print(f"warning: {len(leftover)} creatures did not fit")

    db = {"_format": "dm1-cards/1", "cards": slots}
    outp = products.data_path("cards.json", "p2")
    json.dump(db, open(outp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    # budgets
    import cardc
    names = sum(len(cardc._name_bytes(c)) for c in slots)
    descs = sum(len(cardc._desc_bytes(c)) for c in slots)
    print(f"wrote {outp}: {len(slots)} cards")
    print(f"  name pool: {names}/{cardc.NAME_BUDGET}  ({cardc.NAME_BUDGET-names} free)")
    print(f"  desc pool: {descs}/{cardc.DESC_BUDGET}  ({cardc.DESC_BUDGET-descs} free)")
    return 0 if names <= cardc.NAME_BUDGET and descs <= cardc.DESC_BUDGET else 1


if __name__ == "__main__":
    raise SystemExit(main())
