"""Normalize and canonicalize crontab expressions for comparison and display."""

from typing import Dict

ALIAS_MAP: Dict[str, str] = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
}

MONTH_NAMES: Dict[str, str] = {
    "jan": "1", "feb": "2", "mar": "3", "apr": "4",
    "may": "5", "jun": "6", "jul": "7", "aug": "8",
    "sep": "9", "oct": "10", "nov": "11", "dec": "12",
}

WEEKDAY_NAMES: Dict[str, str] = {
    "sun": "0", "mon": "1", "tue": "2", "wed": "3",
    "thu": "4", "fri": "5", "sat": "6",
}


def _replace_names(value: str, mapping: Dict[str, str]) -> str:
    """Replace named aliases (e.g. 'jan', 'mon') with numeric equivalents."""
    result = value.lower()
    for name, num in mapping.items():
        result = result.replace(name, num)
    return result


def _normalize_field(field: str, mapping: Dict[str, str]) -> str:
    """Normalize a single cron field by replacing names and sorting list values."""
    field = _replace_names(field, mapping)
    if "," in field:
        parts = field.split(",")
        try:
            parts_sorted = sorted(parts, key=lambda x: int(x.split("/")[0].split("-")[0]))
            return ",".join(parts_sorted)
        except ValueError:
            return ",".join(parts)
    return field


def normalize(expression: str) -> str:
    """Return a canonical form of the crontab expression.

    Expands @aliases, lowercases name tokens, and sorts comma-separated lists.
    Returns the normalized 5-field schedule string (without any command part).
    """
    expr = expression.strip()

    lower = expr.lower()
    if lower in ALIAS_MAP:
        return ALIAS_MAP[lower]

    parts = expr.split()
    if len(parts) < 5:
        return expr  # Return as-is if malformed; validator will catch it

    minute, hour, dom, month, dow = parts[:5]

    minute = _normalize_field(minute, {})
    hour = _normalize_field(hour, {})
    dom = _normalize_field(dom, {})
    month = _normalize_field(month, MONTH_NAMES)
    dow = _normalize_field(dow, WEEKDAY_NAMES)

    return f"{minute} {hour} {dom} {month} {dow}"


def are_equivalent(expr_a: str, expr_b: str) -> bool:
    """Return True if two crontab expressions are semantically equivalent.

    Equivalence is determined by comparing the normalized forms of both
    expressions, so differences in whitespace, name aliases (e.g. 'jan' vs
    '1'), and comma-list ordering are ignored.

    Examples::

        are_equivalent("@daily", "0 0 * * *")       # True
        are_equivalent("0 0 1 jan *", "0 0 1 1 *")  # True
        are_equivalent("0 0 * * mon", "0 0 * * 2")  # False
    """
    return normalize(expr_a) == normalize(expr_b)
