#!/usr/bin/env python3
"""Minimal IPS patch tool: check or apply.

Usage:
  python ips_tool.py check <rom> <ips>
  python ips_tool.py apply <rom> <ips> <out>

'check' reports whether <rom> already contains the bytes <ips> would write
(i.e. the ROM is already patched) or differs (clean / unpatched).
"""
import sys


def parse_ips(b):
    if b[:5] != b"PATCH":
        raise ValueError("Not an IPS file (missing PATCH header)")
    records = []
    i, n = 5, len(b)
    while i < n:
        if b[i:i + 3] == b"EOF":
            break
        offset = int.from_bytes(b[i:i + 3], "big"); i += 3
        length = int.from_bytes(b[i:i + 2], "big"); i += 2
        if length == 0:  # RLE record
            run = int.from_bytes(b[i:i + 2], "big"); i += 2
            val = b[i]; i += 1
            data = bytes([val]) * run
        else:
            data = b[i:i + length]; i += length
        records.append((offset, data))
    return records


def check(rom, records):
    match = mismatch = beyond = matched_bytes = total_bytes = 0
    samples = []
    for offset, data in records:
        end = offset + len(data)
        total_bytes += len(data)
        if end > len(rom):
            beyond += 1
            continue
        cur = rom[offset:end]
        if cur == data:
            match += 1
            matched_bytes += len(data)
        else:
            mismatch += 1
            if len(samples) < 6:
                samples.append((offset, cur[:8], data[:8]))
    return match, mismatch, beyond, matched_bytes, total_bytes, samples


def apply(rom, records):
    rom = bytearray(rom)
    for offset, data in records:
        end = offset + len(data)
        if end > len(rom):
            rom.extend(b"\x00" * (end - len(rom)))
        rom[offset:end] = data
    return bytes(rom)


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return 1
    mode, rom_path, ips_path = sys.argv[1], sys.argv[2], sys.argv[3]
    rom = open(rom_path, "rb").read()
    records = parse_ips(open(ips_path, "rb").read())

    if mode == "check":
        match, mismatch, beyond, mb, tb, samples = check(rom, records)
        total = len(records)
        print(f"IPS records: {total}")
        print(f"  already-patched (match): {match}")
        print(f"  differ (unpatched):      {mismatch}")
        print(f"  beyond ROM end:          {beyond}")
        print(f"  bytes matched: {mb}/{tb}")
        if match == total:
            print("VERDICT: ROM is ALREADY PATCHED (every record already matches).")
        elif mismatch >= match:
            print("VERDICT: ROM is UNPATCHED / clean (most records differ).")
        else:
            print("VERDICT: MIXED - inspect samples below.")
        for off, cur, want in samples:
            print(f"  @0x{off:06X}: rom={cur.hex()} patch={want.hex()}")
    elif mode == "apply":
        if len(sys.argv) < 5:
            print("apply needs an output path"); return 1
        out = apply(rom, records)
        open(sys.argv[4], "wb").write(out)
        print(f"Wrote {len(out)} bytes to {sys.argv[4]}")
    else:
        print(__doc__); return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
