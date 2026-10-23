# tr-normalize

[![CI](https://github.com/YusufBeratZengin/tr-normalize/actions/workflows/ci.yml/badge.svg)](https://github.com/YusufBeratZengin/tr-normalize/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/tr-normalize)](https://pypi.org/project/tr-normalize/)
[![License](https://img.shields.io/pypi/l/tr-normalize)](LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/tr-normalize)](pyproject.toml)

English | [Türkçe](README.tr.md)

Correct Turkish `lower`, `upper`, `title` and `casefold`, alphabetical sorting, ASCII folding, slugs and text cleanup, as a Python library and a CLI.
Pure standard library: zero dependencies, fully typed, no locale setup, no network.

```sh
pip install tr-normalize   # not yet published; use `pip install .` from a clone for now
```

```python
from tr_normalize import tr_lower, tr_upper, tr_title, tr_sorted

tr_lower("IĞDIR İZMİR")  # 'ığdır izmir'
tr_upper("ılık iyi")  # 'ILIK İYİ'
tr_title("istanbul'da")  # "İstanbul'da"
tr_sorted(["şeker", "çay", "ılık", "ilk"])  # ['çay', 'ılık', 'ilk', 'şeker']
```

```sh
tr-normalize slug "Çığlık Atan Şöför’ün Günü!"   # ciglik-atan-soforun-gunu
```

## Demo

![Python's built-in methods versus tr-normalize](docs/demo.svg)

Generated from real output by `python scripts/make-demo.py`. Red lines are Python's built-ins.

## Why Python's `str.lower()` is wrong for Turkish

Turkish has two letters `i`: dotted (`i`/`İ`) and dotless (`ı`/`I`). Python uses the
locale-independent Unicode defaults, so:

| Call | Python gives | Correct Turkish |
|---|---|---|
| `"ISPARTA".lower()` | `'isparta'` | `'ısparta'` |
| `"İZMİR".lower()` | `'i̇zmi̇r'` (an `i` plus U+0307 combining dot) | `'izmir'` |
| `"istanbul".upper()` | `'ISTANBUL'` | `'İSTANBUL'` |
| `sorted(["çay", "cam", "ılık", "ilk"])` | `['cam', 'ilk', 'çay', 'ılık']` | `['cam', 'çay', 'ılık', 'ilk']` |

Plain `sorted()` orders by code point, so `ç ğ ı ö ş ü` end up after every ASCII letter.

## Install

```sh
pip install tr-normalize
```

Requires Python 3.10 or newer. Until the first release is on PyPI, install from a clone with `pip install .`.

## Usage

### Library

| Function | What it does |
|---|---|
| `tr_lower(s)`, `tr_upper(s)` | Turkish case conversion. `I`↔`ı`, `İ`↔`i`; decomposed `I` + U+0307 is understood. |
| `tr_title(s)` | Title case. An apostrophe inside a word does not start a new one: `istanbul'da` becomes `İstanbul'da`. |
| `tr_casefold(s)` | Caseless form for comparison: `tr_casefold("IŞIK") == tr_casefold("ışık")`. |
| `tr_sort_key(s)`, `tr_sorted(items, key=, reverse=)` | Turkish alphabetical order `a b c ç d e f g ğ h ı i j k l m n o ö p r s ş t u ü v y z`. Digits and punctuation first; lowercase before uppercase on ties. |
| `to_ascii(s)` | `ç ğ ı ö ş ü â î û` to `c g i o s u a i u` (and capitals; `İ` to `I`). Everything else is untouched. |
| `tr_slugify(s, separator="-", max_length=None)` | ASCII lowercase URL slug. Apostrophes are dropped, so `Şöför’ün` becomes `soforun`. |
| `normalize_whitespace(s, keep_newlines=False)` | Collapses runs of any Unicode whitespace (including NBSP), removes zero-width space, soft hyphen, BOM. |
| `normalize_quotes(s)`, `normalize_apostrophes(s)` | Curly and typographic quotes to ASCII `"` and `'`. |
| `nfc(s)` | Unicode NFC (composed form). |
| `normalize(s, whitespace=True, quotes=True, keep_newlines=False)` | NFC, then quotes, then whitespace. |

`to_ascii` is the opposite direction of "deasciify" tools: it removes diacritics, it does not restore them.

### CLI

```sh
tr-normalize <command> [text ...]      # reads standard input when no text is given
python -m tr_normalize <command> ...
```

| Command | Effect |
|---|---|
| `lower`, `upper`, `title`, `casefold` | Case conversion |
| `ascii` | Fold Turkish letters to ASCII |
| `slug [--sep S] [--max-length N]` | Slug (one per input line when reading stdin) |
| `clean [--keep-newlines] [--no-quotes]` | NFC, straight quotes, tidy whitespace |
| `sort [-r] [-u]` | Sort lines in Turkish order, optionally reversed or de-duplicated |

Output is always UTF-8. Exit status is `0`, or `2` for a usage error.

## Examples

`examples/basic.py` and its real output:

```text
ığdır izmir
ILIK İYİ
İstanbul'da Ve Ankara’da
Ciglik Sofor Uc Agac
ciglik-atan-soforun-gunu
['cam', 'çay', 'ılık', 'ilk', 'su', 'şeker']
"Merhaba" dünya
```

Sorting a file of city names (`examples/cities.txt`):

```sh
tr-normalize sort < examples/cities.txt
# Ağrı Çanakkale Çorum Iğdır Isparta İzmir Ordu Sivas Şanlıurfa Zonguldak (one per line)
```

## How it works

Only the letters whose Turkish behavior differs (`I`, `i`, `İ`, `ı`) are handled by hand;
runs of every other character are passed to `str.lower` / `str.upper` / `str.casefold`
unchanged, so Greek final sigma, `ß` and Azerbaijani `ə` keep their normal Unicode behavior.
Sorting builds a tuple key: letters by Turkish alphabet position, then accents, then case.

## Limitations

- Sorting is a practical alphabetical order, not full ICU/CLDR collation (no language tailoring beyond Turkish letters, spaces and punctuation are not ignored).
- `tr_title` capitalizes every word; it does not know Turkish exceptions such as conjunctions.
- A U+0307 directly after `i`/`I` is treated as redundant and removed by `tr_lower`/`tr_casefold`. That is correct for Turkish and Azerbaijani, not for Lithuanian.
- `to_ascii` and `tr_slugify` do not transliterate non-Latin scripts; characters with no ASCII form are kept by `to_ascii` and dropped by `tr_slugify`.
- Letters from other languages (for example Azerbaijani `ə`) are never altered by the case functions beyond standard Unicode casing.

## Development

```sh
git clone https://github.com/YusufBeratZengin/tr-normalize.git
cd tr-normalize
python -m pip install -e ".[dev]"
python -m ruff check . && python -m ruff format --check .
python -m mypy
python -m pytest            # includes a coverage floor of 85%
python scripts/make-demo.py # regenerate docs/demo.svg
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Security reports: [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE)
