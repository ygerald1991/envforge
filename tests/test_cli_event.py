"""Tests for envforge.cli_event."""

from __future__ import annotations

import argparse
import pytest

from envforge.cli_event import cmd_event, build_event_parser
from envforge.snapshot_event import register_hook, get_hooks


@pytest.fixture
def edir(tmp_path):
    return str(tmp_path / "hooks")


def _make_args(edir, event_action, event=None, label=None):
    ns = argparse.Namespace(
        hooks_dir=edir,
        event_action=event_action,
        event=event,
        label=label,
    )
    return ns


class TestCmdEventAdd:
    def test_add_prints_confirmation(self, edir, capsys):
        args = _make_args(edir, "add", event="on_capture", label="alert")
        cmd_event(args)
        out = capsys.readouterr().out
        assert "alert" in out
        assert "on_capture" in out

    def test_add_persists_hook(self, edir):
        args = _make_args(edir, "add", event="on_restore", label="log_it")
        cmd_event(args)
        hooks = get_hooks(edir, event="on_restore")
        assert "log_it" in hooks["on_restore"]


class TestCmdEventRemove:
    def test_remove_existing_prints_confirmation(self, edir, capsys):
        register_hook(edir, "on_delete", "old_hook")
        args = _make_args(edir, "remove", event="on_delete", label="old_hook")
        cmd_event(args)
        out = capsys.readouterr().out
        assert "old_hook" in out
        assert "removed" in out.lower()

    def test_remove_missing_prints_not_found(self, edir, capsys):
        args = _make_args(edir, "remove", event="on_merge", label="ghost")
        cmd_event(args)
        out = capsys.readouterr().out
        assert "not found" in out.lower()


class TestCmdEventList:
    def test_list_shows_hooks(self, edir, capsys):
        register_hook(edir, "on_export", "export_notify")
        args = _make_args(edir, "list", event="on_export")
        cmd_event(args)
        out = capsys.readouterr().out
        assert "export_notify" in out

    def test_list_empty_shows_message(self, edir, capsys):
        args = _make_args(edir, "list")
        cmd_event(args)
        out = capsys.readouterr().out
        assert "No hooks" in out

    def test_list_all_events(self, edir, capsys):
        register_hook(edir, "on_capture", "h1")
        register_hook(edir, "on_restore", "h2")
        args = _make_args(edir, "list")
        cmd_event(args)
        out = capsys.readouterr().out
        assert "h1" in out
        assert "h2" in out


class TestBuildEventParser:
    def test_parser_registers_event_subcommand(self):
        root = argparse.ArgumentParser()
        subs = root.add_subparsers()
        build_event_parser(subs)
        args = root.parse_args(["event", "add", "on_capture", "my_hook"])
        assert args.event_action == "add"
        assert args.event == "on_capture"
        assert args.label == "my_hook"
