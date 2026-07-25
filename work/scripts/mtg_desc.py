#!/usr/bin/env python3
"""Card descriptions for Duel Monsters MTG — condense real MTG flavour to 2x18 tiles.

Creatures: take the card's Scryfall flavour_text, strip attribution/quotes, take
the opening sentence, and greedily wrap it to two <=18-tile lines (overflow
dropped at a word boundary). Cards with no flavour get a generated line from
their creature subtype + colour. Spells get hand-written functional text.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cardtext  # noqa: E402

_DATA = None
LINE = 18


def _load():
    global _DATA
    if _DATA is None:
        # flavour map lives in the session scratch; fall back to empty
        _root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        for p in (os.environ.get("MTG_FLAVOR", ""),
                  os.path.join(_root, "work", "duelmonsters-mtg", "mtg_flavor.json"),
                  os.path.join(os.path.dirname(__file__), "mtg_flavor.json")):
            if p and os.path.exists(p):
                _DATA = json.load(open(p, encoding="utf-8")); break
        else:
            _DATA = {"flavor": {}, "typeline": {}}
    return _DATA


def tiles(s):
    try:
        return len(cardtext.encode(s))
    except Exception:
        return 999


def _encodable(s):
    """Keep only characters the DM1 codec accepts (drop the rest)."""
    out = []
    for ch in s:
        try:
            cardtext.encode(ch if ch != " " else "a")  # space always ok
            out.append(ch)
        except Exception:
            out.append(" ")
    return re.sub(r"\s+", " ", "".join(out)).strip()


def _wrap2(text):
    """Greedily wrap into two <=18-tile lines. Returns (lines, complete) where
    complete is True only if EVERY word fit (no mid-thought truncation)."""
    text = _encodable(text)
    words = text.split()
    l1, i = "", 0
    while i < len(words) and tiles((l1 + " " + words[i]).strip()) <= LINE:
        l1 = (l1 + " " + words[i]).strip(); i += 1
    l2 = ""
    while i < len(words) and tiles((l2 + " " + words[i]).strip()) <= LINE:
        l2 = (l2 + " " + words[i]).strip(); i += 1
    complete = (i == len(words))
    for _ in range(1):  # tidy trailing punctuation
        tgt = 1 if l2 else 0
        ln = (l2 if l2 else l1)
        if ln and ln[-1] not in ".!?" and tiles(ln + ".") <= LINE:
            if tgt: l2 += "."
            else:   l1 += "."
    return [l1, l2], complete


COLOR_PHRASES = {
    "White": ["of law and light.", "sworn to honor.", "clad in armor."],
    "Blue": ["of sea and sky.", "wise and cunning.", "born of cold seas."],
    "Black": ["of death and rot.", "risen from graves.", "steeped in shadow."],
    "Red": ["of fire and rage.", "born of mountains.", "wild and burning."],
    "Green": ["of the deep wood.", "of root and thorn.", "untamed and vast."],
    "Colorless": ["forged of metal.", "wrought by hand.", "cold and tireless."],
}
ALL_PHRASES = {p for v in COLOR_PHRASES.values() for p in v}


def _generated(color, sub, name=""):
    l1 = f"A {color.lower()} {sub}"
    while tiles(l1) > LINE and " " in l1:
        l1 = l1.rsplit(" ", 1)[0]
    opts = COLOR_PHRASES.get(color, ["of Dominaria."])
    return [l1, opts[sum(map(ord, name)) % len(opts)]]


def _clean(flavor):
    t = flavor.replace("\n", " ")
    t = re.sub(r'[""" ]', " ", t).replace('"', "")
    t = re.split(r"\s+[-–—]\s*[A-Z]", t)[0]     # drop "- Attribution"
    return re.sub(r"\s+", " ", t).strip()


def _subtype(typeline):
    for sep in ("—", "–", "-"):
        if sep in (typeline or ""):
            sub = typeline.split(sep, 1)[1].strip()
            return sub.split()[0] if sub else "being"
    return "being"


def for_creature(mtg_name, color):
    d = _load()
    nm = mtg_name.lower()
    fl = d["flavor"].get(nm)
    if fl:
        sents = re.split(r"(?<=[.!?])\s+", _clean(fl))
        best, best_fill = None, 0
        for s in sents:
            s = s.strip()
            if len(s) < 10:
                continue
            lines, complete = _wrap2(s.rstrip(".!?"))
            fill = tiles(lines[0]) + tiles(lines[1])
            if complete and lines[0] and fill > best_fill:  # richest sentence that fits whole
                best, best_fill = lines, fill
        if best:
            return best
    sub = _subtype(d["typeline"].get(nm, "")).lower()
    return _generated(color, sub, nm)


# functional spell descriptions (name in cards.json -> 2 lines)
SPELL = {
    "Holy Strength": ["Fills a creature", "with holy might."],
    "Holy Armor": ["Wards a creature", "with holy steel."],
    "Blessing": ["A blessing lends", "fleeting power."],
    "Unholy Strength": ["Dark power swells", "a creature's form."],
    "Firebreathing": ["The creature now", "breathes fire."],
    "Web": ["Webs bind and", "guard a creature."],
    "Aspect of Wolf": ["The wild's fury", "grips a creature."],
    "Unstable Mutation": ["Wild mutation:", "a great +3/+3."],
    "Coral Helm": ["A coral helm,", "granting +3/+3."],
    "Tawnos Weaponry": ["Ancient armaments", "grant +2/+2."],
    "Thrull Retainer": ["A loyal thrull", "shields its lord."],
    "Shatter": ["Shatter and seal", "all artifacts."],
    "Forest": ["Forest field:", "greens grow."],
    "Wastes": ["Barren field:", "colorless rise."],
    "Mountain": ["Mountain field:", "reds burn hot."],
    "Plains": ["Plains field:", "whites stand tall."],
    "Island": ["Island field:", "blues surge."],
    "Swamp": ["Swamp field:", "blacks fester."],
    "Wrath of God": ["Wrath of God:", "all monsters die."],
    "Terror": ["Terror destroys", "the foe's monsters."],
    "Healing Salve": ["A salve restores", "your life points."],
    "Lightning Bolt": ["A bolt strikes", "the foe."],
    "Psionic Blast": ["A mind blast", "sears the foe."],
    "Fireball": ["A fireball burns", "the foe."],
    "Disintegrate": ["Disintegrate the", "foe with force."],
    "Drain Life": ["Drain the foe's", "very life away."],
    # --- added equips ---
    "Giant Growth": ["Sudden growth:", "a mighty +3/+3."],
    "Berserk": ["Berserk fury -", "attack soars."],
    "Cocoon": ["Wrapped safe,", "then reborn."],
    "DivineTransform": ["Divine power:", "a great +3/+3."],
    "InfinitAuthority": ["Authority guards", "its bearer."],
    "Giant Strength": ["The might of", "giants, +2/+2."],
    "The Brute": ["Brute force lends", "raw power."],
    "Rapid Fire": ["A flurry of blows", "before battle."],
    "Burrowing": ["Burrows through", "the mountain."],
    "Fishliver Oil": ["Slick with oil,", "it slips past."],
    "Elven Lyre": ["The lyre sings;", "a creature swells."],
    "Zelyon Sword": ["A keen blade,", "granting +2/+2."],
    "Spirit Shield": ["A spirit shield", "guards its bearer."],
    "Living Armor": ["Armor that lives", "and shields."],
    "Transmogrant": ["Ashnod's work:", "flesh into metal."],
    # --- added heals / control ---
    "Balm Restoration": ["A healing balm", "restores you."],
    "DarkHeartOfWood": ["The wood's heart", "gives back life."],
    "Fountain of Youth": ["Drink deep and", "be restored."],
    "Ivory Cup": ["The ivory cup", "brims with life."],
    "Siren's Call": ["The siren calls;", "all must attack."],
    "Festival": ["A festival - none", "may attack now."],
    "Marsh Gas": ["Foul gas saps", "every creature."],
    "Amnesia": ["The foe's hand", "is laid bare."],
    "Dance of Many": ["A phantom double", "takes the field."],
}


def for_spell(name, color):
    """Functional two-line text for a spell; falls back to a colour-themed line."""
    if name in SPELL:
        return SPELL[name]
    return _wrap2(f"A {color.lower()} spell of Dominaria")[0]
FILLER = ["A stray token", "of Dominaria."]


def for_card(card):
    """card = a cards.json entry. Uses 'mtg_name' if present else 'name'."""
    nm = card["name"]
    if nm in SPELL:
        return SPELL[nm]
    if card.get("_filler"):
        return FILLER
    return for_creature(card.get("mtg_name", nm), card["color"])
