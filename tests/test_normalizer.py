"""Tests for crontab_lint.normalizer."""

import pytest
from crontab_lint.normalizer import normalize, _normalize_field, MONTH_NAMES, WEEKDAY_NAMES


class TestNormalize:
    def test_at_daily_expands(self):
        assert normalize("@daily") == "0 0 * * *"

    def test_at_midnight_expands(self):
        assert normalize("@midnight") == "0 0 * * *"

    def test_at_hourly_expands(self):
        assert normalize("@hourly") == "0 * * * *"

    def test_at_weekly_expands(self):
        assert normalize("@weekly") == "0 0 * * 0"

    def test_at_monthly_expands(self):
        assert normalize("@monthly") == "0 0 1 * *"

    def test_at_yearly_expands(self):
        assert normalize("@yearly") == "0 0 1 1 *"

    def test_at_annually_expands(self):
        assert normalize("@annually") == "0 0 1 1 *"

    def test_alias_case_insensitive(self):
        assert normalize("@Daily") == "0 0 * * *"

    def test_standard_expression_unchanged(self):
        assert normalize("0 0 * * *") == "0 0 * * *"

    def test_month_name_replaced(self):
        result = normalize("0 0 1 jan *")
        assert result == "0 0 1 1 *"

    def test_weekday_name_replaced(self):
        result = normalize("0 9 * * mon")
        assert result == "0 9 * * 1"

    def test_comma_list_sorted(self):
        result = normalize("5,1,3 * * * *")
        assert result == "1,3,5 * * * *"

    def test_month_comma_list_with_names(self):
        result = normalize("0 0 1 mar,jan,feb *")
        assert result == "0 0 1 1,2,3 *"

    def test_weekday_comma_list_with_names(self):
        result = normalize("0 0 * * fri,mon,wed")
        assert result == "0 0 * * 1,3,5"

    def test_expression_with_command_uses_first_five_fields(self):
        result = normalize("*/5 * * * * /usr/bin/backup")
        assert result == "*/5 * * * *"

    def test_step_value_preserved(self):
        assert normalize("*/15 * * * *") == "*/15 * * * *"

    def test_range_preserved(self):
        assert normalize("0 9-17 * * *") == "0 9-17 * * *"

    def test_malformed_too_few_fields_returned_as_is(self):
        result = normalize("* * *")
        assert result == "* * *"


class TestNormalizeField:
    def test_empty_mapping_leaves_field_unchanged(self):
        assert _normalize_field("5", {}) == "5"

    def test_name_substitution(self):
        assert _normalize_field("jan", MONTH_NAMES) == "1"

    def test_weekday_substitution(self):
        assert _normalize_field("sun", WEEKDAY_NAMES) == "0"

    def test_comma_list_sorted_numerically(self):
        assert _normalize_field("10,2,5", {}) == "2,5,10"
