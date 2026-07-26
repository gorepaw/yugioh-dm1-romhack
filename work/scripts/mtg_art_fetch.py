#!/usr/bin/env python3
"""Fetch source artwork for Duel Monsters MTG cards into work/duelmonsters-mtg/art_in/.

Feeds the same pipeline Duel Monsters Kaizo uses (docs/CARDART.md):

    mtg_art_fetch.py --cards 1-13          -> art_in/NNN.jpg   (gitignored)
    cardart.py import 1 art_in/001.jpg --product duelmonsters-mtg \
        --fit cover --dither bayer8        -> art/001.png       (committed)

Scryfall's `art_crop` is the right image: it is the illustration already cropped
free of frame, title and text box, which is exactly the 52x68 art box we need.
Anything else would need the frame cropped off by hand.

Card id -> real card is rebuilt the way mtg_assemble.py does it (creatures.json
minus _cuts.json, in order), because cards.json stores the *shortname* that fits
DM1's name budget -- "Palladia" is not a card Scryfall has heard of.

Scryfall asks for a descriptive User-Agent and 50-100 ms between requests; this
waits 120 ms and caches, so a re-run costs nothing. Artists are recorded in
art_in/_credits.json -- they are the reason this art exists and the credits file
is what makes acknowledging them possible.

CLI:
  python mtg_art_fetch.py                  every creature that has no source yet
  python mtg_art_fetch.py --cards 1-13,45  just these card numbers
  python mtg_art_fetch.py --report         what is missing, no network
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import products  # noqa: E402

PRODUCT = "duelmonsters-mtg"
UA = "dm1-romhack-cardart/1.0 (personal romhack; contact via github.com/gorepaw)"
DELAY = 0.12          # Scryfall asks for 50-100 ms; be a good citizen
NCREATURE = 300


def roster():
    """[(card_id, scryfall_name, set_code)] for the 300 creature slots."""
    pool = json.load(open(products.data_path("creatures.json", PRODUCT), encoding="utf-8"))
    cutp = products.data_path("_cuts.json", PRODUCT)
    if os.path.exists(cutp):
        cut = set(json.load(open(cutp, encoding="utf-8")))
        pool = [c for c in pool if c.get("shortname", c["name"]) not in cut]
    return [(i + 1, c["name"], c.get("set", "").lower())
            for i, c in enumerate(pool[:NCREATURE])]


def parse_cards(spec):
    out = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            out.update(range(int(a), int(b) + 1))
        elif part:
            out.add(int(part))
    return out


def get(url, accept="application/json"):
    # Scryfall rejects any request lacking BOTH User-Agent and Accept with a 400
    # whose body explains it -- worth reading rather than assuming a bad query.
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def fetch_one(name, setcode):
    """(image_bytes, artist, scryfall_id) or raises. Falls back off the set."""
    base = "https://api.scryfall.com/cards/named?exact=" + urllib.parse.quote(name)
    for url in (f"{base}&set={setcode}" if setcode else base, base):
        try:
            card = json.loads(get(url))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue          # not in that set -- try any printing
            raise
        uris = card.get("image_uris") or {}
        # Double-faced cards keep images on the faces instead of the card.
        if not uris and card.get("card_faces"):
            uris = card["card_faces"][0].get("image_uris") or {}
        if "art_crop" not in uris:
            continue
        time.sleep(DELAY)
        return (get(uris["art_crop"], accept="image/*"),
                card.get("artist", "?"), card.get("id", ""))
    raise LookupError(f"no art_crop for {name!r} ({setcode or 'any set'})")


def main(argv):
    want = None
    report = "--report" in argv
    if "--cards" in argv:
        want = parse_cards(argv[argv.index("--cards") + 1])

    dest = os.path.join(products.data_dir(PRODUCT), "art_in")
    os.makedirs(dest, exist_ok=True)
    credpath = os.path.join(dest, "_credits.json")
    creds = json.load(open(credpath, encoding="utf-8")) if os.path.exists(credpath) else {}

    todo, have = [], 0
    for cid, name, setcode in roster():
        if want is not None and cid not in want:
            continue
        if os.path.exists(os.path.join(dest, f"{cid:03d}.jpg")):
            have += 1
            continue
        todo.append((cid, name, setcode))

    if report or not todo:
        print(f"{have} source image(s) present, {len(todo)} missing"
              + (f": {', '.join(str(c) for c, _, _ in todo[:20])}" if todo else ""))
        return 0

    print(f"fetching {len(todo)} (have {have})")
    ok = 0
    fails = []
    for cid, name, setcode in todo:
        try:
            data, artist, sid = fetch_one(name, setcode)
        except Exception as e:
            fails.append((cid, name, f"{type(e).__name__}: {e}"))
            print(f"  #{cid:3d} {name:26s} FAILED {e}")
            continue
        open(os.path.join(dest, f"{cid:03d}.jpg"), "wb").write(data)
        creds[str(cid)] = {"card": name, "set": setcode.upper(),
                           "artist": artist, "scryfall_id": sid}
        ok += 1
        print(f"  #{cid:3d} {name:26s} {len(data):7,d} B   art by {artist}")
        time.sleep(DELAY)

    json.dump(creds, open(credpath, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"\n{ok} fetched, {len(fails)} failed -> {os.path.relpath(dest, products.ROOT)}")
    for cid, name, why in fails:
        print(f"  #{cid} {name}: {why}")
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
