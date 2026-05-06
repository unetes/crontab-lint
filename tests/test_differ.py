"""Tests for crontab_lint.differ and crontab_lint.diff_formatter."""

import json
import pytest

from crontab_lint.differ import diff, DiffResult, FieldDiff
from crontab_lint.diff_formatter import format_diff_text, format_diff_json


class TestDiff:
    def test_identical_expressions(self):
        result = diff("0 * * * *", "0 * * * *")
        assert result.identical is True
        assert result.field_diffs == []

    def test_identical_reports_valid(self):
        result = diff("0 12 * * 1", "0 12 * * 1")
        assert result.left_valid is True
        assert result.right_valid is True

    def test_different_minute_field(self):
        result = diff("0 * * * *", "30 * * * *")
        assert result.identical is False
        assert any(fd.field_name == "minute" for fd in result.field_diffs)

    def test_different_hour_field(self):
        result = diff("0 6 * * *", "0 12 * * *")
        assert result.identical is False
        assert any(fd.field_name == "hour" for fd in result.field_diffs)

    def test_multiple_field_diffs(self):
        result = diff("0 6 * * 1", "30 12 * * 5")
        field_names = [fd.field_name for fd in result.field_diffs]
        assert "minute" in field_names
        assert "hour" in field_names
        assert "day_of_week" in field_names

    def test_invalid_left_expression(self):
        result = diff("99 * * * *", "0 * * * *")
        assert result.left_valid is False
        assert len(result.left_errors) > 0
        assert result.field_diffs == []

    def test_invalid_right_expression(self):
        result = diff("0 * * * *", "0 99 * * *")
        assert result.right_valid is False
        assert len(result.right_errors) > 0
        assert result.field_diffs == []

    def test_both_invalid_no_field_diffs(self):
        result = diff("99 * * * *", "0 99 * * *")
        assert result.left_valid is False
        assert result.right_valid is False
        assert result.field_diffs == []

    def test_summary_present_when_valid(self):
        result = diff("0 12 * * *", "0 6 * * *")
        assert result.left_summary is not None
        assert result.right_summary is not None

    def test_at_alias_vs_explicit(self):
        result = diff("@daily", "0 0 * * *")
        # Both should be valid; may or may not be identical after normalization
        assert result.left_valid is True
        assert result.right_valid is True


class TestDiffFormatter:
    def test_text_identical(self):
        result = diff("0 * * * *", "0 * * * *")
        text = format_diff_text(result)
        assert "identical" in text.lower()

    def test_text_shows_changed_fields(self):
        result = diff("0 * * * *", "30 * * * *")
        text = format_diff_text(result)
        assert "minute" in text
        assert "- 0" in text
        assert "+ 30" in text

    def test_text_shows_errors_for_invalid(self):
        result = diff("99 * * * *", "0 * * * *")
        text = format_diff_text(result)
        assert "invalid" in text.lower()
        assert "Error" in text

    def test_json_structure(self):
        result = diff("0 6 * * 1", "0 12 * * 5")
        data = json.loads(format_diff_json(result))
        assert "left" in data
        assert "right" in data
        assert "identical" in data
        assert "field_diffs" in data
        assert isinstance(data["field_diffs"], list)

    def test_json_field_diffs_content(self):
        result = diff("0 6 * * *", "0 12 * * *")
        data = json.loads(format_diff_json(result))
        hour_diff = next((d for d in data["field_diffs"] if d["field"] == "hour"), None)
        assert hour_diff is not None
        assert hour_diff["left"] == "6"
        assert hour_diff["right"] == "12"

    def test_json_identical_flag(self):
        result = diff("* * * * *", "* * * * *")
        data = json.loads(format_diff_json(result))
        assert data["identical"] is True
        assert data["field_diffs"] == []
