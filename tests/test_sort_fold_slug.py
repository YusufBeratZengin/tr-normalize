from __future__ import annotations

import pytest

from tr_normalize import ALPHABET, to_ascii, tr_slugify, tr_sort_key, tr_sorted

SORTED_CASES = [
    # each list is already in the expected Turkish order
    ["cam", "çay", "dal"],
    ["gül", "güneş", "hava"],
    ["ılık", "ısı", "ilk", "iyi"],
    ["oda", "ova", "öğle", "ören", "pazar"],
    ["sam", "saz", "şam", "şeker", "tas"],
    ["uzak", "uzun", "üzüm", "vazo"],
    ["aga", "ağa", "ağaç", "ak"],
    ["1", "10", "2", "a"],
    ["a b", "ab"],
    ["zeki", "zeynep", "ə"],
    ["e", "é", "f"],
    ["", "a"],
]


@pytest.mark.parametrize("expected", SORTED_CASES)
def test_sort_order(expected: list[str]) -> None:
    assert tr_sorted(list(reversed(expected))) == expected


def test_alphabet_is_turkish() -> None:
    assert ALPHABET == "abcçdefgğhıijklmnoöpqrsştuüvwxyz"
    assert tr_sorted(list(reversed(ALPHABET))) == list(ALPHABET)


def test_lowercase_before_uppercase_on_ties() -> None:
    assert tr_sorted(["Ali", "ali"]) == ["ali", "Ali"]


def test_case_is_secondary_to_letters() -> None:
    assert tr_sorted(["b", "A", "a", "B"]) == ["a", "A", "b", "B"]


def test_dotted_and_dotless_capitals() -> None:
    assert tr_sorted(["İz", "Iz", "iz", "ız"]) == ["ız", "Iz", "iz", "İz"]


def test_sorted_key_and_reverse() -> None:
    pairs = [("şeker", 1), ("çay", 2), ("su", 3)]
    assert [p[0] for p in tr_sorted(pairs, key=lambda p: p[0])] == ["çay", "su", "şeker"]
    assert tr_sorted(["a", "ç", "z"], reverse=True) == ["z", "ç", "a"]


def test_sort_key_is_comparable_and_hashable() -> None:
    assert tr_sort_key("a") < tr_sort_key("b")
    assert hash(tr_sort_key("çay")) == hash(tr_sort_key("çay"))


def test_python_default_sort_is_wrong() -> None:
    words = ["çay", "cam", "şeker", "sam", "ığdır", "ilk"]
    assert sorted(words) != tr_sorted(words)
    assert tr_sorted(words) == ["cam", "çay", "ığdır", "ilk", "sam", "şeker"]


def test_stray_combining_mark_sorts_after_base() -> None:
    assert tr_sort_key("e\u0301") > tr_sort_key("e")
    assert tr_sorted(["f", "e\u0301", "e"]) == ["e", "e\u0301", "f"]


ASCII_CASES = [
    ("", ""),
    ("çğıöşü", "cgiosu"),
    ("ÇĞİÖŞÜ", "CGIOSU"),
    ("Iıİi", "IiIi"),
    ("Çığlık Şöför Üç Ağaç", "Ciglik Sofor Uc Agac"),
    ("kâğıt hâlâ sûret î", "kagit hala suret i"),
    ("ASCII only 123", "ASCII only 123"),
    ("I" + "\u0307" + "stanbul", "Istanbul"),
    # not Turkish: untouched
    ("Əli və Vüqar", "Əli və Vuqar"),
    ("straße naïve", "straße naïve"),
    ("日本語 🙂", "日本語 🙂"),
]


@pytest.mark.parametrize(("src", "expected"), ASCII_CASES)
def test_to_ascii(src: str, expected: str) -> None:
    assert to_ascii(src) == expected


SLUG_CASES = [
    ("", ""),
    ("Merhaba Dünya", "merhaba-dunya"),
    ("Çığlık Atan Şöför’ün Günü!", "ciglik-atan-soforun-gunu"),
    ("İstanbul'da hava", "istanbulda-hava"),
    ("  çok   boşluk  ", "cok-bosluk"),
    ("a--b__c", "a-b-c"),
    ("IĞDIR", "igdir"),
    ("ISPARTA", "isparta"),
    ("Fiyat: 100 TL (KDV dahil)", "fiyat-100-tl-kdv-dahil"),
    ("Əli və Vüqar", "ali-va-vuqar"),
    ("Straße café", "strasse-cafe"),
    ("日本語", ""),
    ("!!!", ""),
    ("a & b", "a-b"),
    ("kâğıt", "kagit"),
]


@pytest.mark.parametrize(("src", "expected"), SLUG_CASES)
def test_slugify(src: str, expected: str) -> None:
    assert tr_slugify(src) == expected


def test_slug_separator() -> None:
    assert tr_slugify("Şu Çay", separator="_") == "su_cay"
    assert tr_slugify("Şu Çay", separator="") == "sucay"
    assert tr_slugify("Şu Çay Bar", separator="", max_length=4) == "sucay"[:4]


@pytest.mark.parametrize(
    ("src", "limit", "expected"),
    [
        ("bir iki üç dört", 100, "bir-iki-uc-dort"),
        ("bir iki üç dört", 12, "bir-iki-uc"),
        ("bir iki üç dört", 10, "bir-iki-uc"),
        ("bir iki üç dört", 8, "bir-iki"),
        ("bir iki üç dört", 7, "bir-iki"),
        ("bir iki üç dört", 3, "bir"),
        ("uzunkelime", 4, "uzun"),
        ("bir iki", 0, ""),
    ],
)
def test_slug_max_length(src: str, limit: int, expected: str) -> None:
    assert tr_slugify(src, max_length=limit) == expected
