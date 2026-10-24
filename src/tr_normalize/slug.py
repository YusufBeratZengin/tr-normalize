"""URL slugs for Turkish text."""

from __future__ import annotations

import re
import unicodedata

from .fold import to_ascii

__all__ = ["tr_slugify"]

_EXTRA = str.maketrans(
    {
        "ə": "a", "Ə": "A", "ß": "ss", "æ": "ae", "Æ": "AE", "œ": "oe", "Œ": "OE",
        "ø": "o", "Ø": "O", "ł": "l", "Ł": "L", "đ": "d", "Đ": "D",
    }
)  # fmt: skip
_APOSTROPHES = re.compile("['’ʼ‘`´]")
_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def tr_slugify(text: str, *, separator: str = "-", max_length: int | None = None) -> str:
    """Return an ASCII, lowercase, URL-safe slug for ``text``.

    ``"Çığlık Atan Şöför’ün Günü!"`` -> ``"ciglik-atan-soforun-gunu"``.
    Apostrophes are removed (not turned into separators) so suffixes stay
    attached.  Other accented Latin letters lose their accents and a few
    letters get a transliteration (``ə`` -> ``a``, ``ß`` -> ``ss``);
    characters with no ASCII form are dropped.  ``max_length`` cuts at a word
    boundary where possible (a single over-long word is cut hard).
    """
    text = _APOSTROPHES.sub("", text)
    text = to_ascii(text).translate(_EXTRA)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    words = [word for word in _NON_ALNUM.split(text) if word]
    slug = separator.join(words)
    if max_length is not None and len(slug) > max_length:
        limit = max(max_length, 0)
        boundary = 0
        if separator:
            end = 0
            for word in words:
                end += len(word)
                if end > limit:
                    break
                boundary = end
                end += len(separator)
        slug = slug[: boundary or limit]
    return slug
