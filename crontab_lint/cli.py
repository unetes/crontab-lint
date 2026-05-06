"""Command-line interface for crontab-lint."""

import argparse
import json
import sys
from typing import List

from crontab_lint.linter import lint_many
from crontab_lint.formatter import format_text, format_json


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-lint",
        description="Static analyzer and validator for crontab expressions.",
    )
    p.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPRESSION",
        help="One or more cron expressions to lint.",
    )
    p.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Output results as JSON.",
    )
    p.add_argument(
        "--file",
        "-f",
        metavar="FILE",
        help="Read expressions from a file (one per line).",
    )
    return p


def collect_expressions(args: argparse.Namespace) -> List[str]:
    expressions = list(args.expressions)
    if args.file:
        with open(args.file, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#"):
                    expressions.append(line)
    return expressions


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    expressions = collect_expressions(args)
    if not expressions:
        parser.print_help()
        return 0

    results = lint_many(expressions)
    has_errors = any(not r.validation.is_valid for r in results)

    if args.as_json:
        output = [format_json(r) for r in results]
        print(json.dumps(output, indent=2))
    else:
        for r in results:
            print(format_text(r))

    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
