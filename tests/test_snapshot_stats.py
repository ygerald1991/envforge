"""Tests for envforge.snapshot_stats."""

from __future__ import annotations

import json
import os
import pytest

from envforge.snapshot_stats import (
    format_summary,
    key_frequency,
    most_common_keys,
    snapshot_summary,
    unique_values_per_key,
)


@pytest.fixture()
def snapshot_dir(tmp_path):
    d = tmp_path / "snapshots"
    d.mkdir()
    return str(d)


def _write_snapshot(snapshot_dir: str, name: str, vars_: dict) -> None:
    path = os.path.join(snapshot_dir, f"{name}.json")
    with open(path, "w") as fh:
        json.dump({"name": name, "vars": vars_}, fh)


# ---------------------------------------------------------------------------
# key_frequency
# ---------------------------------------------------------------------------

class TestKeyFrequency:
    def test_empty_store_returns_empty(self, snapshot_dir):
        assert key_frequency(snapshot_dir) == {}

    def test_single_snapshot(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "s1", {"A": "1", "B": "2"})
        freq = key_frequency(snapshot_dir)
        assert freq["A"] == 1
        assert freq["B"] == 1

    def test_key_appearing_in_multiple_snapshots(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "s1", {"A": "1", "B": "2"})
        _write_snapshot(snapshot_dir, "s2", {"A": "99", "C": "3"})
        freq = key_frequency(snapshot_dir)
        assert freq["A"] == 2
        assert freq["B"] == 1
        assert freq["C"] == 1


# ---------------------------------------------------------------------------
# most_common_keys
# ---------------------------------------------------------------------------

class TestMostCommonKeys:
    def test_returns_sorted_descending(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "s1", {"X": "1", "Y": "2"})
        _write_snapshot(snapshot_dir, "s2", {"X": "1"})
        top = most_common_keys(snapshot_dir, top_n=5)
        assert top[0][0] == "X"
        assert top[0][1] == 2

    def test_top_n_limits_results(self, snapshot_dir):
        for i in range(10):
            _write_snapshot(snapshot_dir, f"s{i}", {f"KEY{i}": str(i)})
        top = most_common_keys(snapshot_dir, top_n=3)
        assert len(top) == 3


# ---------------------------------------------------------------------------
# unique_values_per_key
# ---------------------------------------------------------------------------

class TestUniqueValuesPerKey:
    def test_collects_distinct_values(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "s1", {"ENV": "dev"})
        _write_snapshot(snapshot_dir, "s2", {"ENV": "prod"})
        _write_snapshot(snapshot_dir, "s3", {"ENV": "dev"})
        uvpk = unique_values_per_key(snapshot_dir)
        assert uvpk["ENV"] == {"dev", "prod"}


# ---------------------------------------------------------------------------
# snapshot_summary
# ---------------------------------------------------------------------------

class TestSnapshotSummary:
    def test_empty_store(self, snapshot_dir):
        s = snapshot_summary(snapshot_dir)
        assert s["total_snapshots"] == 0
        assert s["avg_keys_per_snapshot"] == 0.0

    def test_counts_snapshots(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "a", {"K1": "v", "K2": "v"})
        _write_snapshot(snapshot_dir, "b", {"K1": "v"})
        s = snapshot_summary(snapshot_dir)
        assert s["total_snapshots"] == 2
        assert s["avg_keys_per_snapshot"] == pytest.approx(1.5)

    def test_format_summary_is_string(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "x", {"FOO": "bar"})
        s = snapshot_summary(snapshot_dir)
        out = format_summary(s)
        assert "Total snapshots" in out
        assert "FOO" in out
