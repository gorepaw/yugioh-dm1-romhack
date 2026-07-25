#!/usr/bin/env python3
"""Duel-message editor (bank 5) — what a spell says when it resolves.

The message a card announces is **completely independent of the effect it runs**
(see docs/NOTES.md): the verb tables decide what happens, and a separate table
decides what is printed. That is why a reskinned spell keeps announcing the DM1
card it replaced until you edit it here.

    slot -> message id   0x15162 : 50 bytes, index = card number - 301
    message pointers     0x14980 : 45 x 16-bit CPU addr; file = ptr + 0x10000
    message pool         0x15400 - 0x15ABE = 1726 bytes, [Exit] (0xB4) terminated

The stock pool uses **suffix sharing** (three pointers alias into the middle of
another string), so it packs 1774 bytes of text into 1726. This editor repacks
the pool *without* sharing and enforces the 1726-byte budget, so replacement text
has to be a little more concise than stock. Messages not listed in the config are
carried over byte-identically.

Authoring: work/<product>/message_config.json = {"messages": {"16": "text", ...}}
with ids in decimal and `[Line]`/`[Page]`/`[Exit]` control codes. Applied by
build.py.

CLI:
  python messages.py show [--product duelmonsters-mtg]      every message, with its users
  python messages.py budget [--product duelmonsters-mtg]    pool usage of a product's config
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as cardlib  # noqa: E402
import cardtext          # noqa: E402
import products          # noqa: E402

SLOT_MAP = 0x15162        # 50 bytes: card#-301 -> message id
PTRS = 0x14980            # 45 pointers
NMSG = 45
POOL = 0x15400
POOL_END = 0x15ABE
BUDGET = POOL_END - POOL  # 1726
TERM = 0xB4               # [Exit]
BANK_OFF = 0x10000        # file = cpu + this


def read_all(rom):
    out = []
    for i in range(NMSG):
        p = rom[PTRS + 2 * i] | (rom[PTRS + 2 * i + 1] << 8)
        o = p + BANK_OFF
        e = o
        while rom[e] != TERM:
            e += 1
        out.append(bytes(rom[o:e + 1]))
    return out


def apply_config(rom, cfg):
    msgs = read_all(rom)
    for k, text in (cfg.get("messages") or {}).items():
        i = int(k)
        if not 0 <= i < NMSG:
            raise ValueError(f"message id {i} out of range 0..{NMSG-1}")
        b = cardtext.encode(text)
        if not b.endswith(bytes([TERM])):
            b += bytes([TERM])
        msgs[i] = b
    total = sum(len(m) for m in msgs)
    if total > BUDGET:
        raise ValueError(
            f"duel messages need {total} bytes, pool holds {BUDGET} "
            f"(over by {total - BUDGET}). Shorten some replacement text.")
    cpu = POOL - BANK_OFF
    for i, m in enumerate(msgs):
        rom[PTRS + 2 * i] = cpu & 0xFF
        rom[PTRS + 2 * i + 1] = (cpu >> 8) & 0xFF
        rom[cpu + BANK_OFF:cpu + BANK_OFF + len(m)] = m
        cpu += len(m)
    for o in range(cpu + BANK_OFF, POOL_END):     # pad any freed tail
        rom[o] = TERM
    return len(cfg.get("messages") or {})


def main(argv):
    product, argv = products.pop_arg(argv)
    if not argv:
        print(__doc__)
        return 1
    cmd = argv[0]
    rom = bytearray(open(cardlib.BASE_ROM, "rb").read())

    if cmd == "show":
        users = {}
        for s in range(50):
            users.setdefault(rom[SLOT_MAP + s], []).append(301 + s)
        names = {}
        cj = products.data_path("cards.json", product)
        if os.path.exists(cj):
            names = {c["id"]: c["name"]
                     for c in json.load(open(cj, encoding="utf-8"))["cards"]}
        for i, m in enumerate(read_all(rom)):
            u = users.get(i, [])
            tag = ", ".join(names.get(c, f"#{c}") for c in u[:3]) + (" ..." if len(u) > 3 else "")
            print(f"  {i:2} (0x{i:02X}) {len(m):3}B  {cardtext.decode(m)[:46]!r}")
            if u:
                print(f"          used by {len(u)}: {tag}")

    elif cmd == "budget":
        p = products.data_path("message_config.json", product)
        cfg = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
        test = bytearray(rom)
        try:
            n = apply_config(test, cfg)
            msgs = read_all(test)
            print(f"OK: {n} message(s) replaced; pool "
                  f"{sum(len(m) for m in msgs)}/{BUDGET} bytes")
        except ValueError as e:
            print("FAIL:", e)
            return 1
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
