"""Tests for envforge.snapshot_similarity."""

from __future__ import annotations

import json
import os
import pytest

from envforge.snapshot_similarity import (
    key_similarity,
    value_similarity,
    compare_similarity,
    rank_by_similarity,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_snapshot(directory: str, name: str, variables: dict) -> None:
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"{name}.json")
    with open(path, "w") as fh:
        json.dump({"name": name, "vars": variables}, fh)


@pytest.fixture()
def snapshot_dir(tmp_path):
    return str(tmp_path / "snapshots")


# ---------------------------------------------------------------------------
# key_similarity
# ---------------------------------------------------------------------------


def test_key_similarity_identical():
    v = {"A": "1", "B": "2"}
    assert key_similarity(v, v) == 1.0


def test_key_similarity_disjoint():
    assert key_similarity({"A": "1"}, {"B": "2"}) == 0.0


def test_key_similarity_partial():
    a = {"A": "1", "B": "2", "C": "3"}
    b = {"B": "x", "C": "y", "D": "z"}
    # intersection={B,C}, union={A,B,C,D} -> 2/4
    assert key_similarity(a, b) == pytest.approx(0.5)


def test_key_similarity_both_empty():
    assert key_similarity({}, {}) == 1.0


# ---------------------------------------------------------------------------
# value_similarity
# ---------------------------------------------------------------------------


def test_value_similarity_identical():
    v = {"A": "1", "B": "2"}
    assert value_similarity(v, v) == 1.0


def test_value_similarity_same_keys_different_values():
    a = {"A": "1", "B": "2"}
    b = {"A": "9", "B": "8"}
    assert value_similarity(a, b) == 0.0


def test_value_similarity_partial_match():
    a = {"A": "1", "B": "2"}
    b = {"A": "1", "B": "99"}
    # intersection={(A,1)}, union={(A,1),(B,2),(B,99)} -> 1/3
    assert value_similarity(a, b) == pytest.approx(1 / 3)


# ---------------------------------------------------------------------------
# compare_similarity
# ---------------------------------------------------------------------------


def test_compare_similarity_returns_both_scores(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap1", {"X": "1", "Y": "2"})
    _write_snapshot(snapshot_dir, "snap2", {"X": "1", "Z": "3"})
    result = compare_similarity(snapshot_dir, "snap1", "snap2")
    assert "key_similarity" in result
    assert "value_similarity" in result
    assert 0.0 <= result["key_similarity"] <= 1.0
    assert 0.0 <= result["value_similarity"] <= 1.0


# ---------------------------------------------------------------------------
# rank_by_similarity
# ---------------------------------------------------------------------------


def test_rank_returns_sorted_descending(snapshot_dir):
    _write_snapshot(snapshot_dir, "ref", {"A": "1", "B": "2", "C": "3"})
    _write_snapshot(snapshot_dir, "close", {"A": "1", "B": "2", "D": "4"})
    _write_snapshot(snapshot_dir, "far", {"X": "9", "Y": "8"})
    ranked = rank_by_similarity(snapshot_dir, "ref", ["close", "far"])
    assert ranked[0][0] == "close"
    assert ranked[1][0] == "far"
    assert ranked[0][1] >= ranked[1][1]


def test_rank_invalid_mode_raises(snapshot_dir):
    _write_snapshot(snapshot_dir, "ref", {"A": "1"})
    _write_snapshot(snapshot_dir, "other", {"A": "1"})
    with pytest.raises(ValueError, match="Unknown similarity mode"):
        rank_by_similarity(snapshot_dir, "ref", ["other"], mode="bad")


def test_rank_key_mode(snapshot_dir):
    _write_snapshot(snapshot_dir, "ref", {"A": "1", "B": "2"})
    _write_snapshot(snapshot_dir, "same_keys", {"A": "9", "B": "8"})
    _write_snapshot(snapshot_dir, "diff_keys", {"C": "1", "D": "2"})
    ranked = rank_by_similarity(
        snapshot_dir, "ref", ["same_keys", "diff_keys"], mode="key"
    )
    assert ranked[0][0] == "same_keys"
    assert ranked[0][1] == 1.0
    assert ranked[1][1] == 0.0
