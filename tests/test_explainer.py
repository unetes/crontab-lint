"""Tests for crontab_lint.explainer."""

from datetime import datetime

import pytest

from crontab_lint.explainer import explain_next_run, _field_matches


class TestFieldMatches:
    def test_wildcard_always_matches(self):
        assert _field_matches("*", 42, datetime.now()) is True

    def test_exact_value_matches(self):
        assert _field_matches("5", 5, datetime.now()) is True

    def test_exact_value_no_match(self):
        assert _field_matches("5", 6, datetime.now()) is False

    def test_range_matches(self):
        assert _field_matches("1-5", 3, datetime.now()) is True

    def test_range_boundary(self):
        assert _field_matches("1-5", 5, datetime.now()) is True
        assert _field_matches("1-5", 6, datetime.now()) is False

    def test_step_matches(self):
        assert _field_matches("*/15", 0, datetime.now()) is True
        assert _field_matches("*/15", 15, datetime.now()) is True
        assert _field_matches("*/15", 30, datetime.now()) is True
        assert _field_matches("*/15", 7, datetime.now()) is False

    def test_list_matches(self):
        assert _field_matches("1,3,5", 3, datetime.now()) is True
        assert _field_matches("1,3,5", 4, datetime.now()) is False

    def test_sunday_as_7(self):
        # cron allows Sunday as 7; weekday() returns 6 for Sunday but we map +1 -> 7
        assert _field_matches("7", 0, datetime.now()) is True


class TestExplainNextRun:
    def _fixed_now(self) -> datetime:
        # Monday 2024-01-15 10:00
        return datetime(2024, 1, 15, 10, 0, 0)

    def test_every_minute_next_run_is_one_minute_ahead(self):
        result = explain_next_run("* * * * *", now=self._fixed_now())
        assert result["next_run"] == "2024-01-15T10:01:00"
        assert "in 1 minute" in result["description"]

    def test_specific_hour_and_minute(self):
        # Next run at 11:30 same day
        result = explain_next_run("30 11 * * *", now=self._fixed_now())
        assert result["next_run"] == "2024-01-15T11:30:00"
        assert "11:30" in result["description"]

    def test_past_time_rolls_to_next_day(self):
        # 09:00 is in the past relative to 10:00 now
        result = explain_next_run("0 9 * * *", now=self._fixed_now())
        assert result["next_run"] == "2024-01-16T09:00:00"

    def test_at_daily_alias(self):
        result = explain_next_run("@daily", now=self._fixed_now())
        # @daily = 0 0 * * * — next midnight
        assert result["next_run"] == "2024-01-16T00:00:00"

    def test_at_hourly_alias(self):
        result = explain_next_run("@hourly", now=self._fixed_now())
        # @hourly = 0 * * * * — next top-of-hour
        assert result["next_run"] == "2024-01-15T11:00:00"

    def test_invalid_expression_returns_none(self):
        result = explain_next_run("99 99 99 99 99")
        assert result["next_run"] is None
        assert "No matching" in result["description"] or "Could not parse" in result["description"]

    def test_description_contains_in_hours_for_distant_run(self):
        # Run at 23:00 from 10:00 — 13 hours away
        result = explain_next_run("0 23 * * *", now=self._fixed_now())
        assert "hour" in result["description"]

    def test_result_keys_present(self):
        result = explain_next_run("* * * * *", now=self._fixed_now())
        assert "next_run" in result
        assert "description" in result
