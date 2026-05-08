"""Tests for envforge.cli_quota."""

from __future__ import annotations

import argparse
import pytest

from envforge.cli_quota import cmd_quota
from envforge.snapshot_quota import set_quota


@pytest.fixture()
def qdir(tmp_path):
    return str(tmp_path)


def _make_args(store_dir, quota_action, **kwargs):
    ns = argparse.Namespace(store_dir=store_dir, quota_action=quota_action)
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_set_prints_confirmation(qdir, capsys):
    args = _make_args(qdir, "set", limit=10, namespace=None)
    cmd_quota(args)
    out = capsys.readouterr().out
    assert "global" in out
    assert "10" in out


def test_set_with_namespace_prints_confirmation(qdir, capsys):
    args = _make_args(qdir, "set", limit=5, namespace="staging")
    cmd_quota(args)
    out = capsys.readouterr().out
    assert "staging" in out
    assert "5" in out


def test_get_existing_quota(qdir, capsys):
    set_quota(qdir, 8)
    args = _make_args(qdir, "get", namespace=None)
    cmd_quota(args)
    out = capsys.readouterr().out
    assert "8" in out


def test_get_missing_quota(qdir, capsys):
    args = _make_args(qdir, "get", namespace=None)
    cmd_quota(args)
    out = capsys.readouterr().out
    assert "No quota" in out


def test_remove_existing_quota(qdir, capsys):
    set_quota(qdir, 10)
    args = _make_args(qdir, "remove", namespace=None)
    cmd_quota(args)
    out = capsys.readouterr().out
    assert "removed" in out.lower()


def test_remove_missing_quota(qdir, capsys):
    args = _make_args(qdir, "remove", namespace=None)
    cmd_quota(args)
    out = capsys.readouterr().out
    assert "No quota found" in out


def test_list_empty(qdir, capsys):
    args = _make_args(qdir, "list")
    cmd_quota(args)
    out = capsys.readouterr().out
    assert "No quotas" in out


def test_list_shows_entries(qdir, capsys):
    set_quota(qdir, 10)
    set_quota(qdir, 3, namespace="dev")
    args = _make_args(qdir, "list")
    cmd_quota(args)
    out = capsys.readouterr().out
    assert "__global__" in out
    assert "dev" in out


def test_check_within_quota(qdir, capsys):
    set_quota(qdir, 10)
    args = _make_args(qdir, "check", count=5, namespace=None)
    cmd_quota(args)
    out = capsys.readouterr().out
    assert "within quota" in out


def test_check_exceeds_quota(qdir, capsys):
    set_quota(qdir, 3)
    args = _make_args(qdir, "check", count=3, namespace=None)
    cmd_quota(args)
    out = capsys.readouterr().out
    assert "EXCEEDS quota" in out
