"""Tests for schedule_generator and schedule_formatter."""

import json
from datetime import datetime

import pytest

from crontab_lint.schedule_generator import next_n_runs, format_runs
from crontab_lint.schedule_formatter import format_schedule_text, format_schedule_json


START = datetime(2024, 1, 15, 12, 0)  # fixed reference point


class TestNextNRuns:
    def test_returns_correct_count(self):
        runs = next_n_runs("* * * * *", n=3, start=START)
        assert len(runs) == 3

    def test_every_minute_increments_by_one(self):
        runs = next_n_runs("* * * * *", n=3, start=START)
        for i in range(1, len(runs)):
            delta = runs[i] - runs[i - 1]
            assert delta.total_seconds() == 60

    def test_hourly_returns_correct_hours(self):
        runs = next_n_runs("@hourly", n=3, start=START)
        assert all(dt.minute == 0 for dt in runs)
        assert len(runs) == 3

    def test_daily_midnight_returns_midnight(self):
        runs = next_n_runs("@daily", n=2, start=START)
        assert all(dt.hour == 0 and dt.minute == 0 for dt in runs)

    def test_specific_time_matches(self):
        # 14:30 every day
        runs = next_n_runs("30 14 * * *", n=2, start=START)
        assert all(dt.hour == 14 and dt.minute == 30 for dt in runs)

    def test_invalid_expression_raises(self):
        with pytest.raises(ValueError, match="Invalid cron expression"):
            next_n_runs("99 * * * *", n=1, start=START)

    def test_n_less_than_one_raises(self):
        with pytest.raises(ValueError, match="n must be at least 1"):
            next_n_runs("* * * * *", n=0, start=START)

    def test_default_start_does_not_raise(self):
        runs = next_n_runs("* * * * *", n=1)
        assert len(runs) == 1

    def test_format_runs_returns_strings(self):
        runs = next_n_runs("* * * * *", n=2, start=START)
        formatted = format_runs(runs)
        assert all(isinstance(s, str) for s in formatted)
        assert len(formatted) == 2


class TestScheduleFormatter:
    def setup_method(self):
        self.expression = "0 9 * * 1"
        self.runs = next_n_runs(self.expression, n=3, start=START)

    def test_text_contains_expression(self):
        text = format_schedule_text(self.expression, self.runs)
        assert self.expression in text

    def test_text_contains_count_label(self):
        text = format_schedule_text(self.expression, self.runs)
        assert "3" in text

    def test_text_lines_equal_count_plus_header(self):
        text = format_schedule_text(self.expression, self.runs)
        # header line + separator + 3 run lines
        assert len(text.splitlines()) == 5

    def test_json_is_valid(self):
        raw = format_schedule_json(self.expression, self.runs)
        data = json.loads(raw)
        assert data["expression"] == self.expression
        assert data["count"] == 3
        assert len(data["runs"]) == 3

    def test_json_custom_format(self):
        raw = format_schedule_json(self.expression, self.runs, fmt="%d/%m/%Y")
        data = json.loads(raw)
        # Each entry should match dd/mm/yyyy pattern
        import re
        pattern = re.compile(r"\d{2}/\d{2}/\d{4}")
        assert all(pattern.match(r) for r in data["runs"])
