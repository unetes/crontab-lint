"""CLI entry point for the conflict detection command."""

import argparse
import sys
from .conflict_detector import detect_conflicts
from .conflict_formatter import format_conflict_text, format_conflict_json


def build_conflict_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-lint conflicts",
        description="Detect scheduling conflicts between cron expressions.",
    )
    parser.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="Two or more cron expressions to compare.",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=100,
        metavar="N",
        help="Number of future runs to sample per expression (default: 100).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    return parser


def run_conflict_command(argv=None) -> None:
    parser = build_conflict_parser()
    args = parser.parse_args(argv)

    if len(args.expressions) < 2:
        parser.error("At least two expressions are required to detect conflicts.")

    report = detect_conflicts(args.expressions, window=args.window)

    if args.format == "json":
        print(format_conflict_json(report))
    else:
        print(format_conflict_text(report))

    if report.has_conflicts:
        sys.exit(1)
