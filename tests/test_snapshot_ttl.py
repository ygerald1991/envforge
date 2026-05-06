"""Tests for envforge.snapshot_ttl."""

import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path

from envforge.snapshot_ttl import (
    set_ttl,
    remove_ttl,
    get_ttl,
    is_expired,
    get_expired_snapshots,
)


@pytest.fixture
def tdir(tmp_path):
    return str(tmp_path)


def test_set_ttl_returns_future_datetime(tdir):
    expiry = set_ttl(tdir, "snap1", 3600)
    assert isinstance(expiry, datetime)
    assert expiry > datetime.now(timezone.utc)


def test_set_ttl_persists_to_index(tdir):
    set_ttl(tdir, "snap1", 3600)
    loaded = get_ttl(tdir, "snap1")
    assert loaded is not None
    assert loaded > datetime.now(timezone.utc)


def test_get_ttl_missing_returns_none(tdir):
    result = get_ttl(tdir, "nonexistent")
    assert result is None


def test_set_ttl_zero_raises(tdir):
    with pytest.raises(ValueError, match="positive"):
        set_ttl(tdir, "snap1", 0)


def test_set_ttl_negative_raises(tdir):
    with pytest.raises(ValueError):
        set_ttl(tdir, "snap1", -10)


def test_is_expired_false_for_future_ttl(tdir):
    set_ttl(tdir, "snap1", 9999)
    assert is_expired(tdir, "snap1") is False


def test_is_expired_true_for_past_ttl(tdir):
    # Manually inject a past expiry
    import json
    from envforge.snapshot_ttl import _get_ttl_index_path
    past = (datetime.now(timezone.utc) - timedelta(seconds=10)).isoformat()
    index_path = _get_ttl_index_path(tdir)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w") as f:
        json.dump({"old_snap": past}, f)
    assert is_expired(tdir, "old_snap") is True


def test_is_expired_false_when_no_ttl(tdir):
    assert is_expired(tdir, "no_ttl_snap") is False


def test_remove_ttl_returns_true_when_exists(tdir):
    set_ttl(tdir, "snap1", 3600)
    result = remove_ttl(tdir, "snap1")
    assert result is True
    assert get_ttl(tdir, "snap1") is None


def test_remove_ttl_returns_false_when_missing(tdir):
    result = remove_ttl(tdir, "ghost")
    assert result is False


def test_get_expired_snapshots_returns_expired_only(tdir):
    import json
    from envforge.snapshot_ttl import _get_ttl_index_path
    now = datetime.now(timezone.utc)
    past = (now - timedelta(seconds=5)).isoformat()
    future = (now + timedelta(seconds=9999)).isoformat()
    index_path = _get_ttl_index_path(tdir)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w") as f:
        json.dump({"expired_snap": past, "live_snap": future}, f)
    expired = get_expired_snapshots(tdir)
    assert "expired_snap" in expired
    assert "live_snap" not in expired


def test_get_expired_snapshots_empty_store(tdir):
    result = get_expired_snapshots(tdir)
    assert result == []


def test_overwrite_ttl(tdir):
    set_ttl(tdir, "snap1", 60)
    first = get_ttl(tdir, "snap1")
    set_ttl(tdir, "snap1", 7200)
    second = get_ttl(tdir, "snap1")
    assert second > first
