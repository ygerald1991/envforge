"""Tests for envforge.compare module."""

import json
import os
import pytest
from envforge.compare import compare_snapshots, format_comparison


def _write_snapshot(directory: str, name: str, variables: dict) -> None:
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"{name}.json")
    with open(path, "w") as fh:
        json.dump(variables, fh)


@pytest.fixture()
def snapshot_dir(tmp_path):
    return str(tmp_path)


class TestCompareSnapshots:
    def test_requires_at_least_two_snapshots(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "a", {"X": "1"})
        with pytest.raises(ValueError, match="At least two"):
            compare_snapshots(["a"], base_dir=snapshot_dir)

    def test_all_keys_in_union(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "dev", {"A": "1", "B": "2"})
        _write_snapshot(snapshot_dir, "prod", {"B": "2", "C": "3"})
        result = compare_snapshots(["dev", "prod"], base_dir=snapshot_dir)
        assert result["keys"] == ["A", "B", "C"]

    def test_matrix_contains_none_for_missing_keys(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "dev", {"A": "1"})
        _write_snapshot(snapshot_dir, "prod", {"B": "2"})
        result = compare_snapshots(["dev", "prod"], base_dir=snapshot_dir)
        assert result["matrix"]["A"]["prod"] is None
        assert result["matrix"]["B"]["dev"] is None

    def test_drift_detects_differing_values(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "dev", {"URL": "http://dev", "PORT": "8080"})
        _write_snapshot(snapshot_dir, "prod", {"URL": "http://prod", "PORT": "8080"})
        result = compare_snapshots(["dev", "prod"], base_dir=snapshot_dir)
        assert "URL" in result["drift"]
        assert "PORT" not in result["drift"]

    def test_drift_includes_missing_keys(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "dev", {"ONLY_DEV": "yes"})
        _write_snapshot(snapshot_dir, "prod", {})
        result = compare_snapshots(["dev", "prod"], base_dir=snapshot_dir)
        assert "ONLY_DEV" in result["drift"]

    def test_no_drift_when_identical(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "s1", {"K": "v"})
        _write_snapshot(snapshot_dir, "s2", {"K": "v"})
        result = compare_snapshots(["s1", "s2"], base_dir=snapshot_dir)
        assert result["drift"] == []

    def test_three_snapshots(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "a", {"X": "1"})
        _write_snapshot(snapshot_dir, "b", {"X": "2"})
        _write_snapshot(snapshot_dir, "c", {"X": "1"})
        result = compare_snapshots(["a", "b", "c"], base_dir=snapshot_dir)
        assert "X" in result["drift"]
        assert result["snapshots"] == ["a", "b", "c"]


class TestFormatComparison:
    def test_no_drift_message(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "x", {"A": "1"})
        _write_snapshot(snapshot_dir, "y", {"A": "1"})
        result = compare_snapshots(["x", "y"], base_dir=snapshot_dir)
        output = format_comparison(result)
        assert "No drift" in output

    def test_drifted_key_appears_in_output(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "dev", {"DB": "dev-db"})
        _write_snapshot(snapshot_dir, "prod", {"DB": "prod-db"})
        result = compare_snapshots(["dev", "prod"], base_dir=snapshot_dir)
        output = format_comparison(result)
        assert "DB" in output
        assert "dev-db" in output
        assert "prod-db" in output

    def test_show_all_includes_non_drifted(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "dev", {"SAME": "v", "DIFF": "a"})
        _write_snapshot(snapshot_dir, "prod", {"SAME": "v", "DIFF": "b"})
        result = compare_snapshots(["dev", "prod"], base_dir=snapshot_dir)
        output_default = format_comparison(result, show_all=False)
        output_all = format_comparison(result, show_all=True)
        assert "SAME" not in output_default
        assert "SAME" in output_all
