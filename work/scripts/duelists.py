#!/usr/bin/env python3
"""The opponent roster: names, decks, drop pools and win-count rewards.

16 duelists. Everything about an opponent hangs off one **pool id**, read from
the 16-byte map at 0xB734, which selects all three of their tables:

    name          0x5457 + 8*duelist   fixed-width 8 bytes, space padded
    pool id       0xB734 + duelist
    deck          pointer table 0x2006C (bank 8) -> 365 x cumulative BCD-free
                  16-bit weights, running to exactly 2048
    drop pool     pointer table 0x34072 (bank 13), same 365 x cumulative shape
    rewards       pointer table 0x036F18 (bank 13) -> 10 card ids, one per
                  win-count threshold at 0x036F02

There are **17 pool slots but only 16 duelists** — pool 6 is referenced by
nobody. Its deck pointer is a 44-byte stub (every real deck is 730 bytes) and
drop pools 6 and 7 share one pointer. That makes slot 6 a free slot for a new
opponent's deck and drop table, though the roster size itself is a separate
question (the name table and 0xB734 are both fixed at 16).

Decks are probability distributions, not 40-card lists: the game samples a card
by rolling 0..2047 and finding the bucket. A card's share is
`(cum[i] - cum[i-1]) / 2048`, so "deck size" here means *distinct cards with a
non-zero share*.

CLI:
  python duelists.py list                 the roster
  python duelists.py deck <duelist#>      full deck with percentages
  python duelists.py rewards <duelist#>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as cardlib  # noqa: E402
import cardtext  # noqa: E402

BASE_ROM = cardlib.BASE_ROM

NAME_TABLE = 0x5457
NAME_LEN = 8
NDUELIST = 16
POOL_MAP = 0xB734

DECK_PTRS = 0x2006C
BANK8 = 0x20000

DROP_PTRS = 0x34072
BANK13 = 0x30000

REWARD_PTRS = 0x036F18
THRESHOLDS = 0x036F02

NCARD = 365
TOTAL = 2048
NPOOL = 17


def rd16(rom, o):
    return rom[o] | (rom[o + 1] << 8)


def duelist_name(rom, d):
    return cardtext.decode(
        rom[NAME_TABLE + NAME_LEN * d:NAME_TABLE + NAME_LEN * (d + 1)]).strip()


def apply_config(rom, cfg):
    """Rename the 16 duelists. Names are FIXED 8-byte records (space padded), so
    renaming is in place — there is no pool to repack. This is what the record
    page and the duel HUD read; opponent *dialogue* is separate text elsewhere."""
    names = cfg.get("names") or []
    if len(names) != 16:
        raise ValueError(f"expected 16 duelist names, got {len(names)}")
    for d, nm in enumerate(names):
        enc = cardtext.encode(nm)
        if len(enc) > NAME_LEN:
            raise ValueError(f"duelist {d} name {nm!r} is {len(enc)} tiles, max {NAME_LEN}")
        enc = enc + b"\x00" * (NAME_LEN - len(enc))
        rom[NAME_TABLE + NAME_LEN * d:NAME_TABLE + NAME_LEN * (d + 1)] = enc
    return len(names)


def pool_of(rom, d):
    return rom[POOL_MAP + d]


def _cum(rom, base):
    return [rd16(rom, base + 2 * i) for i in range(NCARD)]


def _weights(cum):
    return [cum[0]] + [cum[i] - cum[i - 1] for i in range(1, NCARD)]


def deck_weights(rom, pool):
    return _weights(_cum(rom, BANK8 + rd16(rom, DECK_PTRS + 2 * pool) - 0x4000))


def drop_weights(rom, pool):
    return _weights(_cum(rom, BANK13 + rd16(rom, DROP_PTRS + 2 * pool)))


def rewards(rom, pool):
    base = rd16(rom, REWARD_PTRS + 2 * pool) + BANK13
    return [rd16(rom, base + 2 * i) for i in range(10)]


def thresholds(rom):
    return [cardlib.bcd_to_int(rd16(rom, THRESHOLDS + 2 * i)) for i in range(10)]


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    rom = open(BASE_ROM, "rb").read()
    names = cardlib.load_names(rom)
    cmd = argv[0]

    def cn(num):
        return names.get(num - 1, f"<#{num}>")

    if cmd == "list":
        print(f"{'#':>2}  {'duelist':10s} {'pool':>4}  {'deck':>4}  {'drops':>5}  "
              f"{'deck file':>10}  top deck cards")
        for d in range(NDUELIST):
            p = pool_of(rom, d)
            dw = deck_weights(rom, p)
            dr = drop_weights(rom, p)
            top = sorted(((w, i) for i, w in enumerate(dw) if w), reverse=True)[:3]
            off = BANK8 + rd16(rom, DECK_PTRS + 2 * p) - 0x4000
            print(f"{d:2d}  {duelist_name(rom, d):10s} {p:4d}  "
                  f"{sum(1 for w in dw if w):4d}  {sum(1 for w in dr if w):5d}  "
                  f"0x{off:06X}  " +
                  ", ".join(f"{cn(i+1)} {w*100//TOTAL}%" for w, i in top))
        unused = sorted(set(range(NPOOL)) - {pool_of(rom, d) for d in range(NDUELIST)})
        print(f"\npool slots with no duelist: {unused}  (deck pointer is a stub)")

    elif cmd == "deck":
        d = int(argv[1])
        p = pool_of(rom, d)
        dw = deck_weights(rom, p)
        print(f"{duelist_name(rom, d)} (duelist {d}, pool {p}) — "
              f"{sum(1 for w in dw if w)} distinct cards")
        for w, i in sorted(((w, i) for i, w in enumerate(dw) if w), reverse=True):
            print(f"  {w * 100 / TOTAL:5.2f}%  ({w:4d}/2048)  #{i+1:3d} {cn(i+1)}")

    elif cmd == "rewards":
        d = int(argv[1])
        p = pool_of(rom, d)
        print(f"{duelist_name(rom, d)} (duelist {d}, pool {p}) win-count rewards:")
        for t, cid in zip(thresholds(rom), rewards(rom, p)):
            print(f"  {t:4d} wins -> #{cid:3d} {cn(cid)}")

    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
