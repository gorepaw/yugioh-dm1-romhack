#!/usr/bin/env python3
"""Generate Duel Monsters MTG fusion recipes into work/duelmonsters-mtg/fusions.json.

MTG has no fusion, so this invents one coherent rule the player can learn:

    two creatures of the SAME COLOUR fuse into a stronger creature of that colour,
    whose power is about the sum of theirs.

So 400 + 400 -> an 800-power body, 800 + 800 -> ~1600, and two 2000+ bodies of a
colour reach that colour's **Elder Dragon** (4000/4000) — the natural capstone.
Colourless tops out at Colossus of Sardia. Same-colour-only keeps the rule simple
and makes each colour a self-contained upgrade ladder.

The table is a fixed **2159 rows** (the count is a hardcoded immediate in three
places), so every row is filled with a real, distinct recipe. Rows are allocated
per colour in proportion to how many creatures that colour has, and within a
colour we take mostly cheap pairs (so fusion is reachable early) plus a slice of
the most expensive pairs (so the Elder Dragon capstones exist).

Materials and results are **1-based card numbers** (the shape every tool here
uses; `fusions.py` converts to the ROM's 0-based indices), and only #1-300 —
the fusion-reachable zone — is used.
"""
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import products  # noqa: E402

NREC = 2159
HIGH_SLICE = 0.25          # fraction of each colour's rows taken from the top pairs
CAPSTONES = {"Arcades Sabboth", "Chromium", "Nicol Bolas", "Palladia-Mors",
             "Vaevictis Asmadi", "Colossus of Sardia"}


def value(c):
    return max(c["atk"], c["def"])


def _pick(cands, target):
    """Closest to target; on a tie prefer the colour's capstone (Leviathan and
    Chromium are both 4000, and the Elder Dragon should be the blue capstone)."""
    return min(cands, key=lambda r: (abs(value(r) - target), r["name"] not in CAPSTONES))


def main():
    cards = json.load(open(products.data_path("cards.json", "duelmonsters-mtg"), encoding="utf-8"))["cards"]
    creatures = [c for c in cards
                 if c["atk"] is not None and not c.get("token") and c["id"] <= 300]
    by_color = {}
    for c in creatures:
        by_color.setdefault(c["color"], []).append(c)
    for g in by_color.values():
        g.sort(key=value)

    total = len(creatures)
    quota = {col: max(1, round(NREC * len(g) / total)) for col, g in by_color.items()}

    recipes = []
    for col, g in by_color.items():
        # every distinct unordered pair, cheapest-combined first
        pairs = sorted(itertools.combinations(g, 2), key=lambda p: value(p[0]) + value(p[1]))
        n = quota[col]
        nhigh = int(n * HIGH_SLICE)
        chosen = pairs[:n - nhigh] + (pairs[-nhigh:] if nhigh else [])
        for a, b in chosen:
            target = value(a) + value(b)
            floor = max(value(a), value(b))
            # the same-colour creature closest to the combined power, strictly
            # stronger than both materials (else the fusion would be a downgrade)
            cands = [r for r in g if value(r) > floor and r["atk"] > 0
                     and r["atk"] >= max(a["atk"], b["atk"])
                     and r["id"] not in (a["id"], b["id"])]
            if not cands:
                continue
            r = _pick(cands, target)
            recipes.append({"a": a["id"], "b": b["id"], "result": r["id"]})

    # dedupe unordered material pairs (the engine takes the FIRST match, so a
    # duplicate pair would be a dead row) and pad/trim to exactly NREC
    seen, out = set(), []
    for r in recipes:
        k = (min(r["a"], r["b"]), max(r["a"], r["b"]))
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
    if len(out) < NREC:
        # top up with further cheap same-colour pairs not already used
        for col, g in by_color.items():
            for a, b in itertools.combinations(g, 2):
                if len(out) >= NREC:
                    break
                k = (min(a["id"], b["id"]), max(a["id"], b["id"]))
                if k in seen:
                    continue
                floor = max(value(a), value(b))
                cands = [r for r in g if value(r) > floor and r["atk"] > 0
                     and r["atk"] >= max(a["atk"], b["atk"])
                     and r["id"] not in (a["id"], b["id"])]
                if not cands:
                    continue
                r = _pick(cands, value(a) + value(b))
                seen.add(k)
                out.append({"a": a["id"], "b": b["id"], "result": r["id"]})
    out = out[:NREC]
    if len(out) != NREC:
        raise SystemExit(f"could only build {len(out)} recipes, need exactly {NREC}")

    db = {"_format": "dm1-fusions/1", "_count": NREC,
          "recipes": [{"i": i, "a": r["a"], "b": r["b"], "result": r["result"]}
                      for i, r in enumerate(out)]}
    path = products.data_path("fusions.json", "duelmonsters-mtg")
    json.dump(db, open(path, "w", encoding="utf-8"), indent=1)

    info = {c["id"]: c for c in cards}
    import collections
    res = collections.Counter(r["result"] for r in out)
    print(f"wrote {path}: {len(out)} recipes, {len(res)} distinct results")
    print("  most-produced:")
    for cid, n in res.most_common(6):
        print(f"    {info[cid]['name']:22} {info[cid]['atk']}/{info[cid]['def']}  x{n}")
    eds = [n for n in ("Arcades Sabboth", "Chromium", "Nicol Bolas", "Palladia-Mors",
                       "Vaevictis Asmadi", "Colossus of Sardia")]
    print("  capstones reachable by fusion:")
    for nm in eds:
        cid = next((c["id"] for c in cards if c["name"] == nm), None)
        print(f"    {nm:22} {'YES x'+str(res[cid]) if res.get(cid) else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
