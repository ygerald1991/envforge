"""Tests for envforge.cli_chain."""

from __future__ import annotations

import argparse
import types

import pytest

from envforge.cli_chain import cmd_chain
from envforge.snapshot_chain import get_parent, set_parent


def _make_args(store_dir, chain_sub, snapshot=None, parent=None):
    ns = types.SimpleNamespace(
        store_dir=store_dir,
        chain_sub=chain_sub,
        snapshot=snapshot,
        parent=parent,
    )
    return ns


@pytest.fixture()
def cdir(tmp_path):
    return str(tmp_path)


class TestCmdChainSetParent:
    def test_prints_confirmation(self, cdir, capsys):
        args = _make_args(cdir, "set-parent", snapshot="child", parent="root")
        cmd_chain(args)
        out = capsys.readouterr().out
        assert "child" in out
        assert "root" in out

    def test_persists_relationship(self, cdir):
        args = _make_args(cdir, "set-parent", snapshot="child", parent="root")
        cmd_chain(args)
        assert get_parent(cdir, "child") == "root"


class TestCmdChainParent:
    def test_shows_parent(self, cdir, capsys):
        set_parent(cdir, "child", "root")
        args = _make_args(cdir, "parent", snapshot="child")
        cmd_chain(args)
        assert "root" in capsys.readouterr().out

    def test_no_parent_message(self, cdir, capsys):
        args = _make_args(cdir, "parent", snapshot="orphan")
        cmd_chain(args)
        assert "No parent" in capsys.readouterr().out


class TestCmdChainAncestors:
    def test_lists_ancestors(self, cdir, capsys):
        set_parent(cdir, "c", "b")
        set_parent(cdir, "b", "a")
        args = _make_args(cdir, "ancestors", snapshot="c")
        cmd_chain(args)
        out = capsys.readouterr().out
        assert "b" in out
        assert "a" in out

    def test_no_ancestors_message(self, cdir, capsys):
        args = _make_args(cdir, "ancestors", snapshot="root")
        cmd_chain(args)
        assert "No ancestors" in capsys.readouterr().out


class TestCmdChainChildren:
    def test_lists_children(self, cdir, capsys):
        set_parent(cdir, "child1", "root")
        set_parent(cdir, "child2", "root")
        args = _make_args(cdir, "children", snapshot="root")
        cmd_chain(args)
        out = capsys.readouterr().out
        assert "child1" in out
        assert "child2" in out

    def test_no_children_message(self, cdir, capsys):
        args = _make_args(cdir, "children", snapshot="leaf")
        cmd_chain(args)
        assert "No children" in capsys.readouterr().out


class TestCmdChainRemove:
    def test_remove_prints_confirmation(self, cdir, capsys):
        set_parent(cdir, "snap", "base")
        args = _make_args(cdir, "remove", snapshot="snap")
        cmd_chain(args)
        assert "Removed" in capsys.readouterr().out

    def test_remove_nonexistent_prints_not_found(self, cdir, capsys):
        args = _make_args(cdir, "remove", snapshot="ghost")
        cmd_chain(args)
        assert "not in" in capsys.readouterr().out
