#!/usr/bin/env python3
"""Card artwork: extract it, convert your own images into it, put it back.

Every card carries a 64 x 80 pixel, 4-shade picture with the rounded card frame
baked into it. See docs/NOTES.md "Card artwork" for the full decode; the short
version:

    art bank table   0x0018F0   365 bytes, card index -> ROM bank ($10..$2C)
    art pointer tbl  0x040028   365 x 16-bit CPU addr, in bank $10 at $4028
    picture          1280 bytes of GB 2bpp = 80 tiles, LZSS-compressed
    tile order       8x16 vertical PAIRS, left to right, band by band
                     (tile 2t = top half of a column, 2t+1 = bottom half)
    palette          BGP $1B - INVERTED: stored colour 0 shows as BLACK and 3
                     as WHITE. Every PNG here is in screen colours, i.e. what
                     the player sees; the conversion happens in this module.

Commands
    python cardart.py extract [--product duelmonsters-kaizo] [--cards 1,2,10-20]
        -> work/<product>/art_src/NNN.png, one 64x80 PNG per card

    python cardart.py show 1 24 --out /tmp/sheet.png
    python cardart.py frame --out /tmp/frame.png       the shared card frame
    python cardart.py budget                           per-bank space report
    python cardart.py verify                           decode/encode round-trip

    python cardart.py import 24 mypic.png [--dither bayer4] [--fit cover] ...
        -> work/<product>/art/024.png    (this is what the build reads)

    python cardart.py preview mypic.png --out /tmp/opts.png
        every dither/fit combination side by side, with encoded sizes

Then `python build.py --product <p>` packs work/<product>/art/*.png into the ROM.

Sizing rule: a picture must still fit the ROM. Each card owns a slot of roughly
1150-1250 bytes; a busy dithered image can exceed it. `import` prints the
encoded size against the slot, and the build repacks a whole bank (which frees
about 2 KB per 13 cards) when a single slot is not enough.
"""
import os
import re
import sys

import gblzss
import products

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.path.join(ROOT, "roms", "dm1-english.gb")

NCARD = 365
BANK_TABLE = 0x0018F0          # 365 bytes: card index -> bank
PTR_TABLE = 0x040028           # bank $10 CPU $4028: 365 x 16-bit LE CPU addr
PTR_TABLE_END = 0x4028 + 2 * NCARD      # CPU $4302
ART_BYTES = 0x0500             # 1280 = 80 tiles
W, H = 64, 80                  # pixels
TW, TH = 8, 10                 # tiles
FRAME_INSET = 6                # frame ring width; art box is 52 x 68

# banks the art may live in. $20 is deliberately absent: the stock bank table
# never selects it (see docs/NOTES.md) and we do not yet know what reads it.
ART_BANKS = tuple(list(range(0x10, 0x20)) + list(range(0x21, 0x2D)))
BANK_START = {b: 0x4002 for b in ART_BANKS}
BANK_START[0x10] = PTR_TABLE_END + 2    # $4304 - the pointer table sits first
BANK_END = 0x8000

# Game Boy shades, indexed the way the hardware numbers them: 0 = white.
SHADES = [(0xF8, 0xF8, 0xF8), (0xA8, 0xA8, 0xA8), (0x58, 0x58, 0x58), (0x08, 0x08, 0x08)]

# DM1 runs BGP = $1B, which is INVERTED: stored colour 0 shows as BLACK and
# colour 3 as WHITE. (Only the three boot logos use the normal $E4, and card art
# is never on screen during those - see docs/SCREENS.md for the proof.) So a
# picture's stored colour index is NOT its brightness, and everything that
# crosses between "stored colour" and "what the player sees" goes through these.
BGP = 0x1B
PALETTE = [SHADES[(BGP >> (2 * i)) & 3] for i in range(4)]   # colour  -> RGB
SHADE_TO_COLOUR = {(BGP >> (2 * i)) & 3: i for i in range(4)}   # 0=white -> colour


# ---------------------------------------------------------------- ROM access

def load_rom(path=None):
    return bytearray(open(path or BASE, "rb").read())


def file_off(bank, cpu):
    return bank * 0x4000 + (cpu - 0x4000)


def art_ptr(rom, card):
    """-> (bank, cpu_addr, file_offset) of card index `card` (0-based)."""
    bank = rom[BANK_TABLE + card]
    cpu = int.from_bytes(rom[PTR_TABLE + 2 * card:PTR_TABLE + 2 * card + 2], "little")
    return bank, cpu, file_off(bank, cpu)


def slots(rom):
    """-> {card: (bank, cpu, stored_capacity)}. A card's slot runs to whichever
    card starts next in the same bank, or to the end of the bank."""
    by_bank = {}
    for c in range(NCARD):
        bank, cpu, _ = art_ptr(rom, c)
        by_bank.setdefault(bank, []).append((cpu, c))
    out = {}
    for bank, items in by_bank.items():
        items.sort()
        for i, (cpu, c) in enumerate(items):
            end = items[i + 1][0] if i + 1 < len(items) else BANK_END
            out[c] = (bank, cpu, end - cpu)
    return out


def read_art(rom, card):
    """-> (1280 raw bytes, compressed length)"""
    _, _, off = art_ptr(rom, card)
    return gblzss.decompress(rom, off, ART_BYTES)


# ------------------------------------------------------- tiles <-> pixels

def _tile_xy(t):
    """tile index -> (tile_col, tile_row) for the 8x16-pair storage order"""
    pair = t // 2
    return pair % TW, (pair // TW) * 2 + (t & 1)


def to_pixels(raw):
    """1280 bytes of 2bpp -> [80][64] of 0..3"""
    g = [[0] * W for _ in range(H)]
    for t in range(TW * TH):
        cx, cy = _tile_xy(t)
        for y in range(8):
            lo, hi = raw[t * 16 + y * 2], raw[t * 16 + y * 2 + 1]
            for x in range(8):
                b = 7 - x
                g[cy * 8 + y][cx * 8 + x] = ((lo >> b) & 1) | (((hi >> b) & 1) << 1)
    return g


def to_raw(g):
    """[80][64] of 0..3 -> 1280 bytes of 2bpp in storage order"""
    raw = bytearray(ART_BYTES)
    for t in range(TW * TH):
        cx, cy = _tile_xy(t)
        for y in range(8):
            lo = hi = 0
            for x in range(8):
                v = g[cy * 8 + y][cx * 8 + x] & 3
                b = 7 - x
                lo |= (v & 1) << b
                hi |= ((v >> 1) & 1) << b
            raw[t * 16 + y * 2] = lo
            raw[t * 16 + y * 2 + 1] = hi
    return bytes(raw)


# ------------------------------------------------------------------ frame

def frame_template(rom, sample=48):
    """The card frame, as the value every card agrees on in the border ring.

    Sampled across the roster rather than copied from one card, so a single
    card whose art bleeds into the border cannot corrupt it.
    """
    import collections
    step = max(1, NCARD // sample)
    imgs = [to_pixels(read_art(rom, c)[0]) for c in range(0, NCARD, step)]
    f = [[None] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if FRAME_INSET <= x < W - FRAME_INSET and FRAME_INSET <= y < H - FRAME_INSET:
                continue
            f[y][x] = collections.Counter(g[y][x] for g in imgs).most_common(1)[0][0]
    return f


def apply_frame(g, frame):
    for y in range(H):
        for x in range(W):
            if frame[y][x] is not None:
                g[y][x] = frame[y][x]
    return g


# ------------------------------------------------------------------- PNG io

def to_image(g, scale=1):
    """[80][64] of stored colour indices -> the picture as the player sees it."""
    from PIL import Image
    im = Image.new("RGB", (W, H))
    px = im.load()
    for y in range(H):
        for x in range(W):
            px[x, y] = PALETTE[g[y][x]]
    return im if scale == 1 else im.resize((W * scale, H * scale), Image.NEAREST)


def save_png(g, path, scale=1):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    to_image(g, scale).save(path)


def load_png(path):
    """A 64x80 picture in the four GB greys -> [80][64] of stored colour indices.

    The PNG is what the player sees, so this undoes BGP on the way in - exactly
    the inverse of `to_image`.
    """
    from PIL import Image
    im = Image.open(path).convert("L")
    if im.size != (W, H):
        raise SystemExit(f"{path}: expected {W}x{H}, got {im.size[0]}x{im.size[1]}"
                         f" - run `cardart.py import` to produce it")
    px = im.load()
    lums = [PALETTE[i][0] for i in range(4)]
    return [[min(range(4), key=lambda i: abs(lums[i] - px[x, y])) for x in range(W)]
            for y in range(H)]


# ------------------------------------------------------- image conversion

BAYER = {
    2: [[0, 2], [3, 1]],
    4: [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]],
    8: None,   # built below
}
BAYER[8] = [[0] * 8 for _ in range(8)]
for _y in range(8):
    for _x in range(8):
        v, m = 0, 0
        xc, yc = _x, _x ^ _y
        for _b in range(3):
            v |= ((yc >> _b) & 1) << m
            m += 1
            v |= ((xc >> _b) & 1) << m
            m += 1
        BAYER[8][_y][_x] = v


def convert_image(path, fit="cover", dither="bayer4", contrast=1.0, gamma=1.0,
                  brightness=0.0, invert=False, autolevels=True, sharpen=0.6,
                  box=None, zoom=1.0, focus=0.40):
    """Any image -> [80][64] of GB shade indices, art placed inside the frame box.

    `zoom` < 1 keeps only that fraction of the source, centred horizontally and
    at `focus` vertically (0.40 favours the upper body, where faces live). At
    52x68 in four shades a busy illustration turns to noise; cropping in on the
    subject trades away background nobody can resolve anyway. It does not
    rescue a genuinely dark, formless painting -- nothing does.
    """
    from PIL import Image, ImageOps, ImageEnhance, ImageFilter

    x0, y0, x1, y1 = box or (FRAME_INSET, FRAME_INSET, W - FRAME_INSET, H - FRAME_INSET)
    bw, bh = x1 - x0, y1 - y0

    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        flat = Image.new("RGBA", im.size, (255, 255, 255, 255))
        flat.alpha_composite(im)
        im = flat
    im = im.convert("L")

    if zoom and zoom != 1.0:
        if not 0 < zoom <= 1.0:
            raise SystemExit(f"--zoom must be in (0, 1], got {zoom}")
        w, h = im.size
        cw, ch = int(w * zoom), int(h * zoom)
        ox, oy = (w - cw) // 2, int((h - ch) * focus)
        im = im.crop((ox, oy, ox + cw, oy + ch))

    if autolevels:
        im = ImageOps.autocontrast(im, cutoff=1)
    if gamma != 1.0:
        lut = [min(255, int(255 * ((i / 255.0) ** (1.0 / gamma)))) for i in range(256)]
        im = im.point(lut)
    if contrast != 1.0:
        im = ImageEnhance.Contrast(im).enhance(contrast)
    if brightness:
        im = im.point(lambda v: max(0, min(255, int(v + brightness * 255))))
    if invert:
        im = ImageOps.invert(im)

    if fit == "cover":
        im = ImageOps.fit(im, (bw, bh), Image.LANCZOS, centering=(0.5, 0.45))
    elif fit == "contain":
        im = ImageOps.contain(im, (bw, bh), Image.LANCZOS)
        pad = Image.new("L", (bw, bh), 255)
        pad.paste(im, ((bw - im.width) // 2, (bh - im.height) // 2))
        im = pad
    elif fit == "stretch":
        im = im.resize((bw, bh), Image.LANCZOS)
    else:
        raise SystemExit(f"unknown --fit {fit!r} (cover|contain|stretch)")

    if sharpen:
        im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=int(sharpen * 120),
                                               threshold=2))

    src = [[im.load()[x, y] for x in range(bw)] for y in range(bh)]
    art = _quantise(src, dither)          # GB shades: 0 = lightest

    # ...which is not the same thing as a stored colour index, because BGP is
    # inverted. Without this the picture goes into the ROM as a negative.
    g = [[SHADE_TO_COLOUR[0]] * W for _ in range(H)]
    for y in range(bh):
        for x in range(bw):
            g[y0 + y][x0 + x] = SHADE_TO_COLOUR[art[y][x]]
    return g


def _quantise(src, dither):
    """[h][w] of 0..255 luminance -> [h][w] of GB SHADES, 0 = lightest.

    Shades, not stored colour indices - `convert_image` maps them through BGP.
    """
    h, w = len(src), len(src[0])
    out = [[0] * w for _ in range(h)]
    if dither == "none":
        for y in range(h):
            for x in range(w):
                out[y][x] = 3 - min(3, int(src[y][x] * 4 / 256))
        return out
    if dither.startswith("bayer"):
        n = int(dither[5:])
        m = BAYER[n]
        span = n * n
        for y in range(h):
            for x in range(w):
                # 0..255 -> 0..3 with the matrix biasing the rounding
                v = src[y][x] * (3 * span + span - 1) / 255.0
                lvl = int((v + (span - 1 - m[y % n][x % n])) / span)
                out[y][x] = 3 - max(0, min(3, lvl))
        return out
    if dither in ("fs", "floyd"):
        buf = [[float(src[y][x]) for x in range(w)] for y in range(h)]
        for y in range(h):
            for x in range(w):
                old = buf[y][x]
                lvl = max(0, min(3, int(round(old * 3 / 255.0))))
                new = lvl * 255.0 / 3.0
                err = old - new
                out[y][x] = 3 - lvl
                for dx, dy, f in ((1, 0, 7 / 16), (-1, 1, 3 / 16),
                                  (0, 1, 5 / 16), (1, 1, 1 / 16)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        buf[ny][nx] += err * f
        return out
    raise SystemExit(f"unknown --dither {dither!r} (none|bayer2|bayer4|bayer8|fs)")


# ------------------------------------------------------------- build hook

def art_dir(product):
    return os.path.join(products.data_dir(product), "art")


def load_overrides(product):
    """-> {card_index: [80][64]} from work/<product>/art/NNN.png"""
    d = art_dir(product)
    if not os.path.isdir(d):
        return {}
    out = {}
    for name in sorted(os.listdir(d)):
        if not name.lower().endswith(".png") or name.startswith("_"):
            continue
        m = re.match(r"0*(\d+)", name)
        if not m:
            continue
        n = int(m.group(1))
        if not 1 <= n <= NCARD:
            raise SystemExit(f"{name}: card number {n} out of range 1..{NCARD}")
        out[n - 1] = load_png(os.path.join(d, name))
    return out


def apply_config(rom, overrides):
    """Write replacement pictures into `rom`. -> (n_cards, n_banks_repacked)

    In-place whenever the new stream fits the card's existing slot, so a build
    that changes two cards touches only those two records. A card that outgrows
    its slot triggers a tight repack of its whole bank, which reclaims the ~82
    bytes of unread padding the original encoder left after every record.
    """
    if not overrides:
        return 0, 0
    sl = slots(rom)
    streams = {}
    for c, g in overrides.items():
        streams[c] = gblzss.compress(to_raw(g))

    repack_banks = set()
    for c, s in streams.items():
        bank, cpu, cap = sl[c]
        if len(s) <= cap:
            rom[file_off(bank, cpu):file_off(bank, cpu) + len(s)] = s
        else:
            repack_banks.add(bank)

    for bank in sorted(repack_banks):
        members = sorted(c for c in range(NCARD) if sl[c][0] == bank)
        blobs = []
        for c in members:
            if c in streams:
                blobs.append((c, streams[c]))
            else:
                _, _, off = art_ptr(rom, c)
                n = gblzss.decompress(rom, off, ART_BYTES)[1]
                blobs.append((c, bytes(rom[off:off + n])))
        need = sum(len(b) for _, b in blobs)
        room = BANK_END - BANK_START[bank]
        if need > room:
            over = need - room
            raise SystemExit(
                f"bank ${bank:02X} overflows by {over} bytes ({need} needed, {room} free).\n"
                f"  Re-import the busiest of cards "
                f"{', '.join('#%d' % (c + 1) for c, _ in blobs)} with a flatter\n"
                f"  setting (--dither bayer4 or none compresses far better than fs).")
        cpu = BANK_START[bank]
        for c, b in blobs:
            rom[file_off(bank, cpu):file_off(bank, cpu) + len(b)] = b
            rom[PTR_TABLE + 2 * c:PTR_TABLE + 2 * c + 2] = cpu.to_bytes(2, "little")
            cpu += len(b)
    return len(streams), len(repack_banks)


# ----------------------------------------------------------------- commands

def parse_cards(spec):
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return [n - 1 for n in out]


def cmd_extract(rom, args, product):
    cards = parse_cards(args["cards"]) if "cards" in args else range(NCARD)
    d = os.path.join(products.data_dir(product), "art_src")
    os.makedirs(d, exist_ok=True)
    for c in cards:
        save_png(to_pixels(read_art(rom, c)[0]), os.path.join(d, f"{c + 1:03d}.png"))
    print(f"extracted {len(list(cards))} pictures -> work/{product}/art_src/")


def cmd_show(rom, nums, out, scale=4):
    from PIL import Image, ImageDraw
    ims = [to_image(to_pixels(read_art(rom, n - 1)[0]), scale) for n in nums]
    cw = ims[0].width + 6
    sheet = Image.new("RGB", (cw * len(ims), ims[0].height + 20), (40, 40, 60))
    dr = ImageDraw.Draw(sheet)
    for i, (n, im) in enumerate(zip(nums, ims)):
        sheet.paste(im, (i * cw + 3, 16))
        dr.text((i * cw + 4, 3), f"#{n}", fill=(255, 255, 0))
    sheet.save(out)
    print("wrote", out)


def cmd_budget(rom, product=None):
    """Per-bank space report. Cards sharing a bank share one 16 KB budget, so
    this is the table to read before planning a batch of replacements."""
    sl = slots(rom)
    by_bank = {}
    for c in range(NCARD):
        by_bank.setdefault(sl[c][0], []).append(c)
    new = {}
    if product:
        for c, g in load_overrides(product).items():
            new[c] = len(gblzss.compress(to_raw(g)))
    print(f"card art: {NCARD} pictures, {W}x{H} px, LZSS"
          + (f"   (+ {len(new)} replacement(s) from work/{product}/art/)" if new else ""))
    print("\nbank  cards         used  capacity   spare  avg/card  cap/card")
    total_used = total_room = 0
    for bank in sorted(by_bank):
        cs = by_bank[bank]
        used = sum(new.get(c) or gblzss.decompress(rom, art_ptr(rom, c)[2], ART_BYTES)[1]
                   for c in cs)
        room = BANK_END - BANK_START[bank]
        flag = " <-- OVER" if used > room else ""
        # banks $1E/$1F interleave (#199 sits with $1E, #196-198 with $1F), so
        # print the exact set when it is not a clean run.
        span = (f"#{cs[0] + 1}-{cs[-1] + 1}" if cs[-1] - cs[0] + 1 == len(cs)
                else ",".join(str(c + 1) for c in cs))
        print(f" ${bank:02X}   {span:<11s} {used:6d}    {room:6d}"
              f"  {room - used:6d}    {used // len(cs):5d}     {room // len(cs):5d}{flag}")
        total_used += used
        total_room += room
    print(f"\ntotal {total_used} / {total_room} bytes"
          f"   ({total_room - total_used} spare across all banks)")
    print("A card written IN PLACE must fit its own slot; overflowing one repacks")
    print("its whole bank, after which only the bank's 'cap/card' average matters.")


def cmd_verify(rom):
    bad = 0
    grew = 0
    for c in range(NCARD):
        raw, used = read_art(rom, c)
        if len(raw) != ART_BYTES:
            print(f"card #{c + 1}: short decode"); bad += 1; continue
        g = to_pixels(raw)
        if to_raw(g) != raw:
            print(f"card #{c + 1}: pixel round-trip differs"); bad += 1
        enc = gblzss.compress(raw)
        back, _ = gblzss.decompress(enc, 0, ART_BYTES)
        if back != raw:
            print(f"card #{c + 1}: codec round-trip differs"); bad += 1
        if len(enc) > used:
            grew += 1
    print(f"{NCARD - bad}/{NCARD} cards verified "
          f"(decode -> pixels -> 2bpp -> re-encode -> decode)")
    print(f"our encoder is larger than the original on {grew} card(s); "
          f"all of them still fit their slot" if grew else
          "our encoder is at least as small as the original on every card")
    return 1 if bad else 0


def cmd_import(rom, card, src, opts, product):
    # `--frame none` means the picture bleeds to all four edges, so it gets the
    # whole 64x80 canvas rather than the inset art box.
    frame = None if opts.get("frame") == "none" else frame_template(rom)
    box = (0, 0, W, H) if frame is None else None
    g = convert_image(src, box=box, fit=opts.get("fit", "cover"),
                      dither=opts.get("dither", "bayer4"),
                      contrast=float(opts.get("contrast", 1.0)),
                      gamma=float(opts.get("gamma", 1.0)),
                      brightness=float(opts.get("brightness", 0.0)),
                      invert="invert" in opts,
                      autolevels="nolevels" not in opts,
                      sharpen=float(opts.get("sharpen", 0.6)),
                      zoom=float(opts.get("zoom", 1.0)),
                      focus=float(opts.get("focus", 0.40)))
    if frame:
        apply_frame(g, frame)
    d = art_dir(product)
    os.makedirs(d, exist_ok=True)
    out = os.path.join(d, f"{card:03d}.png")
    save_png(g, out)
    enc = len(gblzss.compress(to_raw(g)))
    cap = slots(rom)[card - 1][2]
    fits = "fits in place" if enc <= cap else "TOO BIG for its slot - the build will repack the bank"
    print(f"wrote {out}")
    print(f"  encodes to {enc} bytes; card #{card}'s slot holds {cap}  ->  {fits}")
    if opts.get("dither", "bayer4") in ("fs", "floyd") and enc > cap:
        print("  tip: --dither bayer4 (or bayer8) compresses much better than fs")
    save_png(g, os.path.join(d, f"_preview_{card:03d}.png"), 4)


def cmd_preview(rom, src, out):
    from PIL import Image, ImageDraw
    frame = frame_template(rom)
    combos = [(f, d) for f in ("cover", "contain")
              for d in ("none", "bayer2", "bayer4", "bayer8", "fs")]
    cols, scale = 5, 3
    cw, ch = W * scale + 8, H * scale + 26
    sheet = Image.new("RGB", (cols * cw, ((len(combos) + cols - 1) // cols) * ch),
                      (40, 40, 60))
    dr = ImageDraw.Draw(sheet)
    for i, (fit, dth) in enumerate(combos):
        g = apply_frame(convert_image(src, fit=fit, dither=dth), frame)
        sheet.paste(to_image(g, scale), ((i % cols) * cw + 4, (i // cols) * ch + 20))
        n = len(gblzss.compress(to_raw(g)))
        dr.text(((i % cols) * cw + 6, (i // cols) * ch + 4),
                f"{fit}/{dth}  {n}B", fill=(255, 255, 0))
    sheet.save(out)
    print("wrote", out)
    print("byte counts are the compressed size; a card slot holds ~1150-1250")


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
            k = a[2:]
            if i + 1 < len(rest) and not rest[i + 1].startswith("--"):
                opts[k] = rest[i + 1]
                i += 2
            else:
                opts[k] = True
                i += 1
        else:
            pos.append(a)
            i += 1
    rom = load_rom()

    if cmd == "extract":
        cmd_extract(rom, opts, product)
    elif cmd == "show":
        cmd_show(rom, [int(p) for p in pos], opts.get("out", "cards.png"))
    elif cmd == "frame":
        blank = SHADE_TO_COLOUR[0]      # show the art box as white, not as ink
        save_png([[blank if v is None else v for v in row] for row in frame_template(rom)],
                 opts.get("out", "frame.png"), 4)
        print("wrote", opts.get("out", "frame.png"),
              f"  (art box is x {FRAME_INSET}..{W - FRAME_INSET - 1}, "
              f"y {FRAME_INSET}..{H - FRAME_INSET - 1} = "
              f"{W - 2 * FRAME_INSET}x{H - 2 * FRAME_INSET} px)")
    elif cmd == "budget":
        cmd_budget(rom, product)
    elif cmd == "verify":
        return cmd_verify(rom)
    elif cmd == "import":
        if len(pos) != 2:
            raise SystemExit("usage: cardart.py import <card#> <image> [options]")
        cmd_import(rom, int(pos[0]), pos[1], opts, product)
    elif cmd == "preview":
        if len(pos) != 1:
            raise SystemExit("usage: cardart.py preview <image> [--out sheet.png]")
        cmd_preview(rom, pos[0], opts.get("out", "preview.png"))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
