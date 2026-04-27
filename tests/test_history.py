"""Tests for envforge.history module."""

from __future__ import annotations

import json
import os
import time
import pytest

from envforge.history import get_snapshot_history, prune_history, format_history


@pytest.fixture()
def snapshot_dir(tmp_path):
    d = tmp_path / "snapshots"
    d.mkdir()
    return str(d)


def _write_snapshot(directory: str, name: str, variables: dict, delay: float = 0.0):
    path = os.path.join(directory, f"{name}.json")
    with open(path, "w") as fh:
        json.dump(variables, fh)
    if delay:
        time.sleep(delay)
    return path


class TestGetSnapshotHistory:
    def test_returns_entries_for_all_snapshots(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "snap1", {"A": "1"})
        _write_snapshot(snapshot_dir, "snap2", {"B": "2", "C": "3"})
        history = get_snapshot_history(snapshot_dir)
        assert len(history) == 2

    def test_entry_has_required_fields(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "snap1", {"X": "y"})
        entry = get_snapshot_history(snapshot_dir)[0]
        assert "name" in entry
        assert "timestamp" in entry
        assert "var_count" in entry
        assert "path" in entry

    def test_var_count_matches_snapshot(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "snap1", {"A": "1", "B": "2", "C": "3"})
        entry = get_snapshot_history(snapshot_dir)[0]
        assert entry["var_count"] == 3

    def test_prefix_filter(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "prod_snap", {"ENV": "prod"})
        _write_snapshot(snapshot_dir, "dev_snap", {"ENV": "dev"})
        history = get_snapshot_history(snapshot_dir, prefix="prod")
        assert len(history) == 1
        assert history[0]["name"] == "prod_snap"

    def test_empty_dir_returns_empty_list(self, snapshot_dir):
        assert get_snapshot_history(snapshot_dir) == []


class TestPruneHistory:
    def test_keeps_n_most_recent(self, snapshot_dir):
        for i in range(5):
            _write_snapshot(snapshot_dir, f"snap{i}", {"I": str(i)})
        deleted = prune_history(snapshot_dir, keep=3)
        remaining = get_snapshot_history(snapshot_dir)
        assert len(remaining) == 3
        assert len(deleted) == 2

    def test_dry_run_does_not_delete(self, snapshot_dir):
        for i in range(4):
            _write_snapshot(snapshot_dir, f"snap{i}", {})
        deleted = prune_history(snapshot_dir, keep=2, dry_run=True)
        assert len(deleted) == 2
        # files still exist
        assert len(get_snapshot_history(snapshot_dir)) == 4

    def test_keep_greater_than_total_deletes_nothing(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "only", {"K": "v"})
        deleted = prune_history(snapshot_dir, keep=10)
        assert deleted == []

    def test_invalid_keep_raises(self, snapshot_dir):
        with pytest.raises(ValueError):
            prune_history(snapshot_dir, keep=0)

    def test_prefix_limits_pruning(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "prod_old", {})
        _write_snapshot(snapshot_dir, "prod_new", {})
        _write_snapshot(snapshot_dir, "dev_only", {})
        prune_history(snapshot_dir, keep=1, prefix="prod")
        remaining = get_snapshot_history(snapshot_dir)
        names = [e["name"] for e in remaining]
        assert "dev_only" in names
        assert len([n for n in names if n.startswith("prod")]) == 1


class TestFormatHistory:
    def test_empty_returns_message(self):
        assert "No snapshots" in format_history([])

    def test_contains_snapshot_name(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "my_snap", {"A": "1"})
        history = get_snapshot_history(snapshot_dir)
        output = format_history(history)
        assert "my_snap" in output

    def test_contains_var_count(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "snap", {"A": "1", "B": "2"})
        history = get_snapshot_history(snapshot_dir)
        output = format_history(history)
        assert "2" in output
