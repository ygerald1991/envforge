"""Tests for envforge CLI commands."""

import os
import json
import pytest
from unittest.mock import patch, MagicMock
from envforge.cli import build_parser, cmd_capture, cmd_list, cmd_diff, cmd_restore


def _write_snapshot(directory: str, name: str, variables: dict):
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"{name}.json")
    with open(path, "w") as f:
        json.dump({"name": name, "variables": variables}, f)


@pytest.fixture
def snap_dir(tmp_path):
    return str(tmp_path)


class TestCmdCapture:
    def test_saves_snapshot_and_prints(self, snap_dir, capsys):
        parser = build_parser()
        args = parser.parse_args(["--dir", snap_dir, "capture", "mysnap"])
        args.func(args)
        out = capsys.readouterr().out
        assert "mysnap" in out
        assert os.path.exists(os.path.join(snap_dir, "mysnap.json"))


class TestCmdList:
    def test_lists_existing_snapshots(self, snap_dir, capsys):
        _write_snapshot(snap_dir, "dev", {})
        _write_snapshot(snap_dir, "prod", {})
        parser = build_parser()
        args = parser.parse_args(["--dir", snap_dir, "list"])
        args.func(args)
        out = capsys.readouterr().out
        assert "dev" in out
        assert "prod" in out

    def test_empty_dir_prints_no_snapshots(self, snap_dir, capsys):
        parser = build_parser()
        args = parser.parse_args(["--dir", snap_dir, "list"])
        args.func(args)
        out = capsys.readouterr().out
        assert "No snapshots found" in out


class TestCmdDiff:
    def test_diff_prints_output(self, snap_dir, capsys):
        _write_snapshot(snap_dir, "a", {"X": "1", "Y": "old"})
        _write_snapshot(snap_dir, "b", {"X": "1", "Y": "new", "Z": "3"})
        parser = build_parser()
        args = parser.parse_args(["--dir", snap_dir, "diff", "a", "b"])
        args.func(args)
        out = capsys.readouterr().out
        assert len(out) > 0


class TestCmdRestore:
    def test_restore_to_process(self, snap_dir, capsys):
        _write_snapshot(snap_dir, "dev", {"MY_VAR": "hello"})
        parser = build_parser()
        args = parser.parse_args(["--dir", snap_dir, "restore", "dev"])
        args.func(args)
        out = capsys.readouterr().out
        assert "Restored" in out
        assert os.environ.get("MY_VAR") == "hello"

    def test_restore_shell_script_printed(self, snap_dir, capsys):
        _write_snapshot(snap_dir, "dev", {"MY_VAR": "hello"})
        parser = build_parser()
        args = parser.parse_args(["--dir", snap_dir, "restore", "dev", "--shell", "bash"])
        args.func(args)
        out = capsys.readouterr().out
        assert "export MY_VAR" in out

    def test_restore_selective_keys(self, snap_dir, capsys):
        _write_snapshot(snap_dir, "dev", {"A": "1", "B": "2", "C": "3"})
        parser = build_parser()
        args = parser.parse_args(["--dir", snap_dir, "restore", "dev", "--keys", "A", "C"])
        args.func(args)
        out = capsys.readouterr().out
        assert "A=1" in out
        assert "C=3" in out
        assert "B=2" not in out
