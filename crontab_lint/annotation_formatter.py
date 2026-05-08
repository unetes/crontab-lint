"""Format AnnotatedCron results as text or JSON."""

import json
from typing import List

from crontab_lint.tag_annotator import AnnotatedCron


def format_annotation_text(ann: AnnotatedCron) -> str:
    lines = [f"Expression : {ann.expression}"]
    status = "valid" if ann.is_valid else "invalid"
    lines.append(f"Status     : {status}")
    lines.append(f"Tags       : {', '.join(ann.tags) if ann.tags else 'none'}")
    if ann.notes:
        lines.append("Notes      :")
        for note in ann.notes:
            lines.append(f"  - {note}")
    return "\n".join(lines)


def format_annotation_json(ann: AnnotatedCron) -> str:
    return json.dumps({
        "expression": ann.expression,
        "is_valid": ann.is_valid,
        "tags": ann.tags,
        "notes": ann.notes,
    }, indent=2)


def format_many_text(annotations: List[AnnotatedCron]) -> str:
    blocks = [format_annotation_text(a) for a in annotations]
    return "\n\n".join(blocks)


def format_many_json(annotations: List[AnnotatedCron]) -> str:
    return json.dumps(
        [
            {
                "expression": a.expression,
                "is_valid": a.is_valid,
                "tags": a.tags,
                "notes": a.notes,
            }
            for a in annotations
        ],
        indent=2,
    )
