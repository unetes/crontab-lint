"""Format ConflictReport as text or JSON."""

import json
from .conflict_detector import ConflictReport


def format_conflict_text(report: ConflictReport) -> str:
    lines = []
    lines.append(f"Checked {len(report.expressions)} expression(s).")
    if not report.has_conflicts:
        lines.append("No scheduling conflicts detected.")
        return "\n".join(lines)

    lines.append(
        f"Found {len(report.conflicts)} conflict(s) "
        f"({report.total_overlaps} total overlapping run(s)):"
    )
    for i, conflict in enumerate(report.conflicts, 1):
        lines.append(f"\nConflict #{i}:")
        lines.append(f"  Expression A : {conflict.expr_a}")
        lines.append(f"  Expression B : {conflict.expr_b}")
        lines.append(f"  Overlaps     : {conflict.overlap_count}")
        preview = conflict.overlapping_times[:5]
        if len(conflict.overlapping_times) > 5:
            preview_str = ", ".join(preview) + f" ... (+{conflict.overlap_count - 5} more)"
        else:
            preview_str = ", ".join(preview)
        lines.append(f"  Sample times : {preview_str}")
    return "\n".join(lines)


def format_conflict_json(report: ConflictReport) -> str:
    data = {
        "expressions": report.expressions,
        "has_conflicts": report.has_conflicts,
        "total_overlaps": report.total_overlaps,
        "conflicts": [
            {
                "expr_a": c.expr_a,
                "expr_b": c.expr_b,
                "overlap_count": c.overlap_count,
                "overlapping_times": c.overlapping_times,
            }
            for c in report.conflicts
        ],
    }
    return json.dumps(data, indent=2)
