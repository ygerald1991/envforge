"""Tests for envforge/lock.py"""

import pytest
from pathlib import Path
from envforge.lock import (
    lock_snapshot,
    unlock_snapshot,
    is_locked,
    list_locked,
    assert_not_locked,
)


@pytest.fixture
def lock_dir(tmp_path):
    return str(tmp_path / "snapshots")


class TestLockSnapshot:
    def test_lock_creates_entry(self, lock_dir):
        lock_snapshot(lock_dir, "snap1")
        assert is_locked(lock_dir, "snap1")

    def test_lock_multiple_snapshots(self, lock_dir):
        lock_snapshot(lock_dir, "snap1")
        lock_snapshot(lock_dir, "snap2")
        assert is_locked(lock_dir, "snap1")
        assert is_locked(lock_dir, "snap2")

    def test_duplicate_lock_is_idempotent(self, lock_dir):
        lock_snapshot(lock_dir, "snap1")
        lock_snapshot(lock_dir, "snap1")
        assert list_locked(lock_dir).count("snap1") == 1

    def test_unlocked_snapshot_is_not_locked(self, lock_dir):
        assert not is_locked(lock_dir, "nonexistent")


class TestUnlockSnapshot:
    def test_unlock_removes_entry(self, lock_dir):
        lock_snapshot(lock_dir, "snap1")
        unlock_snapshot(lock_dir, "snap1")
        assert not is_locked(lock_dir, "snap1")

    def test_unlock_nonexistent_is_safe(self, lock_dir):
        unlock_snapshot(lock_dir, "ghost")  # should not raise

    def test_unlock_only_removes_target(self, lock_dir):
        lock_snapshot(lock_dir, "snap1")
        lock_snapshot(lock_dir, "snap2")
        unlock_snapshot(lock_dir, "snap1")
        assert not is_locked(lock_dir, "snap1")
        assert is_locked(lock_dir, "snap2")


class TestListLocked:
    def test_empty_when_none_locked(self, lock_dir):
        assert list_locked(lock_dir) == []

    def test_returns_all_locked(self, lock_dir):
        lock_snapshot(lock_dir, "a")
        lock_snapshot(lock_dir, "b")
        result = list_locked(lock_dir)
        assert set(result) == {"a", "b"}


class TestAssertNotLocked:
    def test_raises_when_locked(self, lock_dir):
        lock_snapshot(lock_dir, "snap1")
        with pytest.raises(RuntimeError, match="locked"):
            assert_not_locked(lock_dir, "snap1")

    def test_passes_when_not_locked(self, lock_dir):
        assert_not_locked(lock_dir, "snap1")  # should not raise

    def test_error_message_contains_name(self, lock_dir):
        lock_snapshot(lock_dir, "my_snap")
        with pytest.raises(RuntimeError, match="my_snap"):
            assert_not_locked(lock_dir, "my_snap")
