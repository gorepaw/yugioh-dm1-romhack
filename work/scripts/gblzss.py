#!/usr/bin/env python3
"""The graphics codec DM1 uses for every compressed image (card art, portraits).

It is textbook Okumura LZSS, recovered from the decompressor at ROM `$1B23`
(bank 0) and its two helpers `$1B92` (source byte fetch) and `$1BA5` (output
byte store):

    ring buffer   $C000-$C3FF, 1024 bytes
    prefill       $C000-$C3DD (990 bytes) = $20, the rest is never read
    write cursor  starts at $C3DE  ( = N - F = 1024 - 34, the classic value)
    flag byte     8 tokens, LSB first, 1 = literal, 0 = back-reference
    literal       one byte
    reference     two bytes `lo hi`
                    length   = (hi & $1F) + 3          -> 3..34
                    position = ((hi >> 5) & 3) << 8 | lo   -> 0..1023
                  bit 7 of `hi` is unused
    termination   none - the caller supplies an output byte count and the
                  decompressor stops the instant it has emitted that many
                  bytes, mid-token if need be

Because the ring is just a sliding window over (990 x $20) ++ output, this is
plain LZ77 with a 1024-byte window, which is how the encoder below treats it.
"""

RING = 1024
PREFILL_LEN = 990          # $C000-$C3DD
PREFILL_BYTE = 0x20
START = 0x3DE              # $C3DE
MIN_MATCH = 3
MAX_MATCH = 34             # (hi & $1F) + 3


def decompress(src, off, out_len):
    """Decode `out_len` bytes starting at `src[off]`. -> (bytes, bytes_consumed)"""
    ring = bytearray([PREFILL_BYTE]) * RING
    r = START
    out = bytearray()
    p = off
    while len(out) < out_len:
        flags = src[p]
        p += 1
        for _ in range(8):
            if len(out) >= out_len:
                break
            if flags & 1:
                b = src[p]
                p += 1
                out.append(b)
                ring[r] = b
                r = (r + 1) & (RING - 1)
            else:
                lo, hi = src[p], src[p + 1]
                p += 2
                pos = (((hi >> 5) & 3) << 8) | lo
                for k in range((hi & 0x1F) + 3):
                    if len(out) >= out_len:
                        break
                    b = ring[(pos + k) & (RING - 1)]
                    out.append(b)
                    ring[r] = b
                    r = (r + 1) & (RING - 1)
            flags >>= 1
    return bytes(out), p - off


def compress(data, lazy=True):
    """Encode `data` into a stream `decompress` reproduces exactly.

    The window is a sliding view of V = 990 x $20 ++ data, so a match at
    V-index m is emitted as ring position m % 1024. Matches may overlap the
    write cursor (a run), which the decoder handles byte by byte.
    """
    v = bytearray([PREFILL_BYTE]) * PREFILL_LEN + bytearray(data)
    n = len(v)
    # hash chain over 3-byte keys, so a match search is a short walk
    head, prev = {}, [0] * n

    def add(i):
        if i + MIN_MATCH <= n:
            k = bytes(v[i:i + MIN_MATCH])
            prev[i] = head.get(k, -1)
            head[k] = i

    for i in range(PREFILL_LEN - MIN_MATCH):     # seed the prefill run
        add(i)

    def find(i):
        """longest match for v[i:] starting inside the 1024-byte window"""
        if i + MIN_MATCH > n:
            return 0, 0
        limit = max(0, i - RING)
        best_len, best_pos = 0, 0
        j = head.get(bytes(v[i:i + MIN_MATCH]), -1)
        tried = 0
        while j >= limit and tried < 96:
            tried += 1
            ln = 0
            while ln < MAX_MATCH and i + ln < n and v[j + ln] == v[i + ln]:
                ln += 1
            if ln > best_len:
                best_len, best_pos = ln, j
                if ln == MAX_MATCH:
                    break
            j = prev[j]
        return best_len, best_pos

    out = bytearray()
    tokens = []        # (is_literal, payload)
    i = PREFILL_LEN
    end = n
    while i < end:
        ln, pos = find(i)
        if lazy and MIN_MATCH <= ln < MAX_MATCH and i + 1 < end:
            add(i)
            nxt_len, _ = find(i + 1)
            if nxt_len > ln:
                tokens.append((True, v[i]))
                i += 1
                continue
            # `add(i)` already done; carry on with the match at i
            for k in range(1, ln):
                add(i + k)
            tokens.append((False, (pos % RING, ln)))
            i += ln
            continue
        if ln >= MIN_MATCH:
            for k in range(ln):
                add(i + k)
            tokens.append((False, (pos % RING, ln)))
            i += ln
        else:
            add(i)
            tokens.append((True, v[i]))
            i += 1

    for g in range(0, len(tokens), 8):
        group = tokens[g:g + 8]
        flags = 0
        for b, (is_lit, _) in enumerate(group):
            if is_lit:
                flags |= 1 << b
        out.append(flags)
        for is_lit, payload in group:
            if is_lit:
                out.append(payload)
            else:
                pos, ln = payload
                out.append(pos & 0xFF)
                out.append((((pos >> 8) & 3) << 5) | (ln - MIN_MATCH))
    return bytes(out)


if __name__ == "__main__":
    import random
    random.seed(1)
    for trial in range(200):
        n = random.choice([1, 7, 64, 512, 1280, 3072])
        if trial % 3 == 0:
            d = bytes(random.getrandbits(8) for _ in range(n))
        elif trial % 3 == 1:
            d = bytes(random.choice(b"\x00\xff\x20\x81") for _ in range(n))
        else:
            d = (bytes(random.getrandbits(8) for _ in range(17)) * (n // 17 + 1))[:n]
        enc = compress(d)
        dec, used = decompress(enc, 0, len(d))
        assert dec == d, f"round-trip failed on trial {trial}"
        assert used <= len(enc), (used, len(enc))
    print("gblzss self-test: 200/200 round-trips OK")
