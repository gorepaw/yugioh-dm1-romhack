#!/usr/bin/env python3
"""Cards-per-win patch: award N drop cards after a won duel instead of 1.

Bank $0D holds one contiguous 102-byte block, $400C-$4071, containing exactly
two routines and nothing else:

    $400C  award   (far-call table index 0 — the only way in)
    $4027  picker  (roll 0..2047, walk the duelist's cumulative drop weights)

We verified that the ONLY reference into that block from inside bank $0D is the
award routine's own `call $4027`, and the only reference from outside is table
entry 0. So the whole block can be re-laid-out, provided it still starts at
$400C and still fits in 102 bytes.

Stock award routine:

    push af / push bc / call $23F7 / cp $00 / jr z,done
    call $4027          ; pick a drop card into BC
    rst $08 $11,$01     ; \
    rst $08 $41,$01     ;  > show it and add it to the collection
    rst $08 $29,$02     ; /
    call $6E8E          ; win-count milestone reward (fires only when the win
    done: pop bc / pop af / ret        ; count EXACTLY equals a threshold)

Wrapping a counted loop around the pick-and-give part costs 6 bytes. We fund it
by shortening the picker by 7, without changing what the picker does:

    ld a,$00 / ld [$CE9D],a / ld a,$FF / ld [$CE9E],a     (10 bytes)
 -> ld hl,$CE9D / xor a / ld [hl+],a / ld [hl],$FF        ( 7 bytes)

twice, plus `cp $00` -> `and a` (identical flags, one byte shorter) in both
routines. `call $6E8E` stays OUTSIDE the loop, so milestone rewards are still
handed out exactly once — looping the whole routine would hand out three copies
of the reward card on wins 10, 20, 30...

Edits queue to work/grind_config.json and are applied by build.py.

CLI:
  python grind.py show
  python grind.py set <n>        # 1 = stock behaviour
  python grind.py clear
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards  # noqa: E402

ROOT = cards.ROOT
BASE_ROM = cards.BASE_ROM
import products  # noqa: E402
GRIND_CONFIG = products.data_path("grind_config.json")   # default product (duelmonsters-kaizo)

BANK = 0x0D
BLOCK_CPU = 0x400C
BLOCK_END = 0x4071          # last byte we may touch ($4072 = drop pointer table)
BLOCK_FILE = BANK * 0x4000 + (BLOCK_CPU - 0x4000)
BLOCK_LEN = BLOCK_END - BLOCK_CPU + 1        # 102

PICKER_CPU = 0x402D         # where the picker lands in the new layout
COUNT_CPU = 0x4015          # the `ld b,<n>` immediate — cards awarded per win

# The stock 102 bytes. Refuse to patch anything else.
STOCK = bytes.fromhex(
    "F5C5CDF723FE00280FCD2740CF1101CF4101CF2902CD8E6EC1F1C9F5D5E53E00"
    "EA9DCE3EFFEA9ECECD1221FA9FCE5F3E00EA9DCE3E07EA9ECECD1221FA9FCE57"
    "0600CF19024FCB21217240092A666F010000C52A4F2A47CD0F1DC1FE00280303"
    "18F0E1D1F1C9"
)


def _award(count):
    """$400C: run the pick-and-give sequence `count` times, then check the
    milestone reward once."""
    return bytes([
        0xF5,                    # push af
        0xC5,                    # push bc
        0xCD, 0xF7, 0x23,        # call $23F7      ; A != 0 -> the player won
        0xA7,                    # and a
        0x28, 0x16,              # jr z,$402A      ; -> done
        0x06, count,             # ld b,count
        # --- loop ($4016) ---
        0xC5,                    # push bc         ; the picker clobbers BC
        0xCD, PICKER_CPU & 0xFF, PICKER_CPU >> 8,   # call picker -> BC = card
        0xCF, 0x11, 0x01,        # far-call bank $01 $5AF2
        0xCF, 0x41, 0x01,        # far-call bank $01 $5B04
        0xCF, 0x29, 0x02,        # far-call bank $02 $787E
        0xC1,                    # pop bc
        0x05,                    # dec b
        0x20, 0xEF,              # jr nz,$4016
        # --- once ($4027) ---
        0xCD, 0x8E, 0x6E,        # call $6E8E      ; milestone reward
        # --- done ($402A) ---
        0xC1,                    # pop bc
        0xF1,                    # pop af
        0xC9,                    # ret
    ])


def _picker():
    """$402D: unchanged behaviour, 7 bytes shorter than stock."""
    return bytes([
        0xF5, 0xD5, 0xE5,        # push af / push de / push hl
        0x21, 0x9D, 0xCE,        # ld hl,$CE9D
        0xAF,                    # xor a
        0x22,                    # ld [hl+],a      ; $CE9D = $00
        0x36, 0xFF,              # ld [hl],$FF     ; $CE9E = $FF
        0xCD, 0x12, 0x21,        # call $2112      ; RNG
        0xFA, 0x9F, 0xCE,        # ld a,[$CE9F]
        0x5F,                    # ld e,a          ; roll low byte
        0x21, 0x9D, 0xCE,        # ld hl,$CE9D
        0xAF,                    # xor a
        0x22,                    # ld [hl+],a      ; $CE9D = $00
        0x36, 0x07,              # ld [hl],$07     ; $CE9E = $07
        0xCD, 0x12, 0x21,        # call $2112
        0xFA, 0x9F, 0xCE,        # ld a,[$CE9F]
        0x57,                    # ld d,a          ; DE = roll 0..2047
        0x06, 0x00,              # ld b,$00
        0xCF, 0x19, 0x02,        # far-call bank $02 $7724 -> A = drop pool
        0x4F,                    # ld c,a
        0xCB, 0x21,              # sla c
        0x21, 0x72, 0x40,        # ld hl,$4072     ; drop-pool pointer table
        0x09,                    # add hl,bc
        0x2A, 0x66, 0x6F,        # ld a,[hl+] / ld h,[hl] / ld l,a
        0x01, 0x00, 0x00,        # ld bc,$0000     ; card index
        # --- walk the cumulative weights ($405E) ---
        0xC5,                    # push bc
        0x2A, 0x4F,              # ld a,[hl+] / ld c,a
        0x2A, 0x47,              # ld a,[hl+] / ld b,a
        0xCD, 0x0F, 0x1D,        # call $1D0F      ; compare BC vs DE
        0xC1,                    # pop bc
        0xA7,                    # and a
        0x28, 0x03,              # jr z,$406D
        0x03,                    # inc bc
        0x18, 0xF1,              # jr $405E
        0xE1, 0xD1, 0xF1,        # pop hl / pop de / pop af
        0xC9,                    # ret             ; BC = card index
    ])


def build_block(count):
    if not 1 <= count <= 255:
        raise ValueError("cards per win must be 1-255")
    block = _award(count) + _picker()
    if len(block) > BLOCK_LEN:
        raise AssertionError(f"block is {len(block)} bytes, only {BLOCK_LEN} available")
    # Sanity: the picker must land exactly where the award routine calls it.
    if len(_award(count)) != PICKER_CPU - BLOCK_CPU:
        raise AssertionError("award routine length does not place the picker at "
                             f"${PICKER_CPU:04X}")
    return block + b"\x00" * (BLOCK_LEN - len(block))


def apply_config(rom, cfg):
    count = int(cfg.get("cards_per_win", 1))
    if count == 1:
        return 0
    cur = bytes(rom[BLOCK_FILE:BLOCK_FILE + BLOCK_LEN])
    if cur != STOCK:
        raise AssertionError(
            f"bank $0D {BLOCK_CPU:04X}-{BLOCK_END:04X} is not the stock award "
            "block; refusing to patch")
    rom[BLOCK_FILE:BLOCK_FILE + BLOCK_LEN] = build_block(count)
    return count


def load_cfg():
    return json.load(open(GRIND_CONFIG)) if os.path.exists(GRIND_CONFIG) else {}


def save_cfg(c):
    os.makedirs(os.path.dirname(GRIND_CONFIG), exist_ok=True)
    json.dump(c, open(GRIND_CONFIG, "w"), indent=2)


def main(argv):
    global GRIND_CONFIG
    product, argv = products.pop_arg(argv)
    GRIND_CONFIG = products.data_path("grind_config.json", product)
    if not argv:
        print(__doc__)
        return 1
    cmd = argv[0]

    if cmd == "show":
        cfg = load_cfg()
        n = int(cfg.get("cards_per_win", 1))
        rom = open(BASE_ROM, "rb").read()
        stock = bytes(rom[BLOCK_FILE:BLOCK_FILE + BLOCK_LEN]) == STOCK
        print(f"base ROM award block is {'stock' if stock else 'NOT STOCK'}")
        print(f"queued cards per win: {n}"
              f"{'  (stock — no patch applied)' if n == 1 else ''}")
        if n != 1:
            blk = build_block(n)
            print(f"patch: {len(blk)} bytes at 0x{BLOCK_FILE:06X} "
                  f"(bank $0D ${BLOCK_CPU:04X}-${BLOCK_END:04X})")
            print(f"count byte at 0x{BANK * 0x4000 + COUNT_CPU - 0x4000:06X}")

    elif cmd == "set":
        n = int(argv[1], 0)
        build_block(n)          # validate before saving
        cfg = load_cfg()
        cfg["cards_per_win"] = n
        save_cfg(cfg)
        print(f"queued: {n} card(s) per won duel")

    elif cmd == "clear":
        if os.path.exists(GRIND_CONFIG):
            os.remove(GRIND_CONFIG)
        print(f"cleared {os.path.relpath(GRIND_CONFIG, ROOT)}")

    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
