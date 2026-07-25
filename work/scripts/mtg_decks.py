#!/usr/bin/env python3
"""Generate Duel Monsters MTG opponent decks into work/duelmonsters-mtg/deck_config.json.

Difficulty is expressed as a **target weighted-average ATK**: the engine samples
a deck by weight, so avg-ATK is the honest measure of how hard an opponent hits.
Given a candidate creature list and a target, this solves for weights with a
decaying curve (weaker creatures more common) and binary-searches the decay
until the deck's average lands on target.

Progression is a hard 9/4/3 structure in the ROM (see docs/NOTES.md, "Opponent
progression"): slots 0-8 free choice, 9-12 the second group, 13/14/15 the three
sequential bosses. Deck power must ascend across those stages.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import products  # noqa: E402


def load_pool():
    db = json.load(open(products.data_path("cards.json", "duelmonsters-mtg"), encoding="utf-8"))["cards"]
    return [c for c in db if c["atk"] is not None and not c["name"] in
            ("Rat", "Bat", "Elf", "Orc", "Imp", "Ape", "Eel", "Cat", "Bee",
             "Fox", "Goo", "Elk", "Owl", "Ram", "Hen", "Sow", "Cub")]


def candidates(pool, colors, n_per_color=8, exclude=()):
    """Top n creatures of each colour, excluding the other opponents' signatures."""
    out = []
    for col in colors:
        g = [c for c in pool if c["color"] == col and c["id"] not in exclude
             and c["atk"] > 0]
        g.sort(key=lambda c: -c["atk"])
        out += g[:n_per_color]
    return out


def _gentle_weights(sel):
    """Weights that taper mildly with ATK (weakest ~2x the commonest bomb), so a
    deck plays as a real curve instead of collapsing onto one or two cards."""
    lo = min(c["atk"] for c in sel)
    hi = max(c["atk"] for c in sel)
    span = max(1, hi - lo)
    return {c["id"]: int(round(100 - 55 * (c["atk"] - lo) / span)) for c in sel}


def pick_deck(cands, target_avg, signature=None, per_color=7, sig_share=0.11):
    """Choose creatures whose ATK band centres on `target_avg`, then weight them
    gently. Difficulty is controlled by WHICH creatures appear (a real curve),
    not by extreme weights. The signature is pinned at ~sig_share of the deck."""
    others = [c for c in cands if not signature or c["id"] != signature["id"]]
    by_color = {}
    for c in others:
        by_color.setdefault(c["color"], []).append(c)

    def select(center):
        sel = []
        for col, g in by_color.items():
            g = sorted(g, key=lambda c: abs(c["atk"] - center))[:per_color]
            sel += g
        return sel

    def avg_of(sel):
        w = _gentle_weights(sel)
        tot = sum(w.values())
        base = sum(c["atk"] * w[c["id"]] for c in sel) / tot
        if signature:
            return (1 - sig_share) * base + sig_share * signature["atk"]
        return base

    lo, hi = 200.0, 4000.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if avg_of(select(mid)) < target_avg:
            lo = mid
        else:
            hi = mid
    sel = select((lo + hi) / 2)
    w = _gentle_weights(sel)
    tot = sum(w.values())
    out = {str(c["id"]): max(4, round(w[c["id"]] / tot * (1 - sig_share) * 1000))
           for c in sel}
    if signature:
        out[str(signature["id"])] = round(sig_share * 1000)
    return out


def build(pool, spec):
    """spec: {pool, name, colors, target, signature, exclude}"""
    exclude = set(spec.get("exclude", ()))
    sig = None
    if spec.get("signature"):
        sig = next(c for c in pool if c["name"] == spec["signature"])
        exclude.add(sig["id"])
    cands = candidates(pool, spec["colors"], spec.get("n_per_color", 40), exclude)
    if sig:
        cands = cands + [sig]
    return {"pool": spec["pool"], "name": spec["name"],
            "cards": pick_deck(cands, spec["target"], sig,
                               spec.get("per_color", 7),
                               spec.get("sig_share", 0.11))}


def estimate(pool, deck):
    atk = {c["id"]: c["atk"] for c in pool}
    tot = sum(deck["cards"].values())
    return sum(atk[int(i)] * w for i, w in deck["cards"].items()) / tot
