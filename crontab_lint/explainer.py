"""Human-readable next-run time explainer for cron expressions."""

from datetime import datetime, timedelta
from typing import Optional

from .parser import ParsedCron, normalize_expression


def _next_minute(now: datetime, parsed: ParsedCron) -> Optional[datetime]:
    """Find the next matching datetime within the next year."""
    # Advance by one minute to find *next* run, not current
    candidate = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
    limit = now + timedelta(days=366)

    def matches(dt: datetime) -> bool:
        fields = [
            (parsed.minute, dt.minute),
            (parsed.hour, dt.hour),
            (parsed.day_of_month, dt.day),
            (parsed.month, dt.month),
            (parsed.day_of_week, dt.weekday() + 1),  # Mon=1 .. Sun=7; cron Sun=0 or 7
        ]
        for field_expr, value in fields:
            if not _field_matches(field_expr, value, dt):
                return False
        return True

    while candidate <= limit:
        if matches(candidate):
            return candidate
        candidate += timedelta(minutes=1)

    return None


def _field_matches(field_expr: str, value: int, dt: datetime) -> bool:
    """Check whether a single cron field expression matches the given value."""
    if field_expr == "*":
        return True

    for part in field_expr.split(","):
        if "/" in part:
            range_part, step_str = part.split("/", 1)
            step = int(step_str)
            if range_part == "*":
                start = 0
            elif "-" in range_part:
                start = int(range_part.split("-")[0])
            else:
                start = int(range_part)
            if (value - start) % step == 0 and value >= start:
                return True
        elif "-" in part:
            lo, hi = part.split("-", 1)
            if int(lo) <= value <= int(hi):
                return True
        else:
            # Handle Sunday as 0 or 7
            candidate_val = int(part)
            if candidate_val == 7 and value == 0:
                return True
            if candidate_val == value:
                return True
    return False


def explain_next_run(
    expression: str, now: Optional[datetime] = None
) -> dict:
    """Return a dict with next_run ISO string and a human-readable sentence."""
    if now is None:
        now = datetime.now()

    try:
        normalized = normalize_expression(expression)
        from .parser import parse  # avoid circular at module level
        parsed = parse(normalized)
    except Exception as exc:
        return {"next_run": None, "description": f"Could not parse expression: {exc}"}

    next_run = _next_minute(now, parsed)
    if next_run is None:
        return {"next_run": None, "description": "No matching run time found within the next year."}

    delta = next_run - now.replace(second=0, microsecond=0)
    total_minutes = int(delta.total_seconds() // 60)
    if total_minutes < 60:
        human_delta = f"in {total_minutes} minute(s)"
    elif total_minutes < 1440:
        human_delta = f"in {total_minutes // 60} hour(s) and {total_minutes % 60} minute(s)"
    else:
        days = total_minutes // 1440
        human_delta = f"in {days} day(s)"

    iso = next_run.strftime("%Y-%m-%dT%H:%M:00")
    description = f"Next run at {next_run.strftime('%Y-%m-%d %H:%M')} ({human_delta})."
    return {"next_run": iso, "description": description}
