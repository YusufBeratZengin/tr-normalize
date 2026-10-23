from __future__ import annotations

import io
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

import tr_normalize
from tr_normalize import (
    nfc,
    normalize,
    normalize_apostrophes,
    normalize_quotes,
    normalize_whitespace,
)
from tr_normalize.cli import main

NBSP = "\u00a0"

WHITESPACE_CASES = [
    ("", ""),
    ("  a  b  ", "a b"),
    ("a\tb\nc", "a b c"),
    (f"a{NBSP}{NBSP}b", "a b"),
    ("a\u202fb\u2009c\u3000d", "a b c d"),
    ("a\u200bb", "ab"),
    ("\ufeffmerhaba", "merhaba"),
    ("ko\u00adpru", "kopru"),
    ("a\u2060b", "ab"),
    ("   ", ""),
]


@pytest.mark.parametrize(("src", "expected"), WHITESPACE_CASES)
def test_whitespace(src: str, expected: str) -> None:
    assert normalize_whitespace(src) == expected


KEEP_NEWLINES_CASES = [
    ("a  b\n\n\n\nc  d", "a b\n\nc d"),
    ("  a \r\n b  \r\n", "a\nb"),
    ("a\rb", "a\nb"),
    ("\n\nx\n\n", "x"),
]


@pytest.mark.parametrize(("src", "expected"), KEEP_NEWLINES_CASES)
def test_whitespace_keep_newlines(src: str, expected: str) -> None:
    assert normalize_whitespace(src, keep_newlines=True) == expected


APOSTROPHE_CASES = [
    ("İstanbul’da", "İstanbul'da"),
    ("Ankara‘da", "Ankara'da"),
    ("Ankaraʼda", "Ankara'da"),
    ("Ankara´da", "Ankara'da"),
    ("Ankara`da", "Ankara'da"),
    ("Ankara′da", "Ankara'da"),
    ("‹x›", "'x'"),
    ("düz 'tırnak'", "düz 'tırnak'"),
    ("“çift”", "“çift”"),  # double quotes are not apostrophes
]


@pytest.mark.parametrize(("src", "expected"), APOSTROPHE_CASES)
def test_apostrophes(src: str, expected: str) -> None:
    assert normalize_apostrophes(src) == expected


QUOTE_CASES = [
    ("“merhaba”", '"merhaba"'),
    ("„Hallo“", '"Hallo"'),
    ("«salut»", '"salut"'),
    ("‘a’ ve “b”", "'a' ve \"b\""),
    ("ʺ", "ʺ"),
    ('düz "tırnak"', 'düz "tırnak"'),
    ("5″ ekran", '5" ekran'),
]


@pytest.mark.parametrize(("src", "expected"), QUOTE_CASES)
def test_quotes(src: str, expected: str) -> None:
    assert normalize_quotes(src) == expected


def test_nfc_composes_decomposed_turkish_letters() -> None:
    decomposed = "I\u0307s\u0327i\u0307g\u0306 c\u0327o\u0308u\u0308"
    result = nfc(decomposed)
    assert "\u0130" in result
    assert "\u015f" in result  # ş
    assert "\u011f" in result  # ğ
    assert "\u00e7" in result  # ç
    assert "\u00f6" in result  # ö
    assert "\u00fc" in result  # ü
    assert nfc(result) == result


def test_normalize_pipeline() -> None:
    raw = "\ufeff “İstanbul’da”  I\u0307yi\u00a0günler  "
    assert normalize(raw) == '"İstanbul\'da" İyi günler'
    assert normalize(raw, quotes=False) == "“İstanbul’da” İyi günler"
    assert normalize(raw, whitespace=False).startswith("\ufeff")
    assert normalize("a\n\n\n\nb  c", keep_newlines=True) == "a\n\nb c"


def test_normalize_leaves_azerbaijani_and_other_scripts_alone() -> None:
    text = "Əli Vüqar'ın kitabı — 日本語 🙂"
    assert normalize(text) == text


# ---------------------------------------------------------------- CLI


def run_cli(argv: list[str], stdin: str | None, monkeypatch: pytest.MonkeyPatch) -> tuple[int, str]:
    out = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out)
    if stdin is not None:
        monkeypatch.setattr(sys, "stdin", io.StringIO(stdin))
    code = main(argv)
    return code, out.getvalue()


CLI_ARG_CASES = [
    (["lower", "ISPARTA", "IĞDIR"], "ısparta ığdır\n"),
    (["upper", "istanbul"], "İSTANBUL\n"),
    (["title", "istanbul'da"], "İstanbul'da\n"),
    (["casefold", "IŞIK"], "ışık\n"),
    (["ascii", "Çığlık"], "Ciglik\n"),
    (["slug", "Çığlık Atan"], "ciglik-atan\n"),
    (["slug", "--sep", "_", "--max-length", "6", "Çığlık Atan"], "ciglik\n"),
    (["clean", "“a”  b"], '"a" b\n'),
    (["clean", "--no-quotes", "“a”  b"], "“a” b\n"),
]


@pytest.mark.parametrize(("argv", "expected"), CLI_ARG_CASES)
def test_cli_arguments(argv: list[str], expected: str, monkeypatch: pytest.MonkeyPatch) -> None:
    code, out = run_cli(argv, None, monkeypatch)
    assert code == 0
    assert out == expected


def test_cli_stdin_passthrough_keeps_text_exact(monkeypatch: pytest.MonkeyPatch) -> None:
    code, out = run_cli(["lower"], "IĞDIR\nİZMİR\n", monkeypatch)
    assert (code, out) == (0, "ığdır\nizmir\n")


def test_cli_slug_per_line(monkeypatch: pytest.MonkeyPatch) -> None:
    code, out = run_cli(["slug"], "Şu Çay\nÜç Ağaç\n", monkeypatch)
    assert (code, out) == (0, "su-cay\nuc-agac\n")


def test_cli_clean_keep_newlines(monkeypatch: pytest.MonkeyPatch) -> None:
    code, out = run_cli(["clean", "--keep-newlines"], "a  b\n\n\n\nc\n", monkeypatch)
    assert (code, out) == (0, "a b\n\nc\n")


def test_cli_sort(monkeypatch: pytest.MonkeyPatch) -> None:
    text = "şeker\nçay\nsu\nçay\nığdır\nilk\n"
    assert run_cli(["sort"], text, monkeypatch) == (0, "çay\nçay\nığdır\nilk\nsu\nşeker\n")
    assert run_cli(["sort", "-u"], text, monkeypatch) == (0, "çay\nığdır\nilk\nsu\nşeker\n")
    assert run_cli(["sort", "-r", "-u"], text, monkeypatch) == (
        0,
        "şeker\nsu\nilk\nığdır\nçay\n",
    )


def test_cli_version_and_errors(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as info:
        main(["--version"])
    assert info.value.code == 0
    assert tr_normalize.__version__ in capsys.readouterr().out
    with pytest.raises(SystemExit) as bad:
        main([])
    assert bad.value.code == 2


def test_version_matches_pyproject() -> None:
    pyproject = (Path(__file__).resolve().parent.parent / "pyproject.toml").read_text(
        encoding="utf-8"
    )
    assert f'version = "{tr_normalize.__version__}"' in pyproject


def test_main_module_runs_in_process(monkeypatch: pytest.MonkeyPatch) -> None:
    out = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out)
    monkeypatch.setattr(sys, "argv", ["tr_normalize", "upper", "iğdır"])
    with pytest.raises(SystemExit) as info:
        runpy.run_module("tr_normalize", run_name="__main__")
    assert info.value.code == 0
    assert out.getvalue() == "İĞDIR\n"


def test_module_entry_point_utf8_roundtrip() -> None:
    src = Path(tr_normalize.__file__).resolve().parent.parent
    env = {"PYTHONPATH": str(src), "PYTHONIOENCODING": "utf-8", "SYSTEMROOT": "C:\\Windows"}
    result = subprocess.run(
        [sys.executable, "-m", "tr_normalize", "lower", "IĞDIR"],
        capture_output=True,
        env=env,
        check=False,
        timeout=60,
    )
    assert result.returncode == 0
    assert result.stdout.decode("utf-8").strip() == "ığdır"
