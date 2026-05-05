"""Tests for parser, validator, and summarizer modules."""

import pytest
from crontab_lint.parser import parse
from crontab_lint.validator import validate
from crontab_lint.summarizer import summarize


class TestParser:
    def test_parse_standard_expression(self):
        result = parse("0 12 * * 1")
        assert len(result.fields) == 5
        assert result.fields[0].raw == "0"
        assert result.fields[1].raw == "12"
        assert result.command is None

    def test_parse_with_command(self):
        result = parse("*/5 * * * * /usr/bin/backup.sh")
        assert result.command == "/usr/bin/backup.sh"

    def test_parse_special_at_daily(self):
        result = parse("@daily")
        assert result.fields[0].raw == "0"
        assert result.fields[1].raw == "0"

    def test_parse_special_at_hourly(self):
        result = parse("@hourly")
        assert result.fields[0].raw == "0"
        assert result.fields[1].raw == "*"

    def test_parse_too_few_fields(self):
        with pytest.raises(ValueError, match="expected at least 5 fields"):
            parse("* * * *")


class TestValidator:
    def test_valid_simple_expression(self):
        result = validate(parse("0 12 * * 1"))
        assert result.valid is True
        assert result.errors == []

    def test_invalid_minute_out_of_range(self):
        result = validate(parse("60 12 * * 1"))
        assert result.valid is False
        assert any("minute" in e for e in result.errors)

    def test_invalid_hour_out_of_range(self):
        result = validate(parse("0 25 * * 1"))
        assert result.valid is False
        assert any("hour" in e for e in result.errors)

    def test_valid_step_expression(self):
        result = validate(parse("*/15 * * * *"))
        assert result.valid is True

    def test_invalid_step_zero(self):
        result = validate(parse("*/0 * * * *"))
        assert result.valid is False

    def test_warning_dom_and_dow_both_set(self):
        result = validate(parse("0 0 15 * 1"))
        assert result.valid is True
        assert len(result.warnings) == 1

    def test_valid_month_alias(self):
        result = validate(parse("0 0 1 jan *"))
        assert result.valid is True

    def test_valid_range_expression(self):
        result = validate(parse("0 9-17 * * 1-5"))
        assert result.valid is True


class TestSummarizer:
    def test_summarize_every_minute(self):
        summary = summarize(parse("* * * * *"))
        assert "every minute" in summary
        assert "every hour" in summary

    def test_summarize_specific_time(self):
        summary = summarize(parse("0 12 * * *"))
        assert "0" in summary
        assert "12" in summary

    def test_summarize_with_command(self):
        summary = summarize(parse("0 0 * * * /backup.sh"))
        assert "/backup.sh" in summary

    def test_summarize_day_of_week(self):
        summary = summarize(parse("0 9 * * 1"))
        assert "Mon" in summary

    def test_summarize_month(self):
        summary = summarize(parse("0 0 1 6 *"))
        assert "Jun" in summary
