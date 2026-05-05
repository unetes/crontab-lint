"""Core crontab expression parser."""

from dataclasses import dataclass
from typing import Optional


FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]

FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 7),
}

MONTH_ALIASES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

WEEKDAY_ALIASES = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3,
    "thu": 4, "fri": 5, "sat": 6,
}

SPECIAL_STRINGS = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
}


@dataclass
class CronField:
    name: str
    raw: str
    min_val: int
    max_val: int


@dataclass
class ParsedCron:
    raw: str
    fields: list
    command: Optional[str] = None


def normalize_expression(expression: str) -> str:
    """Expand special strings to standard 5-field expressions."""
    expr = expression.strip().lower()
    if expr in SPECIAL_STRINGS:
        return SPECIAL_STRINGS[expr]
    return expression.strip()


def parse(expression: str) -> ParsedCron:
    """Parse a crontab expression into structured fields."""
    normalized = normalize_expression(expression)
    parts = normalized.split()

    if len(parts) < 5:
        raise ValueError(
            f"Invalid crontab expression: expected at least 5 fields, got {len(parts)}"
        )

    field_parts = parts[:5]
    command = " ".join(parts[5:]) if len(parts) > 5 else None

    fields = []
    for name, raw in zip(FIELD_NAMES, field_parts):
        lo, hi = FIELD_RANGES[name]
        fields.append(CronField(name=name, raw=raw, min_val=lo, max_val=hi))

    return ParsedCron(raw=expression, fields=fields, command=command)
