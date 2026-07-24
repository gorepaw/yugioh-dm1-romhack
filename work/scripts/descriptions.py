#!/usr/bin/env python3
"""Card description / lore text editor (Bank 0x3C) — in-place, single card.

For bulk work prefer `cardc.py`, the card compiler, which owns the whole card
model and repacks the pool. This tool exists for quick one-off edits.

Descriptions are **pointer-indexed and variable-length**, NOT fixed 36-byte
records: the table at 0xF0060 holds one CPU pointer per card into bank 0x3C, and
while most records are 36 bytes (2 lines x 18 tiles), cards 76 and 121 are 35
and card 175 is 37. Computing an offset as 0xF033A + 36*index is therefore
wrong from card #77 onward and corrupts the neighbouring record.

Editing here is in-place, so a replacement must encode to exactly the record's
existing length; anything else needs the compiler, which repacks and re-points.

Ligature squashes (il, li, ll, l!, 's, 't = one tile) are applied automatically,
so a line can hold a bit more than 18 literal characters.

CLI:
  python descriptions.py show <card#> [...]
  python descriptions.py set <card#> "line 1 (<=18)" "line 2 (<=18)"
  python descriptions.py edits
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import text_tool  # noqa: E402
import cards  # noqa: E402

ROOT = cards.ROOT
BASE_ROM = cards.BASE_ROM
TBL = os.path.join(ROOT, "reference", "DM1Translation", "Insertion", "text.tbl")
import products  # noqa: E402
DESC_EDITS = products.data_path("desc_edits.json")   # default product (p1)

LINE = 18
LIGATURES = {"il": 0x4E, "li": 0x4F, "ll": 0x50, "l!": 0x51, "'s": 0x52, "'t": 0x53}


def _table():
    return text_tool.load_table(TBL)


def desc_span(rom, index):
    """(file_offset, length) of a card's record, read from the pointer table."""
    import cardc
    lo = cardc.rd16(rom, cardc.DESC_PTRS + 2 * index)
    hi = (cardc.rd16(rom, cardc.DESC_PTRS + 2 * (index + 1))
          if index + 1 < cardc.NCARD else cardc.DESC_POOL_END_CPU)
    return cardc.DESC_BANK + lo, hi - lo


def decode_desc(rom, index):
    tbl = _table()
    off, ln = desc_span(rom, index)
    return (text_tool.decode(rom[off:off + LINE], tbl),
            text_tool.decode(rom[off + LINE:off + ln], tbl))


def encode_line(s, single):
    tiles, i = [], 0
    while i < len(s):
        if s[i:i + 2] in LIGATURES:
            tiles.append(LIGATURES[s[i:i + 2]])
            i += 2
        elif s[i] in single:
            tiles.append(single[s[i]])
            i += 1
        else:
            raise ValueError(f"character {s[i]!r} is not in the text table")
    if len(tiles) > LINE:
        raise ValueError(f"line encodes to {len(tiles)} tiles (max {LINE}): {s!r}")
    return bytes(tiles + [0x00] * (LINE - len(tiles)))


def encode_desc(line1, line2):
    single = text_tool.reverse_single(_table())
    return encode_line(line1, single) + encode_line(line2, single)


def apply_desc(rom, index, line1, line2):
    """In-place, so the new text must occupy the record's exact byte length."""
    off, ln = desc_span(rom, index)
    new = encode_desc(line1, line2)
    if len(new) != ln:
        raise ValueError(
            f"card #{index + 1}'s description record is {ln} bytes but the "
            f"replacement encodes to {len(new)}. In-place edits cannot resize a "
            f"record — use cardc.py (the compiler), which repacks the pool.")
    rom[off:off + ln] = new
    return f'"{line1.strip()}" / "{line2.strip()}"'


def load_edits():
    return json.load(open(DESC_EDITS)) if os.path.exists(DESC_EDITS) else []


def save_edits(e):
    os.makedirs(os.path.dirname(DESC_EDITS), exist_ok=True)
    json.dump(e, open(DESC_EDITS, "w"), indent=2)


def main(argv):
    global DESC_EDITS
    product, argv = products.pop_arg(argv)
    DESC_EDITS = products.data_path("desc_edits.json", product)
    if not argv:
        print(__doc__)
        return 1
    cmd = argv[0]
    rom = bytearray(open(BASE_ROM, "rb").read())
    names = cards.load_names()

    if cmd == "show":
        for num in argv[1:]:
            i = int(num) - 1
            l1, l2 = decode_desc(rom, i)
            print(f"#{i + 1} {names.get(i, '?')}")
            print(f"   line1: |{l1}|")
            print(f"   line2: |{l2}|")

    elif cmd == "set":
        num = int(argv[1])
        line1 = argv[2] if len(argv) > 2 else ""
        line2 = argv[3] if len(argv) > 3 else ""
        apply_desc(bytearray(rom), num - 1, line1, line2)   # validate on scratch
        edits = [e for e in load_edits() if e["card"] != num]
        edits.append({"card": num, "name": names.get(num - 1, "?"),
                      "line1": line1, "line2": line2})
        edits.sort(key=lambda e: e["card"])
        save_edits(edits)
        print(f'queued desc #{num} {names.get(num - 1, "?")}: "{line1}" / "{line2}"')

    elif cmd == "edits":
        for e in load_edits():
            print(f'  #{e["card"]:3d} {e.get("name", ""):18s} '
                  f'"{e["line1"]}" / "{e["line2"]}"')
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
