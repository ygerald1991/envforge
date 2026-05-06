"""Tests for envforge.cli_comment."""

import argparse
import pytest
from envforge.cli_comment import cmd_comment, build_comment_parser
from envforge.snapshot_comment import add_comment, get_comments


@pytest.fixture
def cdir(tmp_path):
    return str(tmp_path)


def _make_args(base_dir, action, snapshot, **kwargs):
    ns = argparse.Namespace(
        base_dir=base_dir,
        comment_action=action,
        snapshot=snapshot,
        **kwargs,
    )
    return ns


def test_add_prints_confirmation(cdir, capsys):
    args = _make_args(cdir, "add", "snap1", author="alice", text="nice")
    cmd_comment(args)
    out = capsys.readouterr().out
    assert "snap1" in out
    assert "added" in out.lower()


def test_add_persists_comment(cdir):
    args = _make_args(cdir, "add", "snap1", author="alice", text="persisted")
    cmd_comment(args)
    comments = get_comments(cdir, "snap1")
    assert any(c["text"] == "persisted" for c in comments)


def test_list_shows_comments(cdir, capsys):
    add_comment(cdir, "snap1", "bob", "check this")
    args = _make_args(cdir, "list", "snap1")
    cmd_comment(args)
    out = capsys.readouterr().out
    assert "bob" in out
    assert "check this" in out


def test_list_empty_shows_no_comments(cdir, capsys):
    args = _make_args(cdir, "list", "empty_snap")
    cmd_comment(args)
    out = capsys.readouterr().out
    assert "no comments" in out


def test_delete_prints_confirmation(cdir, capsys):
    add_comment(cdir, "snap1", "carol", "to remove")
    args = _make_args(cdir, "delete", "snap1", index=0)
    cmd_comment(args)
    out = capsys.readouterr().out
    assert "removed" in out.lower()


def test_delete_invalid_index_prints_message(cdir, capsys):
    add_comment(cdir, "snap1", "carol", "only")
    args = _make_args(cdir, "delete", "snap1", index=99)
    cmd_comment(args)
    out = capsys.readouterr().out
    assert "no comment" in out.lower()


def test_clear_prints_count(cdir, capsys):
    add_comment(cdir, "snap1", "dave", "a")
    add_comment(cdir, "snap1", "dave", "b")
    args = _make_args(cdir, "clear", "snap1")
    cmd_comment(args)
    out = capsys.readouterr().out
    assert "2" in out


def test_build_comment_parser_returns_parser(cdir):
    p = build_comment_parser()
    assert isinstance(p, argparse.ArgumentParser)


def test_unknown_action_prints_message(cdir, capsys):
    args = _make_args(cdir, "bogus", "snap1")
    cmd_comment(args)
    out = capsys.readouterr().out
    assert "unknown" in out.lower()
