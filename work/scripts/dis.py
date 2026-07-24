#!/usr/bin/env python3
"""Linear SM83 disassembler that understands this game's far-call convention.

mgbdis desyncs on every `rst $08` because the two bytes that follow it are
inline parameters, not code. This one consumes them and annotates the call
with its resolved destination (see farcall.py).

Usage:
  python dis.py <file_offset> [count_bytes]      disassemble from a file offset
  python dis.py bank:<bank>:<cpu_addr> [count]   ... or from a bank/CPU address

Add `--rom <path>` to disassemble a built ROM instead of the pristine base.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "tools", "mgbdis"))

import cards  # noqa: E402
import farcall  # noqa: E402
from instruction_set import instructions, cb_instructions  # noqa: E402

# operand token -> (extra bytes, formatter)
OPS = {
    "d8":  (1, lambda v, pc: f"${v:02X}"),
    "a8":  (1, lambda v, pc: f"$FF{v:02X}"),
    "r8":  (1, lambda v, pc: f"${(pc + (v - 256 if v > 127 else v)) & 0xFFFF:04X}"),
    "d16": (2, lambda v, pc: f"${v:04X}"),
    "a16": (2, lambda v, pc: f"${v:04X}"),
}
RST_VEC = {0xC7: 0x00, 0xCF: 0x08, 0xD7: 0x10, 0xDF: 0x18,
           0xE7: 0x20, 0xEF: 0x28, 0xF7: 0x30, 0xFF: 0x38}


def decode(rom, off, pc, bank):
    """-> (text, length). pc is the CPU address of this opcode."""
    op = rom[off]

    if op == 0xCF:  # rst $08 = far call; next two bytes are parameters
        sel, dbank = rom[off + 1], rom[off + 2]
        tab = farcall.read_table(rom, dbank)
        tgt = next((t for _, s, t in tab if s == sel), None)
        dest = f"${tgt:04X}" if tgt else "??"
        return (f"farcall  bank ${dbank:02X} idx {farcall.sel_to_index(sel)} {dest}"
                f"        ; CF {sel:02X} {dbank:02X}"), 3

    if op == 0xCB:
        return cb_instructions[rom[off + 1]], 2

    text = instructions.get(op)
    if text is None:
        return f"db ${op:02X}   ; invalid", 1
    if text == "rst vec":
        return f"rst ${RST_VEC[op]:02X}", 1

    for tok, (n, fmt) in OPS.items():
        if tok in text:
            v = rom[off + 1] if n == 1 else (rom[off + 1] | (rom[off + 2] << 8))
            return text.replace(tok, fmt(v, pc + 1 + n)), 1 + n
    return text, 1


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    path = cards.BASE_ROM
    if "--rom" in argv:
        i = argv.index("--rom")
        path = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    rom = open(path, "rb").read()

    spec = argv[0]
    if spec.startswith("bank:"):
        _, b, a = spec.split(":")
        bank, cpu = int(b, 0), int(a, 0)
        off = farcall.to_file(bank, cpu)
    else:
        off = int(spec, 0)
        bank, cpu = farcall.to_cpu(off)
    count = int(argv[1], 0) if len(argv) > 1 else 96

    end = off + count
    while off < end:
        text, n = decode(rom, off, cpu, bank)
        raw = " ".join(f"{b:02X}" for b in rom[off:off + n])
        print(f"  {off:06X}  {cpu:04X}  {raw:<9}  {text}")
        off += n
        cpu += n
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
