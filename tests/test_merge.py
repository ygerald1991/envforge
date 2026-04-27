"""Tests for envforge.merge module."""

import json
import os
import pytest

from envforge.merge import (
    merge_snapshots,
    save_merged_snapshot,
    MERGE_STRATEGY_LAST_WINS,
    MERGE_STRATEGY_FIRST_WINS,
    MERGE_STRATEGY_ERROR_ON_CONFLICT,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_snapshot(directory: str, name: str, variables: dict) -> str:
    path = os.path.join(directory, f"{name}.json")
    payload = {"name": name, "variables": variables}
    with open(path, "w") as fh:
        json.dump(payload, fh)
    return path


@pytest.fixture()
def snapshot_dir(tmp_path):
    return str(tmp_path)


# ---------------------------------------------------------------------------
# merge_snapshots
# ---------------------------------------------------------------------------

class TestMergeSnapshots:
    def test_disjoint_keys_are_combined(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "a", {"FOO": "1"})
        _write_snapshot(snapshot_dir, "b", {"BAR": "2"})
        result = merge_snapshots(["a", "b"], snapshot_dir)
        assert result == {"FOO": "1", "BAR": "2"}

    def test_last_wins_strategy_overwrites(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "base", {"KEY": "base_val", "X": "1"})
        _write_snapshot(snapshot_dir, "override", {"KEY": "new_val"})
        result = merge_snapshots(
            ["base", "override"], snapshot_dir, MERGE_STRATEGY_LAST_WINS
        )
        assert result["KEY"] == "new_val"
        assert result["X"] == "1"

    def test_first_wins_strategy_preserves_original(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "base", {"KEY": "original"})
        _write_snapshot(snapshot_dir, "extra", {"KEY": "ignored"})
        result = merge_snapshots(
            ["base", "extra"], snapshot_dir, MERGE_STRATEGY_FIRST_WINS
        )
        assert result["KEY"] == "original"

    def test_error_on_conflict_raises(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "s1", {"CONFLICT": "a"})
        _write_snapshot(snapshot_dir, "s2", {"CONFLICT": "b"})
        with pytest.raises(ValueError, match="Conflict"):
            merge_snapshots(
                ["s1", "s2"], snapshot_dir, MERGE_STRATEGY_ERROR_ON_CONFLICT
            )

    def test_unknown_strategy_raises(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "only", {"A": "1"})
        with pytest.raises(ValueError, match="Unknown merge strategy"):
            merge_snapshots(["only"], snapshot_dir, strategy="bogus")

    def test_missing_snapshot_raises(self, snapshot_dir):
        with pytest.raises(FileNotFoundError):
            merge_snapshots(["nonexistent"], snapshot_dir)

    def test_single_snapshot_returns_its_vars(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "solo", {"ONLY": "val"})
        result = merge_snapshots(["solo"], snapshot_dir)
        assert result == {"ONLY": "val"}


# ---------------------------------------------------------------------------
# save_merged_snapshot
# ---------------------------------------------------------------------------

class TestSaveMergedSnapshot:
    def test_creates_file_on_disk(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "p", {"PORT": "8080"})
        _write_snapshot(snapshot_dir, "q", {"HOST": "localhost"})
        path = save_merged_snapshot(["p", "q"], "combined", snapshot_dir)
        assert os.path.isfile(path)

    def test_merged_snapshot_contains_all_vars(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "m1", {"A": "1"})
        _write_snapshot(snapshot_dir, "m2", {"B": "2"})
        path = save_merged_snapshot(["m1", "m2"], "merged_out", snapshot_dir)
        with open(path) as fh:
            data = json.load(fh)
        assert data["variables"]["A"] == "1"
        assert data["variables"]["B"] == "2"

    def test_metadata_records_source_snapshots(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "src1", {"ENV": "dev"})
        path = save_merged_snapshot(["src1"], "meta_test", snapshot_dir)
        with open(path) as fh:
            data = json.load(fh)
        assert "src1" in data.get("merged_from", [])
