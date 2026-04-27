"""Tests for envforge.cli_validate."""

import json
import os
import sys
from pathlib import Path

import pytest

from envforge.cli_validate import cmd_validate


def _make_args(snap_dir, name, require=None, forbid=None, pattern=None):
    class Args:
        snapshot_dir = str(snap_dir)
        pass

    a = Args()
    a.name = name
    a.require = require
    a.forbid = forbid
    a.pattern = pattern
    return a


def _write_snapshot(snap_dir: Path, name: str, vars_: dict) -> None:
    snap_dir.mkdir(parents=True, exist_ok=True)
    data = {"name": name, "timestamp": "2024-01-01T00:00:00", "vars": vars_}
    (snap_dir / f"{name}.json").write_text(json.dumps(data))


@pytest.fixture
def snap_dir(tmp_path):
    return tmp_path / "snapshots"


class TestCmdValidate:
    def test_passes_when_all_rules_met(self, snap_dir, capsys):
        _write_snapshot(snap_dir, "prod", {"DB_URL": "postgres://", "PORT": "5432"})
        args = _make_args(snap_dir, "prod", require=["DB_URL"], pattern=["PORT=\\d+"])
        cmd_validate(args)  # should not raise
        out = capsys.readouterr().out
        assert "passed" in out

    def test_exits_2_on_missing_required(self, snap_dir):
        _write_snapshot(snap_dir, "dev", {"A": "1"})
        args = _make_args(snap_dir, "dev", require=["MISSING_KEY"])
        with pytest.raises(SystemExit) as exc:
            cmd_validate(args)
        assert exc.value.code == 2

    def test_exits_2_on_forbidden_present(self, snap_dir):
        _write_snapshot(snap_dir, "dev", {"SECRET": "oops"})
        args = _make_args(snap_dir, "dev", forbid=["SECRET"])
        with pytest.raises(SystemExit) as exc:
            cmd_validate(args)
        assert exc.value.code == 2

    def test_exits_2_on_pattern_failure(self, snap_dir):
        _write_snapshot(snap_dir, "dev", {"PORT": "not-a-port"})
        args = _make_args(snap_dir, "dev", pattern=["PORT=\\d+"])
        with pytest.raises(SystemExit) as exc:
            cmd_validate(args)
        assert exc.value.code == 2

    def test_missing_snapshot_exits_1(self, snap_dir, capsys):
        snap_dir.mkdir(parents=True, exist_ok=True)
        args = _make_args(snap_dir, "ghost")
        with pytest.raises(SystemExit) as exc:
            cmd_validate(args)
        assert exc.value.code == 1

    def test_bad_pattern_spec_exits_1(self, snap_dir, capsys):
        _write_snapshot(snap_dir, "dev", {"PORT": "8080"})
        args = _make_args(snap_dir, "dev", pattern=["NOEQUALSSIGN"])
        with pytest.raises(SystemExit) as exc:
            cmd_validate(args)
        assert exc.value.code == 1

    def test_no_rules_always_passes(self, snap_dir, capsys):
        _write_snapshot(snap_dir, "staging", {"X": "y"})
        args = _make_args(snap_dir, "staging")
        cmd_validate(args)
        out = capsys.readouterr().out
        assert "passed" in out
