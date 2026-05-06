"""Diff two crontab expressions and highlight semantic differences."""

from dataclasses import dataclass, field
from typing import List, Optional

from .linter import lint
from .summarizer import summarize
from .parser import parse, normalize_expression


@dataclass
class FieldDiff:
    """Represents a difference in a single cron field."""
    field_name: str
    left: str
    right: str
    left_summary: str
    right_summary: str


@dataclass
class DiffResult:
    """Result of comparing two crontab expressions."""
    left: str
    right: str
    identical: bool
    left_valid: bool
    right_valid: bool
    left_errors: List[str] = field(default_factory=list)
    right_errors: List[str] = field(default_factory=list)
    field_diffs: List[FieldDiff] = field(default_factory=list)
    left_summary: Optional[str] = None
    right_summary: Optional[str] = None


FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]


def diff(left: str, right: str) -> DiffResult:
    """Compare two crontab expressions semantically."""
    left_result = lint(left)
    right_result = lint(right)

    left_valid = left_result.is_valid
    right_valid = right_result.is_valid
    left_errors = left_result.errors
    right_errors = right_result.errors

    left_summary = left_result.summary if left_valid else None
    right_summary = right_result.summary if right_valid else None

    if left.strip() == right.strip():
        return DiffResult(
            left=left, right=right, identical=True,
            left_valid=left_valid, right_valid=right_valid,
            left_errors=left_errors, right_errors=right_errors,
            left_summary=left_summary, right_summary=right_summary,
        )

    field_diffs: List[FieldDiff] = []

    if left_valid and right_valid:
        left_parsed = parse(normalize_expression(left))
        right_parsed = parse(normalize_expression(right))

        left_fields = [
            left_parsed.minute, left_parsed.hour,
            left_parsed.day_of_month, left_parsed.month, left_parsed.day_of_week,
        ]
        right_fields = [
            right_parsed.minute, right_parsed.hour,
            right_parsed.day_of_month, right_parsed.month, right_parsed.day_of_week,
        ]

        for name, lf, rf in zip(FIELD_NAMES, left_fields, right_fields):
            if lf.raw != rf.raw:
                field_diffs.append(FieldDiff(
                    field_name=name,
                    left=lf.raw,
                    right=rf.raw,
                    left_summary=summarize(left).split(",")[0] if left_valid else "",
                    right_summary=summarize(right).split(",")[0] if right_valid else "",
                ))

    return DiffResult(
        left=left, right=right, identical=False,
        left_valid=left_valid, right_valid=right_valid,
        left_errors=left_errors, right_errors=right_errors,
        field_diffs=field_diffs,
        left_summary=left_summary, right_summary=right_summary,
    )
