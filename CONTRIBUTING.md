# Contributing

Small, focused changes with a reproducible case are welcome. For a new function or a change to
existing behavior, open an issue first.

## Setup and checks

```sh
python -m venv .venv          # then activate it
python -m pip install -e ".[dev]"
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m pytest              # enforces at least 85% coverage
python scripts/make-demo.py --check
```

## Tests

Tests are table-driven: add a row `(input, expected)` to the relevant list in `tests/` rather than
a new function. Cover Turkish edge cases (`I`/`ı`/`İ`/`i`, decomposed U+0307, apostrophes) and
check that other languages (for example Azerbaijani `ə`) are not altered. Tests must not use the
network. Runtime code stays dependency-free and typed.

## Commits and pull requests

Use Conventional Commits (`feat:`, `fix:`, `test:`, `docs:`, `ci:`, `chore:`). Update both
`README.md` and `README.tr.md` for user-visible changes, and add a line under `[Unreleased]` in
`CHANGELOG.md`. Run `python scripts/make-demo.py` if CLI or demo output changes.

## Releasing

1. Move the `[Unreleased]` entries to a new version section in `CHANGELOG.md`.
2. Bump `version` in `pyproject.toml` and `__version__` in `src/tr_normalize/__init__.py`.
3. Commit `chore(release): vX.Y.Z`, then `git tag vX.Y.Z`.
4. Dry run: `python -m build && twine check dist/*`.
5. Push the tag. The `Publish` workflow builds and uploads to PyPI through trusted publishing
   (configure a pending publisher on PyPI for this repository, workflow `publish.yml`,
   environment `pypi`); no API token is stored.

Contributions are distributed under the project's MIT license.
