#!/usr/bin/env python3
"""Spell-verb tables (bank 3) — the card -> effect binding.

No indirection patch is needed: the game is ALREADY data-driven here. Two byte
tables map a card id to a verb id, and both index one 53-entry jump table of
verb routines. Reassigning a spell's effect is a one-byte edit.

    jump table    $6F82  file 0x00EF82   53 entries ($00-$34) -> bank 3 routines
    table A       base $6EF2, magic block $701E  file 0x00F01E  (play onto field)
    table B       base $6F62, magic block $708E  file 0x00F08E  (equip / combine)

Both bases are NEGATIVE offsets — the dispatcher does `base + card_id`, and for
table A that means $6EF2 + 300 = $701E. The first 300 notional entries overlap
the jump table and the dispatcher code itself and are never read, because cards
below id 300 are short-circuited before the lookup. Only ids 300-364 (cards
#301-365) are real data: 65 bytes per table.

Dispatchers:
    $6FEE  play path   — card from $CDF2/$CDF3; id < 300 -> verb $2F outright
    $705F  fuse path   — card from $CECD/$CECE; id < 300 -> try fusion (far-call
                         bank $3B idx 2), returning verb $01 if it fused else $02
    $6F49 / $6F64      — take the verb id, x2, index $6F82, and `jp hl`

Why two tables: playing an equip card onto the field is generic (verb $2F), but
combining it with a monster needs per-equip logic, so table B gives each equip
its own verb $15-$2E. Swords of Light, Spellbinding Circle and Dark-Piercing
Light are $00 (a bare `ret`) in table B — they cannot be combined.

> The earlier note that effects were "bound in code by card id, the slot IS the
> verb" was wrong. It came from testing the table at 0x15162, which only selects
> the on-screen MESSAGE ($5148 writes it to $CF47). Message and effect are
> independent tables — change a verb here and the flavour text will not follow.

CLI:
  python spells.py list                  every magic card's verbs
  python spells.py verbs                 the verb catalogue
  python spells.py set <card#> <verb> [--table a|b]
  python spells.py verify
  python spells.py clear
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as cardlib  # noqa: E402

ROOT = cardlib.ROOT
BASE_ROM = cardlib.BASE_ROM
SPELL_CONFIG = os.path.join(ROOT, "work", "spell_config.json")

JUMP_TABLE = 0x00EF82        # bank 3 $6F82
NJUMP = 53
TABLE_A = 0x00EEF2           # base $6EF2 — add card id
TABLE_B = 0x00EF62           # base $6F62 — add card id
FIRST = 300                  # ids below this never reach either table
NCARD = 365
MSG_TABLE = 0x015162         # bank 5 $5162, index = card# - 301 (message only)

# What each verb does, from the stock assignments. Ranges share one routine
# shape with different magnitudes.
VERB_NOTES = {
    0x00: "nothing (bare ret)",
    0x01: "summon a fusion result",
    0x02: "summon (fusion-material monster)",
    0x03: "field: Forest", 0x04: "field: Wasteland", 0x05: "field: Mountain",
    0x06: "field: Sogen", 0x07: "field: Umi", 0x08: "field: Yami",
    0x09: "heal 1", 0x0A: "heal 2", 0x0B: "heal 3", 0x0C: "heal 4",
    0x0D: "heal 5",
    0x0E: "burn 1", 0x0F: "burn 2", 0x10: "burn 3", 0x11: "burn 4",
    0x12: "burn 5",
    0x13: "destroy all monsters (Dark Hole)",
    0x14: "destroy enemy monsters (Raigeki)",
    0x2F: "generic play onto field / summon",
    0x30: "force attack position (Stop Defence)",
    0x31: "seal Dragons (Dragon Capture Jar)",
    0x32: "skip enemy attacks (Swords of Light)",
    0x33: "reveal (Dark-Piercing Light)",
    0x34: "power down all enemies (Spellbinding Circle)",
    0x35: "transform (Elegant Egotist)",
}
for _v in range(0x15, 0x2F):
    VERB_NOTES.setdefault(_v, "equip combine (per-equip stat logic)")


def rd16(rom, o):
    return rom[o] | (rom[o + 1] << 8)


def verb_of(rom, card_index, table=TABLE_A):
    return rom[table + card_index]


def read_all(rom):
    return {i: (rom[TABLE_A + i], rom[TABLE_B + i]) for i in range(FIRST, NCARD)}


def apply_config(rom, cfg):
    n = 0
    for entry in cfg.get("verbs", []):
        idx = int(entry["card"]) - 1
        if not FIRST <= idx < NCARD:
            raise ValueError(
                f"card #{entry['card']} is below #{FIRST + 1}; cards under that "
                "id never reach the verb table (they are short-circuited)")
        v = int(entry["verb"])
        if not 0 <= v < NJUMP:
            raise ValueError(f"verb 0x{v:02X} is out of range (0x00-0x{NJUMP-1:02X})")
        base = TABLE_B if entry.get("table", "a").lower() == "b" else TABLE_A
        rom[base + idx] = v
        n += 1
    return n


def load_cfg():
    return json.load(open(SPELL_CONFIG)) if os.path.exists(SPELL_CONFIG) else {}


def save_cfg(c):
    os.makedirs(os.path.dirname(SPELL_CONFIG), exist_ok=True)
    json.dump(c, open(SPELL_CONFIG, "w"), indent=2)


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    cmd = argv[0]
    rom = bytearray(open(BASE_ROM, "rb").read())
    names = cardlib.load_names(rom)

    if cmd == "list":
        print(f"{'card':>5} {'name':22s} {'A':>4} {'B':>4}  {'msg':>4}  effect")
        for i in range(FIRST, NCARD):
            a, b = rom[TABLE_A + i], rom[TABLE_B + i]
            msg = f"0x{rom[MSG_TABLE + i - FIRST]:02X}" if i - FIRST < 50 else "  - "
            print(f"#{i+1:4d} {names[i]:22s} 0x{a:02X} 0x{b:02X}  {msg}  "
                  f"{VERB_NOTES.get(a, '?')}")

    elif cmd == "verbs":
        print(f"{NJUMP} verbs in the jump table at $6F82:")
        for v in range(NJUMP):
            addr = rd16(rom, JUMP_TABLE + 2 * v)
            users = [names[i] for i in range(FIRST, NCARD) if rom[TABLE_A + i] == v]
            tag = f"  <- {len(users)} card(s)" if users else ""
            print(f"  0x{v:02X}  ${addr:04X}  {VERB_NOTES.get(v, '?'):42s}{tag}")

    elif cmd == "set":
        num, verb = int(argv[1]), int(argv[2], 0)
        table = "a"
        if "--table" in argv:
            table = argv[argv.index("--table") + 1].lower()
        cfg = load_cfg()
        vs = [e for e in cfg.get("verbs", [])
              if not (e["card"] == num and e.get("table", "a") == table)]
        vs.append({"card": num, "name": names.get(num - 1, "?"),
                   "verb": verb, "table": table})
        vs.sort(key=lambda e: (e["card"], e.get("table", "a")))
        cfg["verbs"] = vs
        apply_config(bytearray(rom), cfg)          # validate before saving
        save_cfg(cfg)
        print(f"queued #{num} {names.get(num - 1, '?')} table {table.upper()} "
              f"-> verb 0x{verb:02X} ({VERB_NOTES.get(verb, '?')})")
        print("note: the on-screen message is a SEPARATE table (0x15162) and "
              "will not follow.")

    elif cmd == "verify":
        base = bytes(rom)
        test = bytearray(base)
        n = apply_config(test, {"verbs": [
            {"card": i + 1, "verb": base[TABLE_A + i], "table": "a"}
            for i in range(FIRST, NCARD)]})
        ok = bytes(test) == base
        print(f"rewrote {n} table-A entries with their own values: "
              f"{'byte-identical [OK]' if ok else 'MISMATCH'}")
        print(f"jump table entries all in bank 3: "
              f"{all(0x4000 <= rd16(rom, JUMP_TABLE + 2*v) < 0x8000 for v in range(NJUMP))}")
        return 0 if ok else 1

    elif cmd == "clear":
        if os.path.exists(SPELL_CONFIG):
            os.remove(SPELL_CONFIG)
        print("cleared work/spell_config.json")

    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
