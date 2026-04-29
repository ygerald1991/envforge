"""Tests for envforge.cli_alias."""

from __future__ import annotations

import argparse
import pytest

from envforge import alias as _alias
from envforge.cli_alias import cmd_alias, build_alias_parser


def _make_args(snapshot_dir, sub, **kwargs):
    ns = argparse.Namespace(snapshot_dir=snapshot_dir, alias_sub=sub, **kwargs)
    return ns


@pytest.fixture()
def adir(tmp_path):
    return str(tmp_path / "snaps")


class TestCmdAliasSet:
    def test_prints_confirmation(self, adir, capsys):
        args = _make_args(adir, "set", alias="prod", snapshot="snap_prod")
        cmd_alias(args)
        out = capsys.readouterr().out
        assert "prod" in out
        assert "snap_prod" in out

    def test_persists_alias(self, adir):
        args = _make_args(adir, "set", alias="dev", snapshot="snap_dev")
        cmd_alias(args)
        assert _alias.resolve_alias(adir, "dev") == "snap_dev"


class TestCmdAliasRemove:
    def test_prints_removed(self, adir, capsys):
        _alias.set_alias(adir, "old", "snap_old")
        args = _make_args(adir, "remove", alias="old")
        cmd_alias(args)
        assert "removed" in capsys.readouterr().out.lower()

    def test_prints_not_found(self, adir, capsys):
        args = _make_args(adir, "remove", alias="ghost")
        cmd_alias(args)
        assert "not found" in capsys.readouterr().out.lower()


class TestCmdAliasResolve:
    def test_prints_snapshot_name(self, adir, capsys):
        _alias.set_alias(adir, "ci", "snap_ci")
        args = _make_args(adir, "resolve", alias="ci")
        cmd_alias(args)
        assert "snap_ci" in capsys.readouterr().out

    def test_prints_not_found_message(self, adir, capsys):
        args = _make_args(adir, "resolve", alias="missing")
        cmd_alias(args)
        assert "missing" in capsys.readouterr().out


class TestCmdAliasList:
    def test_empty_message(self, adir, capsys):
        args = _make_args(adir, "list")
        cmd_alias(args)
        assert "no aliases" in capsys.readouterr().out.lower()

    def test_lists_all(self, adir, capsys):
        _alias.set_alias(adir, "a", "snap_a")
        _alias.set_alias(adir, "b", "snap_b")
        args = _make_args(adir, "list")
        cmd_alias(args)
        out = capsys.readouterr().out
        assert "snap_a" in out
        assert "snap_b" in out


class TestCmdAliasLookup:
    def test_prints_aliases(self, adir, capsys):
        _alias.set_alias(adir, "prod", "snap_001")
        _alias.set_alias(adir, "live", "snap_001")
        args = _make_args(adir, "lookup", snapshot="snap_001")
        cmd_alias(args)
        out = capsys.readouterr().out
        assert "prod" in out
        assert "live" in out

    def test_no_aliases_message(self, adir, capsys):
        args = _make_args(adir, "lookup", snapshot="unknown")
        cmd_alias(args)
        assert "no aliases" in capsys.readouterr().out.lower()


def test_build_alias_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    subs = root.add_subparsers()
    build_alias_parser(subs)
    parsed = root.parse_args(["alias", "list"])
    assert parsed.alias_sub == "list"
