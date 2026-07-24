#!/usr/bin/env python3
"""Product routing — keep Project 1 and Project 2 data separate.

The two products SHARE this repo's tools and reverse-engineering knowledge
(NOTES.md, everything in work/scripts/), because the engine is the same for
both. They must NOT share card data: they are two different games occupying the
same 366 card slots, so one cards.json cannot represent both.

Rule: all product-specific data lives under `work/<product>/`. Tools take an
optional `--product p1|p2` (default p1); build.py writes `build/<product>-hack.gb`
so the two never clobber each other's output.

Shared (both edit, mostly additive): docs/NOTES.md, the scripts.
Separate (never share a file): work/p1/*  vs  work/p2/*, and the build outputs.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PRODUCTS = ("p1", "p2")
DEFAULT = "p1"


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
