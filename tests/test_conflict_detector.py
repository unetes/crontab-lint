"""Tests for conflict_detector and conflict_formatter."""

import json
from datetime import datetime
import pytest
from crontab_lint.conflict_detector import detect_conflicts, Conflict, ConflictReport
from crontab_lint.conflict_formatter import format_conflict_text, format_conflict_json

FROM_DT = datetime(2024, 1, 1, 0, 0)


class TestDetectConflicts:
    def test_identical_expressions_conflict(self):
        report = detect_conflicts(["* * * * *", "* * * * *"], window=10, from_dt=FROM_DT)
        assert report.has_conflicts
        assert len(report.conflicts) == 1
        assert report.conflicts[0].overlap_count == 10

    def test_no_conflict_different_hours(self):
        report = detect_conflicts(["0 6 * * *", "0 18 * * *"], window=30, from_dt=FROM_DT)
        assert not report.has_conflicts
        assert report.total_overlaps == 0

    def test_three_expressions_multiple_pairs(self):
        report = detect_conflicts(
            ["0 * * * *", "0 * * * *", "30 * * * *"],
            window=24,
            from_dt=FROM_DT,
        )
        # pair (0,1) should conflict; pairs (0,2) and (1,2) should not
        assert report.has_conflicts
        conflict_pairs = [(c.expr_a, c.expr_b) for c in report.conflicts]
        assert ("0 * * * *", "0 * * * *") in conflict_pairs

    def test_report_total_overlaps_sums_correctly(self):
        report = detect_conflicts(["* * * * *", "* * * * *"], window=5, from_dt=FROM_DT)
        assert report.total_overlaps == 5

    def test_expressions_stored_in_report(self):
        exprs = ["0 6 * * *", "0 18 * * *"]
        report = detect_conflicts(exprs, window=10, from_dt=FROM_DT)
        assert report.expressions == exprs

    def test_invalid_expression_does_not_raise(self):
        report = detect_conflicts(["NOT_VALID", "0 * * * *"], window=5, from_dt=FROM_DT)
        assert isinstance(report, ConflictReport)


class TestConflictFormatter:
    def test_text_no_conflict(self):
        report = detect_conflicts(["0 6 * * *", "0 18 * * *"], window=10, from_dt=FROM_DT)
        text = format_conflict_text(report)
        assert "No scheduling conflicts" in text

    def test_text_with_conflict(self):
        report = detect_conflicts(["* * * * *", "* * * * *"], window=5, from_dt=FROM_DT)
        text = format_conflict_text(report)
        assert "Conflict #1" in text
        assert "Expression A" in text
        assert "Expression B" in text

    def test_json_structure(self):
        report = detect_conflicts(["0 6 * * *", "0 18 * * *"], window=5, from_dt=FROM_DT)
        data = json.loads(format_conflict_json(report))
        assert "has_conflicts" in data
        assert "conflicts" in data
        assert "expressions" in data
        assert "total_overlaps" in data

    def test_json_conflict_fields(self):
        report = detect_conflicts(["* * * * *", "* * * * *"], window=3, from_dt=FROM_DT)
        data = json.loads(format_conflict_json(report))
        assert data["has_conflicts"] is True
        conflict = data["conflicts"][0]
        assert "expr_a" in conflict
        assert "expr_b" in conflict
        assert "overlap_count" in conflict
        assert "overlapping_times" in conflict
        assert conflict["overlap_count"] == 3
