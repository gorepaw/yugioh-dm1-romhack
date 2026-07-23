#!/usr/bin/env python3
"""Card description / lore text editor (Bank 0x3C).

Descriptions are FIXED 36-byte records: 2 lines of 18 tiles, laid consecutively
from ROM 0xF033A. Card index = card number - 1. Editing is in-place and safe
(no pointer/relocation work): each line is encoded and space-padded to 18 tiles.

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
DESC_EDITS = os.path.join(ROOT, "work", "desc_edits.json")

DESC_BASE = 0xF033A
DESC_LEN = 36
LINE = 18
LIGATURES = {"il": 0x4E, "li": 0x4F, "ll": 0x50, "l!": 0x51, "'s": 0x52, "'t": 0x53}


def _table():
    return text_tool.load_table(TBL)


def decode_desc(rom, index):
    tbl = _table()
    off = DESC_BASE + DESC_LEN * index
    return (text_tool.decode(rom[off:off + LINE], tbl),
            text_tool.decode(rom[off + LINE:off + DESC_LEN], tbl))


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
    off = DESC_BASE + DESC_LEN * index
    rom[off:off + DESC_LEN] = encode_desc(line1, line2)
    return f'"{line1.strip()}" / "{line2.strip()}"'


def load_edits():
    return json.load(open(DESC_EDITS)) if os.path.exists(DESC_EDITS) else []


def save_edits(e):
    os.makedirs(os.path.dirname(DESC_EDITS), exist_ok=True)
    json.dump(e, open(DESC_EDITS, "w"), indent=2)


def main(argv):
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
