#!/usr/bin/env python3
"""Text tooling for Yu-Gi-Oh! Duel Monsters (GB), English build.

Uses Darrman's text.tbl (byte <-> character map) to search and decode the
custom-encoded English text stored in the ROM.

Usage:
  python text_tool.py <table.tbl> <rom.gb> search "<text>"
  python text_tool.py <table.tbl> <rom.gb> decode <offset> <length>

'search' encodes <text> literally (one byte per character) and reports every
ROM offset where those bytes occur, with decoded context around each hit.
Pick ligature-free substrings (avoid il/li/ll/l!/'s/'t) for reliable matches.
"""
import sys


def load_table(path):
    """Parse 'HH=VALUE' lines into {byte: string}."""
    m = {}
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        if key.startswith("/"):        # insertion-tool "end token" marker
            key = key[1:]
        if len(key) != 2:
            continue
        try:
            b = int(key, 16)
        except ValueError:
            continue
        m[b] = val.replace("\\n", "")
    return m


def reverse_single(m):
    """Map single-character values -> byte (first/lowest wins)."""
    r = {}
    for b, v in m.items():
        if len(v) == 1:
            r.setdefault(v, b)
    return r


def encode_literal(s, rev):
    out = bytearray()
    for ch in s:
        if ch not in rev:
            raise ValueError(f"character {ch!r} is not in the table")
        out.append(rev[ch])
    return bytes(out)


def decode(data, m):
    return "".join(m.get(b, f"<{b:02X}>") for b in data)


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return 1
    tbl = load_table(sys.argv[1])
    rom = open(sys.argv[2], "rb").read()
    cmd = sys.argv[3]

    if cmd == "search":
        text = sys.argv[4]
        needle = encode_literal(text, reverse_single(tbl))
        print(f"search {text!r} -> bytes [{needle.hex(' ')}]")
        hits, start = [], 0
        while True:
            i = rom.find(needle, start)
            if i < 0:
                break
            hits.append(i)
            start = i + 1
        print(f"{len(hits)} hit(s)")
        for i in hits:
            ctx = rom[max(0, i - 6):i + len(needle) + 12]
            print(f"  @0x{i:06X}  ...{decode(ctx, tbl)}...")

    elif cmd == "decode":
        off, length = int(sys.argv[4], 0), int(sys.argv[5], 0)
        print(f"@0x{off:06X}: {decode(rom[off:off + length], tbl)}")

    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
