#!/usr/bin/env python3
"""Equip eligibility lists (bank 9) — which monsters each equip may attach to.

Engine facts (full decode in docs/NOTES.md, "Equip combine system"): there are
26 equips (verbs $15-$2E). A pointer table at $6BC8 holds 26 x 16-bit CPU
addresses; each points at a list of 16-bit **monster indices (card number - 1)**
terminated by $FFFF. The combine routine walks the list and applies the equip
only if the equipped monster's index is present (comparator $1D00, a plain
16-bit equality). So "who can I attach to" is an explicit id list — there is no
runtime "any type/color" rule, exactly like the fusion recipe table.

The lists are packed contiguously, in equip-index order, in a **fixed pool**
$6BFC..$764E = 2642 bytes; a 12-byte $FF gap then graphics follow, so the pool
cannot grow in place. This tool repacks the pool and refuses to compile a set
that overflows the budget (same discipline as the name/description pools).

    python equips.py extract [--product p2]     -> work/<product>/equips.json
    python equips.py show                        list every equip + its targets
    python equips.py verify                      round-trip against the base ROM
    python equips.py budget [--product p2]       pool usage of a product's equips.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as cardlib  # noqa: E402
import products          # noqa: E402

BASE_ROM = cardlib.BASE_ROM

BANK9 = 0x24000                       # bank 9 file base (CPU $4000)
PTRS_CPU = 0x6BC8                     # pointer table (26 x 16-bit CPU addr)
NEQUIP = 26
POOL_CPU = 0x6BFC                     # first list
POOL_END_CPU = 0x764E                 # one past the last list ($FF gap follows)
BUDGET = POOL_END_CPU - POOL_CPU      # 2642 bytes, hard
TERM = 0xFFFF                         # list terminator

TABLE_B = 0x00EF62                    # spells: card index -> verb; equips are $15-$2E
FORMAT = "dm1-equips/1"


def f(cpu):
    return BANK9 + (cpu - 0x4000)


def rd16(rom, o):
    return rom[o] | (rom[o + 1] << 8)


def wr16(rom, o, v):
    rom[o] = v & 0xFF
    rom[o + 1] = (v >> 8) & 0xFF


def _index_to_card(rom):
    """equip index (0..25) -> card number, via table B (verb $15+i)."""
    m = {}
    for i in range(300, cardlib.NCARD if hasattr(cardlib, "NCARD") else 365):
        v = rom[TABLE_B + i]
        if 0x15 <= v <= 0x2E:
            m[v - 0x15] = i + 1
    return m


def extract(rom):
    names = cardlib.load_names(rom)
    idx2card = _index_to_card(rom)
    ptrs = [rd16(rom, f(PTRS_CPU) + 2 * i) for i in range(NEQUIP)]
    equips = []
    for i, p in enumerate(ptrs):
        off = f(p)
        ids = []
        while rd16(rom, off) != TERM:
            ids.append(rd16(rom, off))
            off += 2
        card = idx2card.get(i)
        equips.append({
            "index": i,
            "verb": 0x15 + i,
            "card": card,
            "name": names.get(card - 1) if card else None,
            # store as human 1-based card numbers; the ROM holds number-1
            "targets": [v + 1 for v in ids],
        })
    return {"_format": FORMAT, "equips": equips}


def _list_bytes(equip):
    b = bytearray()
    for n in equip["targets"]:
        v = n - 1                                     # 1-based number -> ROM index
        b += bytes([v & 0xFF, (v >> 8) & 0xFF])
    b += bytes([TERM & 0xFF, TERM >> 8])
    return bytes(b)


def compile_into(rom, db):
    if db.get("_format") != FORMAT:
        raise ValueError(f"unknown equips.json format {db.get('_format')!r}")
    equips = sorted(db["equips"], key=lambda e: e["index"])
    if len(equips) != NEQUIP:
        raise ValueError(f"expected {NEQUIP} equips, got {len(equips)}")

    blobs = [_list_bytes(e) for e in equips]
    total = sum(len(b) for b in blobs)
    if total > BUDGET:
        raise ValueError(f"equip lists need {total} bytes, pool holds {BUDGET} "
                         f"(over by {total - BUDGET}). Narrow some eligibility "
                         f"(fewer colors / smaller sets).")
    cpu = POOL_CPU
    for i, b in enumerate(blobs):
        wr16(rom, f(PTRS_CPU) + 2 * i, cpu)
        rom[f(cpu):f(cpu) + len(b)] = b
        cpu += len(b)
    for o in range(f(cpu), f(POOL_END_CPU)):          # pad any freed tail
        rom[o] = 0xFF
    return {"equips": len(equips), "bytes": total, "budget": BUDGET}


def apply_config(rom, cfg):
    return compile_into(rom, cfg)["equips"]


def load_db(path):
    return json.load(open(path, encoding="utf-8"))


def main(argv):
    product, argv = products.pop_arg(argv)
    if not argv:
        print(__doc__)
        return 1
    cmd = argv[0]
    rom = bytearray(open(BASE_ROM, "rb").read())

    if cmd == "extract":
        out = products.data_path("equips.json", product)
        db = extract(rom)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(db, fh, indent=1, ensure_ascii=False)
        tot = sum(2 * (len(e["targets"]) + 1) for e in db["equips"])
        print(f"extracted {len(db['equips'])} equips -> {out}")
        print(f"  pool: {tot}/{BUDGET} bytes ({BUDGET - tot} free)")

    elif cmd == "show":
        db = extract(rom)
        for e in db["equips"]:
            t = e["targets"]
            preview = ", ".join(str(x) for x in t[:10]) + (" ..." if len(t) > 10 else "")
            print(f"idx {e['index']:2d} verb 0x{e['verb']:02X}  "
                  f"#{e['card']} {e['name']:20}  {len(t):3d} targets: {preview}")

    elif cmd == "verify":
        base = bytes(rom)
        rebuilt = bytearray(base)
        s = compile_into(rebuilt, extract(bytearray(base)))
        ok = bytes(rebuilt) == base
        print(f"pool: {s['bytes']}/{s['budget']} bytes ({s['budget']-s['bytes']} free)")
        if ok:
            print("ROUND-TRIP OK - recompiled equip pool is byte-identical to base.")
            return 0
        diffs = [i for i in range(len(base)) if base[i] != rebuilt[i]]
        print(f"ROUND-TRIP FAILED - {len(diffs)} byte(s) differ")
        for i in diffs[:16]:
            print(f"   0x{i:06X}: base {base[i]:02X} != rebuilt {rebuilt[i]:02X}")
        return 1

    elif cmd == "budget":
        path = products.data_path("equips.json", product)
        if not os.path.exists(path):
            print(f"no equips.json for {product} (run: equips.py extract --product {product})")
            return 1
        db = load_db(path)
        tot = sum(2 * (len(e["targets"]) + 1) for e in db["equips"])
        print(f"equip pool: {tot}/{BUDGET} bytes ({BUDGET - tot} free)")

    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
