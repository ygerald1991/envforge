"""Tests for envforge.cli_deps."""

import argparse
import pytest
from envforge.cli_deps import cmd_deps
from envforge.snapshot_deps import add_dependency, get_dependencies


def _make_args(ddir, deps_action, snapshot=None, depends_on=None):
    args = argparse.Namespace(
        base_dir=ddir,
        deps_action=deps_action,
        snapshot=snapshot,
        depends_on=depends_on,
    )
    return args


@pytest.fixture
def ddir(tmp_path):
    return str(tmp_path)


def test_add_prints_confirmation(ddir, capsys):
    args = _make_args(ddir, "add", snapshot="snap_b", depends_on="snap_a")
    cmd_deps(args)
    out = capsys.readouterr().out
    assert "snap_b" in out
    assert "snap_a" in out


def test_add_persists_dependency(ddir):
    args = _make_args(ddir, "add", snapshot="snap_b", depends_on="snap_a")
    cmd_deps(args)
    assert get_dependencies(ddir, "snap_b") == ["snap_a"]


def test_remove_existing_prints_confirmation(ddir, capsys):
    add_dependency(ddir, "snap_b", "snap_a")
    args = _make_args(ddir, "remove", snapshot="snap_b", depends_on="snap_a")
    cmd_deps(args)
    out = capsys.readouterr().out
    assert "removed" in out.lower()


def test_remove_nonexistent_prints_not_found(ddir, capsys):
    args = _make_args(ddir, "remove", snapshot="snap_b", depends_on="snap_a")
    cmd_deps(args)
    out = capsys.readouterr().out
    assert "No such dependency" in out


def test_list_with_deps(ddir, capsys):
    add_dependency(ddir, "snap_b", "snap_a")
    args = _make_args(ddir, "list", snapshot="snap_b")
    cmd_deps(args)
    out = capsys.readouterr().out
    assert "snap_a" in out


def test_list_no_deps(ddir, capsys):
    args = _make_args(ddir, "list", snapshot="snap_b")
    cmd_deps(args)
    out = capsys.readouterr().out
    assert "no recorded dependencies" in out


def test_dependents_found(ddir, capsys):
    add_dependency(ddir, "snap_b", "snap_a")
    args = _make_args(ddir, "dependents", snapshot="snap_a")
    cmd_deps(args)
    out = capsys.readouterr().out
    assert "snap_b" in out


def test_dependents_none(ddir, capsys):
    args = _make_args(ddir, "dependents", snapshot="snap_a")
    cmd_deps(args)
    out = capsys.readouterr().out
    assert "No snapshots depend" in out


def test_all_empty(ddir, capsys):
    args = _make_args(ddir, "all")
    cmd_deps(args)
    out = capsys.readouterr().out
    assert "No dependencies" in out


def test_all_populated(ddir, capsys):
    add_dependency(ddir, "snap_b", "snap_a")
    args = _make_args(ddir, "all")
    cmd_deps(args)
    out = capsys.readouterr().out
    assert "snap_b" in out
    assert "snap_a" in out
