"""Human-readable summary generator for crontab expressions."""

from .parser import ParsedCron, MONTH_ALIASES, WEEKDAY_ALIASES

_MONTH_NAMES = {v: k.capitalize() for k, v in MONTH_ALIASES.items()}
_DOW_NAMES = {v: k.capitalize() for k, v in WEEKDAY_ALIASES.items()}
_DOW_NAMES[7] = "Sun"


def _describe_field(raw: str, field_name: str, unit: str) -> str:
    if raw == "*":
        return f"every {unit}"

    parts = raw.split(",")
    descriptions = []

    for part in parts:
        if "/" in part:
            base, step = part.split("/", 1)
            base_desc = "every" if base == "*" else f"starting at {base}"
            descriptions.append(f"every {step} {unit}s ({base_desc})")
        elif "-" in part:
            lo, hi = part.split("-", 1)
            descriptions.append(f"{unit}s {lo} through {hi}")
        else:
            if field_name == "month":
                try:
                    descriptions.append(_MONTH_NAMES.get(int(part), part))
                except ValueError:
                    descriptions.append(part)
            elif field_name == "day_of_week":
                try:
                    descriptions.append(_DOW_NAMES.get(int(part) % 7, part))
                except ValueError:
                    descriptions.append(part)
            else:
                descriptions.append(part)

    return ", ".join(descriptions)


def summarize(parsed: ParsedCron) -> str:
    """Return a human-readable description of the crontab schedule."""
    minute, hour, dom, month, dow = parsed.fields

    minute_desc = _describe_field(minute.raw, "minute", "minute")
    hour_desc = _describe_field(hour.raw, "hour", "hour")
    dom_desc = _describe_field(dom.raw, "day_of_month", "day")
    month_desc = _describe_field(month.raw, "month", "month")
    dow_desc = _describe_field(dow.raw, "day_of_week", "weekday")

    summary = f"At {minute_desc} past {hour_desc}"

    if dom.raw != "*" or dow.raw != "*":
        if dom.raw != "*" and dow.raw != "*":
            summary += f", on {dom_desc} of the month or on {dow_desc}"
        elif dom.raw != "*":
            summary += f", on {dom_desc} of the month"
        else:
            summary += f", on {dow_desc}"

    if month.raw != "*":
        summary += f", in {month_desc}"

    if parsed.command:
        summary += f" — runs: {parsed.command}"

    return summary
