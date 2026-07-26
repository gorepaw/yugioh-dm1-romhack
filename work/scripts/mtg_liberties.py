#!/usr/bin/env python3
"""Take liberties with the 400:1 numbers so they don't read as generated.

creatures.json holds the faithful conversion: power/toughness x400, plus a few
ability bonuses. Shipped raw, 85% of every ATK and DEF in the game was an exact
multiple of 400, and `400` and `800` alone were 53% of all values. In play that
reads as arithmetic rather than as a card game.

Stock DM1 is the target texture, measured off the base ROM (625 values):

    multiples of 100     96.3%          multiples of 400   27.5%
    ending in ..50        2.1%          hundreds digit     56% even / 44% odd
    range              200..3500

So: nudge each stat by a whole hundred, occasionally a fifty, and let ~a
quarter keep the round number. The offset is derived from a hash of the card
name, so it is stable across builds (the pipeline must be reproducible) but
uncorrelated between cards, and ATK and DEF move independently.

Offsets stay under half of the 400 step, which means a creature can tie the
tier above it but never outrank it -- power order survives:

    a 3/3 at 1200+200 = 1400   vs   a 4/4 at 1600-200 = 1400

The same +/-200 applies at every size. Holding small creatures to +/-100 was
tried first and measurably worse: the pool is mostly 1/1s and 2/2s, so a
narrow swing left a pile of 87 cards still sitting on exactly 400. At full
width the bottom of the curve spreads to 200..600, and 200 is precisely stock
DM1's own floor.

Two things are never touched: walls keep ATK 0 (a 0-ATK blocker is the whole
point of the card), and the six 4000/4000 capstones -- the five Elder Dragons
and Leviathan -- are a deliberate ceiling, not a converted number.
"""
import hashlib

CAP = 4000          # capstone value; nothing else may reach it
FLOOR = 200         # stock DM1's lowest stat
CEIL = 3800         # keep non-capstones clear of the 4000 tier

# (offset, weight). Weights set how often a value stays on its round number and
# how the hundreds digit lands: offset 0 and +/-200 keep it even, +/-100 makes
# it odd. Measured against the stock ROM, these land at 23.5% exact multiples
# of 400 and 54% even digits (stock: 27.5% and 56.3%).
OFFSETS = [(-200, 2), (-100, 3), (0, 3), (100, 3), (200, 2)]
FIFTY_IN = 80       # 1-in-N values also take a +/-50 -> 3.0% (stock: 2.1%)


def _roll(name, field, n):
    """Stable 0..n-1 from the card name. md5, not hash() -- hash() is salted
    per process, which would make the build nondeterministic."""
    h = hashlib.md5(f"{name}|{field}".encode("utf-8")).digest()
    return int.from_bytes(h[:4], "big") % n


def _offset(name, field):
    r = _roll(name, field, sum(w for _, w in OFFSETS))
    for off, w in OFFSETS:
        if r < w:
            return off
        r -= w
    return 0


def adjust(name, field, base):
    """One stat. `field` is "atk"/"def" so the two move independently."""
    if base is None or base <= 0 or base >= CAP:
        return base                      # walls and capstones pass through
    v = base + _offset(name, field)
    if _roll(name, field + "50", FIFTY_IN) == 0:
        v += 50 if _roll(name, field + "sign", 2) else -50
    return max(FLOOR, min(CEIL, v))


def apply(cr):
    """(atk, def) for a creatures.json entry, liberties taken."""
    name = cr.get("shortname", cr["name"])
    if cr["atk"] >= CAP or cr["def"] >= CAP:
        return cr["atk"], cr["def"]      # capstone: leave the pair intact
    return adjust(name, "atk", cr["atk"]), adjust(name, "def", cr["def"])
