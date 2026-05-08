"""Tests for the conflict detection CLI."""

import json
import pytest
from unittest.mock import patch
from crontab_lint.cli_conflict import build_conflict_parser, run_conflict_command


class TestBuildConflictParser:
    def test_parses_two_expressions(self):
        parser = build_conflict_parser()
        args = parser.parse_args(["0 6 * * *", "0 18 * * *"])
        assert args.expressions == ["0 6 * * *", "0 18 * * *"]

    def test_default_window(self):
        parser = build_conflict_parser()
        args = parser.parse_args(["* * * * *", "0 * * * *"])
        assert args.window == 100

    def test_custom_window(self):
        parser = build_conflict_parser()
        args = parser.parse_args(["--window", "50", "* * * * *", "0 * * * *"])
        assert args.window == 50

    def test_default_format_is_text(self):
        parser = build_conflict_parser()
        args = parser.parse_args(["* * * * *", "0 * * * *"])
        assert args.format == "text"

    def test_json_format_flag(self):
        parser = build_conflict_parser()
        args = parser.parse_args(["--format", "json", "* * * * *", "0 * * * *"])
        assert args.format == "json"


class TestRunConflictCommand:
    def test_no_conflict_exits_zero(self):
        with pytest.raises(SystemExit) as exc_info:
            run_conflict_command(["0 6 * * *", "0 18 * * *"])
        assert exc_info.value.code == 0 or exc_info.value.code is None

    def test_conflict_exits_one(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            run_conflict_command(["* * * * *", "* * * * *", "--window", "5"])
        assert exc_info.value.code == 1

    def test_text_output_printed(self, capsys):
        try:
            run_conflict_command(["0 6 * * *", "0 18 * * *"])
        except SystemExit:
            pass
        captured = capsys.readouterr()
        assert "expression" in captured.out.lower() or "conflict" in captured.out.lower()

    def test_json_output_is_valid_json(self, capsys):
        try:
            run_conflict_command(["0 6 * * *", "0 18 * * *", "--format", "json"])
        except SystemExit:
            pass
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "has_conflicts" in data

    def test_single_expression_raises_error(self):
        with pytest.raises(SystemExit):
            run_conflict_command(["0 6 * * *"])
