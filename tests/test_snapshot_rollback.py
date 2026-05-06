"""Tests for envforge.snapshot_rollback."""

from __future__ import annotations

import pytest

from envforge.snapshot_rollback import (
    format_rollback_log,
    get_last_rollback,
    get_rollback_log,
    record_rollback,
)


@pytest.fixture()
def rdir(tmp_path):
    return str(tmp_path / "rollbacks")


def test_record_rollback_returns_entry(rdir):
    entry = record_rollback(rdir, "snap-a", "snap-b")
    assert entry["from"] == "snap-a"
    assert entry["to"] == "snap-b"
    assert "timestamp" in entry


def test_record_rollback_persists_to_file(rdir):
    record_rollback(rdir, "snap-a", "snap-b", reason="hotfix")
    log = get_rollback_log(rdir)
    assert len(log) == 1
    assert log[0]["reason"] == "hotfix"


def test_multiple_rollbacks_are_appended(rdir):
    record_rollback(rdir, "snap-a", "snap-b")
    record_rollback(rdir, "snap-b", "snap-c")
    log = get_rollback_log(rdir)
    assert len(log) == 2


def test_get_rollback_log_empty_store(rdir):
    assert get_rollback_log(rdir) == []


def test_get_rollback_log_filtered_by_snapshot(rdir):
    record_rollback(rdir, "snap-a", "snap-b")
    record_rollback(rdir, "snap-c", "snap-d")
    filtered = get_rollback_log(rdir, snapshot="snap-a")
    assert len(filtered) == 1
    assert filtered[0]["from"] == "snap-a"


def test_get_rollback_log_filter_matches_to_field(rdir):
    record_rollback(rdir, "snap-x", "snap-y")
    filtered = get_rollback_log(rdir, snapshot="snap-y")
    assert len(filtered) == 1


def test_get_last_rollback_returns_most_recent(rdir):
    record_rollback(rdir, "snap-1", "snap-2")
    record_rollback(rdir, "snap-2", "snap-3")
    last = get_last_rollback(rdir)
    assert last["from"] == "snap-2"
    assert last["to"] == "snap-3"


def test_get_last_rollback_empty_returns_none(rdir):
    assert get_last_rollback(rdir) is None


def test_format_rollback_log_empty():
    result = format_rollback_log([])
    assert "No rollback" in result


def test_format_rollback_log_includes_arrow(rdir):
    entry = record_rollback(rdir, "snap-a", "snap-b", reason="emergency")
    result = format_rollback_log([entry])
    assert "snap-a -> snap-b" in result
    assert "emergency" in result


def test_format_rollback_log_no_reason_omits_parens(rdir):
    entry = record_rollback(rdir, "snap-a", "snap-b")
    result = format_rollback_log([entry])
    assert "()" not in result
