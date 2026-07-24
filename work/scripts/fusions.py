#!/usr/bin/env python3
"""Fusion recipe table (bank $3B) — decoded.

Fusion is three PARALLEL arrays of 2159 16-bit entries, not a grouped or
variable-length structure:

    material A   $4155   file 0x0EC155
    material B   $5233   file 0x0ED233
    result       $6311   file 0x0EE311   (ends 0x0EF3EF)

Recipe i is `A[i] + B[i] -> result[i]`, and all three hold **0-based card
indices** (card number - 1). $016D = 365 is the "empty slot" sentinel and never
appears in the tables themselves. Observed id range is 1..299, i.e. only
monsters (#2..#300) — Magic cards start at #301 and never fuse.

How the game resolves a fusion (`$4091`):
  - the two chosen cards live in RAM at $CECB/$CECC and $CECD/$CECE; the result
    is written to $CECF/$CED0, and the routine returns 0 on success, 1 on none
  - `$40E2` LINEAR-SCANS material A for a match, and on each hit calls `$411F`
    to check material B at the same index; first match wins
  - if that fails the pair is swapped (`$4070`) and scanned again, so recipes
    are order-insensitive even though each is stored in one direction only

> The entry count 2159 is hardcoded as the immediate $086E in three places —
> $40E4, $4112 and $4122. The table size is therefore fixed unless all three are
> patched; to retire a recipe, point it at an unreachable pair rather than
> shortening the array.

CLI:
  python fusions.py extract [--out work/fusions.json]
  python fusions.py verify                 round-trip against the base ROM
  python fusions.py list [start] [count]
  python fusions.py find "<card name>"     every recipe using or making it
  python fusions.py stats
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as cardlib  # noqa: E402

ROOT = cardlib.ROOT
BASE_ROM = cardlib.BASE_ROM
FUSIONS_JSON = os.path.join(ROOT, "work", "fusions.json")

TAB_A = 0x0EC155
TAB_B = 0x0ED233
TAB_R = 0x0EE311
NFUSION = 2159
SENTINEL = 365           # $016D — "no card"

FORMAT = "dm1-fusions/1"


def rd16(rom, o):
    return rom[o] | (rom[o + 1] << 8)


def wr16(rom, o, v):
    rom[o] = v & 0xFF
    rom[o + 1] = (v >> 8) & 0xFF


def extract(rom):
    """Recipes as 1-based card NUMBERS, matching every other tool here."""
    out = []
    for i in range(NFUSION):
        out.append({
            "i": i,
            "a": rd16(rom, TAB_A + 2 * i) + 1,
            "b": rd16(rom, TAB_B + 2 * i) + 1,
            "result": rd16(rom, TAB_R + 2 * i) + 1,
        })
    return {"_format": FORMAT, "_count": NFUSION, "recipes": out}


def compile_into(rom, db):
    if db.get("_format") != FORMAT:
        raise ValueError(f"unknown fusions.json format {db.get('_format')!r}")
    rec = db["recipes"]
    if len(rec) != NFUSION:
        raise ValueError(
            f"expected exactly {NFUSION} recipes, got {len(rec)}. The count is "
            "hardcoded in three places in bank $3B; to disable a recipe give it "
            "an unreachable material pair instead of deleting the row.")
    for i, r in enumerate(rec):
        for key, tab in (("a", TAB_A), ("b", TAB_B), ("result", TAB_R)):
            v = int(r[key]) - 1
            if not 0 <= v <= SENTINEL:
                raise ValueError(f"recipe {i} {key}={r[key]} is out of range")
            wr16(rom, tab + 2 * i, v)
    return len(rec)


def apply_config(rom, db):
    return compile_into(rom, db)


def load_db(path=FUSIONS_JSON):
    return json.load(open(path, encoding="utf-8"))


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    cmd = argv[0]
    rom = bytearray(open(BASE_ROM, "rb").read())
    names = cardlib.load_names(rom)

    def nm(num):
        return names.get(num - 1, f"<#{num}>")

    if cmd == "extract":
        out = FUSIONS_JSON
        if "--out" in argv:
            out = argv[argv.index("--out") + 1]
        db = extract(rom)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=1, ensure_ascii=False)
        print(f"extracted {db['_count']} fusion recipes -> {out}")

    elif cmd == "verify":
        db = extract(rom)
        rebuilt = bytearray(open(BASE_ROM, "rb").read())
        compile_into(rebuilt, db)
        if bytes(rebuilt) == bytes(rom):
            print(f"ROUND-TRIP OK — {NFUSION} recipes recompile byte-identically.")
            return 0
        diffs = [i for i in range(len(rom)) if rom[i] != rebuilt[i]]
        print(f"ROUND-TRIP FAILED — {len(diffs)} byte(s) differ")
        return 1

    elif cmd == "list":
        start = int(argv[1]) if len(argv) > 1 else 0
        count = int(argv[2]) if len(argv) > 2 else 20
        for r in extract(rom)["recipes"][start:start + count]:
            print(f"  [{r['i']:4d}] {nm(r['a']):20s} + {nm(r['b']):20s} "
                  f"-> {nm(r['result'])}")

    elif cmd == "find":
        needle = argv[1].lower()
        hits = 0
        for r in extract(rom)["recipes"]:
            line = (f"  [{r['i']:4d}] {nm(r['a']):20s} + {nm(r['b']):20s} "
                    f"-> {nm(r['result'])}")
            if any(needle in nm(r[k]).lower() for k in ("a", "b", "result")):
                print(line)
                hits += 1
        print(f"  ({hits} recipe(s))")

    elif cmd == "stats":
        rec = extract(rom)["recipes"]
        pairs = {(r["a"], r["b"]) for r in rec}
        results = {r["result"] for r in rec}
        mats = {r["a"] for r in rec} | {r["b"] for r in rec}
        print(f"recipes            : {len(rec)}")
        print(f"distinct pairs     : {len(pairs)}"
              f"   ({len(rec) - len(pairs)} duplicate row(s))")
        print(f"distinct results   : {len(results)}")
        print(f"distinct materials : {len(mats)}")
        from collections import Counter
        top = Counter(r["result"] for r in rec).most_common(5)
        print("most-produced results:")
        for cid, n in top:
            print(f"    {nm(cid):20s} {n:4d} recipe(s)")

    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
