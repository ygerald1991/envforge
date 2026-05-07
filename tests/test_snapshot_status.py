"""Tests for envforge.snapshot_status."""

from __future__ import annotations

import pytest

from envforge.snapshot_status import (
    VALID_STATUSES,
    get_all_statuses,
    get_status,
    list_by_status,
    remove_status,
    set_status,
)


@pytest.fixture()
def sdir(tmp_path):
    return str(tmp_path)


def test_set_and_get_status(sdir):
    set_status(sdir, "snap-a", "active")
    assert get_status(sdir, "snap-a") == "active"


def test_get_missing_status_returns_none(sdir):
    assert get_status(sdir, "nonexistent") is None


def test_overwrite_existing_status(sdir):
    set_status(sdir, "snap-a", "active")
    set_status(sdir, "snap-a", "deprecated")
    assert get_status(sdir, "snap-a") == "deprecated"


def test_invalid_status_raises(sdir):
    with pytest.raises(ValueError, match="Invalid status"):
        set_status(sdir, "snap-a", "unknown-state")


def test_remove_existing_status_returns_true(sdir):
    set_status(sdir, "snap-a", "stable")
    assert remove_status(sdir, "snap-a") is True
    assert get_status(sdir, "snap-a") is None


def test_remove_missing_status_returns_false(sdir):
    assert remove_status(sdir, "snap-a") is False


def test_list_by_status_returns_matching(sdir):
    set_status(sdir, "snap-a", "active")
    set_status(sdir, "snap-b", "deprecated")
    set_status(sdir, "snap-c", "active")
    result = list_by_status(sdir, "active")
    assert set(result) == {"snap-a", "snap-c"}


def test_list_by_status_empty_when_none_match(sdir):
    set_status(sdir, "snap-a", "active")
    assert list_by_status(sdir, "stable") == []


def test_list_by_invalid_status_raises(sdir):
    with pytest.raises(ValueError):
        list_by_status(sdir, "bad-status")


def test_get_all_statuses_returns_full_index(sdir):
    set_status(sdir, "snap-a", "active")
    set_status(sdir, "snap-b", "experimental")
    index = get_all_statuses(sdir)
    assert index == {"snap-a": "active", "snap-b": "experimental"}


def test_get_all_statuses_empty_store(sdir):
    assert get_all_statuses(sdir) == {}


def test_all_valid_statuses_accepted(sdir):
    for i, status in enumerate(VALID_STATUSES):
        set_status(sdir, f"snap-{i}", status)
        assert get_status(sdir, f"snap-{i}") == status


def test_persists_across_calls(sdir):
    set_status(sdir, "snap-a", "stable")
    # Simulate a fresh load by calling get_status independently
    assert get_status(sdir, "snap-a") == "stable"
    set_status(sdir, "snap-b", "archived")
    assert get_status(sdir, "snap-a") == "stable"
    assert get_status(sdir, "snap-b") == "archived"
