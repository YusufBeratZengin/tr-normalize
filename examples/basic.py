"""Run with: python examples/basic.py (after `pip install -e .`, or PYTHONPATH=src)."""

from tr_normalize import (
    normalize,
    to_ascii,
    tr_lower,
    tr_slugify,
    tr_sorted,
    tr_title,
    tr_upper,
)

print(tr_lower("IĞDIR İZMİR"))
print(tr_upper("ılık iyi"))
print(tr_title("istanbul'da ve ankara’da"))
print(to_ascii("Çığlık Şöför Üç Ağaç"))
print(tr_slugify("Çığlık Atan Şöför’ün Günü!"))
print(tr_sorted(["şeker", "çay", "su", "ılık", "ilk", "cam"]))
print(normalize("  “Merhaba”   dünya  "))
