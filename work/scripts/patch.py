#!/usr/bin/env python3
"""Emit a distributable BPS patch (built ROM - base ROM).

We can't ship the built .gb: it is 1 MB of which almost all is Konami's 1998
game, so publishing it would be distributing the game rather than our edits.
A patch holds only the difference. The player supplies their own legally
dumped ROM and applies the patch locally, which is how every romhack ships.

BPS over IPS on purpose: BPS stores a CRC32 of the source, the target and the
patch itself, so applying it to the wrong dump fails loudly instead of
producing a silently corrupt ROM. IPS has no such check, and "my game crashes
at the title screen" is almost always a wrong-base-ROM report.

Output: dist/<product>-<md5-prefix>.bps, plus dist/<product>.md5 recording the
expected base and target hashes so a mismatch is diagnosable from the repo.

CLI:
  python patch.py [--product NAME]        build patch from build/<product>-hack.gb
  python patch.py verify [--product NAME] re-apply the patch and check it round-trips
"""
import hashlib
import os
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import products  # noqa: E402

ROOT = products.ROOT
BASE = os.path.join(ROOT, "roms", "dm1-english.gb")


def _num(n):
    """BPS variable-length number: 7 bits/byte, high bit marks the last byte.

    Note the `n -= 1` — BPS numbers are biased so that each continuation byte
    encodes a value one greater than plain base-128 would, which is why a
    naive varint encoder produces patches Flips rejects.
    """
    out = bytearray()
    while True:
        x = n & 0x7F
        n >>= 7
        if n == 0:
            out.append(0x80 | x)
            return bytes(out)
        out.append(x)
        n -= 1


def encode(source, target, metadata=b""):
    """Minimal BPS: SourceRead over matching runs, TargetRead over differing ones.

    A full encoder would also emit SourceCopy/TargetCopy to exploit moved or
    repeated blocks. We don't need it — our edits are scattered small writes
    into an otherwise identical image, so run-matching already gets the patch
    down to a few KB, and this stays simple enough to audit.
    """
    patch = bytearray(b"BPS1")
    patch += _num(len(source)) + _num(len(target)) + _num(len(metadata)) + metadata

    common = min(len(source), len(target))
    pos = 0
    pending = bytearray()   # differing bytes not yet flushed as a TargetRead

    def flush():
        if pending:
            patch.extend(_num(((len(pending) - 1) << 2) | 1))  # 1 = TargetRead
            patch.extend(pending)
            pending.clear()

    while pos < common:
        if source[pos] == target[pos]:
            run = pos
            while run < common and source[run] == target[run]:
                run += 1
            flush()
            patch.extend(_num(((run - pos - 1) << 2) | 0))     # 0 = SourceRead
            pos = run
        else:
            pending.append(target[pos])
            pos += 1
    # Anything past the shared length can only come from the target.
    pending.extend(target[common:])
    flush()

    patch += zlib.crc32(source).to_bytes(4, "little")
    patch += zlib.crc32(target).to_bytes(4, "little")
    patch += zlib.crc32(bytes(patch)).to_bytes(4, "little")
    return bytes(patch)


def _read_num(buf, i):
    n, shift = 0, 0
    while True:
        x = buf[i]
        i += 1
        n += (x & 0x7F) << shift
        if x & 0x80:
            return n, i
        shift += 7
        n += 1 << shift


def apply(source, patch):
    """Reference decoder — used by `verify` so we never ship an unproven patch."""
    if patch[:4] != b"BPS1":
        raise ValueError("not a BPS patch")
    if zlib.crc32(patch[:-4]) != int.from_bytes(patch[-4:], "little"):
        raise ValueError("patch is corrupt (self-checksum mismatch)")
    if zlib.crc32(source) != int.from_bytes(patch[-12:-8], "little"):
        raise ValueError("wrong base ROM (source checksum mismatch)")

    i = 4
    src_size, i = _read_num(patch, i)
    tgt_size, i = _read_num(patch, i)
    meta_size, i = _read_num(patch, i)
    i += meta_size
    if len(source) != src_size:
        raise ValueError(f"base ROM is {len(source)} bytes, patch expects {src_size}")

    out = bytearray()
    src_rel = tgt_rel = 0
    end = len(patch) - 12
    while i < end:
        cmd, i = _read_num(patch, i)
        action, length = cmd & 3, (cmd >> 2) + 1
        if action == 0:                                   # SourceRead
            out.extend(source[len(out):len(out) + length])
        elif action == 1:                                 # TargetRead
            out.extend(patch[i:i + length])
            i += length
        elif action == 2:                                 # SourceCopy
            raw, i = _read_num(patch, i)
            src_rel += (-1 if raw & 1 else 1) * (raw >> 1)
            out.extend(source[src_rel:src_rel + length])
            src_rel += length
        else:                                             # TargetCopy
            raw, i = _read_num(patch, i)
            tgt_rel += (-1 if raw & 1 else 1) * (raw >> 1)
            for _ in range(length):                       # may overlap; byte-wise
                out.append(out[tgt_rel])
                tgt_rel += 1
    if len(out) != tgt_size:
        raise ValueError(f"produced {len(out)} bytes, patch expects {tgt_size}")
    if zlib.crc32(bytes(out)) != int.from_bytes(patch[-8:-4], "little"):
        raise ValueError("result checksum mismatch")
    return bytes(out)


def paths(product):
    built = products.build_path(product)
    dist = os.path.join(ROOT, "dist")
    return built, dist


def main(argv):
    product, argv = products.pop_arg(argv)
    cmd = argv[0] if argv else "build"
    built, dist = paths(product)

    if not os.path.exists(BASE):
        raise SystemExit(f"missing base ROM: {BASE}")
    if not os.path.exists(built):
        raise SystemExit(f"missing build: {built}\nrun build.py --product {product} first")

    source = open(BASE, "rb").read()
    target = open(built, "rb").read()
    tgt_md5 = hashlib.md5(target).hexdigest()
    out = os.path.join(dist, f"{product}-{tgt_md5[:8]}.bps")

    if cmd == "verify":
        existing = sorted(f for f in os.listdir(dist) if f.startswith(product) and
                          f.endswith(".bps")) if os.path.isdir(dist) else []
        if not existing:
            raise SystemExit(f"no patch in dist/ for {product}; run patch.py first")
        p = os.path.join(dist, existing[-1])
        got = apply(source, open(p, "rb").read())
        ok = hashlib.md5(got).hexdigest() == tgt_md5
        print(f"{os.path.relpath(p, ROOT)}: "
              f"{'round-trips to the built ROM' if ok else 'MISMATCH'}")
        return 0 if ok else 1

    patch = encode(source, target)
    check = apply(source, patch)        # never write a patch we can't re-apply
    if hashlib.md5(check).hexdigest() != tgt_md5:
        raise SystemExit("internal error: patch does not round-trip")

    os.makedirs(dist, exist_ok=True)
    open(out, "wb").write(patch)
    with open(os.path.join(dist, f"{product}.md5"), "w") as f:
        f.write(f"base   dm1-english.gb  {hashlib.md5(source).hexdigest()}\n")
        f.write(f"result {product}-hack.gb  {tgt_md5}\n")
    print(f"wrote: {os.path.relpath(out, ROOT)}  ({len(patch):,} bytes, "
          f"{100 * len(patch) / len(target):.1f}% of the ROM)")
    print(f"  base   {hashlib.md5(source).hexdigest()}")
    print(f"  result {tgt_md5}")
    print("  verified: re-applying the patch to the base reproduces the build")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
