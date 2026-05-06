"""Tests for envforge.snapshot_namespace."""

from __future__ import annotations

import pytest

from envforge.snapshot_namespace import (
    add_to_namespace,
    remove_from_namespace,
    get_namespace,
    list_namespaces,
    delete_namespace,
    _load_namespace_index,
)


@pytest.fixture()
def nsdir(tmp_path):
    return str(tmp_path)


def test_add_creates_namespace(nsdir):
    add_to_namespace(nsdir, "production", "snap_001")
    assert "production" in list_namespaces(nsdir)


def test_add_snapshot_appears_in_namespace(nsdir):
    add_to_namespace(nsdir, "staging", "snap_abc")
    members = get_namespace(nsdir, "staging")
    assert "snap_abc" in members


def test_add_multiple_snapshots_to_same_namespace(nsdir):
    add_to_namespace(nsdir, "dev", "snap_1")
    add_to_namespace(nsdir, "dev", "snap_2")
    members = get_namespace(nsdir, "dev")
    assert "snap_1" in members
    assert "snap_2" in members


def test_duplicate_add_is_idempotent(nsdir):
    add_to_namespace(nsdir, "dev", "snap_x")
    add_to_namespace(nsdir, "dev", "snap_x")
    members = get_namespace(nsdir, "dev")
    assert members.count("snap_x") == 1


def test_get_missing_namespace_returns_none(nsdir):
    result = get_namespace(nsdir, "nonexistent")
    assert result is None


def test_list_namespaces_empty(nsdir):
    assert list_namespaces(nsdir) == []


def test_list_namespaces_returns_all(nsdir):
    add_to_namespace(nsdir, "ns_a", "snap_1")
    add_to_namespace(nsdir, "ns_b", "snap_2")
    ns = list_namespaces(nsdir)
    assert "ns_a" in ns
    assert "ns_b" in ns


def test_remove_snapshot_from_namespace(nsdir):
    add_to_namespace(nsdir, "prod", "snap_old")
    result = remove_from_namespace(nsdir, "prod", "snap_old")
    assert result is True
    members = get_namespace(nsdir, "prod")
    assert members is None  # namespace deleted when empty


def test_remove_nonexistent_snapshot_returns_false(nsdir):
    add_to_namespace(nsdir, "prod", "snap_a")
    result = remove_from_namespace(nsdir, "prod", "snap_missing")
    assert result is False


def test_remove_from_missing_namespace_returns_false(nsdir):
    result = remove_from_namespace(nsdir, "ghost", "snap_1")
    assert result is False


def test_delete_namespace(nsdir):
    add_to_namespace(nsdir, "temp", "snap_1")
    result = delete_namespace(nsdir, "temp")
    assert result is True
    assert "temp" not in list_namespaces(nsdir)


def test_delete_missing_namespace_returns_false(nsdir):
    result = delete_namespace(nsdir, "never_existed")
    assert result is False


def test_persists_to_file(nsdir):
    add_to_namespace(nsdir, "ci", "snap_ci_001")
    index = _load_namespace_index(nsdir)
    assert "ci" in index
    assert "snap_ci_001" in index["ci"]
