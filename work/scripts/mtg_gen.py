#!/usr/bin/env python3
"""Regenerate every Duel Monsters MTG config from work/duelmonsters-mtg/cards.json.

Card ids shift whenever the roster changes, so nothing here stores ids: the three
hand-built boss decks are declared **by card name** and resolved at generation
time. Run this after `mtg_assemble.py`, then `build.py --product duelmonsters-mtg`.

Produces: deck_config.json, equips.json, reward_config.json, drop_config.json
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mtg_decks    # noqa: E402
import products   # noqa: E402

# --- the three bosses, hand-picked by name: {card name: weight} ---
BOSSES = {
    16: ("Mishra (slot 13, BOSS 1)", {
        "Mishra'sWarMachine": 120, "Colossus of Sardia": 95, "Juggernaut": 90,
        "Orgg": 90, "Shivan Dragon": 85, "Ball Lightning": 85, "Mijae Djinn": 80,
        "Fire Elemental": 60, "Frost Giant": 55, "Su-Chi": 55,
        "TwoHeadGiantForiys": 50, "Diabolic Machine": 50, "Bronze Horse": 50,
        "Earth Elemental": 48, "Stone Giant": 45, "Roc of Kher Ridges": 45,
        "Firestorm Phoenix": 42, "Grapeshot Catapult": 40, "Hill Giant": 38,
        "Clay Statue": 35, "Dragon Engine": 30, "Leviathan": 60}),
    15: ("Urza (slot 14, BOSS 2)", {
        "Akron Legionnaire": 170, "Colossus of Sardia": 150, "Urza's Avenger": 130,
        "PersonalIncarnatn": 130, "Juggernaut": 120, "Serra Angel": 110,
        "Bronze Horse": 70, "Su-Chi": 70, "Diabolic Machine": 70,
        "Obsianus Golem": 60, "Moorish Cavalry": 50, "Northern Paladin": 45,
        "White Knight": 45, "Righteous Avengers": 40, "Ivory Guardians": 40,
        "Petra Sphinx": 40, "Thunder Spirit": 40, "Triskelion": 10,
        "Tetravus": 10, "Yotian Soldier": 10, "Ornithopter": 6,
        "Clockwork Avian": 6, "Leviathan": 70}),
    4: ("Yawgmoth (slot 15, BOSS 3)", {
        "Yawgmoth Demon": 100, "Cosmic Horror": 90, "Colossus of Sardia": 70,
        "Lord of the Pit": 65, "Mold Demon": 65, "Nightmare": 60,
        "Ebon Praetor": 55, "Sengir Vampire": 50, "Juzam Djinn": 50,
        "Demonic Hordes": 48, "Juggernaut": 48, "Mishra'sWarMachine": 45,
        "Urza's Avenger": 42, "Fallen Angel": 38, "Derelor": 35,
        "Nameless Race": 32, "Bog Wraith": 28, "Junun Efreet": 26,
        "Obsianus Golem": 26, "Su-Chi": 24, "Black Knight": 22, "Leviathan": 60}),
}

# generated opponents: (pool, name, colours, target avg ATK, signature)
GENERATED = [
    (5,  "Sindbad (slot 9)",   ["Blue"],   520,  "Sindbad"),
    (10, "Ali Baba (slot 10)", ["Red"],    680,  None),
    (7,  "Feldon (slot 11)",   ["Red"],    840,  None),
    (11, "Jasmine (slot 12)",  ["Green"],  1000, None),
    (0,  "Serra (slot 0)",     ["White"],  1150, "Serra Angel"),
    (1,  "Ashnod (slot 1)",    ["Black", "Colorless"], 1250, "Su-Chi"),
    (2,  "Tawnos (slot 2)",    ["Colorless"], 1600, "Bronze Horse"),
    (3,  "Teferi (slot 3)",    ["Blue"],   1450, "Mahamoti Djinn"),
    (8,  "Arcades (slot 4) - Bant",  ["Green", "White", "Blue"],  1550, "Arcades Sabboth"),
    (9,  "Chromium (slot 5) - Esper", ["White", "Blue", "Black"], 1650, "Chromium"),
    (12, "Palladia (slot 6) - Naya",  ["Red", "Green", "White"],  1750, "Palladia-Mors"),
    (13, "Vaevictis (slot 7) - Jund", ["Black", "Red", "Green"],  1830, "Vaevictis Asmadi"),
    (14, "Nicol Bolas (slot 8) - Grixis", ["Blue", "Black", "Red"], 1910, "Nicol Bolas"),
]
EDS = ("Arcades Sabboth", "Chromium", "Nicol Bolas", "Palladia-Mors", "Vaevictis Asmadi")


def main():
    cards = json.load(open(products.data_path("cards.json", "duelmonsters-mtg"), encoding="utf-8"))["cards"]
    byname = {c["name"]: c for c in cards}
    info = {c["id"]: c for c in cards}
    pool = mtg_decks.load_pool()
    edids = {byname[n]["id"] for n in EDS if n in byname}

    decks = []
    for p, (nm, colours, target, sig) in [(g[0], (g[1], g[2], g[3], g[4])) for g in GENERATED]:
        spec = dict(pool=p, name=nm, colors=colours, target=target,
                    exclude=edids, n_per_color=99,
                    per_color=7 if len(colours) > 2 else (10 if len(colours) == 2 else 18))
        if sig:
            spec["signature"] = sig
        decks.append(mtg_decks.build(pool, spec))
        decks[-1]["name"] = nm
    for p, (nm, cardmap) in BOSSES.items():
        missing = [k for k in cardmap if k not in byname]
        if missing:
            raise SystemExit(f"boss deck {nm}: unknown card(s) {missing}")
        decks.append({"pool": p, "name": nm,
                      "cards": {str(byname[k]["id"]): w for k, w in cardmap.items()}})
    json.dump({"decks": decks},
              open(products.data_path("deck_config.json", "duelmonsters-mtg"), "w", encoding="utf-8"), indent=1)

    atk = {c["id"]: (c["atk"] or 0) for c in cards}
    print("deck ladder:")
    for d in decks:
        t = sum(d["cards"].values())
        print(f"   pool {d['pool']:2} {d['name'][:32]:32} avg "
              f"{sum(atk[int(i)]*w for i, w in d['cards'].items())/t:5.0f}")

    # rewards: 10 best of each deck by max(ATK, DEF), weakest -> best
    val = lambda cid: max(info[cid]["atk"] or 0, info[cid]["def"] or 0)   # noqa: E731
    rewards = {}
    for d in decks:
        ids = [int(i) for i in d["cards"]]
        rewards[str(d["pool"])] = sorted(sorted(ids, key=lambda c: -val(c))[:10], key=val)
    json.dump({"rewards": rewards},
              open(products.data_path("reward_config.json", "duelmonsters-mtg"), "w", encoding="utf-8"), indent=1)
    print(f"rewards: {len(rewards)} pools x 10")

    # --- starter pool: exactly 100 cards, the six lands + a low-power spread ---
    byid = {c["id"]: c for c in cards}
    val = lambda c: max(c["atk"], c["def"])            # noqa: E731
    SPELLS = ["Forest", "Wastes", "Mountain", "Plains", "Island", "Swamp",
              "Lightning Bolt", "Healing Salve", "Holy Strength", "Giant Growth"]
    starter = [byname[n]["id"] for n in SPELLS]
    crs = [c for c in cards if c["atk"] is not None and not c.get("token") and c["id"] <= 300]
    # Starting bodies must be able to attack but stay clearly weak — the first
    # opponents average ~530-1050 ATK. A hard total-stat cap is what matters:
    # ranking by max(ATK,DEF) alone let the thin Colourless pool contribute
    # 0/1600 walls, which are brutally strong blockers this early.
    def eligible(c):
        # atk>=300 also bars 0-ATK walls, which are brutal early blockers.
        return 300 <= c["atk"] <= 800 and c["atk"] + c["def"] <= 1600
    deficit = 0
    for col in ("White", "Blue", "Black", "Red", "Green", "Colorless"):
        g = sorted([c for c in crs if c["color"] == col and eligible(c)],
                   key=lambda c: (c["atk"] + c["def"], c["atk"]))
        take = g[:15]
        deficit += 15 - len(take)
        starter += [c["id"] for c in take]
    if deficit:      # a thin colour short-changes us; top up from any colour
        have = set(starter)
        rest = sorted([c for c in crs if eligible(c) and c["id"] not in have],
                      key=lambda c: (c["atk"] + c["def"], c["atk"]))
        starter += [c["id"] for c in rest[:deficit]]
    starter = starter[:100]
    json.dump({"cards": starter},
              open(products.data_path("starter_config.json", "duelmonsters-mtg"), "w", encoding="utf-8"), indent=1)
    print(f"starter pool: {len(starter)} cards "
          f"({sum(1 for i in starter if byid[i]['atk'] is None)} spells incl. all six lands)")

    here = os.path.dirname(os.path.abspath(__file__))
    for tool, args in (("mtg_colors.py", ["equips"]), ("mtg_drops.py", []), ("mtg_fusions.py", [])):
        r = subprocess.run([sys.executable, os.path.join(here, tool)] + args,
                           capture_output=True, text=True)
        print(r.stdout.strip().splitlines()[0] if r.stdout.strip() else r.stderr.strip()[:200])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
