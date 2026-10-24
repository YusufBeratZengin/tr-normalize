# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Fixed

- Preserve Greek final sigma context across Turkish I mappings in `tr_lower`.
- Preserve word characters with custom slug separators, including when applying `max_length`.

## [0.1.0] - 2026-10-23

### Added

- `tr_lower`, `tr_upper`, `tr_title`, `tr_casefold` with Turkish `I`/`ı`/`İ`/`i` rules and handling of the combining dot above (U+0307).
- `tr_sort_key` and `tr_sorted` for Turkish alphabetical order.
- `to_ascii` (ç ğ ı ö ş ü â î û to ASCII) and `tr_slugify`.
- `normalize_whitespace`, `normalize_quotes`, `normalize_apostrophes`, `nfc` and `normalize`.
- `tr-normalize` CLI (`lower`, `upper`, `title`, `casefold`, `ascii`, `slug`, `clean`, `sort`) and `python -m tr_normalize`.
- Typed package (`py.typed`), zero runtime dependencies, English and Turkish READMEs, generated terminal demo.

[Unreleased]: https://github.com/YusufBeratZengin/tr-normalize/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/YusufBeratZengin/tr-normalize/releases/tag/v0.1.0
