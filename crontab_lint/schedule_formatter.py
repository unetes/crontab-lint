"""Text and JSON formatters for schedule generation results."""

import json
from datetime import datetime
from typing import List


def format_schedule_text(
    expression: str,
    runs: List[datetime],
    fmt: str = "%Y-%m-%d %H:%M",
) -> str:
    """Return a human-readable multi-line schedule report."""
    lines = [f"Next {len(runs)} run(s) for: {expression}"]
    lines.append("-" * 40)
    for i, dt in enumerate(runs, 1):
        lines.append(f"  {i:>2}. {dt.strftime(fmt)}")
    return "\n".join(lines)


def format_schedule_json(
    expression: str,
    runs: List[datetime],
    fmt: str = "%Y-%m-%d %H:%M",
) -> str:
    """Return a JSON string with schedule information."""
    payload = {
        "expression": expression,
        "count": len(runs),
        "runs": [dt.strftime(fmt) for dt in runs],
    }
    return json.dumps(payload, indent=2)
