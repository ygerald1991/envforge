"""Tests for envforge.cli_ttl."""

import json
import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from types import SimpleNamespace

from envforge.cli_ttl import cmd_ttl
from envforge.snapshot_ttl import _get_ttl_index_path


@pytest.fixture
def tdir(tmp_path):
    return str(tmp_path)


def _make_args(**kwargs):
    defaults = {"ttl_command": None, "snapshot": None, "seconds": None}
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _inject_past_ttl(tdir, name):
    past = (datetime.now(timezone.utc) - timedelta(seconds=30)).isoformat()
    path = _get_ttl_index_path(tdir)
    Path(tdir).mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump({name: past}, f)


def test_set_prints_confirmation(tdir, capsys):
    args = _make_args(ttl_command="set", snapshot="snap1", seconds=3600)
    cmd_ttl(args, store_dir=tdir)
    out = capsys.readouterr().out
    assert "snap1" in out
    assert "expires at" in out


def test_set_persists_ttl(tdir):
    from envforge.snapshot_ttl import get_ttl
    args = _make_args(ttl_command="set", snapshot="snap1", seconds=3600)
    cmd_ttl(args, store_dir=tdir)
    assert get_ttl(tdir, "snap1") is not None


def test_remove_existing_prints_confirmation(tdir, capsys):
    from envforge.snapshot_ttl import set_ttl
    set_ttl(tdir, "snap1", 3600)
    args = _make_args(ttl_command="remove", snapshot="snap1")
    cmd_ttl(args, store_dir=tdir)
    out = capsys.readouterr().out
    assert "removed" in out.lower()


def test_remove_missing_prints_not_found(tdir, capsys):
    args = _make_args(ttl_command="remove", snapshot="ghost")
    cmd_ttl(args, store_dir=tdir)
    out = capsys.readouterr().out
    assert "No TTL" in out


def test_show_active_ttl(tdir, capsys):
    from envforge.snapshot_ttl import set_ttl
    set_ttl(tdir, "snap1", 9999)
    args = _make_args(ttl_command="show", snapshot="snap1")
    cmd_ttl(args, store_dir=tdir)
    out = capsys.readouterr().out
    assert "active" in out
    assert "snap1" in out


def test_show_expired_ttl(tdir, capsys):
    _inject_past_ttl(tdir, "old_snap")
    args = _make_args(ttl_command="show", snapshot="old_snap")
    cmd_ttl(args, store_dir=tdir)
    out = capsys.readouterr().out
    assert "EXPIRED" in out


def test_show_no_ttl(tdir, capsys):
    args = _make_args(ttl_command="show", snapshot="unknown")
    cmd_ttl(args, store_dir=tdir)
    out = capsys.readouterr().out
    assert "No TTL" in out


def test_list_expired_shows_names(tdir, capsys):
    _inject_past_ttl(tdir, "expired_snap")
    args = _make_args(ttl_command="list-expired")
    cmd_ttl(args, store_dir=tdir)
    out = capsys.readouterr().out
    assert "expired_snap" in out


def test_list_expired_empty(tdir, capsys):
    args = _make_args(ttl_command="list-expired")
    cmd_ttl(args, store_dir=tdir)
    out = capsys.readouterr().out
    assert "No expired" in out
