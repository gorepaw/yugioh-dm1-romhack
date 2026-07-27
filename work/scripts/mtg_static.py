#!/usr/bin/env python3
"""Replace the full-screen picture screens for Duel Monsters MTG.

Six of the 21 static screens are pictures rather than font-drawn layouts (see
docs/SCREENS.md §2). Three of them carry text baked into the tiles, which is the
thing to be careful about:

  title       the four MENU LABELS live in the picture. Replace the whole screen
              and the player is choosing between four blank lines. So the art is
              composited UNDER the stock menu column instead, which is kept
              pixel-for-pixel.
  simon       the boss's NAME is drawn into the picture, so a replacement has to
  pegasus     render the new name itself. These three are the game's boss
  yami-yugi   intro cards -> Mishra, Urza, Yawgmoth.
  ruins       pure scenery, safe to replace outright.
  cast        pure art.

The Konami / KCE Shinjuku / copyright boot splashes are deliberately NOT touched:
they are the real publisher's logos and replacing them would misrepresent who
made the underlying game.

Budget is distinct TILES, not bytes -- 360 cells, and a cap per screen that is
often 256 but sometimes lower. mtg_portraits.reduce_tiles does the merging.

CLI:
  python mtg_static.py fetch
  python mtg_static.py convert
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mtg_portraits as P   # noqa: E402  (reduce_tiles)
import products            # noqa: E402
import screens             # noqa: E402

PRODUCT = "duelmonsters-mtg"
FONT = "C:/Windows/Fonts/BOOKOSB.TTF"     # serif, closest to the stock nameplate

# screen -> (source card art, caption drawn into the picture or None)
PLAN = {
    "yami-yugi": ("Yawgmoth, Thran Physician", "Yawgmoth"),
    "pegasus":   ("Urza, Lord High Artificer", "Urza"),
    "simon":     ("Mishra, Artificer Prodigy", "Mishra"),
    "ruins":     ("Ruins of Trokair", None),
    "cast":      ("Sword of the Ages", None),
    "title":     ("Urza's Tower", None),
}


def src_dir():
    return os.path.join(products.data_dir(PRODUCT), "screens_in")


def cmd_fetch(rom):
    import mtg_art_fetch as F
    import time
    d = src_dir()
    os.makedirs(d, exist_ok=True)
    todo = [(i, card, "") for i, (name, (card, _cap)) in enumerate(PLAN.items())
            if not os.path.exists(os.path.join(d, f"{name}.jpg"))]
    keys = list(PLAN)
    if not todo:
        print("all static sources present")
        return 0
    urls, missing = F.lookup(todo)
    for i, (url, artist, sid) in sorted(urls.items()):
        name = keys[i]
        open(os.path.join(d, f"{name}.jpg"), "wb").write(F.get(url, accept="image/*"))
        print(f"  {name:11s} {PLAN[name][0]:28s} art by {artist}")
        time.sleep(F.DELAY)
    for i, c, _ in missing:
        print(f"  {keys[i]}: NOT FOUND ({c})")
    return 1 if missing else 0


def caption(im, text, h):
    """Draw the boss's name into the lower band, as the stock screens do."""
    from PIL import ImageDraw, ImageFont
    dr = ImageDraw.Draw(im)
    size = 22
    while size > 9:
        try:
            f = ImageFont.truetype(FONT, size)
        except OSError:
            f = ImageFont.load_default()
            break
        if dr.textlength(text, font=f) <= 148:
            break
        size -= 1
    box = dr.textbbox((0, 0), text, font=f)
    tw, th = box[2] - box[0], box[3] - box[1]
    x, y = (160 - tw) // 2 - box[0], h - th - 10 - box[1]
    # a dark plate behind the glyphs so the name survives posterising
    dr.rectangle([0, y + box[1] - 3, 160, y + box[1] + th + 4], fill=0)
    dr.text((x, y), text, fill=255, font=f)
    return im


def title_plate(im):
    """Draw the game's name into the top band, where the stock logo lived.

    Replacing the title art without this leaves a game that never says what it
    is. The band is y 0-74; everything below belongs to the menu and the
    copyright line.
    """
    from PIL import ImageDraw, ImageFont
    dr = ImageDraw.Draw(im)

    def fit(text, want, lo=8):
        size = want
        while size > lo:
            try:
                f = ImageFont.truetype(FONT, size)
            except OSError:
                return ImageFont.load_default()
            if dr.textlength(text, font=f) <= 152:
                return f
            size -= 1
        return ImageFont.truetype(FONT, lo)

    dr.rectangle([0, 6, 160, 70], fill=0)          # dark plate, so text survives
    for text, y, want in (("DUEL MONSTERS", 12, 20), ("MTG", 36, 30)):
        f = fit(text, want)
        b = dr.textbbox((0, 0), text, font=f)
        dr.text(((160 - (b[2] - b[0])) // 2 - b[0], y - b[1]), text, fill=255, font=f)
    return im


def cmd_convert(rom):
    from PIL import Image
    infos = {i["name"]: i for i in screens.static_info(rom)}
    out_dir = screens.screens_dir(PRODUCT)
    os.makedirs(out_dir, exist_ok=True)
    stock_dir = os.path.join(products.data_dir(PRODUCT), "screens_src")

    for name, (card, cap_text) in PLAN.items():
        src = os.path.join(src_dir(), f"{name}.jpg")
        if not os.path.exists(src):
            print(f"  {name}: no source, skipped")
            continue
        info = infos[name]
        W, H = screens.SCREEN_W * 8, screens.SCREEN_H * 8      # 160x144

        im = Image.open(src).convert("L")
        # fill the 160x144 frame from the middle of the art
        w, h = im.size
        want = W / H
        if w / h > want:
            nw = int(h * want)
            im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else:
            nh = int(w / want)
            im = im.crop((0, int((h - nh) * 0.25), w, int((h - nh) * 0.25) + nh))
        im = im.resize((W, H), Image.LANCZOS)
        if cap_text:
            im = caption(im, cap_text, H)
        if name == "title":
            im = title_plate(im)
        tmp = os.path.join(out_dir, f"_src_{name}.png")
        im.save(tmp)

        px = screens.convert_image(tmp, W, H, info["bgp"], dither="none",
                                   fit="stretch", contrast=1.0)
        os.remove(tmp)

        if name == "title":
            # Keep the stock menu labels and the copyright notice EXACTLY. The
            # menu block is the only thing telling the player what they are
            # choosing, and the 1998 Konami line is a statement about the
            # underlying game that stays true. Read off the screen with a grid:
            # menu x>=98 y 78-118, copyright reaches further LEFT, to x=66.
            stock = screens.load_png(os.path.join(stock_dir, "title.png"),
                                     info["bgp"], screens.SCREEN_W, screens.SCREEN_H)
            for x0, y0, x1, y1 in ((96, 76, W, 118), (64, 114, W, H)):
                for y in range(y0, y1):
                    for x in range(x0, x1):
                        px[y][x] = stock[y][x]

        px, n = P.reduce_tiles(px, screens.SCREEN_W, screens.SCREEN_H, info["cap_tiles"])
        screens.save_png(px, info["bgp"], os.path.join(out_dir, f"{name}.png"))
        screens.save_png(px, info["bgp"],
                         os.path.join(out_dir, f"_preview_{name}.png"), 3)
        flag = "  <-- OVER" if n > info["cap_tiles"] else ""
        print(f"  {name:11s} {n:3d}/{info['cap_tiles']} tiles"
              + (f'  caption "{cap_text}"' if cap_text else "") + flag)
    return 0


def main(argv):
    rom = screens.load_rom()
    cmd = argv[0] if argv else "help"
    if cmd == "fetch":
        return cmd_fetch(rom)
    if cmd == "convert":
        return cmd_convert(rom)
    print(__doc__)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
