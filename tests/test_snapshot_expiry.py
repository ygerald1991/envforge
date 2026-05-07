"""Tests for envforge.snapshot_expiry."""

import pytest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from envforge.snapshot_expiry import (
    set_expiry,
    get_expiry,
    remove_expiry,
    is_expired,
    list_expired,
)


@pytest.fixture()
def edir(tmp_path: Path) -> str:
    return str(tmp_path / "expiry_store")


def _future(days: int = 1) -> datetime:
    return datetime.now(tz=timezone.utc) + timedelta(days=days)


def _past(days: int = 1) -> datetime:
    return datetime.now(tz=timezone.utc) - timedelta(days=days)


def test_set_and_get_expiry(edir):
    dt = _future()
    iso = set_expiry(edir, "snap1", dt)
    result = get_expiry(edir, "snap1")
    assert result is not None
    assert result.tzinfo is not None
    assert iso == result.isoformat()


def test_get_missing_expiry_returns_none(edir):
    assert get_expiry(edir, "nonexistent") is None


def test_overwrite_existing_expiry(edir):
    set_expiry(edir, "snap1", _future(1))
    new_dt = _future(5)
    set_expiry(edir, "snap1", new_dt)
    result = get_expiry(edir, "snap1")
    assert abs((result - new_dt).total_seconds()) < 1


def test_remove_existing_expiry(edir):
    set_expiry(edir, "snap1", _future())
    removed = remove_expiry(edir, "snap1")
    assert removed is True
    assert get_expiry(edir, "snap1") is None


def test_remove_missing_expiry_returns_false(edir):
    assert remove_expiry(edir, "ghost") is False


def test_is_expired_false_for_future(edir):
    set_expiry(edir, "snap1", _future())
    assert is_expired(edir, "snap1") is False


def test_is_expired_true_for_past(edir):
    set_expiry(edir, "snap1", _past())
    assert is_expired(edir, "snap1") is True


def test_is_expired_false_when_no_expiry_set(edir):
    assert is_expired(edir, "snap_no_expiry") is False


def test_list_expired_returns_only_past(edir):
    set_expiry(edir, "old", _past(2))
    set_expiry(edir, "fresh", _future(2))
    expired = list_expired(edir)
    assert "old" in expired
    assert "fresh" not in expired


def test_list_expired_empty_store(edir):
    assert list_expired(edir) == []


def test_naive_datetime_is_treated_as_utc(edir):
    naive = datetime(2000, 1, 1)  # no tzinfo
    set_expiry(edir, "snap1", naive)
    result = get_expiry(edir, "snap1")
    assert result.tzinfo is not None
    assert is_expired(edir, "snap1") is True


def test_persists_multiple_snapshots(edir):
    set_expiry(edir, "a", _future(1))
    set_expiry(edir, "b", _past(1))
    set_expiry(edir, "c", _future(3))
    assert get_expiry(edir, "a") is not None
    assert get_expiry(edir, "b") is not None
    assert get_expiry(edir, "c") is not None
    assert list_expired(edir) == ["b"]
