"""Detect scheduling conflicts and overlaps between multiple cron expressions."""

from dataclasses import dataclass, field
from typing import List, Tuple
from .normalizer import normalize
from .schedule_generator import next_n_runs


@dataclass
class Conflict:
    expr_a: str
    expr_b: str
    overlapping_times: List[str]
    overlap_count: int


@dataclass
class ConflictReport:
    expressions: List[str]
    conflicts: List[Conflict]
    has_conflicts: bool
    total_overlaps: int


def _runs_set(expr: str, n: int, from_dt=None) -> set:
    """Return a set of ISO-formatted run times for the expression."""
    try:
        runs = next_n_runs(expr, n, from_dt=from_dt)
        return {r.isoformat(timespec="minutes") for r in runs}
    except Exception:
        return set()


def detect_conflicts(
    expressions: List[str], window: int = 100, from_dt=None
) -> ConflictReport:
    """Detect overlapping run times among a list of cron expressions.

    Args:
        expressions: list of cron expression strings.
        window: number of future runs to sample per expression.
        from_dt: optional datetime to start sampling from.

    Returns:
        ConflictReport describing any detected overlaps.
    """
    normalized = []
    for expr in expressions:
        try:
            normalized.append(normalize(expr))
        except Exception:
            normalized.append(expr)

    run_sets = [
        _runs_set(expr, window, from_dt) for expr in normalized
    ]

    conflicts: List[Conflict] = []
    n = len(expressions)
    for i in range(n):
        for j in range(i + 1, n):
            overlap = run_sets[i] & run_sets[j]
            if overlap:
                conflicts.append(
                    Conflict(
                        expr_a=expressions[i],
                        expr_b=expressions[j],
                        overlapping_times=sorted(overlap),
                        overlap_count=len(overlap),
                    )
                )

    total = sum(c.overlap_count for c in conflicts)
    return ConflictReport(
        expressions=expressions,
        conflicts=conflicts,
        has_conflicts=bool(conflicts),
        total_overlaps=total,
    )
