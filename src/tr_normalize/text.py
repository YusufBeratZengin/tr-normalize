"""Unicode, whitespace, quote and apostrophe normalization."""

from __future__ import annotations

import re
import unicodedata

__all__ = [
    "nfc",
    "normalize",
    "normalize_apostrophes",
    "normalize_quotes",
    "normalize_whitespace",
]

_INVISIBLE = re.compile("[\u00ad\u200b\u2060\ufeff]")
_APOSTROPHE_TABLE = str.maketrans(
    dict.fromkeys(
        "‘’‚‛′ʹʻʼˈ´`‹›＇",
        "'",
    )
)
_DOUBLE_QUOTE_TABLE = str.maketrans(dict.fromkeys("“”„‟″«»〝〞＂", '"'))


def nfc(text: str) -> str:
    """Return ``text`` in Unicode normalization form C (composed)."""
    return unicodedata.normalize("NFC", text)


def normalize_apostrophes(text: str) -> str:
    """Turn typographic apostrophes and single quotes into ASCII ``'``.

    Covers the curly single quotes, prime, modifier-letter apostrophes, acute
    accent, backtick and single guillemets.  Turkish proper-noun suffixes then
    always use the same character: ``Ankara’da`` -> ``Ankara'da``.
    """
    return text.translate(_APOSTROPHE_TABLE)


def normalize_quotes(text: str) -> str:
    """Turn typographic quotes into ASCII ``"`` and ``'``.

    Double quotes (curly, low-9, double prime, guillemets) become ``"``;
    single quotes and apostrophes are handled by :func:`normalize_apostrophes`.
    """
    return normalize_apostrophes(text).translate(_DOUBLE_QUOTE_TABLE)


def normalize_whitespace(text: str, *, keep_newlines: bool = False) -> str:
    """Collapse runs of whitespace and remove invisible characters.

    Non-breaking and other Unicode spaces count as whitespace; zero-width
    space, word joiner, soft hyphen and BOM are removed.  By default the result
    is a single line with single spaces.  With ``keep_newlines=True`` line
    breaks survive: each line is cleaned separately and blank-line runs are
    reduced to one blank line.
    """
    text = _INVISIBLE.sub("", text)
    if not keep_newlines:
        return " ".join(text.split())
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [" ".join(line.split()) for line in text.split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip("\n")


def normalize(
    text: str,
    *,
    whitespace: bool = True,
    quotes: bool = True,
    keep_newlines: bool = False,
) -> str:
    """Apply NFC, then (optionally) quote and whitespace normalization."""
    text = nfc(text)
    if quotes:
        text = normalize_quotes(text)
    if whitespace:
        text = normalize_whitespace(text, keep_newlines=keep_newlines)
    return text
