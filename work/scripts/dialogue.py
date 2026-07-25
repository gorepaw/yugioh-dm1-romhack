#!/usr/bin/env python3
"""Opponent intro dialogue (bank 15) — the "I am X, beat me 5 times" speeches.

Block at **0x3C17F**, **17 `[Exit]`(0xB4)-terminated strings**, 1384 bytes
(0x3C17F..0x3C6E7), one per duelist plus a short label. There is **no pointer
table** — strings are found by scanning forward counting terminators — and the
per-opponent *battle taunts* follow immediately at 0x3C6E7. So a rewrite must
keep exactly 17 strings AND occupy exactly 1384 bytes; short text is padded with
spaces inside the last string, never with extra terminators (which would insert
empty strings and shift every later block).

> **Dialogue order is NOT duelist-slot order.** The block runs Weevil, Mai, Rex,
> Mako, **YamiYugi**, Yugi, Joey, Kaiba, Mokuba, Tristan, Bakura, Puppeteer,
> PaniK, Keith, Pegasus, + one short trailing string. Slot 13 (Simon) has no
> entry here. `DIALOGUE_TO_SLOT` records the mapping.

Renaming a duelist in the 8-byte name table at `0x5457` does **not** touch this
text — the record page and the HUD read the name table, the intros read this
block, so both must be edited.

Authoring: work/<product>/dialogue_config.json = {"dialogues": [16 strings]}.
Applied by build.py.

CLI:
  python dialogue.py show                  the current 16 strings
  python dialogue.py budget [--product duelmonsters-mtg] config size vs the 1294-byte block
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as cardlib  # noqa: E402
import cardtext          # noqa: E402
import products          # noqa: E402

BLOCK = 0x3C17F
NSTR = 17
BUDGET = 1384      # 0x3C17F..0x3C6E7 — 17 strings, ends right before the taunts
TERM = 0xB4

# Second block: the in-duel lines. 48 strings = THREE groups of 16, each in the
# same opponent order as the intros: pre-duel taunt, opponent-victory,
# opponent-defeat. Same rules — no pointer table, exact byte length required.
BATTLE = 0x3C6E7
NBATTLE = 48
BATTLE_BUDGET = 0x3D209 - 0x3C6E7      # 2850

# taunt index -> duelist slot (same order as the intros, minus the short label)
BATTLE_TO_SLOT = [0, 1, 2, 3, 15, 9, 11, 4, 5, 10, 12, 6, 7, 8, 14, 13]

# dialogue index -> duelist slot (stock roster), for reference when writing text
DIALOGUE_TO_SLOT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 15, 5: 9, 6: 11, 7: 4, 8: 5,
                    9: 10, 10: 12, 11: 6, 12: 7, 13: 8, 14: 14, 15: None, 16: 13}


def _write_block(rom, texts, base, nstr, budget, what):
    if len(texts) != nstr:
        raise ValueError(f"{what}: expected {nstr} strings, got {len(texts)}")
    blobs = [cardtext.encode(t) + bytes([TERM]) for t in texts]
    total = sum(len(x) for x in blobs)
    if total > budget:
        raise ValueError(f"{what} needs {total} bytes, block holds {budget} "
                         f"(over by {total - budget}). Shorten some lines.")
    # Pad INSIDE the last string, and specifically before its final [Page] so the
    # filler is trailing whitespace on a page the player already sees. Putting it
    # after [Page] would render an extra, blank text box.
    SPACE, PAGE = 0x00, 0xB1
    pad = bytes([SPACE]) * (budget - total)
    last = blobs[-1][:-1]                       # drop the terminator
    cut = last.rfind(bytes([PAGE]))
    last = (last[:cut] + pad + last[cut:]) if cut >= 0 else (last + pad)
    blobs[-1] = last + bytes([TERM])
    o = base
    for x in blobs:
        rom[o:o + len(x)] = x
        o += len(x)
    assert o == base + budget, (o, base + budget)
    return len(blobs)


def read_battle(rom):
    out, o = [], BATTLE
    for _ in range(NBATTLE):
        e = o
        while rom[e] != TERM:
            e += 1
        out.append(bytes(rom[o:e]))
        o = e + 1
    return out


def read_all(rom):
    out, o = [], BLOCK
    for _ in range(NSTR):
        e = o
        while rom[e] != TERM:
            e += 1
        out.append(bytes(rom[o:e]))
        o = e + 1
    return out


def apply_config(rom, cfg):
    """Rewrite the intro block and (optionally) the 48 in-duel lines.

    Both blocks are located by counting terminators and are immediately followed
    by more text, so each must occupy EXACTLY its original byte count: short text
    is padded with spaces inside the last string, never with extra terminators."""
    n = _write_block(rom, cfg.get("dialogues") or [], BLOCK, NSTR, BUDGET, "intros")
    battle = cfg.get("battle")
    if battle:
        n += _write_block(rom, battle, BATTLE, NBATTLE, BATTLE_BUDGET, "battle lines")
    return n


def main(argv):
    product, argv = products.pop_arg(argv)
    if not argv:
        print(__doc__)
        return 1
    cmd = argv[0]
    rom = bytearray(open(cardlib.BASE_ROM, "rb").read())

    if cmd == "show":
        for i, s in enumerate(read_all(rom)):
            slot = DIALOGUE_TO_SLOT.get(i)
            print(f"  [{i:2}] slot {slot}  ({len(s)+1:3}B) {cardtext.decode(s)[:70]!r}")

    elif cmd == "budget":
        p = products.data_path("dialogue_config.json", product)
        if not os.path.exists(p):
            print(f"no dialogue_config.json for {product}")
            return 1
        try:
            n = apply_config(bytearray(rom), json.load(open(p, encoding="utf-8")))
            cfg = json.load(open(p, encoding="utf-8"))
            tot = sum(len(cardtext.encode(t)) + 1 for t in cfg["dialogues"])
            print(f"OK: {n} strings, {tot}/{BUDGET} bytes ({BUDGET-tot} free)")
        except ValueError as e:
            print("FAIL:", e)
            return 1
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
