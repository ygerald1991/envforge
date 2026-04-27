"""Tests for envforge.cli_tag module."""

import argparse
import sys

import pytest

from envforge.cli_tag import cmd_tag
from envforge.tag import add_tag


def _make_args(tag_dir, tag_action, **kwargs):
    ns = argparse.Namespace(snapshot_dir=tag_dir, tag_action=tag_action)
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


@pytest.fixture
def tag_dir(tmp_path):
    return str(tmp_path / "snapshots")


class TestCmdTagAdd:
    def test_add_prints_confirmation(self, tag_dir, capsys):
        args = _make_args(tag_dir, "add", snapshot="snap1", tag="prod")
        cmd_tag(args)
        out = capsys.readouterr().out
        assert "snap1" in out
        assert "prod" in out


class TestCmdTagRemove:
    def test_remove_existing_tag(self, tag_dir, capsys):
        add_tag("snap1", "dev", tag_dir)
        args = _make_args(tag_dir, "remove", snapshot="snap1", tag="dev")
        cmd_tag(args)
        out = capsys.readouterr().out
        assert "Removed" in out

    def test_remove_missing_tag_exits(self, tag_dir):
        args = _make_args(tag_dir, "remove", snapshot="snap1", tag="ghost")
        with pytest.raises(SystemExit):
            cmd_tag(args)


class TestCmdTagList:
    def test_list_empty(self, tag_dir, capsys):
        args = _make_args(tag_dir, "list")
        cmd_tag(args)
        out = capsys.readouterr().out
        assert "No tags" in out

    def test_list_shows_tags(self, tag_dir, capsys):
        add_tag("snap1", "alpha", tag_dir)
        add_tag("snap2", "beta", tag_dir)
        args = _make_args(tag_dir, "list")
        cmd_tag(args)
        out = capsys.readouterr().out
        assert "alpha" in out
        assert "beta" in out


class TestCmdTagFind:
    def test_find_returns_snapshots(self, tag_dir, capsys):
        add_tag("snap1", "release", tag_dir)
        args = _make_args(tag_dir, "find", tag="release")
        cmd_tag(args)
        out = capsys.readouterr().out
        assert "snap1" in out

    def test_find_no_match(self, tag_dir, capsys):
        args = _make_args(tag_dir, "find", tag="unknown")
        cmd_tag(args)
        out = capsys.readouterr().out
        assert "No snapshots" in out


class TestCmdTagShow:
    def test_show_tags_for_snapshot(self, tag_dir, capsys):
        add_tag("snap1", "prod", tag_dir)
        add_tag("snap1", "v2", tag_dir)
        args = _make_args(tag_dir, "show", snapshot="snap1")
        cmd_tag(args)
        out = capsys.readouterr().out
        assert "prod" in out
        assert "v2" in out

    def test_show_no_tags(self, tag_dir, capsys):
        args = _make_args(tag_dir, "show", snapshot="untagged")
        cmd_tag(args)
        out = capsys.readouterr().out
        assert "No tags" in out
