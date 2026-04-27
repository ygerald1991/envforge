"""Tests for envforge.audit module."""

import json
import os
import pytest
from pathlib import Path

from envforge.audit import (
    record_event,
    read_audit_log,
    format_audit_log,
    AUDIT_LOG_FILENAME,
)


@pytest.fixture()
def audit_dir(tmp_path):
    return str(tmp_path)


class TestRecordEvent:
    def test_creates_log_file(self, audit_dir):
        record_event(audit_dir, "capture", "snap1")
        assert (Path(audit_dir) / AUDIT_LOG_FILENAME).exists()

    def test_entry_has_required_fields(self, audit_dir):
        record_event(audit_dir, "capture", "snap1")
        log_path = Path(audit_dir) / AUDIT_LOG_FILENAME
        entry = json.loads(log_path.read_text().strip())
        assert entry["action"] == "capture"
        assert entry["snapshot"] == "snap1"
        assert "timestamp" in entry
        assert "user" in entry

    def test_metadata_is_stored(self, audit_dir):
        record_event(audit_dir, "restore", "snap2", metadata={"keys": 5})
        log_path = Path(audit_dir) / AUDIT_LOG_FILENAME
        entry = json.loads(log_path.read_text().strip())
        assert entry["metadata"] == {"keys": 5}

    def test_multiple_events_appended(self, audit_dir):
        record_event(audit_dir, "capture", "snap1")
        record_event(audit_dir, "diff", "snap2")
        entries = read_audit_log(audit_dir)
        assert len(entries) == 2
        assert entries[0]["action"] == "capture"
        assert entries[1]["action"] == "diff"

    def test_empty_metadata_default(self, audit_dir):
        record_event(audit_dir, "list", "snap1")
        entries = read_audit_log(audit_dir)
        assert entries[0]["metadata"] == {}


class TestReadAuditLog:
    def test_returns_empty_list_when_no_log(self, audit_dir):
        result = read_audit_log(audit_dir)
        assert result == []

    def test_returns_list_of_dicts(self, audit_dir):
        record_event(audit_dir, "export", "snap3")
        result = read_audit_log(audit_dir)
        assert isinstance(result, list)
        assert isinstance(result[0], dict)


class TestFormatAuditLog:
    def test_empty_log_message(self):
        assert format_audit_log([]) == "No audit events recorded."

    def test_format_contains_action_and_snapshot(self, audit_dir):
        record_event(audit_dir, "merge", "merged_snap")
        entries = read_audit_log(audit_dir)
        output = format_audit_log(entries)
        assert "merge" in output
        assert "merged_snap" in output

    def test_format_includes_metadata(self, audit_dir):
        record_event(audit_dir, "restore", "snap1", metadata={"strategy": "last_wins"})
        entries = read_audit_log(audit_dir)
        output = format_audit_log(entries)
        assert "strategy=last_wins" in output
