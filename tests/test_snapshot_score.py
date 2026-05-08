"""Tests for envforge.snapshot_score."""

from __future__ import annotations

import pytest

from envforge.snapshot_score import (
    get_score,
    rank_snapshots,
    remove_score,
    set_score,
)


@pytest.fixture()
def sdir(tmp_path):
    return str(tmp_path)


def test_set_and_get_score(sdir):
    result = set_score(sdir, "snap_a", 87.5)
    assert result == 87.5
    assert get_score(sdir, "snap_a") == 87.5


def test_get_missing_score_returns_none(sdir):
    assert get_score(sdir, "nonexistent") is None


def test_overwrite_existing_score(sdir):
    set_score(sdir, "snap_a", 50.0)
    set_score(sdir, "snap_a", 99.0)
    assert get_score(sdir, "snap_a") == 99.0


def test_score_out_of_range_raises(sdir):
    with pytest.raises(ValueError, match="0.0 and 100.0"):
        set_score(sdir, "snap_a", 101.0)


def test_score_negative_raises(sdir):
    with pytest.raises(ValueError):
        set_score(sdir, "snap_a", -1.0)


def test_score_boundary_values(sdir):
    set_score(sdir, "low", 0.0)
    set_score(sdir, "high", 100.0)
    assert get_score(sdir, "low") == 0.0
    assert get_score(sdir, "high") == 100.0


def test_remove_existing_score(sdir):
    set_score(sdir, "snap_a", 42.0)
    removed = remove_score(sdir, "snap_a")
    assert removed is True
    assert get_score(sdir, "snap_a") is None


def test_remove_missing_score_returns_false(sdir):
    assert remove_score(sdir, "ghost") is False


def test_rank_descending(sdir):
    set_score(sdir, "a", 30.0)
    set_score(sdir, "b", 90.0)
    set_score(sdir, "c", 60.0)
    ranked = rank_snapshots(sdir, descending=True)
    scores = [s for _, s in ranked]
    assert scores == sorted(scores, reverse=True)
    assert ranked[0][0] == "b"


def test_rank_ascending(sdir):
    set_score(sdir, "a", 30.0)
    set_score(sdir, "b", 90.0)
    ranked = rank_snapshots(sdir, descending=False)
    assert ranked[0][0] == "a"


def test_rank_empty_store(sdir):
    assert rank_snapshots(sdir) == []


def test_persists_across_calls(sdir):
    set_score(sdir, "snap_x", 77.7)
    # Re-load by calling get_score (reads from disk)
    assert get_score(sdir, "snap_x") == pytest.approx(77.7)
