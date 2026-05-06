"""Tests for envforge.snapshot_priority."""

from __future__ import annotations

import pytest

from envforge.snapshot_priority import (
    get_priority,
    list_by_priority,
    remove_priority,
    set_priority,
)


@pytest.fixture()
def pdir(tmp_path):
    return str(tmp_path)


def test_set_and_get_priority(pdir):
    set_priority(pdir, "snap_a", 5)
    assert get_priority(pdir, "snap_a") == 5


def test_get_missing_priority_returns_none(pdir):
    assert get_priority(pdir, "nonexistent") is None


def test_overwrite_existing_priority(pdir):
    set_priority(pdir, "snap_a", 3)
    set_priority(pdir, "snap_a", 8)
    assert get_priority(pdir, "snap_a") == 8


def test_priority_out_of_range_raises(pdir):
    with pytest.raises(ValueError, match="Priority must be between"):
        set_priority(pdir, "snap_a", 0)
    with pytest.raises(ValueError, match="Priority must be between"):
        set_priority(pdir, "snap_a", 11)


def test_priority_boundary_values_accepted(pdir):
    set_priority(pdir, "snap_low", 1)
    set_priority(pdir, "snap_high", 10)
    assert get_priority(pdir, "snap_low") == 1
    assert get_priority(pdir, "snap_high") == 10


def test_remove_existing_priority(pdir):
    set_priority(pdir, "snap_a", 7)
    result = remove_priority(pdir, "snap_a")
    assert result is True
    assert get_priority(pdir, "snap_a") is None


def test_remove_missing_priority_returns_false(pdir):
    result = remove_priority(pdir, "ghost")
    assert result is False


def test_list_by_priority_sorted_descending(pdir):
    set_priority(pdir, "snap_c", 2)
    set_priority(pdir, "snap_a", 9)
    set_priority(pdir, "snap_b", 5)
    entries = list_by_priority(pdir)
    levels = [lvl for _, lvl in entries]
    assert levels == sorted(levels, reverse=True)


def test_list_by_priority_empty_store(pdir):
    assert list_by_priority(pdir) == []


def test_list_by_priority_contains_all_entries(pdir):
    names = {"snap_x", "snap_y", "snap_z"}
    for i, name in enumerate(names, start=1):
        set_priority(pdir, name, i)
    result_names = {n for n, _ in list_by_priority(pdir)}
    assert result_names == names


def test_priority_persists_across_calls(pdir):
    set_priority(pdir, "persistent", 6)
    # Simulate a fresh load by calling get without caching
    assert get_priority(pdir, "persistent") == 6
