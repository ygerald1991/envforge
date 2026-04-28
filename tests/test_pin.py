"""Tests for envforge.pin and envforge.cli_pin."""

import argparse
import pytest
from pathlib import Path

from envforge.pin import (
    pin_snapshot,
    unpin_snapshot,
    is_pinned,
    list_pinned,
    _get_pin_index_path,
)
from envforge.cli_pin import cmd_pin


@pytest.fixture()
def pin_dir(tmp_path):
    return str(tmp_path)


def _make_args(pin_dir, action, name=None):
    ns = argparse.Namespace(snapshot_dir=pin_dir, pin_action=action)
    if name is not None:
        ns.name = name
    return ns


class TestPinSnapshot:
    def test_pin_creates_index(self, pin_dir):
        pin_snapshot(pin_dir, "snap1")
        assert _get_pin_index_path(pin_dir).exists()

    def test_pinned_snapshot_is_detected(self, pin_dir):
        pin_snapshot(pin_dir, "snap1")
        assert is_pinned(pin_dir, "snap1")

    def test_unpinned_snapshot_not_detected(self, pin_dir):
        assert not is_pinned(pin_dir, "snap_missing")

    def test_duplicate_pin_is_idempotent(self, pin_dir):
        pin_snapshot(pin_dir, "snap1")
        pin_snapshot(pin_dir, "snap1")
        assert list_pinned(pin_dir).count("snap1") == 1

    def test_unpin_removes_entry(self, pin_dir):
        pin_snapshot(pin_dir, "snap1")
        unpin_snapshot(pin_dir, "snap1")
        assert not is_pinned(pin_dir, "snap1")

    def test_unpin_nonexistent_is_safe(self, pin_dir):
        unpin_snapshot(pin_dir, "ghost")  # should not raise

    def test_list_pinned_returns_all(self, pin_dir):
        pin_snapshot(pin_dir, "a")
        pin_snapshot(pin_dir, "b")
        pins = list_pinned(pin_dir)
        assert "a" in pins
        assert "b" in pins

    def test_list_pinned_empty(self, pin_dir):
        assert list_pinned(pin_dir) == []


class TestCmdPin:
    def test_add_prints_confirmation(self, pin_dir, capsys):
        cmd_pin(_make_args(pin_dir, "add", "snap1"))
        assert "Pinned" in capsys.readouterr().out

    def test_remove_prints_confirmation(self, pin_dir, capsys):
        pin_snapshot(pin_dir, "snap1")
        cmd_pin(_make_args(pin_dir, "remove", "snap1"))
        assert "Unpinned" in capsys.readouterr().out

    def test_remove_not_pinned_warns(self, pin_dir, capsys):
        cmd_pin(_make_args(pin_dir, "remove", "ghost"))
        assert "not pinned" in capsys.readouterr().out

    def test_list_shows_pinned(self, pin_dir, capsys):
        pin_snapshot(pin_dir, "snap_x")
        cmd_pin(_make_args(pin_dir, "list"))
        assert "snap_x" in capsys.readouterr().out

    def test_list_empty_message(self, pin_dir, capsys):
        cmd_pin(_make_args(pin_dir, "list"))
        assert "No pinned" in capsys.readouterr().out

    def test_check_pinned(self, pin_dir, capsys):
        pin_snapshot(pin_dir, "snap1")
        cmd_pin(_make_args(pin_dir, "check", "snap1"))
        assert "pinned" in capsys.readouterr().out

    def test_check_not_pinned(self, pin_dir, capsys):
        cmd_pin(_make_args(pin_dir, "check", "snap1"))
        assert "not pinned" in capsys.readouterr().out
