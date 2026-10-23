"""Correct Turkish case conversion, sorting, ASCII folding, slugs and text cleanup."""

from __future__ import annotations

from .case import tr_casefold, tr_lower, tr_title, tr_upper
from .fold import to_ascii
from .slug import tr_slugify
from .sort import ALPHABET, tr_sort_key, tr_sorted
from .text import (
    nfc,
    normalize,
    normalize_apostrophes,
    normalize_quotes,
    normalize_whitespace,
)

__version__ = "0.1.0"

__all__ = [
    "ALPHABET",
    "__version__",
    "nfc",
    "normalize",
    "normalize_apostrophes",
    "normalize_quotes",
    "normalize_whitespace",
    "to_ascii",
    "tr_casefold",
    "tr_lower",
    "tr_slugify",
    "tr_sort_key",
    "tr_sorted",
    "tr_title",
    "tr_upper",
]
