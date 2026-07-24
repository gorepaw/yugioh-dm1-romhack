#!/usr/bin/env python3
"""The game's text codec, built from the character table rather than hardcoded.

Bytes map to characters through Darrman's `text.tbl`. Most bytes are one
character, but a handful are ligatures that squash two glyphs into one tile
(`il` `li` `ll` `l!` `'s` `'t`), plus control codes rendered as `[Line]`,
`[CardName]` and friends. Encoding therefore has to be longest-match-first, or
"ll" would come back as two tiles and every downstream pointer would shift.

Note `0x00` is SPACE, not a terminator — card names and descriptions are
delimited by their pointer tables, not by a sentinel byte.

Verified: all 365 card names and all 365 descriptions survive
decode -> encode byte-identically.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import text_tool  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TBL = os.path.join(ROOT, "reference", "DM1Translation", "Insertion", "text.tbl")

_dec = None   # {byte: str}
_enc = None   # {str: byte}
_maxlen = 1


def _load():
    global _dec, _enc, _maxlen
    if _dec is not None:
        return
    if not os.path.exists(TBL):
        raise SystemExit(
            f"missing character table: {TBL}\n"
            "It comes from Darrman's translation and is not redistributed here:\n"
            "  git clone https://github.com/Darrman/DM1Translation.git "
            "reference/DM1Translation")
    _dec = text_tool.load_table(TBL)
    _enc = {}
    for b, v in _dec.items():
        if v and v not in _enc:     # lowest byte wins on duplicates
            _enc[v] = b
    _maxlen = max(len(v) for v in _enc)


def decode(data):
    _load()
    return "".join(_dec.get(b, f"<{b:02X}>") for b in data)


def encode(s):
    """Longest-match-first. Raises ValueError on anything unrepresentable."""
    _load()
    out, i = bytearray(), 0
    while i < len(s):
        for ln in range(min(_maxlen, len(s) - i), 0, -1):
            chunk = s[i:i + ln]
            if chunk in _enc:
                out.append(_enc[chunk])
                i += ln
                break
        else:
            raise ValueError(f"character {s[i]!r} (at {i}) is not in the text table")
    return bytes(out)


def roundtrips(data):
    """True if these bytes survive decode -> encode unchanged."""
    try:
        return encode(decode(data)) == bytes(data)
    except ValueError:
        return False
