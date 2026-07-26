#!/usr/bin/env python3
"""Convert every fetched source image into card art.

Doing 350 cards by hand is not on, so this applies the settings the pilot
established and flags the ones a human still has to look at.

**Settings.** 1993 Magic art is painterly and busy; at 52x68 in four shades
Floyd-Steinberg plus a contrast lift is a large win over the bayer8 defaults
Kaizo uses. See docs/CARDART.md.

**No automatic cropping.** Zooming in on the subject was tried and rejected on
measurement. A tighter crop nearly always raises local contrast, so picking the
crop that maximises any structure metric picks the tightest one -- which
decapitates figures. Calibrated against thirteen hand-judged cards, the gain
from zooming had no relationship to whether the result looked better: the two
best-composed pictures in the batch both "improved" 10-13% while losing their
subject entirely. Zoom is a per-card rescue, not an objective to maximise, so
it lives in art_tuning.json where a human decides.

**The legibility score is kept as a detector, not a chooser.** It is the
standard deviation after 2x2 block-averaging -- averaging first because
Floyd-Steinberg dither is high-frequency noise that would otherwise read as
detail and score flat mush as excellent. Genuine mush scores far below
everything else (21 against a floor of 40 across the pilot), so cards under
MUSH_BELOW are reported for hand work rather than silently shipped.

**Dither.** fs gives the best detail and the worst compression. Cards share a
16 KB bank, so a bank of busy pictures can overflow even when each fits its own
slot. Anything over budget gets its biggest cards stepped down (fs -> bayer8 ->
bayer4 -> none) until the bank fits -- worst-first, so one busy picture is
flattened rather than thirteen.

Per-card overrides live in work/duelmonsters-mtg/art_tuning.json (tracked):

    {"8": {"zoom": 0.6, "contrast": 1.8, "focus": 0.3, "dither": "bayer8"}}

CLI:
  python mtg_art_convert.py                 convert everything with a source
  python mtg_art_convert.py --cards 1-13    just these
  python mtg_art_convert.py --dry-run       report choices, write nothing
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cardart    # noqa: E402
import gblzss     # noqa: E402
import products   # noqa: E402

PRODUCT = "duelmonsters-mtg"
BASE = dict(fit="cover", dither="fs", contrast=1.4, gamma=1.15, sharpen=0.9, zoom=1.0)
STEPS = ["fs", "bayer8", "bayer4", "none"]
MUSH_BELOW = 34.0     # pilot: real mush scored 21, everything legible scored 40+


def legibility(g):
    """Structure score. Block-average away the dither, then measure spread."""
    pal = cardart.PALETTE
    vals = []
    for y in range(6, 73, 2):
        for x in range(6, 57, 2):
            vals.append((pal[g[y][x]][0] + pal[g[y][x + 1]][0]
                         + pal[g[y + 1][x]][0] + pal[g[y + 1][x + 1]][0]) / 4.0)
    mean = sum(vals) / len(vals)
    return (sum((v - mean) ** 2 for v in vals) / len(vals)) ** 0.5


def convert(src, frame, **over):
    kw = dict(BASE, **over)
    g = cardart.convert_image(src, **kw)
    if frame:
        cardart.apply_frame(g, frame)     # the black border ring every card shares
    return g


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


def main(argv):
    want = parse_cards(argv[argv.index("--cards") + 1]) if "--cards" in argv else None
    dry = "--dry-run" in argv

    rom = cardart.load_rom()
    sl = cardart.slots(rom)
    frame = cardart.frame_template(rom)
    src_dir = os.path.join(products.data_dir(PRODUCT), "art_in")
    out_dir = cardart.art_dir(PRODUCT)
    os.makedirs(out_dir, exist_ok=True)

    tunep = products.data_path("art_tuning.json", PRODUCT)
    tuning = json.load(open(tunep, encoding="utf-8")) if os.path.exists(tunep) else {}

    jobs = [(cid, os.path.join(src_dir, f"{cid:03d}.jpg"))
            for cid in range(1, cardart.NCARD + 1)
            if (want is None or cid in want)
            and os.path.exists(os.path.join(src_dir, f"{cid:03d}.jpg"))]
    print(f"{len(jobs)} card(s) with a source image"
          + (f", {len(tuning)} hand-tuned" if tuning else ""))

    picked = {}
    for i, (cid, p) in enumerate(jobs, 1):
        # keys starting with _ are notes for the reader (_card, _why), not kwargs
        over = {k: v for k, v in tuning.get(str(cid), {}).items()
                if not k.startswith("_")}
        g = convert(p, frame, **over)
        picked[cid] = {"g": g, "src": p, "over": over,
                       "dither": over.get("dither", BASE["dither"]),
                       "score": legibility(g),
                       "enc": len(gblzss.compress(cardart.to_raw(g)))}
        if i % 50 == 0 or i == len(jobs):
            print(f"  converted {i}/{len(jobs)}")

    # --- per-bank budget: cards sharing a 16 KB bank share one budget ---
    by_bank = {}
    for cid in picked:
        by_bank.setdefault(sl[cid - 1][0], []).append(cid)
    stock = {c + 1: cardart.read_art(rom, c)[1] for c in range(cardart.NCARD)}

    downgraded, over_banks = [], []
    for bank, cids in sorted(by_bank.items()):
        members = [c + 1 for c in range(cardart.NCARD) if sl[c][0] == bank]
        room = cardart.BANK_END - cardart.BANK_START[bank]

        def used():
            return sum(picked[m]["enc"] if m in picked else stock[m] for m in members)

        for step in STEPS[1:]:
            while used() > room:
                worst = max((m for m in cids if picked[m]["dither"] != step),
                            key=lambda m: picked[m]["enc"], default=None)
                if worst is None:
                    break
                d = picked[worst]
                g = convert(d["src"], frame, **dict(d["over"], dither=step))
                d.update(g=g, dither=step,
                         enc=len(gblzss.compress(cardart.to_raw(g))))
                downgraded.append((worst, step))
            if used() <= room:
                break
        if used() > room:
            over_banks.append((bank, used() - room))
        print(f"  bank ${bank:02X}  {used():6d}/{room}"
              + ("   <-- STILL OVER" if used() > room else ""))

    mush = sorted((d["score"], c) for c, d in picked.items() if d["score"] < MUSH_BELOW)
    if downgraded:
        by_card = {}
        for c, s in downgraded:
            by_card[c] = s
        print(f"\nflattened to fit its bank ({len(by_card)}): "
              + ", ".join(f"#{c}->{s}" for c, s in sorted(by_card.items())))
    print(f"\n{len(mush)} card(s) below the legibility floor -- these need hand work:")
    print("  " + ", ".join(f"#{c}({s:.0f})" for s, c in mush) if mush else "  none")
    if over_banks:
        print("\nBANKS STILL OVER: " + ", ".join(f"${b:02X} by {n}B" for b, n in over_banks))

    if dry:
        print("\n--dry-run: nothing written")
        return 0
    for cid, d in picked.items():
        cardart.save_png(d["g"], os.path.join(out_dir, f"{cid:03d}.png"))
    print(f"\nwrote {len(picked)} picture(s) to {os.path.relpath(out_dir, products.ROOT)}")
    return 1 if over_banks else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
