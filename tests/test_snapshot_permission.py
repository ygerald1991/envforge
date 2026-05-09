"""Tests for envforge.snapshot_permission."""

from __future__ import annotations

import pytest

from envforge.snapshot_permission import (
    set_permission,
    remove_permission,
    get_permission,
    list_permissions,
    get_users_with_role,
    VALID_ROLES,
)


@pytest.fixture()
def pdir(tmp_path):
    return str(tmp_path)


def test_set_and_get_permission(pdir):
    set_permission(pdir, "snap1", "alice", "owner")
    assert get_permission(pdir, "snap1", "alice") == "owner"


def test_get_missing_permission_returns_none(pdir):
    assert get_permission(pdir, "snap1", "bob") is None


def test_overwrite_existing_permission(pdir):
    set_permission(pdir, "snap1", "alice", "editor")
    set_permission(pdir, "snap1", "alice", "viewer")
    assert get_permission(pdir, "snap1", "alice") == "viewer"


def test_invalid_role_raises(pdir):
    with pytest.raises(ValueError, match="Invalid role"):
        set_permission(pdir, "snap1", "alice", "superuser")


def test_remove_existing_permission(pdir):
    set_permission(pdir, "snap1", "alice", "editor")
    result = remove_permission(pdir, "snap1", "alice")
    assert result is True
    assert get_permission(pdir, "snap1", "alice") is None


def test_remove_missing_permission_returns_false(pdir):
    result = remove_permission(pdir, "snap1", "ghost")
    assert result is False


def test_list_permissions_returns_all_users(pdir):
    set_permission(pdir, "snap1", "alice", "owner")
    set_permission(pdir, "snap1", "bob", "viewer")
    perms = list_permissions(pdir, "snap1")
    assert perms == {"alice": "owner", "bob": "viewer"}


def test_list_permissions_empty_snapshot(pdir):
    assert list_permissions(pdir, "nonexistent") == {}


def test_multiple_snapshots_independent(pdir):
    set_permission(pdir, "snap1", "alice", "owner")
    set_permission(pdir, "snap2", "bob", "editor")
    assert get_permission(pdir, "snap1", "bob") is None
    assert get_permission(pdir, "snap2", "alice") is None


def test_get_users_with_role(pdir):
    set_permission(pdir, "snap1", "alice", "viewer")
    set_permission(pdir, "snap1", "bob", "viewer")
    set_permission(pdir, "snap1", "carol", "editor")
    viewers = get_users_with_role(pdir, "snap1", "viewer")
    assert sorted(viewers) == ["alice", "bob"]


def test_get_users_with_role_empty(pdir):
    assert get_users_with_role(pdir, "snap1", "owner") == []


def test_permissions_persist_across_calls(pdir):
    set_permission(pdir, "snap1", "alice", "editor")
    # Simulate fresh load by calling get without caching
    role = get_permission(pdir, "snap1", "alice")
    assert role == "editor"


def test_remove_last_user_cleans_snapshot_entry(pdir):
    set_permission(pdir, "snap1", "alice", "owner")
    remove_permission(pdir, "snap1", "alice")
    assert list_permissions(pdir, "snap1") == {}


def test_all_valid_roles_accepted(pdir):
    for i, role in enumerate(VALID_ROLES):
        set_permission(pdir, f"snap{i}", "user", role)
        assert get_permission(pdir, f"snap{i}", "user") == role
