"""High-level linting API that ties parser, validator, and summarizer together."""

import json
from typing import List, Optional

from crontab_lint.parser import parse
from crontab_lint.validator import validate
from crontab_lint.summarizer import summarize
from crontab_lint.formatter import LintResult, format_text, format_json


def lint(expression: str) -> LintResult:
    """Lint a single cron expression and return a structured LintResult."""
    try:
        parsed = parse(expression)
    except Exception as exc:  # noqa: BLE001
        from crontab_lint.validator import ValidationResult

        validation = ValidationResult(
            is_valid=False,
            errors=[f"Parse error: {exc}"],
            warnings=[],
        )
        return LintResult(
            expression=expression,
            parsed=None,
            validation=validation,
            summary=None,
        )

    validation = validate(parsed)
    summary: Optional[str] = None
    if validation.is_valid:
        try:
            summary = summarize(parsed)
        except Exception:  # noqa: BLE001
            summary = None

    return LintResult(
        expression=expression,
        parsed=parsed,
        validation=validation,
        summary=summary,
    )


def lint_many(expressions: List[str]) -> List[LintResult]:
    """Lint multiple cron expressions and return a list of LintResults."""
    return [lint(expr) for expr in expressions]


def lint_to_text(expression: str) -> str:
    """Convenience wrapper: lint and return plain-text output."""
    return format_text(lint(expression))


def lint_to_json(expression: str) -> str:
    """Convenience wrapper: lint and return JSON string output."""
    return json.dumps(format_json(lint(expression)), indent=2)
