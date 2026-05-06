"""Tests for envforge.cli_webhook."""

from __future__ import annotations

import argparse
import pytest
from envforge.cli_webhook import cmd_webhook, build_webhook_parser
from envforge.snapshot_webhook import register_webhook, list_webhooks


@pytest.fixture
def wdir(tmp_path):
    return str(tmp_path)


def _make_args(wdir, webhook_cmd, **kwargs):
    ns = argparse.Namespace(base_dir=wdir, webhook_cmd=webhook_cmd, **kwargs)
    return ns


def test_add_prints_confirmation(wdir, capsys):
    args = _make_args(wdir, "add", name="slack", url="https://hooks.example.com", events=None)
    cmd_webhook(args)
    out = capsys.readouterr().out
    assert "slack" in out
    assert "registered" in out


def test_add_persists_webhook(wdir):
    args = _make_args(wdir, "add", name="slack", url="https://hooks.example.com", events=None)
    cmd_webhook(args)
    hooks = list_webhooks(wdir)
    assert "slack" in hooks


def test_add_with_custom_events(wdir, capsys):
    args = _make_args(wdir, "add", name="ci", url="https://ci.example.com", events="capture,restore")
    cmd_webhook(args)
    hooks = list_webhooks(wdir)
    assert hooks["ci"]["events"] == ["capture", "restore"]


def test_remove_existing_prints_confirmation(wdir, capsys):
    register_webhook(wdir, "slack", "https://hooks.example.com")
    args = _make_args(wdir, "remove", name="slack")
    cmd_webhook(args)
    out = capsys.readouterr().out
    assert "removed" in out


def test_remove_missing_prints_not_found(wdir, capsys):
    args = _make_args(wdir, "remove", name="ghost")
    cmd_webhook(args)
    out = capsys.readouterr().out
    assert "not found" in out


def test_list_empty_shows_message(wdir, capsys):
    args = _make_args(wdir, "list")
    cmd_webhook(args)
    out = capsys.readouterr().out
    assert "No webhooks" in out


def test_list_shows_registered_hooks(wdir, capsys):
    register_webhook(wdir, "slack", "https://hooks.example.com", events=["capture"])
    args = _make_args(wdir, "list")
    cmd_webhook(args)
    out = capsys.readouterr().out
    assert "slack" in out
    assert "https://hooks.example.com" in out


def test_build_webhook_parser_returns_parser(wdir):
    root = argparse.ArgumentParser()
    subs = root.add_subparsers()
    p = build_webhook_parser(subs)
    assert p is not None
