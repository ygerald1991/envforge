"""Tests for envforge.snapshot_bookmark."""

import pytest
from pathlib import Path
from envforge.snapshot_bookmark import (
    set_bookmark,
    remove_bookmark,
    resolve_bookmark,
    list_bookmarks,
    bookmarks_for_snapshot,
)


@pytest.fixture
def bdir(tmp_path):
    return str(tmp_path / "bookmarks")


def test_set_and_resolve(bdir):
    set_bookmark(bdir, "prod", "snap_2024_prod")
    assert resolve_bookmark(bdir, "prod") == "snap_2024_prod"


def test_resolve_missing_returns_none(bdir):
    assert resolve_bookmark(bdir, "nonexistent") is None


def test_overwrite_existing_bookmark(bdir):
    set_bookmark(bdir, "latest", "snap_v1")
    set_bookmark(bdir, "latest", "snap_v2")
    assert resolve_bookmark(bdir, "latest") == "snap_v2"


def test_remove_existing_bookmark(bdir):
    set_bookmark(bdir, "staging", "snap_staging")
    result = remove_bookmark(bdir, "staging")
    assert result is True
    assert resolve_bookmark(bdir, "staging") is None


def test_remove_nonexistent_returns_false(bdir):
    assert remove_bookmark(bdir, "ghost") is False


def test_list_bookmarks_empty(bdir):
    assert list_bookmarks(bdir) == {}


def test_list_bookmarks_multiple(bdir):
    set_bookmark(bdir, "a", "snap_a")
    set_bookmark(bdir, "b", "snap_b")
    result = list_bookmarks(bdir)
    assert result == {"a": "snap_a", "b": "snap_b"}


def test_bookmarks_for_snapshot_none(bdir):
    set_bookmark(bdir, "x", "snap_x")
    assert bookmarks_for_snapshot(bdir, "snap_y") == []


def test_bookmarks_for_snapshot_multiple(bdir):
    set_bookmark(bdir, "alpha", "snap_shared")
    set_bookmark(bdir, "beta", "snap_shared")
    set_bookmark(bdir, "gamma", "snap_other")
    result = bookmarks_for_snapshot(bdir, "snap_shared")
    assert sorted(result) == ["alpha", "beta"]


def test_creates_directory_if_missing(tmp_path):
    bdir = str(tmp_path / "deep" / "nested" / "bookmarks")
    set_bookmark(bdir, "env", "snap_env")
    assert resolve_bookmark(bdir, "env") == "snap_env"


def test_persists_across_calls(bdir):
    set_bookmark(bdir, "persist", "snap_persist")
    # Re-read by calling list_bookmarks (fresh load from disk)
    data = list_bookmarks(bdir)
    assert data["persist"] == "snap_persist"
