"""Tests for tag_annotator and annotation_formatter."""

import json
import pytest

from crontab_lint.tag_annotator import annotate, AnnotatedCron
from crontab_lint.annotation_formatter import (
    format_annotation_text,
    format_annotation_json,
    format_many_text,
    format_many_json,
)


class TestAnnotate:
    def test_every_minute_tagged(self):
        ann = annotate("* * * * *")
        assert "every-minute" in ann.tags
        assert ann.is_valid

    def test_daily_tagged(self):
        ann = annotate("0 9 * * *")
        assert "daily" in ann.tags
        assert ann.is_valid

    def test_weekly_tagged(self):
        ann = annotate("0 8 * * 1")
        assert "weekly" in ann.tags

    def test_monthly_tagged(self):
        ann = annotate("0 6 1 * *")
        assert "monthly" in ann.tags

    def test_yearly_tagged(self):
        ann = annotate("0 0 1 1 *")
        assert "yearly" in ann.tags

    def test_step_minute_tagged(self):
        ann = annotate("*/5 * * * *")
        assert "step-minute" in ann.tags

    def test_step_hour_tagged(self):
        ann = annotate("0 */2 * * *")
        assert "step-hour" in ann.tags

    def test_multi_value_tagged(self):
        ann = annotate("0,30 * * * *")
        assert "multi-value" in ann.tags

    def test_dom_and_dow_tagged_and_noted(self):
        ann = annotate("0 9 1 * 1")
        assert "dom-and-dow" in ann.tags
        assert any("OR" in n for n in ann.notes)

    def test_every_minute_note(self):
        ann = annotate("* * * * *")
        assert any("every minute" in n.lower() for n in ann.notes)

    def test_invalid_expression_returns_invalid(self):
        ann = annotate("99 * * * *")
        assert not ann.is_valid
        assert "invalid" in ann.tags

    def test_parse_error_returns_parse_error_tag(self):
        ann = annotate("not a cron")
        assert not ann.is_valid
        assert "parse-error" in ann.tags


class TestAnnotationFormatter:
    def test_text_contains_expression(self):
        ann = annotate("0 9 * * *")
        text = format_annotation_text(ann)
        assert "0 9 * * *" in text

    def test_text_contains_status_valid(self):
        ann = annotate("0 9 * * *")
        text = format_annotation_text(ann)
        assert "valid" in text

    def test_text_contains_tags(self):
        ann = annotate("0 9 * * *")
        text = format_annotation_text(ann)
        assert "daily" in text

    def test_json_is_parseable(self):
        ann = annotate("0 9 * * *")
        data = json.loads(format_annotation_json(ann))
        assert data["expression"] == "0 9 * * *"
        assert data["is_valid"] is True
        assert isinstance(data["tags"], list)

    def test_format_many_text_separates_blocks(self):
        anns = [annotate("0 9 * * *"), annotate("*/5 * * * *")]
        text = format_many_text(anns)
        assert "0 9 * * *" in text
        assert "*/5 * * * *" in text

    def test_format_many_json_returns_list(self):
        anns = [annotate("0 9 * * *"), annotate("0 8 * * 1")]
        data = json.loads(format_many_json(anns))
        assert len(data) == 2
        assert data[0]["expression"] == "0 9 * * *"
