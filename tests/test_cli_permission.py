"""Tests for envforge.cli_permission."""

from __future__ import annotations

import argparse
import pytest

from envforge.cli_permission import cmd_permission
from envforge.snapshot_permission import set_permission, get_permission


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"base_dir": None, "perm_cmd": None, "snapshot": "snap1", "user": "alice", "role": "viewer"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def pdir(tmp_path):
    return str(tmp_path)


def test_grant_prints_confirmation(pdir, capsys):
    args = _make_args(perm_cmd="grant", role="editor")
    cmd_permission(args, base_dir=pdir)
    out = capsys.readouterr().out
    assert "Granted" in out
    assert "editor" in out
    assert "alice" in out


def test_grant_persists_permission(pdir, capsys):
    args = _make_args(perm_cmd="grant", role="owner")
    cmd_permission(args, base_dir=pdir)
    assert get_permission(pdir, "snap1", "alice") == "owner"


def test_revoke_existing_prints_confirmation(pdir, capsys):
    set_permission(pdir, "snap1", "alice", "viewer")
    args = _make_args(perm_cmd="revoke")
    cmd_permission(args, base_dir=pdir)
    out = capsys.readouterr().out
    assert "Revoked" in out


def test_revoke_missing_prints_not_found(pdir, capsys):
    args = _make_args(perm_cmd="revoke")
    cmd_permission(args, base_dir=pdir)
    out = capsys.readouterr().out
    assert "No permission found" in out


def test_get_existing_prints_role(pdir, capsys):
    set_permission(pdir, "snap1", "alice", "editor")
    args = _make_args(perm_cmd="get")
    cmd_permission(args, base_dir=pdir)
    out = capsys.readouterr().out
    assert "editor" in out


def test_get_missing_prints_not_found(pdir, capsys):
    args = _make_args(perm_cmd="get")
    cmd_permission(args, base_dir=pdir)
    out = capsys.readouterr().out
    assert "No permission found" in out


def test_list_shows_all_users(pdir, capsys):
    set_permission(pdir, "snap1", "alice", "owner")
    set_permission(pdir, "snap1", "bob", "viewer")
    args = _make_args(perm_cmd="list")
    cmd_permission(args, base_dir=pdir)
    out = capsys.readouterr().out
    assert "alice" in out
    assert "bob" in out


def test_list_empty_prints_no_permissions(pdir, capsys):
    args = _make_args(perm_cmd="list")
    cmd_permission(args, base_dir=pdir)
    out = capsys.readouterr().out
    assert "No permissions" in out
