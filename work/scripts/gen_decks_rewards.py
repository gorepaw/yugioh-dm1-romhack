#!/usr/bin/env python3
"""Generate work/duelmonsters-kaizo/deck_config.json and reward_config.json from the design.

Decks: re-run the RECALC recompute (pruned DECKLISTS stock + new cards weighted by
power, low-weight midrange padding for the weak decks) and emit each pool as
{card_id: relative_weight}. New cards resolve to their assigned slot id via the ledger.

Rewards: non-boss opponents get their 10 highest-ATK cards (max(ATK,DEF)>=1000 floor),
100->10 wins. The four boss reward tables (Yami/Pegasus/Simon/Kaiba) are the designed
lists from their docs.

Run after apply_new_cards.py (needs the ledger's slot ids). P1 only.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as cardlib  # noqa: E402
import products  # noqa: E402

rom = open(cardlib.BASE_ROM, "rb").read()
stock_names = cardlib.load_names(rom)


def atk(i): return cardlib.bcd_to_int(cardlib.rd(rom, cardlib.BASE_ATK + 2 * i))
def dfn(i): return cardlib.bcd_to_int(cardlib.rd(rom, cardlib.BASE_DEF + 2 * i))


ROOTP1 = products.data_dir("duelmonsters-kaizo")
ledger = json.load(open(os.path.join(ROOTP1, "new_cards.json")))
new_by_name = {c["name"]: c["id"] for c in ledger}          # new card name -> slot id
retired = {c["id"] - 1 for c in ledger}
stock_id_by_name = {stock_names[i]: i + 1 for i in range(365) if i not in retired}


def resolve(name):
    """card name -> 1-based id. New cards first, then kept stock cards."""
    if name in new_by_name:
        return new_by_name[name]
    if name in stock_id_by_name:
        return stock_id_by_name[name]
    raise KeyError(f"cannot resolve card name {name!r}")


# --- parse the pruned decklists ---
txt = open(os.path.join(cardlib.ROOT, "docs", "DECKLISTS.md"), encoding="utf-8").read()
blocks = re.split(r"^## (\d+)\. (\w+)", txt, flags=re.M)[1:]
decks = {}
for k in range(0, len(blocks), 3):
    d = int(blocks[k]); stock = []; new = []
    for line in blocks[k + 2].splitlines():
        m = re.match(r"\s*#\s*(\d+)\s+.*\|\s*wt\s+(\d+)", line)
        if m:
            stock.append((int(m.group(1)) - 1, int(m.group(2)))); continue
        m = re.match(r"\s*NEW\s+(.+?)\s*\|\s*(\d+)/(\d+)", line)
        if m:
            new.append((m.group(1).strip(), int(m.group(2)), int(m.group(3))))
    decks[d] = {"name": blocks[k + 1], "stock": stock, "new": new}

# the design names used in DECKLISTS map to ledger names; a few were display-shortened
DISPLAY = {
    "Skilled Dark Magn": "SkilledDarkMagcn", "Skilled Blue Magn": "SkilledBlueMagcn",
    "Skilled White Magn": "SkilledWhiteMagcn", "Legendary Kn Timaeus": "LegndKnghtTimaeus",
    "Timaeus Utd Dragon": "TimaeusUnitedDragn", "DMG the Drgn Knight": "DMGirl:DrgnKnight",
    "Magician's Rod": "Magicn'sRod", "Magician's Robe": "Magicn'sRobe",
    "Dark Magn of Chaos": "DarkMagicnChaos", "Dark Magician Girl": "DarkMagicnGirl",
    "Chronicle Magician": "ChronicleMagicn", "Timestar Magician": "TimestarMagicn",
    "The Dark Magicians": "TheDarkMagicns", "Buster Blade DD": "BusterBladeDrgnDst",
    "Master of Chaos": "MasterofChaos", "Illusion of Chaos": "IllusionofChaos",
    "Amulet Dragon": "AmuletDragon", "Dark Cavalry": "DarkCavalry", "Dark Paladin": "DarkPaladin",
    "Dark Sage": "DarkSage", "Buster Blader": "BusterBlader", "Buster Dragon": "BusterDragon",
    "Obelisk": "ObeliskTormentor", "Slifer": "SliferSkyDragon",
    "Winged Dragon of Ra": "WingedDragonOfRa", "Dark Magician Knight": "DarkMagicnKnight",
    "Red-Eyes Dark Dragoon": "RedEyesDarkDragoon",
    # stage 1/2 display -> ledger (de-spaced)
    "Insect Queen": "InsectQueen", "Harpie'sPetDragn": "Harpie'sPetDragn",
    "Cyber Harpie": "CyberHarpie", "AmazonSwordsWmn": "AmazonSwordsWmn",
    "Black Tyranno": "BlackTyranno", "Ultimate Tyranno": "UltimateTyranno",
    "SuperCondTyranno": "SuperCondTyranno", "Legend Fisherman": "LegendFisherman",
    "Fortress Whale": "FortressWhale", "Levia-Daedalus": "Levia-Daedalus",
    "Amphibian Beast": "AmphibianBeast", "Barrel Dragon": "BarrelDragon",
    "Machine King": "MachineKing", "Slot Machine": "SlotMachine", "Jinzo": "Jinzo",
    "Queen's Knight": "Queen'sKnight", "King's Knight": "King'sKnight",
    "Jack's Knight": "Jack'sKnight", "GearfriedIronKngt": "GearfriedIronKngt",
    "Panther Warrior": "PantherWarrior", "Rocket Warrior": "RocketWarrior",
    "GilfordLightning": "GilfordLightning", "Dark Necrofear": "DarkNecrofear",
    "Headless Knight": "HeadlessKnight", "Portrait'sSecret": "Portrait'sSecret",
    "Gyno Sphinx": "GynoSphinx", "Andro Sphinx": "AndroSphinx",
    "TheinenGrtSphinx": "TheinenGrtSphinx", "ExxodMasterGuard": "ExxodMasterGuard",
    "D.D. Dragon": "D.D.Dragon", "Luster Dragon 2": "LusterDragon2",
    "Kaiser Glider": "KaiserGlider", "Tyrant Dragon": "TyrantDragon",
    "Rabidragon": "Rabidragon", "ChaosEmperorDrgn": "ChaosEmperorDrgn",
    "BlueEyesTyrantDrg": "BlueEyesTyrantDrg", "BlueEyesChaosMax": "BlueEyesChaosMax",
    "BlueEyesUltDragon": "BlueEyesUltDragon", "DragonMasterKnght": "DragonMasterKnght",
    # Pegasus toons
    "Toon Alligator": "ToonAlligator", "Toon Mermaid": "ToonMermaid",
    "ToonSummonSkull": "ToonSummonSkull", "Manga Ryu-Ran": "MangaRyu-Ran",
    "Toon Gemini Elf": "ToonGeminiElf", "ToonMaskSorcerer": "ToonMaskSorcerer",
    "ToonCannonSoldier": "ToonCannonSoldier", "BlueEyesToonDrgn": "BlueEyesToonDrgn",
    "RedEyesToonDragon": "RedEyesToonDragon", "Toon DarkMagician": "ToonDarkMagicn",
    "ToonDarkMagGirl": "ToonDarkMagGirl", "ToonGoblinForce": "ToonGoblinForce",
    "Toon Harpie Lady": "ToonHarpieLady", "Toon Cyber Dragon": "ToonCyberDragon",
    "Toon Barrel Dragon": "ToonBarrelDragon", "ToonBlackLuster": "ToonBlackLuster",
    "Toon Buster Blader": "ToonBusterBlader", "ToonAncientGolem": "ToonAncientGolem",
}

BOSS = {4, 13, 14, 15}
YAMI_CUT = {14, 11, 67, 13}
PADW = 14
PAD = {0: [56, 71], 2: [58], 8: [354],
       10: [25, 77, 65, 43, 63, 90, 42, 76, 26, 45],
       11: [14, 77, 25], 12: [84, 86, 280, 83, 161, 193, 170]}
TOTAL = 2048


def newshare(a):
    if a is None:
        return 0.02
    return (0.030 if a <= 1500 else 0.025 if a <= 2000 else 0.018 if a <= 2600
            else 0.009 if a <= 3000 else 0.003 if a <= 3500 else 0.00049)


def recompute(d):
    """-> list of (card_id_1based, atk, def, weight) summing to 2048."""
    v = decks[d]
    stock = [(i, w) for i, w in v["stock"]]
    if d == 15:
        stock = [(i, w) for i, w in stock if i not in YAMI_CUT]
    if d == 14:
        stock = []
    have = {s for s, _ in stock}
    for i in PAD.get(d, []):
        if i not in have:
            stock.append((i, PADW))
    nw = []
    for nm, a, dd in v["new"]:
        w = max(1, round(newshare(a) * TOTAL))
        nw.append((resolve(DISPLAY.get(nm, nm)), a, dd, w))
    if d == 14:  # Pegasus toons fill the whole deck by power-inverse
        raw = [(resolve(DISPLAY.get(nm, nm)), a, dd,
                (200 if a <= 1400 else 150 if a <= 2000 else 100 if a <= 2400
                 else 60 if a <= 2600 else 30)) for nm, a, dd in v["new"]]
        s = sum(w for *_, w in raw)
        nw = [(cid, a, dd, round(w * TOTAL / s)) for cid, a, dd, w in raw]
    newsum = sum(w for *_, w in nw)
    stocksum = sum(w for _, w in stock)
    rem = TOTAL - newsum
    out = []
    if stocksum > 0 and rem > 0:
        for i, w in stock:
            out.append((i + 1, atk(i), dfn(i), max(1, round(w * rem / stocksum))))
    out += nw
    diff = TOTAL - sum(w for *_, w in out)
    if out:
        j = max(range(len(out)), key=lambda k: out[k][3])
        out[j] = (*out[j][:3], out[j][3] + diff)
    return out


def rewards_auto(f):
    pool = [c for c in f if c[1] is not None and max(c[1], c[2]) >= 1000]
    top = sorted(pool, key=lambda c: -c[1])[:10]
    return [c[0] for c in sorted(top, key=lambda c: c[1])]   # ascending: 10..100 wins


# boss reward lists (10..100 wins), by card name, from the design docs
BOSS_REWARDS = {
    4:  ["LusterDragon2", "KaiserGlider", "TyrantDragon", "Rabidragon", "ChaosEmperorDrgn",
         "BlueEyes W.Dragon", "BlueEyesTyrantDrg", "BlueEyesChaosMax", "BlueEyesUltDragon",
         "DragonMasterKnght"],
    13: ["SpiritOfWinds", "R.Leg of Forbidden", "L.Leg of Forbidden", "R.Arm of Forbidden",
         "L.Arm of Forbidden", "Exodia:Forbidden", "GynoSphinx", "AndroSphinx",
         "TheinenGrtSphinx", "ExxodMasterGuard"],
    14: ["MangaRyu-Ran", "ToonGoblinForce", "RedEyesToonDragon", "ToonSummonSkull",
         "ToonDarkMagicn", "ToonBarrelDragon", "ToonBusterBlader", "BlueEyesToonDrgn",
         "ToonBlackLuster", "ToonAncientGolem"],
    15: ["BusterDragon", "TimestarMagicn", "DMGirl:DrgnKnight", "TheDarkMagicns",
         "DarkCavalry", "BusterBladeDrgnDst", "DarkMagicnKnight", "AmuletDragon",
         "DarkPaladin", "RedEyesDarkDragoon"],
}


def pool_of(d):
    return rom[0xB734 + d]


def main():
    deck_cfg = {"decks": []}
    reward_cfg = {"rewards": {}}
    DN = {d: decks[d]["name"] for d in decks}
    for d in sorted(decks):
        f = recompute(d)
        p = pool_of(d)
        cards_map = {}
        for cid, a, dd, w in f:
            cards_map[str(cid)] = cards_map.get(str(cid), 0) + w
        deck_cfg["decks"].append({"pool": p, "name": DN[d], "cards": cards_map})
        rl = [resolve(n) for n in BOSS_REWARDS[d]] if d in BOSS else rewards_auto(f)
        reward_cfg["rewards"][str(p)] = rl

    json.dump(deck_cfg, open(os.path.join(ROOTP1, "deck_config.json"), "w"), indent=1)
    json.dump(reward_cfg, open(os.path.join(ROOTP1, "reward_config.json"), "w"), indent=1)
    print(f"wrote deck_config.json ({len(deck_cfg['decks'])} decks) and "
          f"reward_config.json ({len(reward_cfg['rewards'])} pools)")
    # quick sanity: every reward list has 10 entries
    bad = {p: len(r) for p, r in reward_cfg["rewards"].items() if len(r) != 10}
    print("reward lists != 10 entries:", bad or "none")


if __name__ == "__main__":
    main()
