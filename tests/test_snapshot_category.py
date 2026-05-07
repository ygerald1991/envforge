"""Tests for envforge.snapshot_category."""

import pytest

from envforge.snapshot_category import (
    all_categories,
    get_category,
    list_by_category,
    remove_from_category,
    set_category,
)


@pytest.fixture()
def cdir(tmp_path):
    return str(tmp_path)


def test_set_and_get_category(cdir):
    set_category(cdir, "snap_a", "production")
    assert get_category(cdir, "snap_a") == "production"


def test_get_missing_category_returns_none(cdir):
    assert get_category(cdir, "nonexistent") is None


def test_overwrite_existing_category(cdir):
    set_category(cdir, "snap_a", "staging")
    set_category(cdir, "snap_a", "production")
    assert get_category(cdir, "snap_a") == "production"
    assert "snap_a" not in list_by_category(cdir, "staging")


def test_list_by_category_returns_members(cdir):
    set_category(cdir, "snap_a", "dev")
    set_category(cdir, "snap_b", "dev")
    members = list_by_category(cdir, "dev")
    assert "snap_a" in members
    assert "snap_b" in members


def test_list_by_category_missing_returns_empty(cdir):
    assert list_by_category(cdir, "unknown") == []


def test_remove_from_category_returns_true(cdir):
    set_category(cdir, "snap_a", "dev")
    result = remove_from_category(cdir, "snap_a")
    assert result is True
    assert get_category(cdir, "snap_a") is None


def test_remove_nonexistent_returns_false(cdir):
    assert remove_from_category(cdir, "ghost") is False


def test_all_categories_sorted(cdir):
    set_category(cdir, "snap_c", "production")
    set_category(cdir, "snap_b", "dev")
    set_category(cdir, "snap_a", "staging")
    cats = all_categories(cdir)
    assert cats == sorted(cats)
    assert set(cats) == {"production", "dev", "staging"}


def test_all_categories_excludes_empty(cdir):
    set_category(cdir, "snap_a", "dev")
    remove_from_category(cdir, "snap_a")
    assert "dev" not in all_categories(cdir)


def test_empty_category_name_raises(cdir):
    with pytest.raises(ValueError):
        set_category(cdir, "snap_a", "")


def test_whitespace_only_category_raises(cdir):
    with pytest.raises(ValueError):
        set_category(cdir, "snap_a", "   ")


def test_multiple_snapshots_independent_categories(cdir):
    set_category(cdir, "snap_x", "prod")
    set_category(cdir, "snap_y", "staging")
    assert get_category(cdir, "snap_x") == "prod"
    assert get_category(cdir, "snap_y") == "staging"


def test_persists_across_calls(cdir):
    set_category(cdir, "snap_p", "qa")
    # Re-read from disk by calling get again (no in-memory cache)
    assert get_category(cdir, "snap_p") == "qa"
