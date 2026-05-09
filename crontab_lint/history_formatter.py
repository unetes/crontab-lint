"""Format History objects as human-readable text or JSON."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import List

from crontab_lint.history_tracker import History, HistoryEntry


def _status(entry: HistoryEntry) -> str:
    return "✓" if entry.is_valid else "✗"


def format_history_text(history: History, last: int = 10) -> str:
    entries = history.last(last)
    if not entries:
        return "No history entries found."
    lines: List[str] = [f"History (last {len(entries)} entries):", ""]
    for i, e in enumerate(entries, 1):
        cmd_part = f"  command : {e.command}" if e.command else ""
        error_part = (
            "  errors  : " + "; ".join(e.errors) if e.errors else ""
        )
        block = [
            f"{i}. [{_status(e)}] {e.expression}",
            f"   timestamp : {e.timestamp}",
            f"   summary   : {e.summary}",
        ]
        if cmd_part:
            block.append(f"   {cmd_part}")
        if error_part:
            block.append(f"   {error_part}")
        lines.extend(block)
        lines.append("")
    return "\n".join(lines).rstrip()


def format_history_json(history: History, last: int = 10) -> str:
    entries = history.last(last)
    return json.dumps(
        {"history": [asdict(e) for e in entries]},
        indent=2,
    )


def format_invalid_text(history: History) -> str:
    invalid = history.filter_invalid()
    if not invalid:
        return "No invalid expressions in history."
    lines = [f"Invalid expressions ({len(invalid)} total):", ""]
    for e in invalid:
        lines.append(f"  {e.expression}")
        for err in e.errors:
            lines.append(f"    - {err}")
        lines.append("")
    return "\n".join(lines).rstrip()
