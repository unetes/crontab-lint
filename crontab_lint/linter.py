"""High-level lint API combining parsing, validation, summarization, and normalization."""

from typing import List

from crontab_lint.parser import parse, ParsedCron
from crontab_lint.validator import validate, ValidationResult
from crontab_lint.summarizer import summarize
from crontab_lint.formatter import LintResult, format_text, format_json
from crontab_lint.normalizer import normalize


def lint(expression: str) -> LintResult:
    """Lint a single crontab expression and return a structured result."""
    try:
        parsed: ParsedCron = parse(expression)
    except Exception as exc:  # noqa: BLE001
        return LintResult(
            expression=expression,
            is_valid=False,
            errors=[f"Parse error: {exc}"],
            summary=None,
            normalized=None,
        )

    result: ValidationResult = validate(parsed)
    summary = summarize(parsed) if result.is_valid else None

    try:
        normalized = normalize(expression) if result.is_valid else None
    except Exception:  # noqa: BLE001
        normalized = None

    return LintResult(
        expression=expression,
        is_valid=result.is_valid,
        errors=result.errors,
        summary=summary,
        normalized=normalized,
    )


def lint_many(expressions: List[str]) -> List[LintResult]:
    """Lint multiple crontab expressions and return a list of results."""
    return [lint(expr) for expr in expressions]


def lint_to_text(expression: str) -> str:
    """Lint an expression and return a human-readable text report."""
    return format_text(lint(expression))


def lint_to_json(expression: str) -> str:
    """Lint an expression and return a JSON-encoded report."""
    return format_json(lint(expression))
