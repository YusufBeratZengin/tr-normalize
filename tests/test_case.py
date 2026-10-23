from __future__ import annotations

from collections.abc import Callable

import pytest

from tr_normalize import tr_casefold, tr_lower, tr_title, tr_upper

DOT = "\u0307"

LOWER = [
    ("", ""),
    ("ISPARTA", "ısparta"),
    ("IĞDIR", "ığdır"),
    ("İSTANBUL", "istanbul"),
    ("İzmir", "izmir"),
    ("ISIK", "ısık"),
    ("Iı İi", "ıı ii"),
    ("ÇĞÖŞÜ", "çğöşü"),
    ("ABC xyz 123", "abc xyz 123"),
    # decomposed capital dotted I: I + U+0307
    ("I" + DOT + "stanbul", "istanbul"),
    ("I" + DOT, "i"),
    # already-broken Python lowering: i + U+0307
    ("i" + DOT + "zmir", "izmir"),
    # a lone combining dot is kept when nothing precedes it
    (DOT + "a", DOT + "a"),
    # other combining class does not block the dot (cedilla below, ccc 202)
    ("I\u0327" + DOT, "i\u0327"),
    # a mark with class 230 between I and the dot blocks it
    ("I\u0301" + DOT, "ı\u0301" + DOT),
    # other languages keep standard casing
    ("ƏLİ", "əli"),
    ("Straße ÀÉ", "straße àé"),
    ("ΑΒΓ", "αβγ"),
    ("ΟΔΟΣ", "οδος"),  # Greek final sigma keeps its context
    ("🙂 I", "🙂 ı"),
]

UPPER = [
    ("", ""),
    ("isparta", "İSPARTA"),
    ("ığdır", "IĞDIR"),
    ("istanbul", "İSTANBUL"),
    ("ılık", "ILIK"),
    ("çğöşü", "ÇĞÖŞÜ"),
    ("i" + DOT, "İ"),
    ("i" + DOT + "zmir", "İZMİR"),
    ("İI", "İI"),
    ("abc 123", "ABC 123"),
    ("əli", "ƏLİ"),
    ("straße", "STRASSE"),
]

TITLE = [
    ("", ""),
    ("istanbul'da", "İstanbul'da"),
    ("İSTANBUL'DA", "İstanbul'da"),
    ("ankara’da yaşıyorum", "Ankara’da Yaşıyorum"),
    ("ıspanak ve ışık", "Ispanak Ve Işık"),
    ("iyi akşamlar", "İyi Akşamlar"),
    ("IĞDIR İLİ", "Iğdır İli"),
    ("ali-veli", "Ali-Veli"),
    ("ağaç, çay; şeker", "Ağaç, Çay; Şeker"),
    ("3d model", "3d Model"),
    ("snake_case word", "Snake_Case Word"),
    ("i" + DOT + "zmir", "İzmir"),
    ("elazığ'ın", "Elazığ'ın"),
    ("'tırnak' içinde", "'Tırnak' İçinde"),
    ("  boşluk   korunur  ", "  Boşluk   Korunur  "),
    ("ƏLİ vəli", "Əli Vəli"),
]

CASEFOLD_PAIRS = [
    ("IŞIK", "ışık"),
    ("İSTANBUL", "istanbul"),
    ("ISPARTA", "ısparta"),
    ("Straße", "STRASSE"),
    ("ığdır", "IĞDIR"),
]


@pytest.mark.parametrize(("src", "expected"), LOWER)
def test_lower(src: str, expected: str) -> None:
    assert tr_lower(src) == expected


@pytest.mark.parametrize(("src", "expected"), UPPER)
def test_upper(src: str, expected: str) -> None:
    assert tr_upper(src) == expected


@pytest.mark.parametrize(("src", "expected"), TITLE)
def test_title(src: str, expected: str) -> None:
    assert tr_title(src) == expected


@pytest.mark.parametrize(("a", "b"), CASEFOLD_PAIRS)
def test_casefold_equates(a: str, b: str) -> None:
    assert tr_casefold(a) == tr_casefold(b)


def test_casefold_keeps_dotless_and_dotted_apart() -> None:
    assert tr_casefold("ı") != tr_casefold("i")
    assert tr_casefold("I") == "ı"
    assert tr_casefold("İ") == "i"
    assert tr_casefold("I" + DOT) == "i"


def test_python_lower_is_wrong_for_turkish() -> None:
    # Documents why the library exists.
    assert "ISPARTA".lower() == "isparta" != tr_lower("ISPARTA")
    assert "İ".lower() == "i" + DOT
    assert tr_lower("İ") == "i"


def test_roundtrip_lowercase_letters() -> None:
    word = "çağrışım ığdır öğüt şişe"
    assert tr_lower(tr_upper(word)) == word


@pytest.mark.parametrize("func", [tr_lower, tr_upper, tr_title, tr_casefold])
def test_idempotent(func: Callable[[str], str]) -> None:
    sample = "İstanbul'da IĞDIR ılık ƏLİ straße"
    assert func(func(sample)) == func(sample)
