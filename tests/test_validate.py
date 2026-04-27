"""Tests for envforge.validate."""

import pytest

from envforge.validate import (
    format_validation_report,
    validate_forbidden_keys,
    validate_required_keys,
    validate_snapshot,
    validate_value_pattern,
)


def _make_snapshot(vars_: dict) -> dict:
    return {"name": "test", "timestamp": "2024-01-01T00:00:00", "vars": vars_}


class TestValidateRequiredKeys:
    def test_all_present(self):
        snap = _make_snapshot({"A": "1", "B": "2"})
        assert validate_required_keys(snap, ["A", "B"]) == []

    def test_some_missing(self):
        snap = _make_snapshot({"A": "1"})
        missing = validate_required_keys(snap, ["A", "B", "C"])
        assert set(missing) == {"B", "C"}

    def test_empty_required_list(self):
        snap = _make_snapshot({})
        assert validate_required_keys(snap, []) == []


class TestValidateForbiddenKeys:
    def test_none_present(self):
        snap = _make_snapshot({"A": "1"})
        assert validate_forbidden_keys(snap, ["SECRET", "TOKEN"]) == []

    def test_forbidden_key_present(self):
        snap = _make_snapshot({"SECRET": "abc", "A": "1"})
        result = validate_forbidden_keys(snap, ["SECRET"])
        assert result == ["SECRET"]


class TestValidateValuePattern:
    def test_matching_pattern(self):
        snap = _make_snapshot({"PORT": "8080"})
        assert validate_value_pattern(snap, "PORT", r"\d+") is True

    def test_non_matching_pattern(self):
        snap = _make_snapshot({"PORT": "abc"})
        assert validate_value_pattern(snap, "PORT", r"\d+") is False

    def test_missing_key_returns_false(self):
        snap = _make_snapshot({})
        assert validate_value_pattern(snap, "PORT", r"\d+") is False


class TestValidateSnapshot:
    def test_all_pass(self):
        snap = _make_snapshot({"A": "hello", "B": "123"})
        result = validate_snapshot(
            snap, required=["A"], forbidden=["SECRET"], patterns={"B": r"\d+"}
        )
        assert result["valid"] is True
        assert result["missing_required"] == []
        assert result["present_forbidden"] == []
        assert result["pattern_failures"] == {}

    def test_missing_required_fails(self):
        snap = _make_snapshot({"A": "1"})
        result = validate_snapshot(snap, required=["A", "MISSING"])
        assert result["valid"] is False
        assert "MISSING" in result["missing_required"]

    def test_forbidden_present_fails(self):
        snap = _make_snapshot({"SECRET": "x"})
        result = validate_snapshot(snap, forbidden=["SECRET"])
        assert result["valid"] is False
        assert "SECRET" in result["present_forbidden"]

    def test_pattern_failure(self):
        snap = _make_snapshot({"PORT": "not-a-number"})
        result = validate_snapshot(snap, patterns={"PORT": r"\d+"})
        assert result["valid"] is False
        assert "PORT" in result["pattern_failures"]

    def test_no_rules_is_valid(self):
        snap = _make_snapshot({"X": "1"})
        result = validate_snapshot(snap)
        assert result["valid"] is True


class TestFormatValidationReport:
    def test_passing_report(self):
        result = {
            "valid": True,
            "missing_required": [],
            "present_forbidden": [],
            "pattern_failures": {},
        }
        assert "passed" in format_validation_report(result)

    def test_failing_report_contains_details(self):
        result = {
            "valid": False,
            "missing_required": ["DB_URL"],
            "present_forbidden": ["SECRET"],
            "pattern_failures": {"PORT": r"\d+"},
        }
        report = format_validation_report(result)
        assert "DB_URL" in report
        assert "SECRET" in report
        assert "PORT" in report
