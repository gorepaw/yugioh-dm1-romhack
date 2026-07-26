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
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import products  # noqa: E402

PRODUCT = "duelmonsters-mtg"
UA = "dm1-romhack-cardart/1.0 (personal romhack; contact via github.com/gorepaw)"
DELAY = 0.25          # Scryfall asks 50-100 ms; go slower, we are not in a hurry
SCRYFALL = "https://api.scryfall.com"
NCREATURE = 300


# DM1's name budget forces abbreviations that Scryfall has never heard of, and a
# few slots are invented filler. Map them back to a real card to illustrate.
NAME_OVERRIDES = {
    "DivineTransform": "Divine Transformation",
    "InfinitAuthority": "Infinite Authority",
    "Tawnos Weaponry": "Tawnos's Weaponry",
    "DarkHeartOfWood": "Dark Heart of the Wood",
    "Balm Restoration": "Ivory Cup",          # invented heal card; reuse the cup
    "Wastes": "Wasteland",                    # our colourless "land" slot
    # The 15 filler tokens are invented names; illustrate each with a real
    # creature of that kind from our own era so they don't keep Konami's art.
    "Rat": "Sewer Rats", "Bat": "Sengir Bats", "Elf": "Llanowar Elves",
    "Orc": "Orcish Artillery", "Imp": "Wall of Wonder", "Ape": "Kird Ape",
    "Eel": "Giant Slug", "Cat": "Savannah Lions", "Bee": "Killer Bees",
    "Fox": "Scavenging Ghoul", "Goo": "Blight", "Elk": "Grizzly Bears",
    "Owl": "Birds of Paradise", "Ram": "Wall of Stone", "Hen": "Thicket Basilisk",
}


def roster(include_spells=True):
    """[(card_id, scryfall_name, set_code)] over every slot we can illustrate."""
    pool = json.load(open(products.data_path("creatures.json", PRODUCT), encoding="utf-8"))
    cutp = products.data_path("_cuts.json", PRODUCT)
    if os.path.exists(cutp):
        cut = set(json.load(open(cutp, encoding="utf-8")))
        pool = [c for c in pool if c.get("shortname", c["name"]) not in cut]
    out = [(i + 1, c["name"], c.get("set", "").lower())
           for i, c in enumerate(pool[:NCREATURE])]
    if include_spells:
        # Read the slot tables from the assembler rather than restating them,
        # so adding a spell there cannot silently leave it without a picture.
        import mtg_assemble as A
        for slot, (nm, _col) in zip(A.EQUIP_SLOTS, A.EQUIPS):
            out.append((slot, NAME_OVERRIDES.get(nm, nm), ""))
        for slot, (nm, _col) in A.FIXED.items():
            out.append((slot, NAME_OVERRIDES.get(nm, nm), ""))
        for k, cid in enumerate(range(351, 366)):
            nm = A.FILLER[k]
            out.append((cid, NAME_OVERRIDES.get(nm, nm), ""))
    return sorted(out)


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


def get(url, accept="application/json", data=None, tries=5):
    """GET/POST with 429 backoff.

    Scryfall rejects any request lacking BOTH User-Agent and Accept with a 400
    whose body explains it -- worth reading rather than assuming a bad query.
    Hammering it earns a 429 instead, so back off and honour Retry-After.
    """
    hdr = {"User-Agent": UA, "Accept": accept}
    if data is not None:
        hdr["Content-Type"] = "application/json"
    delay = 1.0
    for attempt in range(tries):
        req = urllib.request.Request(url, headers=hdr, data=data)
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == tries - 1:
                raise
            wait = float(e.headers.get("Retry-After") or delay)
            time.sleep(wait)
            delay *= 2


def lookup(entries):
    """[(cid, name, set)] -> {cid: (art_crop_url, artist, scryfall_id)}.

    Uses /cards/collection, which takes 75 identifiers per request: 350 cards
    become 5 calls instead of 350, which is the difference between being a good
    API citizen and being throttled.
    """
    found, pending = {}, list(entries)
    for use_set in (True, False):        # second pass drops the set constraint
        misses = []
        for i in range(0, len(pending), 75):
            chunk = pending[i:i + 75]
            ids = [({"name": n, "set": s} if use_set and s else {"name": n})
                   for _, n, s in chunk]
            body = json.dumps({"identifiers": ids}).encode()
            res = json.loads(get(SCRYFALL + "/cards/collection", data=body))
            by_name = {}
            for card in res.get("data", []):
                by_name.setdefault(card["name"].lower(), card)
            for cid, name, setcode in chunk:
                card = by_name.get(name.lower())
                uris = (card or {}).get("image_uris") or {}
                if not uris and card and card.get("card_faces"):
                    uris = card["card_faces"][0].get("image_uris") or {}
                if "art_crop" in uris:
                    found[cid] = (uris["art_crop"], card.get("artist", "?"),
                                  card.get("id", ""))
                else:
                    misses.append((cid, name, setcode))
            time.sleep(DELAY)
        pending = misses
        if not pending:
            break

    # Last resort: fuzzy match, one request each. Arabian Nights names carry
    # diacritics our ASCII card data drops -- "Juzam Djinn" is really
    # "Juzam Djinn" with an accented a -- and exact lookup cannot see through that.
    still = []
    for cid, name, setcode in pending:
        try:
            card = json.loads(get(SCRYFALL + "/cards/named?fuzzy="
                                  + urllib.parse.quote(name)))
            uris = card.get("image_uris") or {}
            if not uris and card.get("card_faces"):
                uris = card["card_faces"][0].get("image_uris") or {}
            if "art_crop" in uris:
                found[cid] = (uris["art_crop"], card.get("artist", "?"),
                              card.get("id", ""))
                print(f"  fuzzy: {name!r} -> {card['name']!r}")
            else:
                still.append((cid, name, setcode))
        except Exception:
            still.append((cid, name, setcode))
        time.sleep(DELAY)
    return found, still


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
    urls, missing = lookup(todo)
    print(f"resolved {len(urls)}/{len(todo)} via /cards/collection")
    names = {cid: (n, s) for cid, n, s in todo}

    ok = 0
    fails = [(cid, n, "not on Scryfall") for cid, n, _ in missing]
    for cid, (url, artist, sid) in sorted(urls.items()):
        try:
            data = get(url, accept="image/*")
        except Exception as e:
            fails.append((cid, names[cid][0], f"{type(e).__name__}: {e}"))
            continue
        open(os.path.join(dest, f"{cid:03d}.jpg"), "wb").write(data)
        creds[str(cid)] = {"card": names[cid][0], "set": names[cid][1].upper(),
                           "artist": artist, "scryfall_id": sid}
        ok += 1
        if ok % 25 == 0:
            print(f"  downloaded {ok}/{len(urls)}")
        time.sleep(DELAY)

    json.dump(creds, open(credpath, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"\n{ok} fetched, {len(fails)} failed -> {os.path.relpath(dest, products.ROOT)}")
    for cid, name, why in fails:
        print(f"  #{cid} {name}: {why}")
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
