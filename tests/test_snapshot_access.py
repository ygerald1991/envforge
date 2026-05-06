"""Tests for envforge.snapshot_access."""

import json
import pytest
from pathlib import Path

from envforge.snapshot_access import (
    record_access,
    get_access_log,
    get_last_accessed,
    format_access_log,
)


@pytest.fixture
def adir(tmp_path):
    return str(tmp_path)


def test_record_access_creates_log_file(adir):
    record_access(adir, "snap1")
    log_path = Path(adir) / ".envforge_access_log.json"
    assert log_path.exists()


def test_record_access_entry_has_required_fields(adir):
    entry = record_access(adir, "snap1", action="read", actor="alice")
    assert entry["snapshot"] == "snap1"
    assert entry["action"] == "read"
    assert "timestamp" in entry
    assert entry["actor"] == "alice"


def test_multiple_records_are_appended(adir):
    record_access(adir, "snap1", actor="alice")
    record_access(adir, "snap2", actor="bob")
    log = get_access_log(adir)
    assert len(log) == 2
    assert log[0]["snapshot"] == "snap1"
    assert log[1]["snapshot"] == "snap2"


def test_get_access_log_filtered_by_snapshot(adir):
    record_access(adir, "snap1", actor="alice")
    record_access(adir, "snap2", actor="bob")
    record_access(adir, "snap1", actor="carol")
    entries = get_access_log(adir, snapshot_name="snap1")
    assert len(entries) == 2
    assert all(e["snapshot"] == "snap1" for e in entries)


def test_get_access_log_empty_store_returns_empty(adir):
    assert get_access_log(adir) == []


def test_get_last_accessed_returns_most_recent(adir):
    record_access(adir, "snap1", actor="alice")
    record_access(adir, "snap1", actor="bob")
    last = get_last_accessed(adir, "snap1")
    assert last is not None
    assert last["actor"] == "bob"


def test_get_last_accessed_missing_returns_none(adir):
    assert get_last_accessed(adir, "nonexistent") is None


def test_default_action_is_read(adir):
    entry = record_access(adir, "snap1", actor="alice")
    assert entry["action"] == "read"


def test_custom_action_is_stored(adir):
    entry = record_access(adir, "snap1", action="export", actor="alice")
    assert entry["action"] == "export"


def test_format_access_log_empty_returns_message(adir):
    result = format_access_log([])
    assert "No access records" in result


def test_format_access_log_contains_snapshot_name(adir):
    entry = record_access(adir, "my_snap", actor="dave")
    result = format_access_log([entry])
    assert "my_snap" in result
    assert "dave" in result


def test_log_persists_across_calls(adir):
    record_access(adir, "snap1", actor="alice")
    log_path = Path(adir) / ".envforge_access_log.json"
    with open(log_path) as f:
        data = json.load(f)
    assert len(data) == 1
    assert data[0]["snapshot"] == "snap1"
