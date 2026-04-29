"""Tests for envforge/cli_lock.py"""

import pytest
from types import SimpleNamespace
from envforge.lock import lock_snapshot, is_locked
from envforge.cli_lock import cmd_lock, cmd_unlock, cmd_lock_list


def _make_args(name=None, snapshot_dir=None):
    return SimpleNamespace(name=name, snapshot_dir=snapshot_dir)


@pytest.fixture
def lock_dir(tmp_path):
    return str(tmp_path / "snapshots")


class TestCmdLock:
    def test_prints_confirmation(self, lock_dir, capsys):
        args = _make_args(name="snap1", snapshot_dir=lock_dir)
        cmd_lock(args)
        out = capsys.readouterr().out
        assert "snap1" in out
        assert "Locked" in out

    def test_persists_lock(self, lock_dir):
        args = _make_args(name="snap1", snapshot_dir=lock_dir)
        cmd_lock(args)
        assert is_locked(lock_dir, "snap1")

    def test_already_locked_message(self, lock_dir, capsys):
        lock_snapshot(lock_dir, "snap1")
        args = _make_args(name="snap1", snapshot_dir=lock_dir)
        cmd_lock(args)
        out = capsys.readouterr().out
        assert "already locked" in out


class TestCmdUnlock:
    def test_prints_confirmation(self, lock_dir, capsys):
        lock_snapshot(lock_dir, "snap1")
        args = _make_args(name="snap1", snapshot_dir=lock_dir)
        cmd_unlock(args)
        out = capsys.readouterr().out
        assert "Unlocked" in out
        assert "snap1" in out

    def test_removes_lock(self, lock_dir):
        lock_snapshot(lock_dir, "snap1")
        args = _make_args(name="snap1", snapshot_dir=lock_dir)
        cmd_unlock(args)
        assert not is_locked(lock_dir, "snap1")

    def test_not_locked_message(self, lock_dir, capsys):
        args = _make_args(name="ghost", snapshot_dir=lock_dir)
        cmd_unlock(args)
        out = capsys.readouterr().out
        assert "not locked" in out


class TestCmdLockList:
    def test_empty_message(self, lock_dir, capsys):
        args = _make_args(snapshot_dir=lock_dir)
        cmd_lock_list(args)
        out = capsys.readouterr().out
        assert "No locked" in out

    def test_lists_locked_snapshots(self, lock_dir, capsys):
        lock_snapshot(lock_dir, "snap_a")
        lock_snapshot(lock_dir, "snap_b")
        args = _make_args(snapshot_dir=lock_dir)
        cmd_lock_list(args)
        out = capsys.readouterr().out
        assert "snap_a" in out
        assert "snap_b" in out
