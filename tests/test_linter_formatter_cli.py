"""Tests for linter, formatter, and CLI modules."""

import json
from unittest.mock import patch

import pytest

from crontab_lint.linter import lint, lint_many, lint_to_text, lint_to_json
from crontab_lint.formatter import format_text, format_json
from crontab_lint.cli import main


# ---------------------------------------------------------------------------
# Linter
# ---------------------------------------------------------------------------

class TestLinter:
    def test_valid_expression_returns_is_valid(self):
        result = lint("0 12 * * *")
        assert result.validation.is_valid is True
        assert result.parsed is not None
        assert result.summary is not None

    def test_invalid_expression_returns_errors(self):
        result = lint("99 * * * *")
        assert result.validation.is_valid is False
        assert result.validation.errors

    def test_parse_error_captured_gracefully(self):
        result = lint("not-a-cron")
        assert result.validation.is_valid is False
        assert result.parsed is None

    def test_lint_many_returns_list(self):
        results = lint_many(["0 * * * *", "@daily"])
        assert len(results) == 2
        assert all(r.validation.is_valid for r in results)

    def test_lint_to_text_returns_string(self):
        text = lint_to_text("*/5 * * * *")
        assert isinstance(text, str)
        assert "VALID" in text

    def test_lint_to_json_returns_valid_json(self):
        raw = lint_to_json("0 0 * * 1")
        data = json.loads(raw)
        assert "valid" in data
        assert "expression" in data


# ---------------------------------------------------------------------------
# Formatter
# ---------------------------------------------------------------------------

class TestFormatter:
    def test_format_text_valid(self):
        result = lint("0 6 * * *")
        text = format_text(result)
        assert "✓ VALID" in text
        assert result.expression in text

    def test_format_text_invalid_shows_errors(self):
        result = lint("60 * * * *")
        text = format_text(result)
        assert "✗ INVALID" in text
        assert "ERROR" in text

    def test_format_json_structure(self):
        result = lint("30 8 * * 1-5")
        data = format_json(result)
        assert set(data.keys()) == {"expression", "valid", "summary", "errors", "warnings", "fields"}
        assert isinstance(data["errors"], list)
        assert isinstance(data["warnings"], list)

    def test_format_json_fields_none_on_parse_error(self):
        result = lint("bad expression here")
        data = format_json(result)
        assert data["fields"] is None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

class TestCLI:
    def test_valid_expression_exits_zero(self):
        assert main(["0 * * * *"]) == 0

    def test_invalid_expression_exits_one(self):
        assert main(["99 * * * *"]) == 1

    def test_json_flag_outputs_json(self, capsys):
        main(["--json", "@daily"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert isinstance(data, list)
        assert data[0]["valid"] is True

    def test_no_args_exits_zero(self):
        assert main([]) == 0

    def test_file_flag(self, tmp_path, capsys):
        cron_file = tmp_path / "crons.txt"
        cron_file.write_text("# comment\n0 * * * *\n@hourly\n")
        code = main(["--file", str(cron_file)])
        assert code == 0
        captured = capsys.readouterr()
        assert captured.out.count("✓ VALID") == 2
