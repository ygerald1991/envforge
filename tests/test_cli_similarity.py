"""Tests for envforge.cli_similarity."""

from __future__ import annotations

import json
import os
import types
import pytest

from envforge.cli_similarity import cmd_similarity, build_similarity_parser


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_snapshot(directory: str, name: str, variables: dict) -> None:
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"{name}.json")
    with open(path, "w") as fh:
        json.dump({"name": name, "vars": variables}, fh)


@pytest.fixture()
def snap_dir(tmp_path):
    return str(tmp_path / "snapshots")


def _args(snap_dir, **kwargs):
    ns = types.SimpleNamespace(snapshot_dir=snap_dir, func=cmd_similarity, **kwargs)
    return ns


# ---------------------------------------------------------------------------
# compare sub-command
# ---------------------------------------------------------------------------


def test_compare_prints_key_similarity(snap_dir, capsys):
    _write_snapshot(snap_dir, "a", {"K": "1"})
    _write_snapshot(snap_dir, "b", {"K": "1"})
    args = _args(snap_dir, sub="compare", snapshot_a="a", snapshot_b="b")
    cmd_similarity(args)
    out = capsys.readouterr().out
    assert "Key similarity" in out
    assert "1.0000" in out


def test_compare_prints_value_similarity(snap_dir, capsys):
    _write_snapshot(snap_dir, "a", {"K": "1"})
    _write_snapshot(snap_dir, "b", {"K": "2"})
    args = _args(snap_dir, sub="compare", snapshot_a="a", snapshot_b="b")
    cmd_similarity(args)
    out = capsys.readouterr().out
    assert "Value similarity" in out


# ---------------------------------------------------------------------------
# rank sub-command
# ---------------------------------------------------------------------------


def test_rank_prints_header(snap_dir, capsys):
    _write_snapshot(snap_dir, "ref", {"A": "1", "B": "2"})
    _write_snapshot(snap_dir, "c1", {"A": "1", "B": "2"})
    args = _args(
        snap_dir,
        sub="rank",
        reference="ref",
        against=["c1"],
        mode="value",
    )
    cmd_similarity(args)
    out = capsys.readouterr().out
    assert "ref" in out
    assert "value" in out


def test_rank_shows_candidate_names(snap_dir, capsys):
    _write_snapshot(snap_dir, "ref", {"A": "1"})
    _write_snapshot(snap_dir, "snap_x", {"A": "1"})
    _write_snapshot(snap_dir, "snap_y", {"Z": "9"})
    args = _args(
        snap_dir,
        sub="rank",
        reference="ref",
        against=["snap_x", "snap_y"],
        mode="value",
    )
    cmd_similarity(args)
    out = capsys.readouterr().out
    assert "snap_x" in out
    assert "snap_y" in out


def test_rank_no_candidates_message(snap_dir, capsys):
    _write_snapshot(snap_dir, "ref", {"A": "1"})
    args = _args(
        snap_dir,
        sub="rank",
        reference="ref",
        against=[],
        mode="value",
    )
    cmd_similarity(args)
    out = capsys.readouterr().out
    assert "No candidate" in out


# ---------------------------------------------------------------------------
# Parser smoke test
# ---------------------------------------------------------------------------


def test_build_similarity_parser_returns_parser():
    parser = build_similarity_parser()
    assert parser is not None
