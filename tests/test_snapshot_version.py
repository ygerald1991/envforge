"""Tests for envforge.snapshot_version."""

import pytest
from pathlib import Path
from envforge.snapshot_version import (
    bump_version,
    get_version,
    set_version,
    reset_version,
    list_versions,
)


@pytest.fixture
def vdir(tmp_path):
    return str(tmp_path / "versions")


def test_bump_starts_at_one(vdir):
    ver = bump_version(vdir, "snap_a")
    assert ver == 1


def test_bump_increments_each_call(vdir):
    bump_version(vdir, "snap_a")
    bump_version(vdir, "snap_a")
    ver = bump_version(vdir, "snap_a")
    assert ver == 3


def test_bump_independent_per_snapshot(vdir):
    bump_version(vdir, "snap_a")
    bump_version(vdir, "snap_a")
    ver_b = bump_version(vdir, "snap_b")
    assert ver_b == 1


def test_get_missing_returns_none(vdir):
    assert get_version(vdir, "nonexistent") is None


def test_get_after_bump(vdir):
    bump_version(vdir, "snap_a")
    bump_version(vdir, "snap_a")
    assert get_version(vdir, "snap_a") == 2


def test_set_explicit_version(vdir):
    result = set_version(vdir, "snap_a", 5)
    assert result == 5
    assert get_version(vdir, "snap_a") == 5


def test_set_version_below_one_raises(vdir):
    with pytest.raises(ValueError, match=">= 1"):
        set_version(vdir, "snap_a", 0)


def test_set_version_negative_raises(vdir):
    with pytest.raises(ValueError):
        set_version(vdir, "snap_a", -3)


def test_reset_removes_version(vdir):
    bump_version(vdir, "snap_a")
    reset_version(vdir, "snap_a")
    assert get_version(vdir, "snap_a") is None


def test_reset_missing_snapshot_is_noop(vdir):
    reset_version(vdir, "ghost")  # should not raise
    assert get_version(vdir, "ghost") is None


def test_list_versions_empty(vdir):
    assert list_versions(vdir) == {}


def test_list_versions_multiple(vdir):
    bump_version(vdir, "snap_a")
    bump_version(vdir, "snap_a")
    bump_version(vdir, "snap_b")
    versions = list_versions(vdir)
    assert versions == {"snap_a": 2, "snap_b": 1}


def test_persists_across_calls(vdir):
    bump_version(vdir, "snap_a")
    # Simulate fresh load by calling get directly
    assert get_version(vdir, "snap_a") == 1
    bump_version(vdir, "snap_a")
    assert get_version(vdir, "snap_a") == 2


def test_creates_directory_if_missing(tmp_path):
    nested = str(tmp_path / "deep" / "nested" / "store")
    ver = bump_version(nested, "snap")
    assert ver == 1
    assert Path(nested).exists()
