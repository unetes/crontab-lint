"""Track and persist a history of linted crontab expressions."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class HistoryEntry:
    expression: str
    command: Optional[str]
    is_valid: bool
    errors: List[str]
    summary: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class History:
    entries: List[HistoryEntry] = field(default_factory=list)

    def add(self, entry: HistoryEntry) -> None:
        self.entries.append(entry)

    def clear(self) -> None:
        self.entries.clear()

    def last(self, n: int = 10) -> List[HistoryEntry]:
        return self.entries[-n:]

    def filter_invalid(self) -> List[HistoryEntry]:
        return [e for e in self.entries if not e.is_valid]


def load_history(path: str) -> History:
    """Load history from a JSON file. Returns empty History if file missing."""
    if not os.path.exists(path):
        return History()
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    entries = [HistoryEntry(**item) for item in raw.get("entries", [])]
    return History(entries=entries)


def save_history(history: History, path: str) -> None:
    """Persist history to a JSON file, creating parent directories as needed."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(
            {"entries": [asdict(e) for e in history.entries]},
            fh,
            indent=2,
        )


def record_lint_result(lint_result, path: str) -> HistoryEntry:
    """Append a LintResult to the history file and return the new entry."""
    history = load_history(path)
    entry = HistoryEntry(
        expression=lint_result.expression,
        command=lint_result.command,
        is_valid=lint_result.is_valid,
        errors=list(lint_result.errors),
        summary=lint_result.summary or "",
    )
    history.add(entry)
    save_history(history, path)
    return entry
