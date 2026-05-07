"""Generate the next N scheduled run times for a cron expression."""

from datetime import datetime, timedelta
from typing import List, Optional

from .explainer import matches, _next_minute
from .normalizer import normalize
from .validator import validate


MAX_SEARCH_MINUTES = 527_040  # 366 days * 24h * 60min


def next_n_runs(
    expression: str,
    n: int = 5,
    start: Optional[datetime] = None,
) -> List[datetime]:
    """Return the next *n* datetimes that match *expression*.

    Parameters
    ----------
    expression:
        A cron expression (standard 5-field or @special).
    n:
        How many future run times to return.
    start:
        The reference point in time (defaults to *now*, seconds truncated).

    Raises
    ------
    ValueError
        If the expression is invalid or no run times are found within one year.
    """
    if n < 1:
        raise ValueError("n must be at least 1")

    normalized = normalize(expression)
    result = validate(normalized)
    if not result.valid:
        raise ValueError(
            f"Invalid cron expression: {', '.join(result.errors)}"
        )

    if start is None:
        start = datetime.now().replace(second=0, microsecond=0)

    current = _next_minute(start)
    runs: List[datetime] = []

    for _ in range(MAX_SEARCH_MINUTES):
        if len(runs) == n:
            break
        if matches(normalized, current):
            runs.append(current)
        current = _next_minute(current)
    else:
        if len(runs) < n:
            raise ValueError(
                f"Could only find {len(runs)} run(s) within the search window."
            )

    return runs


def format_runs(runs: List[datetime], fmt: str = "%Y-%m-%d %H:%M") -> List[str]:
    """Format a list of datetimes using *fmt*."""
    return [dt.strftime(fmt) for dt in runs]
