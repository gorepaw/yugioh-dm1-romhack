#!/usr/bin/env python3
"""Assemble work/duelmonsters-mtg/cards.json (dm1-cards/1) from the P2 design pool.

Every one of the engine's **50 effect-capable slots** in #301-365 now carries a
real spell, chosen so the card sits on a slot that already has the right verb —
so effects work with NO rebinding (see docs/NOTES.md for the verb map):

  #301-317,319,321-328  the 26 equip verbs ($15-$2E)   <- stat-buff auras/gear
  #318  transform ($35)          #320  Stop Defence ($30)
  #329  seal ($31)               #330-335  the six fields ($03-$08) = basic lands
  #336  Dark Hole ($13)          #337  Raigeki ($14)
  #338-342  heal 1-5 ($09-$0D)   #343-347  burn 1-5 ($0E-$12)
  #348  Swords ($32)             #349  Spellbinding ($34)   #350  Dark-Piercing ($33)

Creatures fill #1-300 exactly (the fusion-reachable zone); #351-365 are tokens.
Colours drive the type byte and the six terrain tables (via mtg_colors).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as cardlib      # noqa: E402
import mtg_colors             # noqa: E402
import mtg_desc               # noqa: E402
import products             # noqa: E402

COLOR_BYTE = {"White": 0, "Blue": 1, "Black": 2, "Red": 3, "Green": 4, "Colorless": 5}
NCARD = 365

# --- the 26 equip slots, in slot order. (in-game name, colour it attaches to) ---
EQUIP_SLOTS = [301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311,
               312, 313, 314, 315, 316, 317, 319,
               321, 322, 323, 324, 325, 326, 327, 328]
EQUIPS = [
    ("Holy Strength", "White"), ("Holy Armor", "White"), ("Blessing", "White"),
    ("Unholy Strength", "Black"), ("Firebreathing", "Red"), ("Web", "Green"),
    ("Aspect of Wolf", "Green"), ("Unstable Mutation", "Blue"),
    ("Coral Helm", "Colorless"), ("Tawnos Weaponry", "Colorless"),
    ("Thrull Retainer", "Black"),
    # --- added so the game is not spell-starved ---
    ("Giant Growth", "Green"), ("Berserk", "Green"), ("Cocoon", "Green"),
    ("DivineTransform", "White"), ("InfinitAuthority", "White"),
    ("Giant Strength", "Red"), ("The Brute", "Red"),
    ("Rapid Fire", "Red"), ("Burrowing", "Red"),
    ("Fishliver Oil", "Blue"),
    ("Elven Lyre", "Colorless"), ("Zelyon Sword", "Colorless"),
    ("Spirit Shield", "Colorless"), ("Living Armor", "Colorless"),
    ("Transmogrant", "Colorless"),
]

# --- fixed-slot spells: slot -> (name, colour) ---
FIXED = {
    318: ("Dance of Many", "Blue"),      # transform $35
    320: ("Siren's Call", "Blue"),       # Stop Defence $30 (creatures must attack)
    329: ("Shatter", "Colorless"),       # seal $31 -> artifact-hate
    330: ("Forest", "Green"), 331: ("Wastes", "Colorless"), 332: ("Mountain", "Red"),
    333: ("Plains", "White"), 334: ("Island", "Blue"), 335: ("Swamp", "Black"),
    336: ("Wrath of God", "White"),      # Dark Hole $13
    337: ("Terror", "Black"),            # Raigeki $14
    338: ("Healing Salve", "White"),     # heal 1
    339: ("Balm Restoration", "White"),  # heal 2
    340: ("DarkHeartOfWood", "Green"),   # heal 3
    341: ("Fountain of Youth", "Colorless"),  # heal 4
    342: ("Ivory Cup", "Colorless"),     # heal 5
    343: ("Lightning Bolt", "Red"), 344: ("Psionic Blast", "Blue"),
    345: ("Fireball", "Red"), 346: ("Disintegrate", "Red"), 347: ("Drain Life", "Black"),
    348: ("Festival", "White"),          # Swords $32 (creatures can't attack)
    349: ("Marsh Gas", "Black"),         # Spellbinding $34 (all creatures -2/-0)
    350: ("Amnesia", "Blue"),            # Dark-Piercing $33 (reveal the hand)
}
FILLER = ["Rat", "Bat", "Elf", "Orc", "Imp", "Ape", "Eel", "Cat", "Bee",
          "Fox", "Goo", "Elk", "Owl", "Ram", "Hen"]   # 15 tokens -> #351-365


def creature_card(cid, cr):
    color = cr["color"]
    fa, fd = mtg_colors.derive_fields(color, cr["atk"], cr["def"])
    return {"id": cid, "name": cr.get("shortname", cr["name"]), "color": color,
            "type": str(COLOR_BYTE[color]), "atk": cr["atk"], "def": cr["def"],
            "field_atk": fa, "field_def": fd,
            "desc": mtg_desc.for_creature(cr["name"], color)}


def spell_card(cid, name, color, attaches=None):
    c = {"id": cid, "name": name, "color": color, "type": str(COLOR_BYTE[color]),
         "atk": None, "def": None, "field_atk": [None] * 6, "field_def": [None] * 6,
         "desc": mtg_desc.for_spell(name, color)}
    if attaches:
        c["attaches_to"] = attaches
    return c


def main():
    pool = json.load(open(products.data_path("creatures.json", "duelmonsters-mtg"), encoding="utf-8"))
    cutp = products.data_path("_cuts.json", "duelmonsters-mtg")
    if os.path.exists(cutp):
        cut = set(json.load(open(cutp, encoding="utf-8")))
        pool = [c for c in pool if c.get("shortname", c["name"]) not in cut]
    if len(pool) != 300:
        print(f"warning: expected 300 creatures after cuts, got {len(pool)}")

    slots = [None] * NCARD
    for cid in range(1, 301):
        slots[cid - 1] = creature_card(cid, pool[cid - 1])
    for slot, (nm, col) in zip(EQUIP_SLOTS, EQUIPS):
        slots[slot - 1] = spell_card(slot, nm, col, attaches=[col])
    for slot, (nm, col) in FIXED.items():
        slots[slot - 1] = spell_card(slot, nm, col)
    for k, cid in enumerate(range(351, 366)):
        nm = FILLER[k]
        fa, fd = mtg_colors.derive_fields("Colorless", 400, 400)
        slots[cid - 1] = {"id": cid, "name": nm, "color": "Colorless",
                          "type": str(COLOR_BYTE["Colorless"]), "atk": 400, "def": 400,
                          "field_atk": fa, "field_def": fd, "desc": mtg_desc.FILLER,
                          "token": True}   # tokens are not valid equip targets

    missing = [i + 1 for i, s in enumerate(slots) if s is None]
    assert not missing, f"unfilled slots: {missing}"

    db = {"_format": "dm1-cards/1", "cards": slots}
    outp = products.data_path("cards.json", "duelmonsters-mtg")
    json.dump(db, open(outp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    import cardc
    names = sum(len(cardc._name_bytes(c)) for c in slots)
    descs = sum(len(cardc._desc_bytes(c)) for c in slots)
    nspell = sum(1 for s in slots if s["atk"] is None)
    print(f"wrote {outp}: {len(slots)} cards  ({len(pool)} creatures, {nspell} spells, "
          f"{len(FILLER)} tokens)")
    print(f"  name pool: {names}/{cardc.NAME_BUDGET}  ({cardc.NAME_BUDGET-names} free)")
    print(f"  desc pool: {descs}/{cardc.DESC_BUDGET}  ({cardc.DESC_BUDGET-descs} free)")
    return 0 if names <= cardc.NAME_BUDGET and descs <= cardc.DESC_BUDGET else 1


if __name__ == "__main__":
    raise SystemExit(main())
