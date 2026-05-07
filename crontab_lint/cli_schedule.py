"""CLI sub-command: generate next N scheduled run times."""

import argparse
import sys
from datetime import datetime

from .schedule_generator import next_n_runs
from .schedule_formatter import format_schedule_text, format_schedule_json


def build_schedule_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the *schedule* sub-command onto *subparsers*."""
    p = subparsers.add_parser(
        "schedule",
        help="Show the next N run times for a cron expression.",
    )
    p.add_argument("expression", help="Cron expression (quote if it contains spaces).")
    p.add_argument(
        "-n",
        "--count",
        type=int,
        default=5,
        metavar="N",
        help="Number of future run times to display (default: 5).",
    )
    p.add_argument(
        "--start",
        metavar="DATETIME",
        help="Reference datetime in 'YYYY-MM-DD HH:MM' format (default: now).",
    )
    p.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Output results as JSON.",
    )
    p.add_argument(
        "--fmt",
        default="%Y-%m-%d %H:%M",
        help="strftime format string for displayed datetimes.",
    )
    p.set_defaults(func=run_schedule_command)


def run_schedule_command(args: argparse.Namespace) -> int:
    """Execute the *schedule* sub-command; returns an exit code."""
    start: datetime | None = None
    if args.start:
        try:
            start = datetime.strptime(args.start, "%Y-%m-%d %H:%M")
        except ValueError:
            print(
                f"Error: --start must be in 'YYYY-MM-DD HH:MM' format, got: {args.start}",
                file=sys.stderr,
            )
            return 2

    try:
        runs = next_n_runs(args.expression, n=args.count, start=start)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.as_json:
        print(format_schedule_json(args.expression, runs, fmt=args.fmt))
    else:
        print(format_schedule_text(args.expression, runs, fmt=args.fmt))

    return 0
