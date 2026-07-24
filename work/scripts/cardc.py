#!/usr/bin/env python3
"""The card compiler — P1.1.

One human-editable source of truth (`work/cards.json`) holding every card's
complete model, and a compiler that regenerates all four ROM structures from it:

  names         pointer table 0x440F (365 + a sentinel) -> string pool
                $6E80-$7FFF in bank 1. Strings are NOT terminated; each one's
                length is the gap to the next pointer, and 0x00 is a space.
                The pool fills the bank exactly: 4480 bytes, zero slack.
  type          0x2409E, one byte per card (21-value species/Magic enum)
  ATK / DEF     seven (ATK, DEF) table pairs in bank 9 — the base stats plus one
                pair per terrain. 365 x BCD16 LE each. Magic cards store $FFFF.
  descriptions  pointer table 0xF0060 -> variable-length records from $433A in
                bank $3C, 13139 bytes total.

Descriptions are **not** fixed 36-byte records, which is the trap this replaces:
cards 76 and 121 are 35 bytes and card 175 is 37, so from card #77 onward a
fixed-width writer lands 1-2 bytes off and corrupts its neighbours.

Correctness is enforced by a round-trip: extract from the pristine ROM, compile
straight back, and require the result to be byte-identical. `verify` does that,
so a decoding mistake anywhere shows up as a diff instead of a silent bug.

CLI:
  python cardc.py extract [--out work/cards.json]
  python cardc.py verify                 round-trip against the base ROM
  python cardc.py show <card#> [...]
  python cardc.py budget                 name/description pool usage
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as cardlib  # noqa: E402
import cardtext  # noqa: E402
import products  # noqa: E402

ROOT = cardlib.ROOT
BASE_ROM = cardlib.BASE_ROM
CARDS_JSON = products.data_path("cards.json")   # default product (p1)

NCARD = 365

# --- names: bank 1, where file offset == CPU address --------------------
NAME_PTRS = 0x440F
NAME_POOL = 0x6E80
NAME_POOL_END = 0x8000
NAME_BUDGET = NAME_POOL_END - NAME_POOL          # 4480

# --- descriptions: bank $3C ---------------------------------------------
DESC_PTRS = 0xF0060
DESC_BANK = 0xEC000
DESC_POOL_CPU = 0x433A
DESC_POOL_END_CPU = 0x768D
DESC_BUDGET = DESC_POOL_END_CPU - DESC_POOL_CPU  # 13139
DESC_LINE = 18                                   # tiles per rendered line

FORMAT = "dm1-cards/1"


def rd16(rom, o):
    return rom[o] | (rom[o + 1] << 8)


def wr16(rom, o, v):
    rom[o] = v & 0xFF
    rom[o + 1] = (v >> 8) & 0xFF


def _stat(word):
    """BCD word -> int, or None for the $FFFF that Magic cards carry."""
    return None if word == 0xFFFF else cardlib.bcd_to_int(word)


def _stat_word(value):
    return 0xFFFF if value is None else cardlib.int_to_bcd(value)


# --- extract -------------------------------------------------------------
def extract(rom):
    name_ptr = [rd16(rom, NAME_PTRS + 2 * i) for i in range(NCARD + 1)]
    desc_ptr = [rd16(rom, DESC_PTRS + 2 * i) for i in range(NCARD)]
    desc_ptr.append(DESC_POOL_END_CPU)      # no sentinel in ROM; supply the end

    out = []
    for i in range(NCARD):
        name_raw = rom[name_ptr[i]:name_ptr[i + 1]]
        d0 = DESC_BANK + desc_ptr[i]
        d1 = DESC_BANK + desc_ptr[i + 1]
        desc_raw = rom[d0:d1]

        atk = [_stat(rd16(rom, a + 2 * i)) for a, _ in cardlib.TABLES]
        deff = [_stat(rd16(rom, d + 2 * i)) for _, d in cardlib.TABLES]

        card = {
            "id": i + 1,
            "name": cardtext.decode(name_raw),
            "type": cardlib.type_name(rom[cardlib.TYPE_ARRAY + i]),
            "atk": atk[0],
            "def": deff[0],
            "field_atk": atk[1:],
            "field_def": deff[1:],
            "desc": [cardtext.decode(desc_raw[:DESC_LINE]),
                     cardtext.decode(desc_raw[DESC_LINE:])],
        }
        # Guarantee the round-trip even if some record ever fails to re-encode.
        if not cardtext.roundtrips(name_raw):
            card["name_raw"] = name_raw.hex()
        if not cardtext.roundtrips(desc_raw):
            card["desc_raw"] = desc_raw.hex()
        out.append(card)

    return {
        "_format": FORMAT,
        "_base_rom_md5": hashlib.md5(bytes(rom)).hexdigest(),
        "_budgets": {"name_pool": NAME_BUDGET, "desc_pool": DESC_BUDGET},
        "cards": out,
    }


# --- compile -------------------------------------------------------------
def _name_bytes(card):
    if "name_raw" in card:
        return bytes.fromhex(card["name_raw"])
    return cardtext.encode(card["name"])


def _desc_bytes(card):
    if "desc_raw" in card:
        return bytes.fromhex(card["desc_raw"])
    l1, l2 = (list(card["desc"]) + ["", ""])[:2]
    b1, b2 = cardtext.encode(l1), cardtext.encode(l2)
    # Line 1 is structural: it must be exactly one row, or line 2 rides up onto
    # it. Extracted records already split at DESC_LINE, so padding is a no-op
    # for unedited cards. Line 2 is the last row of the record and is left
    # alone — card 175 ships with 19 tiles there, so 18 is not a hard limit.
    if len(b1) > DESC_LINE:
        raise ValueError(f"card #{card['id']} description line 1 is {len(b1)} "
                         f"tiles, max {DESC_LINE}: {l1!r}")
    b1 += b"\x00" * (DESC_LINE - len(b1))
    return b1 + b2


def compile_into(rom, db):
    """Write every card structure into `rom` (a bytearray). Returns a summary."""
    if db.get("_format") != FORMAT:
        raise ValueError(f"unknown cards.json format {db.get('_format')!r}")
    cl = db["cards"]
    if len(cl) != NCARD:
        raise ValueError(f"expected {NCARD} cards, got {len(cl)}")

    # --- names: repack the pool, then rewrite the pointer table ---
    blobs = [_name_bytes(c) for c in cl]
    total = sum(len(b) for b in blobs)
    if total > NAME_BUDGET:
        raise ValueError(f"card names need {total} bytes, pool holds "
                         f"{NAME_BUDGET} (over by {total - NAME_BUDGET})")
    pos = NAME_POOL
    for i, b in enumerate(blobs):
        wr16(rom, NAME_PTRS + 2 * i, pos)
        rom[pos:pos + len(b)] = b
        pos += len(b)
    wr16(rom, NAME_PTRS + 2 * NCARD, pos)               # sentinel = pool end
    for o in range(pos, NAME_POOL_END):                 # 0x00 is a space
        rom[o] = 0x00

    # --- descriptions: same shape, different bank ---
    dblobs = [_desc_bytes(c) for c in cl]
    dtotal = sum(len(b) for b in dblobs)
    if dtotal > DESC_BUDGET:
        raise ValueError(f"descriptions need {dtotal} bytes, pool holds "
                         f"{DESC_BUDGET} (over by {dtotal - DESC_BUDGET})")
    cpu = DESC_POOL_CPU
    for i, b in enumerate(dblobs):
        wr16(rom, DESC_PTRS + 2 * i, cpu)
        rom[DESC_BANK + cpu:DESC_BANK + cpu + len(b)] = b
        cpu += len(b)
    for o in range(DESC_BANK + cpu, DESC_BANK + DESC_POOL_END_CPU):
        rom[o] = 0x00

    # --- type, ATK, DEF ---
    for i, c in enumerate(cl):
        rom[cardlib.TYPE_ARRAY + i] = cardlib.resolve_type(c["type"]) & 0xFF
        atk = [c["atk"]] + list(c["field_atk"])
        deff = [c["def"]] + list(c["field_def"])
        for (a, d), av, dv in zip(cardlib.TABLES, atk, deff):
            wr16(rom, a + 2 * i, _stat_word(av))
            wr16(rom, d + 2 * i, _stat_word(dv))

    return {"names": total, "name_budget": NAME_BUDGET,
            "descs": dtotal, "desc_budget": DESC_BUDGET}


def apply_config(rom, db):
    s = compile_into(rom, db)
    return s


def load_db(path=CARDS_JSON):
    return json.load(open(path, encoding="utf-8"))


# --- CLI -----------------------------------------------------------------
def main(argv):
    product, argv = products.pop_arg(argv)
    cards_json = products.data_path("cards.json", product)
    if not argv:
        print(__doc__)
        return 1
    cmd = argv[0]
    rom = bytearray(open(BASE_ROM, "rb").read())

    if cmd == "extract":
        out = cards_json
        if "--out" in argv:
            out = argv[argv.index("--out") + 1]
        db = extract(rom)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=1, ensure_ascii=False)
        raws = sum(1 for c in db["cards"] if "name_raw" in c or "desc_raw" in c)
        print(f"extracted {len(db['cards'])} cards -> {out}")
        print(f"  records needing a raw-hex fallback: {raws}")

    elif cmd == "verify":
        db = extract(rom)
        rebuilt = bytearray(open(BASE_ROM, "rb").read())
        s = compile_into(rebuilt, db)
        base = bytes(rom)
        ok = bytes(rebuilt) == base
        print(f"name pool : {s['names']:6d} / {s['name_budget']} bytes"
              f"   ({s['name_budget'] - s['names']} free)")
        print(f"desc pool : {s['descs']:6d} / {s['desc_budget']} bytes"
              f"   ({s['desc_budget'] - s['descs']} free)")
        if ok:
            print("\nROUND-TRIP OK — recompiled ROM is byte-identical to the base.")
            return 0
        diffs = [i for i in range(len(base)) if base[i] != rebuilt[i]]
        print(f"\nROUND-TRIP FAILED — {len(diffs)} byte(s) differ")
        for i in diffs[:20]:
            print(f"   0x{i:06X}: base {base[i]:02X} != rebuilt {rebuilt[i]:02X}")
        return 1

    elif cmd == "show":
        db = extract(rom)
        for num in argv[1:]:
            c = db["cards"][int(num) - 1]
            print(f"#{c['id']} {c['name']}  [{c['type']}]  {c['atk']}/{c['def']}")
            print(f"    field ATK {c['field_atk']}")
            print(f"    field DEF {c['field_def']}")
            print(f"    desc |{c['desc'][0]}|{c['desc'][1]}|")

    elif cmd == "budget":
        db = extract(rom)
        n = sum(len(_name_bytes(c)) for c in db["cards"])
        d = sum(len(_desc_bytes(c)) for c in db["cards"])
        print(f"name pool : {n:6d} / {NAME_BUDGET} bytes  ({NAME_BUDGET - n} free)")
        print(f"desc pool : {d:6d} / {DESC_BUDGET} bytes  ({DESC_BUDGET - d} free)")
        print("\nBoth pools are pointer-indexed and repacked on compile, so any")
        print("distribution of lengths is fine as long as the total fits.")

    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
