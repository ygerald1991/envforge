"""Tests for envforge.cli_schedule module."""

import argparse
import pytest
from unittest.mock import patch, MagicMock
from envforge.cli_schedule import cmd_schedule, build_schedule_parser
from envforge.schedule import set_schedule, load_schedule


def _make_args(**kwargs):
    defaults = {"dir": ".", "schedule_action": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture
def sched_dir(tmp_path):
    return str(tmp_path)


class TestCmdScheduleSet:
    def test_set_prints_confirmation(self, sched_dir, capsys):
        args = _make_args(schedule_action="set", name="nightly", interval=86400, prefix="auto", dir=sched_dir)
        cmd_schedule(args)
        out = capsys.readouterr().out
        assert "nightly" in out
        assert "86400" in out

    def test_set_persists_entry(self, sched_dir):
        args = _make_args(schedule_action="set", name="ci", interval=600, prefix="ci", dir=sched_dir)
        cmd_schedule(args)
        data = load_schedule(sched_dir)
        assert "ci" in data
        assert data["ci"]["interval_seconds"] == 600


class TestCmdScheduleRemove:
    def test_remove_existing(self, sched_dir, capsys):
        set_schedule("temp", 60, base_dir=sched_dir)
        args = _make_args(schedule_action="remove", name="temp", dir=sched_dir)
        cmd_schedule(args)
        out = capsys.readouterr().out
        assert "removed" in out

    def test_remove_nonexistent(self, sched_dir, capsys):
        args = _make_args(schedule_action="remove", name="ghost", dir=sched_dir)
        cmd_schedule(args)
        out = capsys.readouterr().out
        assert "not found" in out


class TestCmdScheduleList:
    def test_list_empty(self, sched_dir, capsys):
        args = _make_args(schedule_action="list", dir=sched_dir)
        cmd_schedule(args)
        out = capsys.readouterr().out
        assert "No schedules" in out

    def test_list_shows_entries(self, sched_dir, capsys):
        set_schedule("prod", 3600, base_dir=sched_dir)
        args = _make_args(schedule_action="list", dir=sched_dir)
        cmd_schedule(args)
        out = capsys.readouterr().out
        assert "prod" in out
        assert "3600" in out


class TestCmdScheduleRunDue:
    def test_run_due_no_schedules(self, sched_dir, capsys):
        args = _make_args(schedule_action="run-due", dir=sched_dir)
        cmd_schedule(args)
        out = capsys.readouterr().out
        assert "No schedules are due" in out

    def test_run_due_saves_snapshot(self, sched_dir, capsys):
        set_schedule("auto", 3600, base_dir=sched_dir)
        fake_env = {"HOME": "/home/user", "PATH": "/usr/bin"}
        with patch("envforge.cli_schedule.capture_env", return_value=fake_env), \
             patch("envforge.cli_schedule.save_snapshot") as mock_save:
            args = _make_args(schedule_action="run-due", dir=sched_dir)
            cmd_schedule(args)
            assert mock_save.called
        out = capsys.readouterr().out
        assert "auto" in out


def test_build_schedule_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    build_schedule_parser(subparsers)
    args = parser.parse_args(["schedule", "--dir", "/tmp", "list"])
    assert args.schedule_action == "list"
    assert args.dir == "/tmp"
