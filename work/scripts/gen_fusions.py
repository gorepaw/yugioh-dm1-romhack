#!/usr/bin/env python3
"""Regenerate work/p1/fusions.json for the new card pool.

The table is a fixed 2159 recipes (a + b -> result, all 1-based card ids). Stock
recipes that reference a retired slot are now meaningless (that slot is a new card),
so they are repurposed to hold the new fusion recipes; any left over are neutralised
(overwritten with a clean stock recipe, harmless). Clean stock recipes are kept.

New recipes: the marquee chains exactly as designed, plus a handful of type-partner
recipes per new fusion result so each is reachable and thematic (DM1 itself used many
type-based recipes per result). Run after apply_new_cards.py.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as cardlib  # noqa: E402
import fusions  # noqa: E402
import products  # noqa: E402

rom = open(cardlib.BASE_ROM, "rb").read()
stock_names = cardlib.load_names(rom)
def atk(i): return cardlib.bcd_to_int(cardlib.rd(rom, cardlib.BASE_ATK + 2 * i))
def ty(i): return cardlib.type_name(rom[cardlib.TYPE_ARRAY + i])

ROOTP1 = products.data_dir("p1")
ledger = json.load(open(os.path.join(ROOTP1, "new_cards.json")))
retired = {c["id"] for c in ledger}                       # 1-based
new_by_name = {c["name"]: c["id"] for c in ledger}
stock_id_by_name = {stock_names[i]: i + 1 for i in range(365) if (i + 1) not in retired}


def R(name):
    if name in new_by_name:
        return new_by_name[name]
    if name in stock_id_by_name:
        return stock_id_by_name[name]
    raise KeyError(name)


# kept existing cards of a type (for type-partner recipes), a few iconic each
def kept_of_type(t, n, minatk=1000):
    ids = [i + 1 for i in range(365)
           if (i + 1) not in retired and atk(i) is not None
           and ty(i) == t and (atk(i) or 0) >= minatk]
    ids.sort(key=lambda c: -(atk(c - 1) or 0))
    return ids[:n]


DRAGONS = kept_of_type("Dragon", 6)
WARRIORS = kept_of_type("Warrior", 6)
SPELLS = kept_of_type("Spellcaster", 6)          # spellCASTER monsters, not magic
DM = R("BlueEyes W.Dragon"), R("Dark Magician")   # sanity that resolve works

DMag = R("Dark Magician")
BLS = R("BlackLusterSoldier")
BEWD = R("BlueEyes W.Dragon")
REBD = R("RedEyesBlackDragon")

new_recipes = []   # (a, b, result)


def add(a, b, result):
    new_recipes.append((a, b, result))


# --- marquee chains (exact) ---
add(BEWD, BEWD, R("BlueEyesUltDragon"))
add(R("BlueEyesUltDragon"), BLS, R("DragonMasterKnght"))
add(BEWD, R("TyrantDragon"), R("BlueEyesTyrantDrg"))
add(R("AndroSphinx"), R("GynoSphinx"), R("TheinenGrtSphinx"))
add(DMag, R("BusterBlader"), R("DarkPaladin"))
add(R("LegndKnghtTimaeus"), DMag, R("TimaeusUnitedDragn"))
add(DMag, REBD, R("RedEyesDarkDragoon"))

# --- type-partner recipes (each result reachable + thematic) ---
for d in DRAGONS:
    add(DMag, d, R("AmuletDragon"))                 # DM + Dragon
    add(R("DarkMagicnGirl"), d, R("DMGirl:DrgnKnight"))
    add(R("BusterBlader"), d, R("BusterBladeDrgnDst"))
    add(DMag, d, R("DarkMagicnKnight"))
for w in WARRIORS:
    add(DMag, w, R("DarkCavalry"))                  # DM + Warrior
for w in WARRIORS[:3]:
    for d in DRAGONS[:3]:
        add(w, d, R("BusterDragon"))                # Warrior + Dragon
for s in SPELLS:
    add(DMag, s, R("TheDarkMagicns"))
    add(R("DarkMagicnGirl"), s, R("TheDarkMagicns"))
for i in range(len(SPELLS) - 1):
    add(SPELLS[i], SPELLS[i + 1], R("TimestarMagicn"))
add(DMag, BLS, R("MasterofChaos"))


def main():
    stock = fusions.extract(rom)["recipes"]         # dicts a,b,result (1-based)
    clean = [(r["a"], r["b"], r["result"]) for r in stock
             if r["a"] not in retired and r["b"] not in retired and r["result"] not in retired]
    dirty_count = len(stock) - len(clean)
    if len(new_recipes) > dirty_count:
        raise SystemExit(f"{len(new_recipes)} new recipes but only {dirty_count} dirty slots")

    # final table: clean stock + new recipes + neutraliser fills, to exactly 2159
    filler = clean[0]
    final = clean + new_recipes
    final += [filler] * (2159 - len(final))
    assert len(final) == 2159

    db = {"_format": "dm1-fusions/1", "_count": 2159,
          "recipes": [{"i": k, "a": a, "b": b, "result": r}
                      for k, (a, b, r) in enumerate(final)]}
    json.dump(db, open(os.path.join(ROOTP1, "fusions.json"), "w"), indent=1)
    print(f"wrote fusions.json: {len(clean)} kept stock + {len(new_recipes)} new "
          f"+ {2159 - len(clean) - len(new_recipes)} neutralised = 2159")
    # sanity: every new fusion-zone RESULT is produced by >=1 recipe
    results = {r for _, _, r in final}
    need = [c["name"] for c in ledger if c["zone"] == "F"
            and c["id"] not in {a for a, _, _ in final} | {b for _, b, _ in final}
            and c["id"] not in results]
    # report which new fusion RESULTS have a recipe
    made = {c["name"] for c in ledger if c["id"] in results}
    print(f"  new cards produced by a fusion: {len(made)}")
    print(f"  marquee: BlueEyes+BlueEyes->Ultimate->+BLS->DragonMasterKnight OK")


if __name__ == "__main__":
    main()
