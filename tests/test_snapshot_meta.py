"""Tests for envforge.snapshot_meta."""

import pytest
from envforge.snapshot_meta import (
    set_meta,
    get_meta,
    get_all_meta,
    remove_meta_key,
    clear_meta,
    list_meta_snapshots,
)


@pytest.fixture()
def mdir(tmp_path):
    return str(tmp_path)


def test_set_and_get_single_key(mdir):
    set_meta(mdir, "snap1", "author", "alice")
    assert get_meta(mdir, "snap1", "author") == "alice"


def test_get_missing_key_returns_none(mdir):
    assert get_meta(mdir, "snap1", "nonexistent") is None


def test_get_meta_for_missing_snapshot_returns_none(mdir):
    assert get_meta(mdir, "ghost", "key") is None


def test_overwrite_existing_key(mdir):
    set_meta(mdir, "snap1", "env", "dev")
    set_meta(mdir, "snap1", "env", "prod")
    assert get_meta(mdir, "snap1", "env") == "prod"


def test_multiple_keys_on_same_snapshot(mdir):
    set_meta(mdir, "snap1", "author", "bob")
    set_meta(mdir, "snap1", "version", 3)
    all_meta = get_all_meta(mdir, "snap1")
    assert all_meta["author"] == "bob"
    assert all_meta["version"] == 3


def test_get_all_meta_returns_empty_for_unknown(mdir):
    assert get_all_meta(mdir, "unknown") == {}


def test_multiple_snapshots_independent(mdir):
    set_meta(mdir, "snap1", "role", "dev")
    set_meta(mdir, "snap2", "role", "prod")
    assert get_meta(mdir, "snap1", "role") == "dev"
    assert get_meta(mdir, "snap2", "role") == "prod"


def test_remove_meta_key_returns_true(mdir):
    set_meta(mdir, "snap1", "owner", "carol")
    result = remove_meta_key(mdir, "snap1", "owner")
    assert result is True
    assert get_meta(mdir, "snap1", "owner") is None


def test_remove_missing_key_returns_false(mdir):
    result = remove_meta_key(mdir, "snap1", "ghost")
    assert result is False


def test_remove_last_key_cleans_snapshot_entry(mdir):
    set_meta(mdir, "snap1", "x", 1)
    remove_meta_key(mdir, "snap1", "x")
    assert "snap1" not in list_meta_snapshots(mdir)


def test_clear_meta_removes_all_keys(mdir):
    set_meta(mdir, "snap1", "a", 1)
    set_meta(mdir, "snap1", "b", 2)
    clear_meta(mdir, "snap1")
    assert get_all_meta(mdir, "snap1") == {}


def test_clear_meta_on_missing_snapshot_is_noop(mdir):
    clear_meta(mdir, "nonexistent")  # should not raise


def test_list_meta_snapshots_returns_names(mdir):
    set_meta(mdir, "snap_a", "k", "v")
    set_meta(mdir, "snap_b", "k", "v")
    names = list_meta_snapshots(mdir)
    assert "snap_a" in names
    assert "snap_b" in names


def test_list_meta_snapshots_empty_dir(mdir):
    assert list_meta_snapshots(mdir) == []


def test_meta_value_can_be_dict(mdir):
    payload = {"region": "us-east", "tier": "free"}
    set_meta(mdir, "snap1", "config", payload)
    assert get_meta(mdir, "snap1", "config") == payload
