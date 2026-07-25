#!/usr/bin/env python3
"""Full-screen graphics: title, splashes, portraits, menus, duel backdrops, font.

Everything the player sees that is NOT card art. Three families, three formats:

  1. STATIC SCREENS (21)  uncompressed tiles + a 20x18 tilemap, both in banks
     $0A/$0B/$0C, blitted straight to VRAM by a loader that this module parses
     out of the ROM rather than hard-coding. Title screen, the KONAMI/KCE/
     copyright splashes, the three character portraits, the deck/trunk/trade
     menus, name entry, records.

  2. DUEL BACKDROPS (18)  LZSS-compressed 192-tile sets in banks $2E/$2F/$30
     (the same codec as card art, `gblzss`), arranged by a 20x11 tilemap in
     bank $06. These are the duelist portraits behind the duel text window, so
     this is the "dialogue screen" backdrop.

  3. THE FONT           128 glyphs, 1 bit per pixel, 8 bytes each, at 0x080D9.
     The game expands each byte into both 2bpp planes on the way to VRAM, so a
     glyph is pure black-on-white with no greys.

PALETTE. The game runs BGP = $1B, which is INVERTED: colour 0 is BLACK and
colour 3 is WHITE. Only the three boot splashes (KONAMI, KCE, copyright) use
the normal $E4. Every PNG this tool reads or writes is in SCREEN colours - what
the player sees - and the conversion to raw colour indices happens here.

Commands
    python screens.py list                       every screen, with its addresses
    python screens.py budget                     tile/byte budgets
    python screens.py extract [name ...]         -> work/<p>/screens_src/<name>.png
    python screens.py import <name> <image>      -> work/<p>/screens/<name>.png
    python screens.py tiles <name> --out s.png   the screen's tile sheet
    python screens.py font extract|import <png>  the 128-glyph 1bpp font
    python screens.py verify                     round-trip every screen

`build.py` packs work/<product>/screens/*.png and font.png back into the ROM.
Add `--product <name>` to work on the other product (see products.py).
"""
import os
import sys

import gblzss
import products

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.path.join(ROOT, "roms", "dm1-english.gb")

SCREEN_W, SCREEN_H = 20, 18            # tiles
SHADES = [(0xF8, 0xF8, 0xF8), (0xA8, 0xA8, 0xA8), (0x58, 0x58, 0x58), (0x08, 0x08, 0x08)]

# ---- the two palettes the game actually uses (BGP register values) ----------
BGP_NORMAL = 0xE4      # colour 0 = white  ... 3 = black   (boot splashes only)
BGP_GAME = 0x1B        # colour 0 = black  ... 3 = white   (everything else)


def bgp_shades(bgp):
    """BGP register value -> [shade index for colour 0..3]"""
    return [(bgp >> (2 * i)) & 3 for i in range(4)]


# ---------------------------------------------------------------- ROM access

def load_rom(path=None):
    return bytearray(open(path or BASE, "rb").read())


def to_file(bank, cpu):
    return bank * 0x4000 + (cpu - (0x4000 if bank else 0))


def to_cpu(off):
    bank = off // 0x4000
    return bank, (off % 0x4000) + (0x4000 if bank else 0)


def w16(rom, off):
    return rom[off] | (rom[off + 1] << 8)


# ============================================================ static screens
#
# A loader is a fixed idiom. Two blit shapes appear, differing only in which
# register holds the source:
#
#     ld de,<vram> / ld hl,<src> / ld b,<n> / ld c,$10
#   .loop  ld a,[hl+] / ld [de],a / inc de / dec c / jr nz,.loop
#          dec b / jr nz
#
# and the 20x18 map blit, which adds 12 to de after every row of 20 to step
# across the 32-tile-wide BG map:
#
#     ld de,$9800 / ld hl,<map> / ld b,$12 / ld c,$14 ...
#
# We locate the map blits by pattern and walk backwards, so the addresses come
# out of the ROM instead of being copied into a table that can go stale.

MAP_BLIT = bytes.fromhex("06120E142A12130D20FA")
TILE_BLIT_HL = bytes.fromhex("0E102A12130D20FA0520F5")   # hl = source
TILE_BLIT_DE = bytes.fromhex("0E101A22130D20FA0520F5")   # de = source

# map-blit file offset -> (name, BGP, description). The offsets are stable in
# the base ROM; `list` prints any that go missing rather than guessing.
STATIC = [
    (0x0283AF, "trunk",         BGP_GAME, "Trunk (card storage) menu"),
    (0x0285F1, "trunk-trade",   BGP_GAME, "Trunk, opened from a trade"),
    (0x028793, "deck",          BGP_GAME, "Deck edit menu"),
    (0x0289D5, "trade-review",  BGP_GAME, "Trade: review cards"),
    (0x028B77, "duel-prep",     BGP_GAME, "Duel preparation (Trunk/Deck/Duel)"),
    (0x028E29, "trade-prep",    BGP_GAME, "Trade preparation"),
    (0x028FDE, "link-menu",     BGP_GAME, "Two-player / link menu"),
    (0x029190, "duel-field",    BGP_GAME, "DUEL FIELD frame: two card boxes + two LP boxes"),
    (0x02944F, "title",         BGP_GAME, "TITLE SCREEN"),
    (0x02A5F1, "duel-field-jp", BGP_GAME, "Leftover Japanese duel layout; loader has no call site"),
    (0x02A840, "ruins",         BGP_GAME, "Ruins / altar establishing shot"),
    (0x02C037, "konami",        BGP_NORMAL, "KONAMI boot logo"),
    (0x02C4F6, "kce-shinjuku",  BGP_NORMAL, "KCE Shinjuku boot logo"),
    (0x02CBB5, "copyright",     BGP_NORMAL, "Copyright / translation credits splash"),
    (0x02D744, "cast",          BGP_GAME, "Cast collage"),
    (0x03003B, "simon",         BGP_GAME, "Simon Muran portrait"),
    (0x03118A, "pegasus",       BGP_GAME, "Maximillion Pegasus portrait"),
    (0x032339, "yami-yugi",     BGP_GAME, "Yami Yugi portrait"),
    (0x0334D8, "name-lower",    BGP_GAME, "Name entry, lower-case keyboard"),
    (0x033737, "name-upper",    BGP_GAME, "Name entry, upper-case keyboard"),
    (0x0338D6, "records",       BGP_GAME, "Records screen"),
]


def _walk_back(rom, p, bank):
    """Collect the tile blits that precede the map blit at `p`."""
    copies = []
    while True:
        if rom[p - 3:p] != bytes.fromhex("0520F5"):
            break
        for pat, src_is_hl in ((TILE_BLIT_HL, True), (TILE_BLIT_DE, False)):
            q = p - len(pat)
            if rom[q:q + len(pat)] == pat:
                break
        else:
            break
        if rom[q - 2] != 0x06:
            break
        n = rom[q - 1]
        r = q - 2
        src = dest = None
        for _ in range(2):
            if rom[r - 3] == 0x21:
                v, r = w16(rom, r - 2), r - 3
                (src, dest) = (v, dest) if src_is_hl else (src, v)
            elif rom[r - 3] == 0x11:
                v, r = w16(rom, r - 2), r - 3
                (src, dest) = (src, v) if src_is_hl else (v, dest)
            else:
                break
        copies.append([dest, src, n])
        p = r
    copies.reverse()
    return copies


def parse_static(rom, blit_off):
    """-> dict(bank, map_off, copies=[(vram_dest, file_off, ntiles)], tiles_off)"""
    bank = blit_off // 0x4000
    if rom[blit_off - 6] != 0x11 or w16(rom, blit_off - 5) != 0x9800:
        raise SystemExit(f"0x{blit_off:06X}: not a 20x18 map blit")
    map_cpu = w16(rom, blit_off - 2)
    copies = _walk_back(rom, blit_off - 6, bank)

    out, cur = [], None
    for dest, src, n in copies:
        if src is not None:
            cur = src
        if cur is None or dest is None:
            continue
        out.append((dest, to_file(bank, cur), n))
        cur += n * 16

    # `duel-layout` and `duel-layout-2` set hl well before the map blit, so the
    # walk misses their single tile copy; recover it by scanning the routine.
    if not out:
        start = blit_off - 0x60
        for pat, src_is_hl in ((TILE_BLIT_HL, True), (TILE_BLIT_DE, False)):
            q = rom.find(pat, start, blit_off)
            if q > 0 and rom[q - 2] == 0x06:
                n, r = rom[q - 1], q - 2
                src = dest = None
                for _ in range(2):
                    if rom[r - 3] in (0x21, 0x11):
                        v = w16(rom, r - 2)
                        if (rom[r - 3] == 0x21) == src_is_hl:
                            src = v
                        else:
                            dest = v
                        r -= 3
                    else:
                        break
                if src is not None and dest is not None:
                    out.append((dest, to_file(bank, src), n))
                break

    return dict(bank=bank, map_off=to_file(bank, map_cpu), copies=out)


MIN_PICTURE_TILES = 32       # below this a screen owns a window frame, not a picture


def static_info(rom):
    """-> [dict] for every entry of STATIC, with capacity worked out."""
    infos = []
    for blit, name, bgp, desc in STATIC:
        d = parse_static(rom, blit)
        d.update(name=name, bgp=bgp, desc=desc, blit=blit)
        d["tiles_off"] = min((off for _, off, _ in d["copies"]), default=None)
        d["base_id"] = min((vram_to_id(dst) for dst, _, _ in d["copies"]), default=0)
        d["loaded"] = sum(n for _, _, n in d["copies"])
        infos.append(d)

    # A loader will happily copy past a screen's own graphics - on several
    # screens the tilemap itself sits inside the copied range and lands in VRAM
    # as tiles nothing references - so the real budget is whichever is smaller:
    # what the loader copies, or the room before the next structure. Three
    # menus share one tile blob, so "next structure" has to be looked up across
    # every screen rather than just this one.
    marks = sorted({d["map_off"] for d in infos} |
                   {d["tiles_off"] for d in infos if d["tiles_off"]})
    for d in infos:
        if d["tiles_off"] is None:
            d["cap_tiles"] = 0
        else:
            nxt = next((m for m in marks if m > d["tiles_off"]), None)
            gap = (nxt - d["tiles_off"]) // 16 if nxt else d["loaded"]
            d["cap_tiles"] = min(d["loaded"], gap)
        # Classify by what the tilemap points at. A PICTURE screen is drawn
        # entirely from its own tile blob. A LAYOUT screen owns only a window
        # frame and spells its content out of FONT glyphs, so there is no
        # picture to replace - only the 360-byte map.
        lo, hi = d["base_id"], d["base_id"] + d["cap_tiles"]
        own = [t for t in rom[d["map_off"]:d["map_off"] + 360] if lo <= t < hi]
        d["used"] = len(set(own))
        d["coverage"] = len(own) / 360.0
        d["kind"] = ("picture" if d["cap_tiles"] >= MIN_PICTURE_TILES
                     and d["coverage"] >= 0.9 else "layout")
    return infos


def vram_to_id(addr):
    """VRAM address -> signed-mode tile id (LCDC.4 = 0: $9000 = id 0)."""
    return ((addr - 0x9000) // 16) if addr >= 0x9000 else (128 + (addr - 0x8800) // 16)


# The tiles that are simply THERE whenever a menu is on screen, put in VRAM
# once and left alone: the font, the ten digit tiles the counters use, and the
# window-frame block. A layout screen's own loader writes none of these, so an
# extract has to merge them in or it comes out as blank boxes.
UI_BLOCK = 0x02805A          # 48 tiles -> VRAM $8D00 = ids $D0-$FF
UI_BLOCK_ID = 0xD0
DIGITS_ID = 0xC6             # bank $02 $4059: glyphs $01-$0A -> ids $C6-$CF


def ui_page(rom):
    page = bytearray(0x1000)
    page[0:0x800] = font_page(rom)
    fp = font_page(rom)
    for k in range(10):
        page[(DIGITS_ID + k) * 16:(DIGITS_ID + k + 1) * 16] = fp[(1 + k) * 16:(2 + k) * 16]
    page[UI_BLOCK_ID * 16:UI_BLOCK_ID * 16 + 48 * 16] = rom[UI_BLOCK:UI_BLOCK + 48 * 16]
    return page


def screen_tiles(rom, info):
    """-> 4096-byte tile page indexed by tile id, as the loader leaves VRAM."""
    buf = ui_page(rom) if info.get("kind") == "layout" else bytearray(0x1000)
    for dest, off, n in info["copies"]:
        base = vram_to_id(dest) * 16
        blob = rom[off:off + n * 16]
        buf[base:base + len(blob)] = blob[:0x1000 - base]
    return buf


# ------------------------------------------------------------ tiles <-> pixels

def tile_pixels(page, tid):
    g = [[0] * 8 for _ in range(8)]
    b = tid * 16
    for y in range(8):
        lo, hi = page[b + y * 2], page[b + y * 2 + 1]
        for x in range(8):
            s = 7 - x
            g[y][x] = ((lo >> s) & 1) | (((hi >> s) & 1) << 1)
    return g


def tile_bytes(g):
    out = bytearray(16)
    for y in range(8):
        lo = hi = 0
        for x in range(8):
            v = g[y][x] & 3
            s = 7 - x
            lo |= (v & 1) << s
            hi |= ((v >> 1) & 1) << s
        out[y * 2], out[y * 2 + 1] = lo, hi
    return bytes(out)


def compose(page, tilemap, w=SCREEN_W, h=SCREEN_H):
    """tile page + tilemap -> [h*8][w*8] of raw colour indices 0..3"""
    px = [[0] * (w * 8) for _ in range(h * 8)]
    for r in range(h):
        for c in range(w):
            g = tile_pixels(page, tilemap[r * w + c])
            for y in range(8):
                row = px[r * 8 + y]
                for x in range(8):
                    row[c * 8 + x] = g[y][x]
    return px


# ------------------------------------------------------------------- PNG i/o

def to_image(px, bgp, scale=1):
    """raw colour indices -> what the player sees, through BGP."""
    from PIL import Image
    sh = bgp_shades(bgp)
    h, w = len(px), len(px[0])
    im = Image.new("RGB", (w, h))
    p = im.load()
    for y in range(h):
        for x in range(w):
            p[x, y] = SHADES[sh[px[y][x]]]
    return im if scale == 1 else im.resize((w * scale, h * scale), Image.NEAREST)


def save_png(px, bgp, path, scale=1):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    to_image(px, bgp, scale).save(path)


def load_png(path, bgp, w, h):
    """A screen PNG -> [h*8][w*8] of raw colour indices (BGP undone)."""
    from PIL import Image
    im = Image.open(path).convert("L")
    if im.size != (w * 8, h * 8):
        raise SystemExit(f"{path}: expected {w * 8}x{h * 8}, got {im.size[0]}x{im.size[1]}")
    p = im.load()
    lums = [s[0] for s in SHADES]
    inv = {sh: c for c, sh in enumerate(bgp_shades(bgp))}
    return [[inv[min(range(4), key=lambda i: abs(lums[i] - p[x, y]))]
             for x in range(w * 8)] for y in range(h * 8)]


# --------------------------------------------------------------- tile packing

def pack(px, w, h, base_id=0, cap=256):
    """pixels -> (tile page bytes in id order starting at base_id, tilemap).

    Identical tiles are shared, which is what makes a 160x144 picture fit in
    256 tiles at all: 20x18 = 360 cells, so at least 104 must repeat.
    """
    order, index = [], {}
    tilemap = bytearray(w * h)
    for r in range(h):
        for c in range(w):
            g = [[px[r * 8 + y][c * 8 + x] for x in range(8)] for y in range(8)]
            blob = tile_bytes(g)
            tid = index.get(blob)
            if tid is None:
                tid = base_id + len(order)
                if tid - base_id >= cap:
                    raise SystemExit(
                        f"too many distinct tiles: this picture needs more than {cap}.\n"
                        f"  Flatten it (fewer unique 8x8 blocks) or reuse more areas.")
                index[blob] = tid
                order.append(blob)
            tilemap[r * w + c] = tid
    return b"".join(order), bytes(tilemap)


# ============================================================ duel backdrops
#
# 18 duelist portraits: a 192-tile LZSS set + a 20x11 tilemap. The tiles land
# at VRAM $9000 (ids $00-$7F) and $8800 (ids $80-$BF); the bottom 7 rows of the
# screen are the text window, whose 16 frame tiles (ids $BB-$CA) are a separate
# raw blit from bank $06.

ARENA_N = 18
ARENA_BYTES = 0x0C00                    # 3072 = 192 tiles
ARENA_BANK_TABLE = 0x001A9D             # 18 bytes: image -> bank ($2E/$2F/$30)
ARENA_PTR_TABLE = to_file(0x10, 0x7E84)  # 18 x 16-bit CPU addr, in bank $10
ARENA_MAP_TABLE = to_file(0x06, 0x4229)  # 18 x 16-bit CPU addr, in bank $06
ARENA_MAP_W, ARENA_MAP_H = 20, 11
HUD_MAP = to_file(0x06, 0x419D)          # 20x7 text-window map
HUD_TILES = to_file(0x06, 0x405E)        # 16 tiles -> VRAM $8BB0 = ids $BB-$CA
HUD_FIRST_ID = 0xBB
# ids $BB upward are overwritten by that blit, so a backdrop may only use $00-$BA
ARENA_ART_TILES = HUD_FIRST_ID
# Stock bank $30 (backdrops 12-17) has only ~700 bytes spare of 16382, and a
# busy replacement runs ~300-500 bytes over a stock one, so that bank cannot
# absorb even two. `budget` flags any bank with less headroom than this.
TIGHT_BANK = 1024


def arena_ptr(rom, i):
    bank = rom[ARENA_BANK_TABLE + i]
    cpu = w16(rom, ARENA_PTR_TABLE + 2 * i)
    return bank, cpu, to_file(bank, cpu)


def arena_slots(rom):
    """-> {i: (bank, cpu, capacity)} - a stream runs to the next one in its bank."""
    by_bank = {}
    for i in range(ARENA_N):
        bank, cpu, _ = arena_ptr(rom, i)
        by_bank.setdefault(bank, []).append((cpu, i))
    out = {}
    for bank, items in by_bank.items():
        items.sort()
        for k, (cpu, i) in enumerate(items):
            end = items[k + 1][0] if k + 1 < len(items) else 0x8000
            out[i] = (bank, cpu, end - cpu)
    return out


def read_arena(rom, i):
    return gblzss.decompress(rom, arena_ptr(rom, i)[2], ARENA_BYTES)


def arena_map(rom, i):
    off = to_file(0x06, w16(rom, ARENA_MAP_TABLE + 2 * i))
    return rom[off:off + ARENA_MAP_W * ARENA_MAP_H], off


def arena_page(rom, i):
    """192 tiles laid out by tile id, plus the 16 text-window tiles."""
    raw = read_arena(rom, i)[0]
    page = bytearray(0x1000)
    page[0:0x800] = raw[0:0x800]                     # ids $00-$7F -> $9000
    page[0x800:0xC00] = raw[0x800:0xC00]             # ids $80-$BF -> $8800
    page[HUD_FIRST_ID * 16:HUD_FIRST_ID * 16 + 16 * 16] = rom[HUD_TILES:HUD_TILES + 256]
    return page


def arena_screen(rom, i):
    """The full 160x144 dialogue screen: portrait on top, text window below."""
    page = arena_page(rom, i)
    m, _ = arena_map(rom, i)
    full = bytearray(m) + bytearray(rom[HUD_MAP:HUD_MAP + 140])
    return compose(page, full)


# ==================================================================== the font
#
# 128 glyphs, 1bpp, 8 bytes each. The loader (bank $02 $40B4) writes each byte
# TWICE, into both bitplanes, so a set bit is colour 3 and a clear bit colour 0
# - white paper, black ink under BGP $1B. Character codes are the ones in
# reference/DM1Translation/Insertion/text.tbl.

FONT_OFF = 0x0080D9
FONT_GLYPHS = 128
FONT_COLS = 16
# Codes >= $7D come from a separate 2bpp table (16 bytes/glyph), used for the
# few glyphs that need grey - see bank $02 $4096.
FONT_2BPP_OFF = to_file(0x02, 0x44C1)


def font_page(rom):
    """The font as the loader leaves it in VRAM: 128 tiles of 2bpp.

    Bank $02 $40B4 writes each 1bpp byte into BOTH planes, so every pixel is
    colour 0 or colour 3 - no greys. Codes >= $7D come from a 2bpp table
    instead (bank $02 $4096), which is where the few grey glyphs live.
    """
    page = bytearray(0x800)
    for g in range(FONT_GLYPHS):
        if g >= 0x7D:
            page[g * 16:(g + 1) * 16] = rom[FONT_2BPP_OFF + (g - 0x7D) * 16:
                                            FONT_2BPP_OFF + (g - 0x7D) * 16 + 16]
            continue
        for y in range(8):
            b = rom[FONT_OFF + g * 8 + y]
            page[g * 16 + y * 2] = page[g * 16 + y * 2 + 1] = b
    return bytes(page)


def font_pixels(rom):
    """-> [64][128] of raw colour indices (0 = ink, 3 = paper)"""
    px = [[0] * (8 * FONT_COLS) for _ in range(8 * (FONT_GLYPHS // FONT_COLS))]
    for g in range(FONT_GLYPHS):
        gx, gy = (g % FONT_COLS) * 8, (g // FONT_COLS) * 8
        for y in range(8):
            b = rom[FONT_OFF + g * 8 + y]
            for x in range(8):
                px[gy + y][gx + x] = 3 if (b >> (7 - x)) & 1 else 0
    return px


def font_bytes(px):
    out = bytearray(FONT_GLYPHS * 8)
    for g in range(FONT_GLYPHS):
        gx, gy = (g % FONT_COLS) * 8, (g // FONT_COLS) * 8
        for y in range(8):
            b = 0
            for x in range(8):
                if px[gy + y][gx + x] >= 2:      # nearest of the two extremes
                    b |= 1 << (7 - x)
            out[g * 8 + y] = b
    return bytes(out)


# ================================================================ build hook

def screens_dir(product):
    return os.path.join(products.data_dir(product), "screens")


def load_overrides(product):
    """-> ({name: png_path}, font_png or None) from work/<product>/screens/"""
    d = screens_dir(product)
    if not os.path.isdir(d):
        return {}, None
    names = {n for _, n, _, _ in STATIC} | {f"arena{i:02d}" for i in range(ARENA_N)}
    out, font = {}, None
    for fn in sorted(os.listdir(d)):
        if not fn.lower().endswith(".png") or fn.startswith("_"):
            continue
        stem = os.path.splitext(fn)[0]
        if stem == "font":
            font = os.path.join(d, fn)
        elif stem in names:
            out[stem] = os.path.join(d, fn)
        else:
            raise SystemExit(f"{fn}: unknown screen {stem!r}; see `screens.py list`")
    return out, font


def apply_config(rom, overrides, font_png=None):
    """Write replacement screens into `rom`. -> (n_static, n_arena, font?)"""
    infos = {d["name"]: d for d in static_info(rom)}
    n_static = 0
    for name, path in sorted(overrides.items()):
        if name in infos:
            info = infos[name]
            if info["kind"] != "picture":
                raise SystemExit(f"{name} is a layout screen - see `screens.py import`")
            px = load_png(path, info["bgp"], SCREEN_W, SCREEN_H)
            page, tmap = pack(px, SCREEN_W, SCREEN_H,
                              info["base_id"], info["cap_tiles"])
            rom[info["tiles_off"]:info["tiles_off"] + len(page)] = page
            rom[info["map_off"]:info["map_off"] + len(tmap)] = tmap
            n_static += 1

    arenas = {int(n[5:]): p for n, p in overrides.items() if n.startswith("arena")}
    n_arena = _apply_arenas(rom, arenas) if arenas else 0

    if font_png:
        px = load_png(font_png, BGP_GAME, FONT_COLS, FONT_GLYPHS // FONT_COLS)
        rom[FONT_OFF:FONT_OFF + FONT_GLYPHS * 8] = font_bytes(px)
    return n_static, n_arena, bool(font_png)


def _apply_arenas(rom, arenas):
    """Repack whole banks - 6 streams share each of $2E/$2F/$30."""
    slots = arena_slots(rom)
    streams = {}
    for i, path in arenas.items():
        px = load_png(path, BGP_GAME, ARENA_MAP_W, ARENA_MAP_H)
        # ids $BB-$CA are the text-window frame, blitted over the backdrop from
        # bank $06 after it loads, so a backdrop must not use them.
        blob, tmap = pack(px, ARENA_MAP_W, ARENA_MAP_H, 0, ARENA_ART_TILES)
        raw = bytearray(ARENA_BYTES)
        raw[:len(blob)] = blob
        streams[i] = gblzss.compress(bytes(raw))
        off = to_file(0x06, w16(rom, ARENA_MAP_TABLE + 2 * i))
        rom[off:off + len(tmap)] = tmap

    banks = {slots[i][0] for i in streams}
    for bank in sorted(banks):
        members = sorted(i for i in range(ARENA_N) if slots[i][0] == bank)
        blobs = []
        for i in members:
            if i in streams:
                blobs.append((i, streams[i]))
            else:
                off = arena_ptr(rom, i)[2]
                n = gblzss.decompress(rom, off, ARENA_BYTES)[1]
                blobs.append((i, bytes(rom[off:off + n])))
        need = sum(len(b) for _, b in blobs)
        room = 0x8000 - 0x4002
        if need > room:
            raise SystemExit(
                f"duel-backdrop bank ${bank:02X} overflows by {need - room} bytes "
                f"({need} needed, {room} free).\n"
                f"  Backdrops {', '.join(str(i) for i, _ in blobs)} share it; "
                f"flatten the busiest one.")
        cpu = 0x4002
        for i, b in blobs:
            rom[to_file(bank, cpu):to_file(bank, cpu) + len(b)] = b
            rom[ARENA_PTR_TABLE + 2 * i:ARENA_PTR_TABLE + 2 * i + 2] = \
                cpu.to_bytes(2, "little")
            cpu += len(b)
    return len(streams)


# ==================================================================== commands

def cmd_list(rom):
    print("STATIC SCREENS - uncompressed tiles + 20x18 map, banks $0A/$0B/$0C\n")
    print("name           bank  tiles      map       kind     ids   used/cap  BGP  what")
    for d in static_info(rom):
        t = f"0x{d['tiles_off']:06X}" if d["tiles_off"] else "    -     "
        print(f"{d['name']:<14} ${d['bank']:02X}  {t} 0x{d['map_off']:06X} "
              f" {d['kind']:<7}  ${d['base_id']:02X}+  {d['used']:3d}/{d['cap_tiles']:<3d}"
              f"   ${d['bgp']:02X}  {d['desc']}")
    print("\nDUEL BACKDROPS - LZSS 192-tile sets + 20x11 map (the dialogue screen)\n")
    sl = arena_slots(rom)
    print("name      bank  stream      map        compressed/slot")
    for i in range(ARENA_N):
        bank, cpu, off = arena_ptr(rom, i)
        _, moff = arena_map(rom, i)
        used = read_arena(rom, i)[1]
        print(f"arena{i:02d}   ${bank:02X}  0x{off:06X}  0x{moff:06X}  {used:6d}/{sl[i][2]}")
    print(f"\nFONT - 0x{FONT_OFF:06X}, {FONT_GLYPHS} glyphs x 8 bytes, 1bpp "
          f"(codes >= $7D also read 2bpp tiles at 0x{FONT_2BPP_OFF:06X})")
    print(f"duel text-window frame - 0x{HUD_TILES:06X}, 16 tiles -> ids "
          f"${HUD_FIRST_ID:02X}-${HUD_FIRST_ID + 15:02X}; its map 0x{HUD_MAP:06X}")


def cmd_budget(rom):
    print("PICTURE SCREENS  'cap' = tiles the loader copies, capped by the room")
    print("before the next structure. 20x18 = 360 cells, so tiles MUST repeat.\n")
    print("name             distinct   cap   spare")
    for d in static_info(rom):
        if d["kind"] != "picture":
            continue
        flag = "  <-- FULL" if d["used"] >= d["cap_tiles"] else ""
        print(f"{d['name']:<16} {d['used']:6d}   {d['cap_tiles']:5d}"
              f"  {d['cap_tiles'] - d['used']:5d}{flag}")
    print("\nLAYOUT SCREENS   only a window-frame tile set of their own; everything")
    print("else on them is FONT glyphs. Edit the 360-byte tilemap, not a picture.\n")
    print("name             frame tiles  map offset")
    for d in static_info(rom):
        if d["kind"] == "picture":
            continue
        print(f"{d['name']:<16} {d['cap_tiles']:6d}       0x{d['map_off']:06X}")
    print("\nDUEL BACKDROPS   6 share each 16 KB bank; a stream that outgrows its")
    print("slot repacks the whole bank, exactly like card art.\n")
    sl = arena_slots(rom)
    by_bank = {}
    for i in range(ARENA_N):
        by_bank.setdefault(sl[i][0], []).append(i)
    room = 0x8000 - 0x4002
    spare = {}
    for bank in sorted(by_bank):
        used = sum(read_arena(rom, i)[1] for i in by_bank[bank])
        spare[bank] = room - used
        flag = "  <-- TIGHT" if room - used < TIGHT_BANK else ""
        print(f"  bank ${bank:02X}  arenas {by_bank[bank][0]:2d}-{by_bank[bank][-1]:2d}"
              f"  {used:6d}/{room}  ({room - used} spare){flag}")
    worst = min(spare, key=spare.get)
    print(f"\nTightest is bank ${worst:02X} (backdrops "
          f"{by_bank[worst][0]}-{by_bank[worst][-1]}) with only {spare[worst]} bytes")
    print("spare. Spread replacements across the three banks rather than")
    print("clustering them, and flatten anything you put in that one.")


def cmd_extract(rom, names, product):
    d = os.path.join(products.data_dir(product), "screens_src")
    os.makedirs(d, exist_ok=True)
    infos = {i["name"]: i for i in static_info(rom)}
    wanted = names or (list(infos) + [f"arena{i:02d}" for i in range(ARENA_N)] + ["font"])
    for name in wanted:
        if name == "font":
            save_png(font_pixels(rom), BGP_GAME, os.path.join(d, "font.png"))
        elif name.startswith("arena"):
            i = int(name[5:])
            # the editable payload is the 20x11 portrait; the 20x7 text window
            # under it belongs to the engine, so it only goes in the preview.
            px = compose(arena_page(rom, i), arena_map(rom, i)[0],
                         ARENA_MAP_W, ARENA_MAP_H)
            save_png(px, BGP_GAME, os.path.join(d, f"{name}.png"))
            save_png(arena_screen(rom, i), BGP_GAME,
                     os.path.join(d, f"_{name}-in-context.png"), 2)
        elif name in infos:
            info = infos[name]
            px = compose(screen_tiles(rom, info),
                         rom[info["map_off"]:info["map_off"] + 360])
            save_png(px, info["bgp"], os.path.join(d, f"{name}.png"))
        else:
            raise SystemExit(f"unknown screen {name!r}; see `screens.py list`")
    print(f"extracted {len(wanted)} screen(s) -> work/{product}/screens_src/")


def cmd_tiles(rom, name, out):
    from PIL import Image
    infos = {i["name"]: i for i in static_info(rom)}
    if name.startswith("arena"):
        page, bgp = arena_page(rom, int(name[5:])), BGP_GAME
    else:
        info = infos[name]
        page, bgp = screen_tiles(rom, info), info["bgp"]
    px = [[0] * (16 * 8) for _ in range(16 * 8)]
    for t in range(256):
        g = tile_pixels(page, t)
        tx, ty = (t % 16) * 8, (t // 16) * 8
        for y in range(8):
            for x in range(8):
                px[ty + y][tx + x] = g[y][x]
    to_image(px, bgp, 4).save(out)
    print("wrote", out)


def cmd_import(rom, name, src, product, opts):
    infos = {i["name"]: i for i in static_info(rom)}
    if name == "font":
        raise SystemExit("use `screens.py font import <128x64.png>`")
    if name.startswith("arena"):
        w, h, cap, bgp = ARENA_MAP_W, ARENA_MAP_H, ARENA_ART_TILES, BGP_GAME
    elif name in infos:
        info = infos[name]
        if info["kind"] != "picture":
            raise SystemExit(
                f"{name} is a LAYOUT screen: it owns only {info['cap_tiles']} window-frame\n"
                f"  tiles and draws everything else with FONT glyphs, so there is no\n"
                f"  picture to replace. Its content is the 360-byte tilemap at\n"
                f"  0x{info['map_off']:06X} - edit that (see docs/SCREENS.md) or restyle the\n"
                f"  font with `screens.py font`.")
        w, h, cap, bgp = SCREEN_W, SCREEN_H, info["cap_tiles"], info["bgp"]
    else:
        raise SystemExit(f"unknown screen {name!r}; see `screens.py list`")

    px = convert_image(src, w * 8, h * 8, bgp,
                       dither=opts.get("dither", "bayer4"),
                       fit=opts.get("fit", "cover"),
                       contrast=float(opts.get("contrast", 1.0)),
                       invert="invert" in opts)
    n = len({tile_bytes([[px[r * 8 + y][c * 8 + x] for x in range(8)]
                         for y in range(8)])
             for r in range(h) for c in range(w)})
    d = screens_dir(product)
    os.makedirs(d, exist_ok=True)
    out = os.path.join(d, f"{name}.png")
    save_png(px, bgp, out)
    save_png(px, bgp, os.path.join(d, f"_preview_{name}.png"), 3)
    verdict = "fits" if n <= cap else f"TOO MANY - the build will refuse this"
    print(f"wrote {out}")
    print(f"  {n} distinct tiles; {name} holds {cap}  ->  {verdict}")
    if n > cap:
        print("  tip: --dither none, or a flatter/less detailed source image")


def cmd_font(rom, sub, arg, product):
    d = screens_dir(product)
    if sub == "extract":
        p = os.path.join(products.data_dir(product), "screens_src", "font.png")
        save_png(font_pixels(rom), BGP_GAME, p)
        save_png(font_pixels(rom), BGP_GAME,
                 os.path.join(products.data_dir(product), "screens_src",
                              "_preview_font.png"), 6)
        print("wrote", p, "  (16 x 8 glyphs, code $00 top-left, row-major)")
    elif sub == "import":
        os.makedirs(d, exist_ok=True)
        from PIL import Image
        im = Image.open(arg).convert("L")
        if im.size != (128, 64):
            raise SystemExit(f"{arg}: expected 128x64 (16 x 8 glyphs of 8x8)")
        im.save(os.path.join(d, "font.png"))
        print("wrote", os.path.join(d, "font.png"))
        print("  1bpp: every pixel becomes pure ink or pure paper, no greys")
    else:
        raise SystemExit("usage: screens.py font extract|import <png>")


def cmd_verify(rom):
    bad = 0
    for info in static_info(rom):
        if info["kind"] != "picture":
            continue
        px = compose(screen_tiles(rom, info), rom[info["map_off"]:info["map_off"] + 360])
        # repacking renumbers tiles, so the test is pixels in -> pixels out
        page, tmap = pack(px, SCREEN_W, SCREEN_H, info["base_id"], info["cap_tiles"])
        buf = bytearray(0x1000)
        buf[info["base_id"] * 16:info["base_id"] * 16 + len(page)] = page
        if compose(buf, tmap) != px:
            print(f"{info['name']}: pixel round-trip differs")
            bad += 1
    for i in range(ARENA_N):
        raw, used = read_arena(rom, i)
        if len(raw) != ARENA_BYTES:
            print(f"arena{i:02d}: short decode")
            bad += 1
            continue
        enc = gblzss.compress(raw)
        if gblzss.decompress(enc, 0, ARENA_BYTES)[0] != raw:
            print(f"arena{i:02d}: codec round-trip differs")
            bad += 1
    if font_bytes(font_pixels(rom)) != bytes(rom[FONT_OFF:FONT_OFF + FONT_GLYPHS * 8]):
        print("font: round-trip differs")
        bad += 1
    n = sum(1 for d in static_info(rom) if d["kind"] == "picture") + ARENA_N + 1
    print(f"{n - bad}/{n} verified "
          f"(picture screens, duel backdrops, font: pixels -> tiles+map -> pixels)")
    return 1 if bad else 0


# ------------------------------------------------------------ image conversion

BAYER4 = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def convert_image(path, w, h, bgp, dither="bayer4", fit="cover", contrast=1.0,
                  invert=False):
    """Any image -> [h][w] of RAW colour indices for a screen using `bgp`."""
    from PIL import Image, ImageOps, ImageEnhance
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        flat = Image.new("RGBA", im.size, (255, 255, 255, 255))
        flat.alpha_composite(im)
        im = flat
    im = ImageOps.autocontrast(im.convert("L"), cutoff=1)
    if contrast != 1.0:
        im = ImageEnhance.Contrast(im).enhance(contrast)
    if invert:
        im = ImageOps.invert(im)
    if fit == "cover":
        im = ImageOps.fit(im, (w, h), Image.LANCZOS)
    elif fit == "stretch":
        im = im.resize((w, h), Image.LANCZOS)
    else:
        c = ImageOps.contain(im, (w, h), Image.LANCZOS)
        im = Image.new("L", (w, h), 255)
        im.paste(c, ((w - c.width) // 2, (h - c.height) // 2))
    p = im.load()

    sh = bgp_shades(bgp)
    inv = {s: c for c, s in enumerate(sh)}          # shade -> raw colour index
    out = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            v = p[x, y]
            if dither == "none":
                shade = 3 - min(3, v * 4 // 256)
            else:
                m = BAYER4[y % 4][x % 4]
                lvl = int((v * 63 / 255.0 + (15 - m)) / 16)
                shade = 3 - max(0, min(3, lvl))
            out[y][x] = inv[shade]
    return out


def main(argv):
    product, argv = products.pop_arg(argv)
    if not argv:
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    opts, pos = {}, []
    i = 0
    while i < len(rest):
        a = rest[i]
        if a.startswith("--"):
            if i + 1 < len(rest) and not rest[i + 1].startswith("--"):
                opts[a[2:]] = rest[i + 1]
                i += 2
            else:
                opts[a[2:]] = True
                i += 1
        else:
            pos.append(a)
            i += 1
    rom = load_rom()

    if cmd == "list":
        cmd_list(rom)
    elif cmd == "budget":
        cmd_budget(rom)
    elif cmd == "extract":
        cmd_extract(rom, pos, product)
    elif cmd == "tiles":
        if not pos:
            raise SystemExit("usage: screens.py tiles <name> [--out sheet.png]")
        cmd_tiles(rom, pos[0], opts.get("out", f"{pos[0]}-tiles.png"))
    elif cmd == "import":
        if len(pos) != 2:
            raise SystemExit("usage: screens.py import <name> <image> [--dither ...]")
        cmd_import(rom, pos[0], pos[1], product, opts)
    elif cmd == "font":
        cmd_font(rom, pos[0] if pos else "", pos[1] if len(pos) > 1 else None, product)
    elif cmd == "verify":
        return cmd_verify(rom)
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
