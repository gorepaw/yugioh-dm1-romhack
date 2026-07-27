#!/usr/bin/env python3
"""Replace the 18 duel backdrops with Magic characters.

The backdrop is the duelist's portrait behind the duel text window -- the screen
the game spends the most time on. See docs/SCREENS.md for the format.

**Which portrait belongs to which duelist is read out of the ROM, not guessed.**
`$7724` in bank $02 returns `table[$CEEF]` where `$CEEF` is the duelist index and
the table is at 0xB734; the caller stores that in `$CD50`, the backdrop selector.
That is the same table drops.py calls DMAP, so one byte picks both a duelist's
portrait and their drop pool -- change it and you move both.

    slot 15 Yawgmoth -> arena04 (stock: Yami Yugi)
    slot 14 Urza     -> arena15 (stock: Pegasus)
    slot 13 Mishra   -> arena16 (stock: Simon)

which lands exactly on the three boss positions the roster was designed around,
and is why the mapping can be trusted.

Arenas 6 and 17 are used by cutscenes rather than duels, so they get scenery.

THE BINDING CONSTRAINT IS BANK $30. Six backdrops share each 16 KB bank and $30
ships with only ~700 bytes spare -- and it holds five of our replacements,
including three Elder Dragons and two of the three bosses. A busy portrait runs
300-500 bytes over the stock stream it displaces, so that bank cannot absorb
them at default settings. `--dither none` is not a downgrade here: these are
single-figure portraits, and flat posterised art both compresses far better and
reads better at 20x11 tiles than dithered art does.

CLI:
  python mtg_portraits.py fetch      art -> work/duelmonsters-mtg/screens_in/
  python mtg_portraits.py convert    -> work/duelmonsters-mtg/screens/arenaNN.png
  python mtg_portraits.py budget     per-bank compressed cost, before building
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gblzss          # noqa: E402
import products        # noqa: E402
import screens         # noqa: E402

PRODUCT = "duelmonsters-mtg"
DMAP = 0xB734          # duelist index -> backdrop index (and drop pool)

# Duelist slot -> the Magic card whose art becomes their portrait. Chosen for a
# single clear figure; era-appropriate where the character exists in our sets
# (the five Elder Dragons and the Arabian Nights pair are all originals).
FACE = {
    0:  "Serra Angel",
    1:  "Ashnod the Uncaring",
    2:  "Tawnos, the Toymaker",
    3:  "Teferi, Mage of Zhalfir",
    4:  "Arcades Sabboth",
    5:  "Chromium",
    6:  "Palladia-Mors",
    7:  "Vaevictis Asmadi",
    8:  "Nicol Bolas",
    9:  "Sindbad",
    10: "Ali Baba",
    11: "Feldon of the Third Path",
    12: "Jasmine Boreal",
    13: "Mishra, Artificer Prodigy",
    14: "Urza, Lord High Artificer",
    15: "Yawgmoth, Thran Physician",
}
# The two cutscene-only backdrops. arena17 sits in the tight bank, so it gets
# something deliberately flat.
CUTSCENE = {6: "Sage of Lat-Nam", 17: "Ruins of Trokair"}


def mapping(rom):
    """-> {arena_index: label} read from the ROM's own duelist table."""
    names = json.load(open(products.data_path("duelist_config.json", PRODUCT),
                           encoding="utf-8"))["names"]
    out = {}
    for slot in range(16):
        out[rom[DMAP + slot]] = (slot, names[slot], FACE[slot])
    return out


def bank_of(rom, arena):
    return rom[screens.ARENA_BANK_TABLE + arena]


def cmd_fetch(rom):
    import mtg_art_fetch as F
    dest = os.path.join(products.data_dir(PRODUCT), "screens_in")
    os.makedirs(dest, exist_ok=True)
    m = mapping(rom)
    want = [(a, m[a][2]) for a in sorted(m)] + [(a, n) for a, n in sorted(CUTSCENE.items())]
    todo = [(a, n, "") for a, n in want
            if not os.path.exists(os.path.join(dest, f"arena{a:02d}.jpg"))]
    if not todo:
        print(f"all {len(want)} portrait sources already present")
        return 0
    urls, missing = F.lookup(todo)
    print(f"resolved {len(urls)}/{len(todo)}")
    creds = {}
    cp = os.path.join(dest, "_credits.json")
    if os.path.exists(cp):
        creds = json.load(open(cp, encoding="utf-8"))
    for a, (url, artist, sid) in sorted(urls.items()):
        open(os.path.join(dest, f"arena{a:02d}.jpg"), "wb").write(
            F.get(url, accept="image/*"))
        nm = dict(want)[a]
        creds[f"arena{a:02d}"] = {"card": nm, "artist": artist, "scryfall_id": sid}
        print(f"  arena{a:02d}  {nm:28s} art by {artist}")
        import time
        time.sleep(F.DELAY)
    json.dump(creds, open(cp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    for a, n, _ in missing:
        print(f"  arena{a:02d} {n}: NOT FOUND")
    return 1 if missing else 0


def _cells(px, w, h):
    return [tuple(px[r * 8 + y][c * 8 + x] for y in range(8) for x in range(8))
            for r in range(h) for c in range(w)]


def reduce_tiles(px, w, h, cap):
    """Merge near-identical 8x8 tiles until at most `cap` remain.

    A 20x11 backdrop is 220 cells but the format allows only 187 distinct tiles,
    so at least 33 must repeat. Konami's hand-drawn portraits satisfy that for
    free through large flat areas; a photograph converted straight through has
    ~220 all-unique tiles and simply cannot be stored.

    Rather than flatten the whole picture to force repeats -- which throws away
    detail everywhere, including on the face -- merge only the most similar
    pairs. Distances are computed once, sorted, and consumed greedily through a
    union-find, so the 33 cheapest merges happen and nothing else is touched.
    """
    cells = _cells(px, w, h)
    uniq = sorted(set(cells))
    if len(uniq) <= cap:
        return px, len(uniq)

    idx = {t: i for i, t in enumerate(uniq)}
    parent = list(range(len(uniq)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    pairs = []
    for i in range(len(uniq)):
        ti = uniq[i]
        for j in range(i + 1, len(uniq)):
            tj = uniq[j]
            d = 0
            for a, b in zip(ti, tj):
                d += (a - b) * (a - b)
            pairs.append((d, i, j))
    pairs.sort()

    count = len(uniq)
    for d, i, j in pairs:
        if count <= cap:
            break
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[rj] = ri
            count -= 1

    rep = {}
    for t in uniq:
        rep[t] = uniq[find(idx[t])]
    out = [row[:] for row in px]
    for n, cell in enumerate(cells):
        r, c = divmod(n, w)
        t = rep[cell]
        for y in range(8):
            for x in range(8):
                out[r * 8 + y][c * 8 + x] = t[y * 8 + x]
    return out, count


FOCUS = 0.32       # vertical crop centre: faces sit above the middle
CONTRAST = 1.0     # measured: 1.3 posterised the midtones away


def _precrop(src, tmp, focus=FOCUS):
    """Crop the source to the backdrop's aspect before scaling.

    A backdrop is 160x88 = 1.82:1 and Scryfall's art_crop is about 1.36:1, so a
    centred `cover` fit slices roughly a quarter off top and bottom -- which on
    a character portrait is the head. Cropping deliberately high keeps the face.
    """
    from PIL import Image
    im = Image.open(src).convert("L")
    w, h = im.size
    want = (screens.ARENA_MAP_W * 8) / (screens.ARENA_MAP_H * 8)
    ch = int(w / want)
    if ch <= h:
        oy = int((h - ch) * focus)
        im = im.crop((0, oy, w, oy + ch))
    im.save(tmp)
    return tmp


def convert_one(rom, arena, src, dither, contrast):
    import tempfile
    tmp = os.path.join(tempfile.gettempdir(), f"_dm1_arena{arena:02d}.png")
    px = screens.convert_image(_precrop(src, tmp), screens.ARENA_MAP_W * 8,
                               screens.ARENA_MAP_H * 8,
                               screens.BGP_GAME, dither=dither, fit="stretch",
                               contrast=contrast)
    px, n = reduce_tiles(px, screens.ARENA_MAP_W, screens.ARENA_MAP_H,
                         screens.ARENA_ART_TILES)
    return px, n


def cmd_convert(rom, argv):
    src_dir = os.path.join(products.data_dir(PRODUCT), "screens_in")
    out_dir = screens.screens_dir(PRODUCT)
    os.makedirs(out_dir, exist_ok=True)
    m = mapping(rom)
    labels = {a: f"{m[a][1]}" for a in m}
    labels.update({a: "(cutscene)" for a in CUTSCENE})

    rows = []
    for arena in sorted(set(m) | set(CUTSCENE)):
        src = os.path.join(src_dir, f"arena{arena:02d}.jpg")
        if not os.path.exists(src):
            continue
        bank = bank_of(rom, arena)
        # Flat posterise everywhere, not just in the tight bank. Dithering makes
        # every 8x8 block unique, which fights BOTH limits at once: it pushes the
        # distinct-tile count to the 220 ceiling so the reducer has to merge
        # aggressively, and it destroys compression. Measured over all 18, bayer4
        # put banks $2E/$2F over budget by 401 and 776 bytes while flat art left
        # 1.6 KB spare. At 187 tiles a dither is noise anyway.
        dither = "none"
        contrast = CONTRAST
        px, ntiles = convert_one(rom, arena, src, dither, contrast)
        screens.save_png(px, screens.BGP_GAME,
                         os.path.join(out_dir, f"arena{arena:02d}.png"))
        screens.save_png(px, screens.BGP_GAME,
                         os.path.join(out_dir, f"_preview_arena{arena:02d}.png"), 3)
        rows.append((arena, bank, labels[arena], ntiles, dither))
    print(f"{'arena':>6} {'bank':>5}  {'duelist':<10} {'tiles':>6}/{screens.ARENA_ART_TILES} {'dither':>7}")
    for arena, bank, lab, n, d in rows:
        flag = "  <-- OVER" if n > screens.ARENA_ART_TILES else ""
        print(f"  {arena:02d}   ${bank:02X}  {lab:<10} {n:6d}     {d:>7}{flag}")
    print(f"\nwrote {len(rows)} portrait(s) to {os.path.relpath(out_dir, products.ROOT)}")
    print("run `mtg_portraits.py budget` before building")
    return 0


def cmd_budget(rom):
    """Per-bank compressed cost with the replacements costed in."""
    slots = screens.arena_slots(rom)
    overrides, _ = screens.load_overrides(PRODUCT)
    newsize = {}
    for a in range(screens.ARENA_N):
        p = overrides.get(f"arena{a:02d}")
        if not p:
            continue
        # Cost it exactly the way _apply_arenas does: pack to tiles, pad to the
        # 3072-byte decode length, compress. Anything else is a guess.
        px = screens.load_png(p, screens.BGP_GAME,
                              screens.ARENA_MAP_W, screens.ARENA_MAP_H)
        blob, _tmap = screens.pack(px, screens.ARENA_MAP_W, screens.ARENA_MAP_H,
                                   0, screens.ARENA_ART_TILES)
        raw = bytearray(screens.ARENA_BYTES)
        raw[:len(blob)] = blob
        newsize[a] = len(gblzss.compress(bytes(raw)))
    m = mapping(rom)
    for bank in (0x2E, 0x2F, 0x30):
        members = [a for a in range(screens.ARENA_N) if bank_of(rom, a) == bank]
        room = 16382
        used = 0
        for a in members:
            if newsize.get(a):
                used += newsize[a]
            else:
                used += screens.read_arena(rom, a)[1]
        rep = sum(1 for a in members if newsize.get(a))
        print(f"  bank ${bank:02X}  arenas {members[0]:2d}-{members[-1]:2d}  "
              f"{used:6d}/{room}  ({room - used:+6d})  {rep} replaced"
              + ("   <-- OVER" if used > room else ""))
    return 0


def main(argv):
    rom = screens.load_rom()
    cmd = argv[0] if argv else "help"
    if cmd == "fetch":
        return cmd_fetch(rom)
    if cmd == "convert":
        return cmd_convert(rom, argv[1:])
    if cmd == "budget":
        return cmd_budget(rom)
    if cmd == "map":
        m = mapping(rom)
        for a in sorted(m):
            slot, nm, face = m[a]
            print(f"  arena{a:02d}  bank ${bank_of(rom, a):02X}  slot {slot:2d}  "
                  f"{nm:10s} <- {face}")
        for a, n in sorted(CUTSCENE.items()):
            print(f"  arena{a:02d}  bank ${bank_of(rom, a):02X}  cutscene   <- {n}")
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
