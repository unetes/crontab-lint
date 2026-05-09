"""Tests for history_tracker and history_formatter."""

import json
import os
import tempfile

import pytest

from crontab_lint.history_tracker import (
    History,
    HistoryEntry,
    load_history,
    record_lint_result,
    save_history,
)
from crontab_lint.history_formatter import (
    format_history_json,
    format_history_text,
    format_invalid_text,
)


def _make_entry(expr="* * * * *", valid=True, errors=None, summary="Every minute"):
    return HistoryEntry(
        expression=expr,
        command=None,
        is_valid=valid,
        errors=errors or [],
        summary=summary,
    )


class TestHistory:
    def test_add_and_last(self):
        h = History()
        h.add(_make_entry("0 * * * *"))
        h.add(_make_entry("0 0 * * *"))
        assert len(h.last(10)) == 2

    def test_last_limits_results(self):
        h = History()
        for i in range(15):
            h.add(_make_entry(f"{i} * * * *"))
        assert len(h.last(5)) == 5
        assert h.last(5)[-1].expression == "14 * * * *"

    def test_clear_empties_history(self):
        h = History()
        h.add(_make_entry())
        h.clear()
        assert h.entries == []

    def test_filter_invalid(self):
        h = History()
        h.add(_make_entry(valid=True))
        h.add(_make_entry(valid=False, errors=["bad field"]))
        assert len(h.filter_invalid()) == 1


class TestPersistence:
    def test_save_and_load_roundtrip(self, tmp_path):
        path = str(tmp_path / "history.json")
        h = History()
        h.add(_make_entry("0 9 * * 1", summary="Weekly Monday 9am"))
        save_history(h, path)
        loaded = load_history(path)
        assert len(loaded.entries) == 1
        assert loaded.entries[0].expression == "0 9 * * 1"

    def test_load_missing_file_returns_empty(self, tmp_path):
        h = load_history(str(tmp_path / "nonexistent.json"))
        assert h.entries == []

    def test_record_lint_result_appends(self, tmp_path):
        path = str(tmp_path / "hist.json")

        class FakeLint:
            expression = "*/5 * * * *"
            command = "backup.sh"
            is_valid = True
            errors = []
            summary = "Every 5 minutes"

        entry = record_lint_result(FakeLint(), path)
        assert entry.expression == "*/5 * * * *"
        loaded = load_history(path)
        assert len(loaded.entries) == 1


class TestHistoryFormatter:
    def test_format_text_empty(self):
        h = History()
        assert "No history" in format_history_text(h)

    def test_format_text_contains_expression(self):
        h = History()
        h.add(_make_entry("0 0 * * *", summary="Daily midnight"))
        text = format_history_text(h)
        assert "0 0 * * *" in text
        assert "Daily midnight" in text

    def test_format_json_structure(self):
        h = History()
        h.add(_make_entry())
        data = json.loads(format_history_json(h))
        assert "history" in data
        assert data["history"][0]["expression"] == "* * * * *"

    def test_format_invalid_text_no_invalid(self):
        h = History()
        h.add(_make_entry(valid=True))
        assert "No invalid" in format_invalid_text(h)

    def test_format_invalid_text_shows_errors(self):
        h = History()
        h.add(_make_entry(valid=False, errors=["minute out of range"]))
        text = format_invalid_text(h)
        assert "minute out of range" in text
