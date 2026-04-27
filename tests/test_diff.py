"""Tests for envforge.diff module."""

import pytest
from envforge.diff import diff_snapshots, format_diff


def _make_snapshot(env: dict) -> dict:
    return {"env": env, "metadata": {}}


SNAP_A = _make_snapshot({
    "APP_ENV": "development",
    "DB_HOST": "localhost",
    "SECRET_KEY": "abc123",
    "LOG_LEVEL": "DEBUG",
})

SNAP_B = _make_snapshot({
    "APP_ENV": "production",
    "DB_HOST": "localhost",
    "API_URL": "https://api.example.com",
    "LOG_LEVEL": "WARNING",
})


class TestDiffSnapshots:
    def test_added_keys(self):
        result = diff_snapshots(SNAP_A, SNAP_B)
        assert "API_URL" in result["added"]
        assert result["added"]["API_URL"] == "https://api.example.com"

    def test_removed_keys(self):
        result = diff_snapshots(SNAP_A, SNAP_B)
        assert "SECRET_KEY" in result["removed"]
        assert result["removed"]["SECRET_KEY"] == "abc123"

    def test_changed_keys(self):
        result = diff_snapshots(SNAP_A, SNAP_B)
        assert "APP_ENV" in result["changed"]
        assert result["changed"]["APP_ENV"]["before"] == "development"
        assert result["changed"]["APP_ENV"]["after"] == "production"
        assert "LOG_LEVEL" in result["changed"]

    def test_unchanged_keys(self):
        result = diff_snapshots(SNAP_A, SNAP_B)
        assert "DB_HOST" in result["unchanged"]
        assert result["unchanged"]["DB_HOST"] == "localhost"

    def test_identical_snapshots_produce_no_diff(self):
        result = diff_snapshots(SNAP_A, SNAP_A)
        assert result["added"] == {}
        assert result["removed"] == {}
        assert result["changed"] == {}
        assert set(result["unchanged"].keys()) == set(SNAP_A["env"].keys())

    def test_empty_snapshots(self):
        result = diff_snapshots(_make_snapshot({}), _make_snapshot({}))
        assert all(len(v) == 0 for v in result.values())


class TestFormatDiff:
    def setup_method(self):
        self.diff = diff_snapshots(SNAP_A, SNAP_B)

    def test_added_section_present(self):
        output = format_diff(self.diff)
        assert "[+] Added" in output
        assert "API_URL" in output

    def test_removed_section_present(self):
        output = format_diff(self.diff)
        assert "[-] Removed" in output
        assert "SECRET_KEY" in output

    def test_changed_section_present(self):
        output = format_diff(self.diff)
        assert "[~] Changed" in output
        assert "APP_ENV" in output
        assert "development" in output
        assert "production" in output

    def test_unchanged_hidden_by_default(self):
        output = format_diff(self.diff)
        assert "[=] Unchanged" not in output

    def test_unchanged_shown_when_requested(self):
        output = format_diff(self.diff, show_unchanged=True)
        assert "[=] Unchanged" in output
        assert "DB_HOST" in output

    def test_no_differences_message(self):
        empty_diff = diff_snapshots(SNAP_A, SNAP_A)
        output = format_diff(empty_diff)
        assert "No differences found" in output
