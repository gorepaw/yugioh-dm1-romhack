#!/usr/bin/env python3
"""Build a romhack: compile one product's data onto the pristine English base ROM.

Reads roms/dm1-english.gb, applies every edit in EDITS (verifying the current
byte first, so a shifted address can never silently corrupt the ROM), then
compiles the selected product's data from work/<product>/, fixes the Game Boy
header + global checksums, and writes build/<product>-hack.gb.

    python build.py                              # duelmonsters-kaizo (default)
    python build.py --product duelmonsters-mtg   # -> build/duelmonsters-mtg-hack.gb

The two products keep SEPARATE data (they are two games in the same 366 card
slots), so each has its own work/<product>/ directory and its own output file.
The tools and reverse-engineering notes are shared; the data is not.
"""
import hashlib
import json
import os

import cards
import products

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.path.join(ROOT, "roms", "dm1-english.gb")

# (offset, expected_old_byte, new_byte, description)
#
# Product-agnostic raw byte edits. Empty on purpose — the demo/test edits that
# used to live here were removed once they had served their purpose. Per-product
# changes belong in work/<product>/, not here.
EDITS = []


def header_checksum(rom):
    c = 0
    for b in rom[0x134:0x14D]:
        c = (c - b - 1) & 0xFF
    return c


def global_checksum(rom):
    return (sum(rom) - rom[0x14E] - rom[0x14F]) & 0xFFFF


def main(argv=None):
    import sys
    product, _ = products.pop_arg(sys.argv[1:] if argv is None else argv)
    data = products.data_dir(product)
    out = products.build_path(product)

    def dpath(name):
        return os.path.join(data, name)

    rom = bytearray(open(BASE, "rb").read())
    print(f"product: {product}   data: work/{product}/")
    print(f"base: {BASE} ({len(rom)} bytes)")

    for off, old, new, desc in EDITS:
        cur = rom[off]
        if cur != old:
            print(f"ABORT @0x{off:06X}: expected 0x{old:02X}, found 0x{cur:02X} - {desc}")
            return 1
        rom[off] = new
        print(f"  @0x{off:06X}: 0x{old:02X} -> 0x{new:02X}   {desc}")

    # --- per-product raw byte patches (patches.json) ---
    # A list of {offset, bytes(hex), old?(hex), desc}. Verifies `old` when given,
    # then writes `bytes`. Used for label-table + effect-byte edits (e.g. the
    # MTG colour labels and the seal-by-colour retarget) that no card table covers.
    patches_path = dpath("patches.json")
    if os.path.exists(patches_path):
        for p in json.load(open(patches_path)):
            off = p["offset"]
            new = bytes.fromhex(p["bytes"])
            if "old" in p:
                old = bytes.fromhex(p["old"])
                cur = bytes(rom[off:off + len(old)])
                if cur != old:
                    print(f"ABORT patch @0x{off:06X}: expected {old.hex()}, "
                          f"found {cur.hex()} - {p.get('desc','')}")
                    return 1
            rom[off:off + len(new)] = new
            print(f"  patch @0x{off:06X}: {len(new)}B  {p.get('desc','')}")

    # --- the card compiler (cards.json): names, types, ATK/DEF, lore ---
    # When present this is the authority for the whole card model and is applied
    # FIRST, so the narrower editors below can still tweak individual cards on
    # top of it. Generate it with `python cardc.py extract [--product duelmonsters-mtg]`.
    cards_json = dpath("cards.json")
    if os.path.exists(cards_json):
        import cardc
        s = cardc.apply_config(rom, cardc.load_db(cards_json))
        print(f"  cards.json compiled: names {s['names']}/{s['name_budget']} B, "
              f"descriptions {s['descs']}/{s['desc_budget']} B")

    # --- fusion recipes (fusions.json) ---
    fusions_json = dpath("fusions.json")
    if os.path.exists(fusions_json):
        import fusions
        n = fusions.apply_config(rom, fusions.load_db(fusions_json))
        print(f"  fusions.json compiled: {n} recipes")

    # --- spell verbs (spell_config.json) ---
    spell_config = dpath("spell_config.json")
    if os.path.exists(spell_config):
        import spells
        n = spells.apply_config(rom, json.load(open(spell_config)))
        if n:
            print(f"  spell verbs reassigned: {n}")

    # --- equip eligibility lists (equips.json) ---
    equips_json = dpath("equips.json")
    if os.path.exists(equips_json):
        import equips
        n = equips.apply_config(rom, equips.load_db(equips_json))
        if n:
            print(f"  equip eligibility lists rewritten: {n}")

    # --- replacement card artwork (work/<product>/art/NNN.png) ---
    # One 64x80 four-shade PNG per card you want to redraw; produce them with
    # `python cardart.py import <card#> <image>`. Cards with no PNG keep their
    # stock picture, byte for byte.
    if os.path.isdir(os.path.join(data, "art")):
        import cardart
        n_art, n_repack = cardart.apply_config(rom, cardart.load_overrides(product))
        if n_art:
            print(f"  card art written: {n_art} picture(s)"
                  + (f", {n_repack} bank(s) repacked" if n_repack else ", all in place"))

    # --- replacement screens + font (work/<product>/screens/*.png) ---
    # One 160x144 PNG per full screen (title, portraits, splashes), 160x88 per
    # duel backdrop, 128x64 for the font. Produce them with
    # `python screens.py import <name> <image>`. See docs/SCREENS.md.
    if os.path.isdir(os.path.join(data, "screens")):
        import screens as screens_mod
        overrides, font_png = screens_mod.load_overrides(product)
        n_scr, n_arena, did_font = screens_mod.apply_config(rom, overrides, font_png)
        if n_scr or n_arena or did_font:
            print(f"  screens written: {n_scr} static, {n_arena} duel backdrop(s)"
                  + (", font replaced" if did_font else ""))

    # --- card stat edits (card_edits.json, applied via cards.py) ---
    card_edits_path = dpath("card_edits.json")
    card_edit_count = 0
    if os.path.exists(card_edits_path):
        for e in json.load(open(card_edits_path)):
            summary = cards.apply_card_stat(rom, e["card"] - 1,
                                            e.get("atk"), e.get("def"), e.get("type"))
            print(f"  card #{e['card']} {e.get('name', '')}: {summary}")
            card_edit_count += 1

    # --- card description text edits (desc_edits.json) ---
    desc_edits_path = dpath("desc_edits.json")
    desc_edit_count = 0
    if os.path.exists(desc_edits_path):
        import descriptions
        for e in json.load(open(desc_edits_path)):
            summary = descriptions.apply_desc(rom, e["card"] - 1,
                                              e.get("line1", ""), e.get("line2", ""))
            print(f"  desc #{e['card']} {e.get('name', '')}: {summary}")
            desc_edit_count += 1

    # --- duelist names (duelist_config.json) ---
    duelist_config = dpath("duelist_config.json")
    if os.path.exists(duelist_config):
        import duelists
        n = duelists.apply_config(rom, json.load(open(duelist_config)))
        print(f"  duelist names written: {n}")

    # --- opponent intro dialogue (dialogue_config.json) ---
    dialogue_config = dpath("dialogue_config.json")
    if os.path.exists(dialogue_config):
        import dialogue
        n = dialogue.apply_config(rom, json.load(open(dialogue_config)))
        print(f"  opponent dialogue rewritten: {n}")

    # --- duel messages (message_config.json) ---
    # What a spell SAYS is a separate table from what it DOES, so a reskinned
    # spell keeps announcing the DM1 card it replaced until this is written.
    message_config = dpath("message_config.json")
    if os.path.exists(message_config):
        import messages
        n = messages.apply_config(rom, json.load(open(message_config)))
        if n:
            print(f"  duel messages rewritten: {n}")

    # --- the player's 100-card starter pool (starter_config.json) ---
    starter_config = dpath("starter_config.json")
    if os.path.exists(starter_config):
        import starter
        n = starter.apply_config(rom, json.load(open(starter_config)))
        print(f"  starter pool written: {n} cards")

    # --- opponent decks (deck_config.json, monsters only) ---
    deck_config_path = dpath("deck_config.json")
    if os.path.exists(deck_config_path):
        import decks
        n = decks.apply_config(rom, json.load(open(deck_config_path)))
        if n:
            print(f"  opponent decks written: {n}")

    # --- card drop-pool changes (drop_config.json) ---
    drop_config_path = dpath("drop_config.json")
    if os.path.exists(drop_config_path):
        import drops
        drop_pool_count = drops.apply_config(rom, json.load(open(drop_config_path)))
        if drop_pool_count:
            print(f"  drop pools rewritten: {drop_pool_count}")

    # --- win-count reward thresholds/cards (reward_config.json) ---
    reward_config_path = dpath("reward_config.json")
    if os.path.exists(reward_config_path):
        import rewards
        reward_changed = rewards.apply_config(rom, json.load(open(reward_config_path)))
        if reward_changed:
            print(f"  reward values written: {reward_changed}")

    # --- cards awarded per won duel (grind_config.json) ---
    grind_config_path = dpath("grind_config.json")
    if os.path.exists(grind_config_path):
        import grind
        cards_per_win = grind.apply_config(rom, json.load(open(grind_config_path)))
        if cards_per_win:
            print(f"  award routine rebuilt: {cards_per_win} cards per won duel")

    rom[0x14D] = header_checksum(rom)
    gc = global_checksum(rom)
    rom[0x14E], rom[0x14F] = (gc >> 8) & 0xFF, gc & 0xFF

    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "wb").write(rom)
    print(f"wrote: {out}")
    print(f"  applied {len(EDITS)} byte + {card_edit_count} card + "
          f"{desc_edit_count} desc edit(s)")
    print(f"  MD5:  {hashlib.md5(bytes(rom)).hexdigest()}")

    # A patch is a *release* artifact, so it is NOT emitted here. Two agents
    # build this tree constantly; auto-emitting meant every routine build
    # rewrote dist/ and raced the other product's owner, and a patch cut from a
    # tree with uncommitted work encodes something git cannot reproduce. Cut it
    # deliberately, from a committed tree:  python patch.py --product <name>
    print(f"  (release: python patch.py --product {product})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
