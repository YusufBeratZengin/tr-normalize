"""Turkish-aware case conversion.

Python's ``str.lower`` and ``str.upper`` follow the locale-independent Unicode
defaults, which are wrong for Turkish (and Azerbaijani): ``"I".lower()`` is
``"i"`` instead of ``"ı"``, and ``"İ".lower()`` is two characters (``i`` plus
U+0307 COMBINING DOT ABOVE) instead of ``"i"``.  The functions here fix exactly
those letters and delegate every other character to the standard library, so
text in other languages (for example Azerbaijani ``ə``) keeps its usual casing.
"""

from __future__ import annotations

import re
import unicodedata

__all__ = ["tr_casefold", "tr_lower", "tr_title", "tr_upper"]

DOT_ABOVE = "\u0307"
_APOSTROPHES = "'’ʼ‘`´"


def _dot_index(text: str, start: int) -> int:
    """Return the index of a U+0307 that attaches to ``text[start]``, else ``-1``.

    Marks with a combining class other than 0 and 230 do not block the dot
    (Unicode ``After_I`` / ``Not_Before_Dot`` context), so they are skipped.
    """
    j = start + 1
    n = len(text)
    while j < n and unicodedata.combining(text[j]) not in (0, 230):
        j += 1
    if j < n and text[j] == DOT_ABOVE:
        return j
    return -1


def _lower_like(text: str, fold: bool) -> str:
    out: list[str] = []
    plain: list[str] = []  # run of ordinary characters, converted in one go

    def flush() -> None:
        if plain:
            chunk = "".join(plain)
            out.append(chunk.casefold() if fold else chunk.lower())
            plain.clear()

    n = len(text)
    i = 0
    while i < n:
        ch = text[i]
        if ch in ("I", "i"):
            flush()
            dot = _dot_index(text, i)
            if dot != -1:
                # I + dot above is "i" in Turkish; the dot is redundant, drop it.
                out.append("i" + text[i + 1 : dot])
                i = dot + 1
                continue
            out.append("ı" if ch == "I" else "i")
        elif ch == "İ":  # İ
            flush()
            out.append("i")
        else:
            plain.append(ch)
        i += 1
    flush()
    return "".join(out)


def tr_lower(text: str) -> str:
    """Lowercase ``text`` with Turkish rules (``I`` -> ``ı``, ``İ`` -> ``i``).

    A U+0307 combining dot above after ``I``/``i`` is absorbed, so both the
    precomposed ``İ`` and its decomposed form ``I`` + U+0307 give ``i``.
    """
    return _lower_like(text, fold=False)


def tr_casefold(text: str) -> str:
    """Return a caseless form of ``text`` for Turkish comparisons.

    Like :func:`tr_lower`, but additionally applies full Unicode case folding
    (``ß`` -> ``ss``).  ``tr_casefold("IŞIK") == tr_casefold("ışık")``.
    """
    return _lower_like(text, fold=True)


def tr_upper(text: str) -> str:
    """Uppercase ``text`` with Turkish rules (``i`` -> ``İ``, ``ı`` -> ``I``)."""
    out: list[str] = []
    n = len(text)
    i = 0
    while i < n:
        ch = text[i]
        if ch == "i":
            dot = _dot_index(text, i)
            if dot != -1:
                out.append("İ")
                out.append(text[i + 1 : dot])
                i = dot + 1
                continue
            out.append("İ")
        elif ch == "ı":  # ı
            out.append("I")
        else:
            out.append(ch.upper())
        i += 1
    return "".join(out)


_MARKS = "\u0300-\u036f"
_WORD_CHAR = rf"(?:[^\W_]|[{_MARKS}])"
_WORD_RE = re.compile(rf"{_WORD_CHAR}+(?:[{re.escape(_APOSTROPHES)}]{_WORD_CHAR}+)*")


def _title_word(match: re.Match[str]) -> str:
    word = match.group(0)
    k = 1
    while k < len(word) and unicodedata.combining(word[k]):
        k += 1
    return tr_upper(word[:k]) + tr_lower(word[k:])


def tr_title(text: str) -> str:
    """Title-case ``text`` with Turkish rules.

    The first letter of every word is uppercased and the rest lowercased.
    An apostrophe between letters does not start a new word, so the suffix of
    a proper noun stays lowercase: ``"istanbul'da"`` -> ``"İstanbul'da"``.
    """
    return _WORD_RE.sub(_title_word, text)
