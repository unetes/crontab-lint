"""Output formatters for crontab-lint results."""

from dataclasses import dataclass
from typing import Optional
from crontab_lint.parser import ParsedCron
from crontab_lint.validator import ValidationResult


@dataclass
class LintResult:
    expression: str
    parsed: Optional[ParsedCron]
    validation: ValidationResult
    summary: Optional[str]


def format_text(result: LintResult) -> str:
    """Format a LintResult as plain human-readable text."""
    lines = []
    status = "✓ VALID" if result.validation.is_valid else "✗ INVALID"
    lines.append(f"{status}  {result.expression}")

    if result.summary:
        lines.append(f"  Summary : {result.summary}")

    if result.validation.errors:
        for err in result.validation.errors:
            lines.append(f"  ERROR   : {err}")

    if result.validation.warnings:
        for warn in result.validation.warnings:
            lines.append(f"  WARNING : {warn}")

    return "\n".join(lines)


def format_json(result: LintResult) -> dict:
    """Format a LintResult as a JSON-serialisable dictionary."""
    return {
        "expression": result.expression,
        "valid": result.validation.is_valid,
        "summary": result.summary,
        "errors": list(result.validation.errors),
        "warnings": list(result.validation.warnings),
        "fields": (
            {
                "minute": result.parsed.minute.raw,
                "hour": result.parsed.hour.raw,
                "day_of_month": result.parsed.day_of_month.raw,
                "month": result.parsed.month.raw,
                "day_of_week": result.parsed.day_of_week.raw,
            }
            if result.parsed
            else None
        ),
    }
