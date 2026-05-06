"""Tests for envforge.cli_access."""

import argparse
import pytest
from unittest.mock import patch

from envforge.snapshot_access import record_access
from envforge.cli_access import cmd_access, build_access_parser


@pytest.fixture
def adir(tmp_path):
    return str(tmp_path)


def _make_args(adir, access_cmd, snapshot=None):
    ns = argparse.Namespace(base_dir=adir, access_cmd=access_cmd, snapshot=snapshot)
    return ns


def test_log_prints_all_entries(adir, capsys):
    record_access(adir, "snap1", actor="alice")
    record_access(adir, "snap2", actor="bob")
    args = _make_args(adir, "log")
    cmd_access(args)
    out = capsys.readouterr().out
    assert "snap1" in out
    assert "snap2" in out


def test_log_filtered_by_snapshot(adir, capsys):
    record_access(adir, "snap1", actor="alice")
    record_access(adir, "snap2", actor="bob")
    args = _make_args(adir, "log", snapshot="snap1")
    cmd_access(args)
    out = capsys.readouterr().out
    assert "snap1" in out
    assert "snap2" not in out


def test_log_empty_shows_no_records_message(adir, capsys):
    args = _make_args(adir, "log")
    cmd_access(args)
    out = capsys.readouterr().out
    assert "No access records" in out


def test_last_prints_most_recent(adir, capsys):
    record_access(adir, "snap1", actor="first")
    record_access(adir, "snap1", actor="second")
    args = _make_args(adir, "last", snapshot="snap1")
    cmd_access(args)
    out = capsys.readouterr().out
    assert "second" in out
    assert "first" not in out


def test_last_missing_snapshot_prints_message(adir, capsys):
    args = _make_args(adir, "last", snapshot="ghost")
    cmd_access(args)
    out = capsys.readouterr().out
    assert "No access records" in out


def test_last_without_snapshot_prints_error(adir, capsys):
    args = _make_args(adir, "last", snapshot=None)
    cmd_access(args)
    out = capsys.readouterr().out
    assert "Error" in out or "required" in out.lower()


def test_unknown_subcommand_prints_message(adir, capsys):
    args = _make_args(adir, "bogus")
    cmd_access(args)
    out = capsys.readouterr().out
    assert "Unknown" in out


def test_build_access_parser_returns_parser():
    parser = build_access_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_build_access_parser_log_subcommand():
    parser = build_access_parser()
    args = parser.parse_args(["log"])
    assert args.access_cmd == "log"


def test_build_access_parser_last_subcommand():
    parser = build_access_parser()
    args = parser.parse_args(["last", "mysnap"])
    assert args.access_cmd == "last"
    assert args.snapshot == "mysnap"
