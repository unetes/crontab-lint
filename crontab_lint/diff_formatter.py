"""Format DiffResult as human-readable text or JSON."""

import json
from .differ import DiffResult


def format_diff_text(result: DiffResult) -> str:
    """Render a DiffResult as a human-readable text report."""
    lines = []
    lines.append(f"Left  : {result.left}")
    lines.append(f"Right : {result.right}")
    lines.append("")

    if result.identical:
        lines.append("✔ Expressions are identical.")
        return "\n".join(lines)

    def validity_line(label: str, valid: bool, errors: list, summary: str) -> None:
        status = "✔ valid" if valid else "✘ invalid"
        lines.append(f"{label}: {status}")
        if not valid:
            for err in errors:
                lines.append(f"  Error: {err}")
        elif summary:
            lines.append(f"  Summary: {summary}")

    validity_line("Left ", result.left_valid, result.left_errors, result.left_summary or "")
    validity_line("Right", result.right_valid, result.right_errors, result.right_summary or "")

    if result.field_diffs:
        lines.append("")
        lines.append("Changed fields:")
        for fd in result.field_diffs:
            lines.append(f"  {fd.field_name}:")
            lines.append(f"    - {fd.left}")
            lines.append(f"    + {fd.right}")
    else:
        if result.left_valid and result.right_valid:
            lines.append("")
            lines.append("No field-level differences detected (expressions may be semantically equivalent).")

    return "\n".join(lines)


def format_diff_json(result: DiffResult) -> str:
    """Render a DiffResult as a JSON string."""
    data = {
        "left": result.left,
        "right": result.right,
        "identical": result.identical,
        "left_valid": result.left_valid,
        "right_valid": result.right_valid,
        "left_errors": result.left_errors,
        "right_errors": result.right_errors,
        "left_summary": result.left_summary,
        "right_summary": result.right_summary,
        "field_diffs": [
            {
                "field": fd.field_name,
                "left": fd.left,
                "right": fd.right,
            }
            for fd in result.field_diffs
        ],
    }
    return json.dumps(data, indent=2)
