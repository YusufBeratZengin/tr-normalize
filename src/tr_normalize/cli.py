"""Command line interface: ``tr-normalize <command> [text...]``."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence

from . import __version__
from .case import tr_casefold, tr_lower, tr_title, tr_upper
from .fold import to_ascii
from .slug import tr_slugify
from .sort import tr_sorted
from .text import normalize

_SIMPLE: dict[str, Callable[[str], str]] = {
    "lower": tr_lower,
    "upper": tr_upper,
    "title": tr_title,
    "casefold": tr_casefold,
    "ascii": to_ascii,
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tr-normalize",
        description="Turkish-aware case conversion, sorting, ASCII folding and text cleanup. "
        "Reads the text arguments, or standard input when none are given.",
    )
    parser.add_argument("--version", action="version", version=f"tr-normalize {__version__}")
    sub = parser.add_subparsers(dest="command", required=True, metavar="command")

    def add(name: str, help_text: str) -> argparse.ArgumentParser:
        p = sub.add_parser(name, help=help_text, description=help_text)
        p.add_argument("text", nargs="*", help="text to process (default: read standard input)")
        return p

    add("lower", "lowercase (I -> ı, İ -> i)")
    add("upper", "uppercase (i -> İ, ı -> I)")
    add("title", "title case (istanbul'da -> İstanbul'da)")
    add("casefold", "caseless form for comparisons")
    add("ascii", "fold ç ğ ı ö ş ü to c g i o s u")
    slug = add("slug", "make a URL slug (one per input line)")
    slug.add_argument("--sep", default="-", help="separator (default: -)")
    slug.add_argument("--max-length", type=int, default=None, help="maximum slug length")
    clean = add("clean", "NFC, straight quotes and apostrophes, tidy whitespace")
    clean.add_argument("--keep-newlines", action="store_true", help="keep line breaks")
    clean.add_argument("--no-quotes", action="store_true", help="leave quotes untouched")
    srt = add("sort", "sort lines in Turkish alphabetical order")
    srt.add_argument("-r", "--reverse", action="store_true", help="reverse order")
    srt.add_argument("-u", "--unique", action="store_true", help="drop repeated lines")
    return parser


def _read_stdin() -> str:
    stream = sys.stdin
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")
    return stream.read()


def _write(text: str) -> None:
    stream = sys.stdout
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", newline="\n")
    stream.write(text)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return the process exit code."""
    args = _build_parser().parse_args(argv)
    from_args = bool(args.text)
    raw = " ".join(args.text) if from_args else _read_stdin()
    command: str = args.command

    if command in _SIMPLE:
        result = _SIMPLE[command](raw)
    elif command == "slug":
        lines = [raw] if from_args else raw.splitlines()
        result = "\n".join(
            tr_slugify(line, separator=args.sep, max_length=args.max_length) for line in lines
        )
        from_args = True  # always end with one newline
    elif command == "clean":
        result = normalize(raw, quotes=not args.no_quotes, keep_newlines=args.keep_newlines)
    else:  # sort
        lines = raw.splitlines()
        if args.unique:
            lines = list(dict.fromkeys(lines))
        result = "\n".join(tr_sorted(lines, reverse=args.reverse))
        from_args = True

    if (from_args or raw.endswith("\n")) and not result.endswith("\n"):
        result += "\n"
    _write(result)
    return 0
