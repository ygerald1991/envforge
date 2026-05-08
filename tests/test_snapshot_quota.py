"""Tests for envforge.snapshot_quota."""

from __future__ import annotations

import pytest

from envforge.snapshot_quota import (
    set_quota,
    get_quota,
    remove_quota,
    list_quotas,
    check_quota,
)


@pytest.fixture()
def qdir(tmp_path):
    return str(tmp_path)


def test_set_and_get_quota(qdir):
    entry = set_quota(qdir, 10)
    assert entry["limit"] == 10
    assert entry["namespace"] == "__global__"
    result = get_quota(qdir)
    assert result == entry


def test_set_quota_with_namespace(qdir):
    entry = set_quota(qdir, 5, namespace="staging")
    assert entry["namespace"] == "staging"
    assert entry["limit"] == 5


def test_get_missing_quota_returns_none(qdir):
    assert get_quota(qdir) is None
    assert get_quota(qdir, namespace="prod") is None


def test_overwrite_existing_quota(qdir):
    set_quota(qdir, 10)
    set_quota(qdir, 20)
    assert get_quota(qdir)["limit"] == 20


def test_remove_existing_quota(qdir):
    set_quota(qdir, 10)
    removed = remove_quota(qdir)
    assert removed is True
    assert get_quota(qdir) is None


def test_remove_missing_quota_returns_false(qdir):
    assert remove_quota(qdir) is False


def test_remove_namespace_quota(qdir):
    set_quota(qdir, 3, namespace="dev")
    removed = remove_quota(qdir, namespace="dev")
    assert removed is True
    assert get_quota(qdir, namespace="dev") is None


def test_list_quotas_empty(qdir):
    assert list_quotas(qdir) == []


def test_list_quotas_multiple(qdir):
    set_quota(qdir, 10)
    set_quota(qdir, 5, namespace="staging")
    entries = list_quotas(qdir)
    assert len(entries) == 2
    namespaces = {e["namespace"] for e in entries}
    assert "__global__" in namespaces
    assert "staging" in namespaces


def test_check_quota_within_limit(qdir):
    set_quota(qdir, 10)
    assert check_quota(qdir, 9) is True


def test_check_quota_at_limit_is_exceeded(qdir):
    set_quota(qdir, 10)
    assert check_quota(qdir, 10) is False


def test_check_quota_no_quota_set_always_passes(qdir):
    assert check_quota(qdir, 9999) is True


def test_check_quota_falls_back_to_global(qdir):
    set_quota(qdir, 3)
    # namespace "prod" has no specific quota → should use global
    assert check_quota(qdir, 2, namespace="prod") is True
    assert check_quota(qdir, 3, namespace="prod") is False


def test_invalid_limit_raises(qdir):
    with pytest.raises(ValueError):
        set_quota(qdir, 0)
    with pytest.raises(ValueError):
        set_quota(qdir, -5)


def test_persists_to_file(qdir):
    set_quota(qdir, 7, namespace="ci")
    # reload by calling get again (reads from disk)
    result = get_quota(qdir, namespace="ci")
    assert result["limit"] == 7
