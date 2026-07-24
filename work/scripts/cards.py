#!/usr/bin/env python3
"""Card stats library + CLI for Yu-Gi-Oh! Duel Monsters (GB), English build.

Card database (Bank 9), all indexed by card id (= card number - 1):
  - TYPE:  1 byte/card at 0x2409E (species / Magic category)
  - ATK:   BCD LE word/card, base table 0x24381 (+ 6 terrain tables)
  - DEF:   BCD LE word/card, base table 0x2465D (+ 6 terrain tables)
See docs/NOTES.md.

CLI:
  python cards.py show <card#> [...]                        decode a card
  python cards.py find "<text>"                             find cards by name
  python cards.py set <card#> [--atk N] [--def N] [--type T]  queue a change
  python cards.py edits                                     list queued changes
  python cards.py types                                     list the type enum

'set' records desired values in work/card_edits.json; build.py applies them to a
fresh copy of the base ROM, propagating ATK/DEF through the terrain tables so
field bonuses stay consistent.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE_ROM = os.path.join(ROOT, "roms", "dm1-english.gb")
CARDNAMES = os.path.join(ROOT, "reference", "DM1Translation",
                         "Insertion", "script", "cardname.txt")
import products  # noqa: E402
CARD_EDITS = products.data_path("card_edits.json")   # default product (p1)

NCARD = 365      # index 365 in the name pointer table is the end sentinel
# (ATK array addr, DEF array addr); index 0 is the base (no-field) table.
TABLES = [
    (0x24381, 0x2465D),   # base
    (0x24939, 0x24C15),   # terrain 1
    (0x24EF1, 0x251CD),   # terrain 2
    (0x254A9, 0x25785),   # terrain 3
    (0x25A61, 0x25D3D),   # terrain 4
    (0x26019, 0x262F5),   # terrain 5
    (0x265D1, 0x268AD),   # terrain 6
]
BASE_ATK, BASE_DEF = TABLES[0]

TYPE_ARRAY = 0x2409E      # 1 byte/card: species, or Magic category
TYPE_NAMES = {
    0x00: "Dragon", 0x01: "Spellcaster", 0x02: "Zombie", 0x03: "Warrior",
    0x04: "Beast-Warrior", 0x05: "Beast", 0x06: "Winged Beast", 0x07: "Fiend",
    0x08: "Fairy", 0x09: "Insect", 0x0A: "Dinosaur", 0x0B: "Reptile",
    0x0C: "Fish", 0x0D: "Sea Serpent", 0x0E: "Machine", 0x0F: "Thunder",
    0x10: "Aqua", 0x11: "Pyro", 0x12: "Rock", 0x13: "Plant", 0x14: "Magic",
}
NAME_TO_TYPE = {v.lower(): k for k, v in TYPE_NAMES.items()}


# --- BCD helpers ---------------------------------------------------------
def bcd_to_int(word):
    d = [(word >> 12) & 0xF, (word >> 8) & 0xF, (word >> 4) & 0xF, word & 0xF]
    if any(x > 9 for x in d):
        return None
    return d[0] * 1000 + d[1] * 100 + d[2] * 10 + d[3]


def int_to_bcd(n):
    n = max(0, min(9999, int(n)))
    return int(f"{n:04d}", 16)


def rd(rom, addr):
    return rom[addr] | (rom[addr + 1] << 8)


def wr(rom, addr, word):
    rom[addr] = word & 0xFF
    rom[addr + 1] = (word >> 8) & 0xFF


def type_name(b):
    return TYPE_NAMES.get(b, f"?0x{b:02X}")


# --- names ---------------------------------------------------------------
NAME_PTRS = 0x440F     # bank 1; file offset == CPU address in this bank


def load_names(rom=None):
    """{card_index: name}, read from the ROM itself.

    Names live in a pointer-indexed pool at $6E80-$7FFF with no terminators —
    each string runs to the next pointer, and 0x00 is a space. Index 365 is the
    end sentinel. Reading the ROM rather than Darrman's script file keeps this
    working on any build we produce, including one with renamed cards.
    """
    import cardtext
    if rom is None:
        rom = open(BASE_ROM, "rb").read()
    ptr = [rd(rom, NAME_PTRS + 2 * i) for i in range(NCARD + 1)]
    return {i: cardtext.decode(rom[ptr[i]:ptr[i + 1]]) for i in range(NCARD)}


# --- read / edit ---------------------------------------------------------
def card_stats(rom, index):
    return {
        "type": rom[TYPE_ARRAY + index],
        "base_atk": bcd_to_int(rd(rom, BASE_ATK + 2 * index)),
        "base_def": bcd_to_int(rd(rom, BASE_DEF + 2 * index)),
        "atk_by_table": [bcd_to_int(rd(rom, a + 2 * index)) for a, _ in TABLES],
        "def_by_table": [bcd_to_int(rd(rom, d + 2 * index)) for _, d in TABLES],
    }


def apply_card_stat(rom, index, atk=None, deff=None, ctype=None):
    """Set ATK/DEF/type for a card. Mutates rom (bytearray). Returns a summary.

    ATK/DEF propagate to terrain tables by each table's per-card ratio so field
    bonuses stay proportional. Raises ValueError on a non-monster ATK/DEF edit."""
    ob_atk = bcd_to_int(rd(rom, BASE_ATK + 2 * index))
    ob_def = bcd_to_int(rd(rom, BASE_DEF + 2 * index))
    if atk is not None and ob_atk is None:
        raise ValueError(f"card #{index + 1} has no ATK (non-monster) - refusing")
    if deff is not None and ob_def is None:
        raise ValueError(f"card #{index + 1} has no DEF (non-monster) - refusing")

    changes = []
    if atk is not None:
        for a, _ in TABLES:
            orig = bcd_to_int(rd(rom, a + 2 * index))
            if orig is None:
                continue
            new = atk if a == BASE_ATK else round(atk * orig / ob_atk) if ob_atk else atk
            wr(rom, a + 2 * index, int_to_bcd(new))
        changes.append(f"ATK {ob_atk}->{atk}")
    if deff is not None:
        for _, d in TABLES:
            orig = bcd_to_int(rd(rom, d + 2 * index))
            if orig is None:
                continue
            new = deff if d == BASE_DEF else round(deff * orig / ob_def) if ob_def else deff
            wr(rom, d + 2 * index, int_to_bcd(new))
        changes.append(f"DEF {ob_def}->{deff}")
    if ctype is not None:
        old = rom[TYPE_ARRAY + index]
        rom[TYPE_ARRAY + index] = ctype & 0xFF
        changes.append(f"type {type_name(old)}->{type_name(ctype)}")
    return ", ".join(changes)


def resolve_type(tok):
    """Accept a type name ('Dragon') or a byte ('0' / '0x00')."""
    if tok.lower() in NAME_TO_TYPE:
        return NAME_TO_TYPE[tok.lower()]
    return int(tok, 0)


def load_edits():
    return json.load(open(CARD_EDITS)) if os.path.exists(CARD_EDITS) else []


def save_edits(edits):
    os.makedirs(os.path.dirname(CARD_EDITS), exist_ok=True)
    json.dump(edits, open(CARD_EDITS, "w"), indent=2)


# --- CLI -----------------------------------------------------------------
def main(argv):
    global CARD_EDITS
    product, argv = products.pop_arg(argv)
    CARD_EDITS = products.data_path("card_edits.json", product)
    if not argv:
        print(__doc__)
        return 1
    cmd = argv[0]

    if cmd == "types":
        for b in sorted(TYPE_NAMES):
            print(f"  0x{b:02X}  {TYPE_NAMES[b]}")
        return 0

    rom = bytearray(open(BASE_ROM, "rb").read())
    names = load_names()

    if cmd == "show":
        for num in argv[1:]:
            i = int(num) - 1
            s = card_stats(rom, i)
            print(f"#{i + 1} {names.get(i, '?')}  [{type_name(s['type'])}]  "
                  f"base {s['base_atk']}/{s['base_def']}")
            print(f"    ATK by table: {s['atk_by_table']}")
            print(f"    DEF by table: {s['def_by_table']}")

    elif cmd == "find":
        needle = argv[1].lower()
        for i in range(NCARD):
            nm = names.get(i)
            if nm and needle in nm.lower():
                s = card_stats(rom, i)
                print(f"#{i + 1:3d} {nm:20s} {type_name(s['type']):13s} "
                      f"{s['base_atk']}/{s['base_def']}")

    elif cmd == "set":
        num = int(argv[1])
        atk = deff = ctype = None
        j = 2
        while j < len(argv):
            if argv[j] == "--atk":
                atk = int(argv[j + 1]); j += 2
            elif argv[j] == "--def":
                deff = int(argv[j + 1]); j += 2
            elif argv[j] == "--type":
                ctype = resolve_type(argv[j + 1]); j += 2
            else:
                j += 1
        summary = apply_card_stat(bytearray(rom), num - 1, atk, deff, ctype)
        edits = [e for e in load_edits() if e["card"] != num]
        entry = {"card": num, "name": names.get(num - 1, "?")}
        if atk is not None:
            entry["atk"] = atk
        if deff is not None:
            entry["def"] = deff
        if ctype is not None:
            entry["type"] = ctype
            entry["type_name"] = type_name(ctype)
        edits.append(entry)
        edits.sort(key=lambda e: e["card"])
        save_edits(edits)
        print(f"queued #{num} {names.get(num - 1, '?')}: {summary}")
        print(f"({len(edits)} card edit(s) queued in work/card_edits.json)")

    elif cmd == "edits":
        for e in load_edits():
            print(f"  #{e['card']:3d} {e.get('name', ''):20s} "
                  f"ATK={e.get('atk', '-')} DEF={e.get('def', '-')} "
                  f"type={e.get('type_name', '-')}")

    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
