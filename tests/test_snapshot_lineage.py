"""Tests for envforge.snapshot_lineage."""

from __future__ import annotations

import pytest

from envforge.snapshot_lineage import (
    get_descendants,
    get_lineage,
    record_fork,
    record_merge,
    remove_lineage,
)


@pytest.fixture()
def ldir(tmp_path):
    return str(tmp_path)


def test_record_fork_returns_entry(ldir):
    entry = record_fork(ldir, "snap-a", "snap-b")
    assert entry["type"] == "fork"
    assert entry["parent"] == "snap-a"


def test_record_fork_persists(ldir):
    record_fork(ldir, "snap-a", "snap-b")
    entry = get_lineage(ldir, "snap-b")
    assert entry is not None
    assert entry["parent"] == "snap-a"


def test_record_merge_returns_entry(ldir):
    entry = record_merge(ldir, ["snap-a", "snap-b"], "snap-c")
    assert entry["type"] == "merge"
    assert "snap-a" in entry["sources"]
    assert "snap-b" in entry["sources"]


def test_record_merge_persists(ldir):
    record_merge(ldir, ["snap-a", "snap-b"], "snap-c")
    entry = get_lineage(ldir, "snap-c")
    assert entry is not None
    assert entry["type"] == "merge"


def test_record_merge_requires_two_sources(ldir):
    with pytest.raises(ValueError, match="at least two"):
        record_merge(ldir, ["snap-a"], "snap-c")


def test_get_lineage_missing_returns_none(ldir):
    assert get_lineage(ldir, "nonexistent") is None


def test_get_descendants_direct(ldir):
    record_fork(ldir, "snap-a", "snap-b")
    record_fork(ldir, "snap-a", "snap-c")
    kids = get_descendants(ldir, "snap-a")
    assert set(kids) == {"snap-b", "snap-c"}


def test_get_descendants_transitive(ldir):
    record_fork(ldir, "snap-a", "snap-b")
    record_fork(ldir, "snap-b", "snap-c")
    kids = get_descendants(ldir, "snap-a")
    assert "snap-b" in kids
    assert "snap-c" in kids


def test_get_descendants_none(ldir):
    assert get_descendants(ldir, "snap-a") == []


def test_remove_existing_lineage(ldir):
    record_fork(ldir, "snap-a", "snap-b")
    removed = remove_lineage(ldir, "snap-b")
    assert removed is True
    assert get_lineage(ldir, "snap-b") is None


def test_remove_missing_lineage_returns_false(ldir):
    assert remove_lineage(ldir, "ghost") is False


def test_multiple_entries_independent(ldir):
    record_fork(ldir, "snap-a", "snap-b")
    record_merge(ldir, ["snap-b", "snap-c"], "snap-d")
    assert get_lineage(ldir, "snap-b")["type"] == "fork"
    assert get_lineage(ldir, "snap-d")["type"] == "merge"
