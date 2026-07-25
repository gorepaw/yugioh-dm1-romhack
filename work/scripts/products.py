#!/usr/bin/env python3
"""Product routing — keep Duel Monsters Kaizo and Duel Monsters MTG data separate.

The two products SHARE this repo's tools and reverse-engineering knowledge
(NOTES.md, everything in work/scripts/), because the engine is the same for
both. They must NOT share card data: they are two different games occupying the
same 366 card slots, so one cards.json cannot represent both.

Rule: all product-specific data lives under `work/<product>/`. Tools take an
optional `--product duelmonsters-kaizo|duelmonsters-mtg` (default
duelmonsters-kaizo); build.py writes `build/<product>-hack.gb` so the two never
clobber each other's output.

Shared (both edit, mostly additive): docs/NOTES.md, the scripts.
Separate (never share a file): work/duelmonsters-kaizo/* vs
work/duelmonsters-mtg/*, and the build outputs.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PRODUCTS = ("duelmonsters-kaizo", "duelmonsters-mtg")
DEFAULT = "duelmonsters-kaizo"


def check(product):
    if product not in PRODUCTS:
        raise SystemExit(f"unknown product {product!r}; expected one of {PRODUCTS}")
    return product


def data_dir(product=DEFAULT, create=True):
    """work/<product>/ — created on demand."""
    check(product)
    d = os.path.join(ROOT, "work", product)
    if create:
        os.makedirs(d, exist_ok=True)
    return d


def data_path(name, product=DEFAULT):
    """Absolute path to a data file for a product, e.g. cards.json."""
    return os.path.join(data_dir(product), name)


def build_path(product=DEFAULT):
    check(product)
    return os.path.join(ROOT, "build", f"{product}-hack.gb")


def pop_arg(argv):
    """Pull an optional `--product X` out of argv (any iterable).

    Returns (product, remaining_argv) so a CLI can do:
        product, argv = products.pop_arg(argv)
    """
    argv = list(argv)
    product = DEFAULT
    if "--product" in argv:
        i = argv.index("--product")
        product = check(argv[i + 1])
        del argv[i:i + 2]
    return product, argv
