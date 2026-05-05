"""Validation logic for parsed crontab fields."""

from dataclasses import dataclass, field
from typing import List

from .parser import CronField, ParsedCron, MONTH_ALIASES, WEEKDAY_ALIASES


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def _resolve_alias(value: str, field_name: str) -> str:
    if field_name == "month":
        return str(MONTH_ALIASES.get(value.lower(), value))
    if field_name == "day_of_week":
        return str(WEEKDAY_ALIASES.get(value.lower(), value))
    return value


def _validate_value(value: str, cron_field: CronField) -> List[str]:
    errors = []
    resolved = _resolve_alias(value, cron_field.name)
    try:
        num = int(resolved)
        if not (cron_field.min_val <= num <= cron_field.max_val):
            errors.append(
                f"Field '{cron_field.name}': value {num} out of range "
                f"[{cron_field.min_val}-{cron_field.max_val}]"
            )
    except ValueError:
        errors.append(
            f"Field '{cron_field.name}': '{value}' is not a valid value"
        )
    return errors


def _validate_field(cron_field: CronField) -> List[str]:
    raw = cron_field.raw
    errors = []

    if raw == "*":
        return []

    for part in raw.split(","):
        if "/" in part:
            base, step = part.split("/", 1)
            try:
                step_val = int(step)
                if step_val <= 0:
                    errors.append(
                        f"Field '{cron_field.name}': step value must be positive, got {step_val}"
                    )
            except ValueError:
                errors.append(
                    f"Field '{cron_field.name}': invalid step '{step}'"
                )
            if base != "*":
                if "-" in base:
                    lo, hi = base.split("-", 1)
                    errors.extend(_validate_value(lo, cron_field))
                    errors.extend(_validate_value(hi, cron_field))
                else:
                    errors.extend(_validate_value(base, cron_field))
        elif "-" in part:
            lo, hi = part.split("-", 1)
            errors.extend(_validate_value(lo, cron_field))
            errors.extend(_validate_value(hi, cron_field))
        else:
            errors.extend(_validate_value(part, cron_field))

    return errors


def validate(parsed: ParsedCron) -> ValidationResult:
    """Validate all fields of a parsed crontab expression."""
    all_errors = []
    for cron_field in parsed.fields:
        all_errors.extend(_validate_field(cron_field))

    warnings = []
    dom = parsed.fields[2].raw
    dow = parsed.fields[4].raw
    if dom != "*" and dow != "*":
        warnings.append(
            "Both day-of-month and day-of-week are set; "
            "the job runs when EITHER condition is true."
        )

    return ValidationResult(valid=len(all_errors) == 0, errors=all_errors, warnings=warnings)
