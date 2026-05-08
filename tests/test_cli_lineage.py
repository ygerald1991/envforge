"""Tests for envforge.cli_lineage."""

from __future__ import annotations

import argparse
import pytest

from envforge.cli_lineage import build_lineage_parser, cmd_lineage
from envforge.snapshot_lineage import get_descendants, get_lineage


@pytest.fixture()
def ldir(tmp_path):
    return str(tmp_path)


def _make_args(**kwargs):
    defaults = {"lineage_sub": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_fork_prints_confirmation(ldir, capsys):
    args = _make_args(lineage_sub="fork", parent="snap-a", child="snap-b")
    cmd_lineage(args, store_dir=ldir)
    out = capsys.readouterr().out
    assert "snap-b" in out
    assert "snap-a" in out


def test_fork_persists(ldir):
    args = _make_args(lineage_sub="fork", parent="snap-a", child="snap-b")
    cmd_lineage(args, store_dir=ldir)
    entry = get_lineage(ldir, "snap-b")
    assert entry["parent"] == "snap-a"


def test_merge_prints_confirmation(ldir, capsys):
    args = _make_args(lineage_sub="merge", sources=["snap-a", "snap-b"], result="snap-c")
    cmd_lineage(args, store_dir=ldir)
    out = capsys.readouterr().out
    assert "snap-c" in out


def test_merge_persists(ldir):
    args = _make_args(lineage_sub="merge", sources=["snap-a", "snap-b"], result="snap-c")
    cmd_lineage(args, store_dir=ldir)
    entry = get_lineage(ldir, "snap-c")
    assert entry["type"] == "merge"


def test_show_fork(ldir, capsys):
    fork_args = _make_args(lineage_sub="fork", parent="snap-a", child="snap-b")
    cmd_lineage(fork_args, store_dir=ldir)
    show_args = _make_args(lineage_sub="show", snapshot="snap-b")
    cmd_lineage(show_args, store_dir=ldir)
    out = capsys.readouterr().out
    assert "forked from" in out
    assert "snap-a" in out


def test_show_missing(ldir, capsys):
    args = _make_args(lineage_sub="show", snapshot="ghost")
    cmd_lineage(args, store_dir=ldir)
    out = capsys.readouterr().out
    assert "No lineage" in out


def test_descendants_lists_children(ldir, capsys):
    cmd_lineage(_make_args(lineage_sub="fork", parent="snap-a", child="snap-b"), store_dir=ldir)
    cmd_lineage(_make_args(lineage_sub="fork", parent="snap-a", child="snap-c"), store_dir=ldir)
    cmd_lineage(_make_args(lineage_sub="descendants", snapshot="snap-a"), store_dir=ldir)
    out = capsys.readouterr().out
    assert "snap-b" in out
    assert "snap-c" in out


def test_descendants_none(ldir, capsys):
    args = _make_args(lineage_sub="descendants", snapshot="snap-a")
    cmd_lineage(args, store_dir=ldir)
    out = capsys.readouterr().out
    assert "No descendants" in out


def test_remove_existing(ldir, capsys):
    cmd_lineage(_make_args(lineage_sub="fork", parent="snap-a", child="snap-b"), store_dir=ldir)
    cmd_lineage(_make_args(lineage_sub="remove", snapshot="snap-b"), store_dir=ldir)
    out = capsys.readouterr().out
    assert "Removed" in out
    assert get_lineage(ldir, "snap-b") is None


def test_remove_missing(ldir, capsys):
    args = _make_args(lineage_sub="remove", snapshot="ghost")
    cmd_lineage(args, store_dir=ldir)
    out = capsys.readouterr().out
    assert "No lineage record" in out


def test_build_lineage_parser_returns_parser(ldir):
    p = build_lineage_parser()
    assert isinstance(p, argparse.ArgumentParser)
