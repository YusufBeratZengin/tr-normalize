"""Turkish alphabetical ordering."""

from __future__ import annotations

import unicodedata
from collections.abc import Callable, Iterable
from typing import Any, TypeVar

from .case import tr_lower

__all__ = ["ALPHABET", "tr_sort_key", "tr_sorted"]

#: Turkish alphabet order.  ``q``, ``w`` and ``x`` are not Turkish letters but
#: keep their Latin positions so that loanwords still sort sensibly.
ALPHABET = "abcçdefgğhıijklmnoöpqrsştuüvwxyz"
_INDEX = {ch: pos for pos, ch in enumerate(ALPHABET)}

T = TypeVar("T")

# Class of a primary key element: other characters < Turkish/Latin letters < other letters.
_OTHER, _LETTER, _FOREIGN = 1, 2, 3


def tr_sort_key(text: str) -> tuple[Any, ...]:
    """Return a key that sorts ``text`` in Turkish alphabetical order.

    Order: ``a b c ç d e f g ğ h ı i j k l m n o ö p r s ş t u ü v y z``
    (with ``q w x`` at their Latin positions).  Comparison is by letters first,
    then by accents (``é`` after ``e``), then lowercase before uppercase.
    Digits and punctuation come before letters; letters outside the Latin
    alphabet (for example ``ə``) come after ``z`` in code point order.
    """
    primary: list[tuple[int, int]] = []
    secondary: list[tuple[int, ...]] = []
    tertiary: list[int] = []
    for ch in unicodedata.normalize("NFC", text):
        if unicodedata.combining(ch):
            secondary.append((ord(ch),))
            continue
        lowered = tr_lower(ch)
        decomposed = unicodedata.normalize("NFD", lowered)
        base, marks = decomposed[0], decomposed[1:]
        if lowered in _INDEX:
            primary.append((_LETTER, _INDEX[lowered]))
            secondary.append(())
        elif base in _INDEX:
            primary.append((_LETTER, _INDEX[base]))
            secondary.append(tuple(ord(m) for m in marks))
        elif ch.isalpha():
            primary.append((_FOREIGN, ord(lowered[0])))
            secondary.append(())
        else:
            primary.append((_OTHER, ord(ch)))
            secondary.append(())
        tertiary.append(0 if ch == lowered else 1)
    return (tuple(primary), tuple(secondary), tuple(tertiary))


def tr_sorted(
    items: Iterable[T],
    *,
    key: Callable[[T], str] | None = None,
    reverse: bool = False,
) -> list[T]:
    """Sort strings (or objects, via ``key``) in Turkish alphabetical order."""
    if key is None:
        return sorted(items, key=lambda item: tr_sort_key(str(item)), reverse=reverse)
    return sorted(items, key=lambda item: tr_sort_key(key(item)), reverse=reverse)
