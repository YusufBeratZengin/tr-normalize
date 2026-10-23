"""Fold Turkish letters to plain ASCII (the reverse of "deasciify")."""

from __future__ import annotations

import unicodedata

__all__ = ["to_ascii"]

_TABLE = str.maketrans(
    {
        "ç": "c", "Ç": "C",
        "ğ": "g", "Ğ": "G",
        "ı": "i", "İ": "I",
        "ö": "o", "Ö": "O",
        "ş": "s", "Ş": "S",
        "ü": "u", "Ü": "U",
        "â": "a", "Â": "A",
        "î": "i", "Î": "I",
        "û": "u", "Û": "U",
    }
)  # fmt: skip


def to_ascii(text: str) -> str:
    """Replace Turkish letters with their ASCII look-alikes.

    ``ç ğ ı ö ş ü`` (and the circumflex vowels ``â î û``) become
    ``c g i o s u``; case is preserved and ``İ`` becomes ``I``.  Every other
    character, including non-Turkish letters such as the Azerbaijani ``ə``,
    is left untouched.  The text is composed (NFC) first, so a decomposed
    ``İ`` (``I`` + U+0307) also gives ``I``.
    """
    return unicodedata.normalize("NFC", text).translate(_TABLE)
