"""Render docs/demo.svg from real library and CLI output; no external tools needed."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import tr_normalize  # noqa: E402,F401  (used by the evaluated demo expressions)
from tr_normalize import tr_lower, tr_sorted, tr_title, tr_upper  # noqa: E402,F401

TARGET = ROOT / "docs" / "demo.svg"

# (expression, label colour) evaluated for real; repr() of the result is shown.
EXPRESSIONS = (
    '"ISPARTA".lower()',
    'tr_lower("ISPARTA")',
    '"İZMİR".lower()',
    'tr_lower("İZMİR")',
    '"istanbul".upper()',
    'tr_upper("istanbul")',
    'tr_title("istanbul\'da")',
    'sorted(["şeker", "çay", "ılık", "ilk", "cam"])',
    'tr_sorted(["şeker", "çay", "ılık", "ilk", "cam"])',
)
CLI = (("slug", "Çığlık Atan Şöför’ün Günü!"), ("ascii", "Çığlık Şöför"))

GREEN = "#8ee6b0"
TEXT = "#d6deeb"
RED = "#ff9b9b"


def render() -> str:
    """Evaluate each snippet, run the CLI and lay the output out as SVG text."""
    lines: list[tuple[str, str]] = []
    for expr in EXPRESSIONS:
        value = repr(eval(expr))  # fixed, trusted expressions above
        wrong = not expr.startswith("tr_")
        lines.append((">>> " + expr, GREEN))
        lines.append((value, RED if wrong else TEXT))
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"), PYTHONIOENCODING="utf-8")
    for args in CLI:
        result = subprocess.run(
            [sys.executable, "-m", "tr_normalize", *args],
            cwd=ROOT,
            env=env,
            capture_output=True,
            check=False,
            timeout=30,
        )
        if result.returncode != 0 or result.stderr:
            raise RuntimeError("Demo command failed: " + " ".join(args))
        lines.append(
            ("$ tr-normalize " + " ".join(f'"{a}"' if " " in a else a for a in args), GREEN)
        )
        lines.extend((line, TEXT) for line in result.stdout.decode("utf-8").splitlines())

    height = 96 + 24 * len(lines)
    rows = "\n".join(
        f'    <text x="28" y="{86 + 24 * index}" fill="{color}">{escape(line)}</text>'
        for index, (line, color) in enumerate(lines)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="960" height="{height}"
     viewBox="0 0 960 {height}" role="img" aria-labelledby="title description">
  <title id="title">tr-normalize: str.lower() versus Turkish-aware functions</title>
  <desc id="description">Real output. Red lines are Python's built-in string methods,
    which give wrong results for Turkish; white lines come from tr-normalize.</desc>
  <rect width="960" height="{height}" rx="16" fill="#0d1117"/>
  <path d="M16 0H944Q960 0 960 16V48H0V16Q0 0 16 0Z" fill="#1c2431"/>
  <circle cx="28" cy="24" r="6" fill="#ff605c"/>
  <circle cx="50" cy="24" r="6" fill="#ffbd44"/>
  <circle cx="72" cy="24" r="6" fill="#00ca4e"/>
  <g font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="16">
    <text x="480" y="30" text-anchor="middle" fill="#b6c2d4"
      >tr-normalize | red = Python built-in</text>
{rows}
  </g>
</svg>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if docs/demo.svg is stale")
    args = parser.parse_args()
    svg = render()
    if args.check:
        if not TARGET.is_file() or TARGET.read_text(encoding="utf-8") != svg:
            print("Demo is stale; run python scripts/make-demo.py", file=sys.stderr)
            return 1
        print("docs/demo.svg matches real output")
        return 0
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    with TARGET.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(svg)
    print(f"wrote {TARGET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
