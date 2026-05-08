"""Tag and annotate crontab expressions with semantic labels."""

from dataclasses import dataclass, field
from typing import List

from crontab_lint.parser import ParsedCron, parse
from crontab_lint.validator import validate


@dataclass
class AnnotatedCron:
    expression: str
    tags: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    is_valid: bool = True


def _tag_frequency(parsed: ParsedCron) -> List[str]:
    tags = []
    m, h, dom, mon, dow = (
        parsed.minute, parsed.hour, parsed.dom, parsed.month, parsed.dow
    )
    if m == "*" and h == "*" and dom == "*" and mon == "*" and dow == "*":
        tags.append("every-minute")
    elif m != "*" and h == "*" and dom == "*" and mon == "*" and dow == "*":
        tags.append("hourly")
    elif m != "*" and h != "*" and dom == "*" and mon == "*" and dow == "*":
        tags.append("daily")
    elif m != "*" and h != "*" and dom == "*" and mon == "*" and dow != "*":
        tags.append("weekly")
    elif m != "*" and h != "*" and dom != "*" and mon == "*" and dow == "*":
        tags.append("monthly")
    elif m != "*" and h != "*" and dom != "*" and mon != "*" and dow == "*":
        tags.append("yearly")
    else:
        tags.append("custom")
    return tags


def _tag_special(parsed: ParsedCron) -> List[str]:
    tags = []
    if "/" in parsed.minute:
        tags.append("step-minute")
    if "/" in parsed.hour:
        tags.append("step-hour")
    if "," in parsed.minute or "," in parsed.hour:
        tags.append("multi-value")
    if parsed.dom != "*" and parsed.dow != "*":
        tags.append("dom-and-dow")
    return tags


def _note_risks(parsed: ParsedCron) -> List[str]:
    notes = []
    if parsed.dom != "*" and parsed.dow != "*":
        notes.append("Both DOM and DOW are set; cron uses OR logic between them.")
    if parsed.minute == "*":
        notes.append("Runs every minute — ensure this is intentional.")
    return notes


def annotate(expression: str) -> AnnotatedCron:
    """Parse, validate, and annotate a crontab expression with semantic tags."""
    try:
        parsed = parse(expression)
    except Exception as exc:
        return AnnotatedCron(expression=expression, tags=["parse-error"],
                             notes=[str(exc)], is_valid=False)

    result = validate(parsed)
    if not result.is_valid:
        return AnnotatedCron(expression=expression, tags=["invalid"],
                             notes=result.errors, is_valid=False)

    tags = _tag_frequency(parsed) + _tag_special(parsed)
    notes = _note_risks(parsed)
    return AnnotatedCron(expression=expression, tags=tags, notes=notes, is_valid=True)
