"""Tests for envforge.cli_archive."""

import json
import argparse
from pathlib import Path
import pytest

from envforge.cli_archive import cmd_archive, build_archive_parser


@pytest.fixture
def snap_dir(tmp_path):
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


@pytest.fixture
def archive_dir(tmp_path):
    return str(tmp_path / "archives")


def _write_snapshot(snap_dir: Path, name: str, data: dict) -> Path:
    p = snap_dir / name
    p.write_text(json.dumps(data))
    return p


def _args(**kwargs) -> argparse.Namespace:
    defaults = {"archive_dir": ".envforge/archives"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_prints_confirmation(capsys, snap_dir, archive_dir):
    snap = _write_snapshot(snap_dir, "dev.json", {"A": "1"})
    args = _args(archive_sub="add", archive_name="test",
                 snapshot_path=str(snap), archive_dir=archive_dir)
    cmd_archive(args)
    out = capsys.readouterr().out
    assert "dev.json" in out
    assert "test.zip" in out


def test_add_creates_archive_file(snap_dir, archive_dir):
    snap = _write_snapshot(snap_dir, "dev.json", {"A": "1"})
    args = _args(archive_sub="add", archive_name="test",
                 snapshot_path=str(snap), archive_dir=archive_dir)
    cmd_archive(args)
    assert (Path(archive_dir) / "test.zip").exists()


def test_list_shows_snapshots(capsys, snap_dir, archive_dir):
    snap = _write_snapshot(snap_dir, "prod.json", {"ENV": "prod"})
    args_add = _args(archive_sub="add", archive_name="myarchive",
                     snapshot_path=str(snap), archive_dir=archive_dir)
    cmd_archive(args_add)
    args_list = _args(archive_sub="list", archive_name="myarchive",
                      archive_dir=archive_dir)
    cmd_archive(args_list)
    out = capsys.readouterr().out
    assert "prod.json" in out


def test_list_empty_archive_shows_message(capsys, archive_dir):
    args = _args(archive_sub="list", archive_name="ghost", archive_dir=archive_dir)
    cmd_archive(args)
    out = capsys.readouterr().out
    assert "empty" in out or "does not exist" in out


def test_extract_restores_file(snap_dir, archive_dir, tmp_path):
    snap = _write_snapshot(snap_dir, "dev.json", {"K": "v"})
    cmd_archive(_args(archive_sub="add", archive_name="arc",
                      snapshot_path=str(snap), archive_dir=archive_dir))
    dest = str(tmp_path / "out")
    Path(dest).mkdir()
    cmd_archive(_args(archive_sub="extract", archive_name="arc",
                      snapshot_name="dev.json", dest_dir=dest,
                      archive_dir=archive_dir))
    assert (Path(dest) / "dev.json").exists()


def test_delete_prints_confirmation(capsys, snap_dir, archive_dir):
    snap = _write_snapshot(snap_dir, "dev.json", {})
    cmd_archive(_args(archive_sub="add", archive_name="arc",
                      snapshot_path=str(snap), archive_dir=archive_dir))
    cmd_archive(_args(archive_sub="delete", archive_name="arc",
                      archive_dir=archive_dir))
    out = capsys.readouterr().out
    assert "Deleted" in out


def test_delete_missing_archive_prints_not_found(capsys, archive_dir):
    cmd_archive(_args(archive_sub="delete", archive_name="ghost",
                      archive_dir=archive_dir))
    out = capsys.readouterr().out
    assert "not found" in out


def test_build_archive_parser_returns_parser():
    root = argparse.ArgumentParser()
    subs = root.add_subparsers()
    p = build_archive_parser(subs)
    assert p is not None
