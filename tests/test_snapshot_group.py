"""Tests for envforge.snapshot_group and envforge.cli_group."""

import argparse
import pytest
from pathlib import Path
from envforge.snapshot_group import (
    create_group,
    add_to_group,
    remove_from_group,
    delete_group,
    get_group,
    list_groups,
)
from envforge.cli_group import cmd_group


@pytest.fixture
def gdir(tmp_path):
    return str(tmp_path)


def _args(gdir, group_action, **kwargs):
    ns = argparse.Namespace(base_dir=gdir, group_action=group_action, **kwargs)
    return ns


# ── snapshot_group unit tests ────────────────────────────────────────────────

class TestCreateGroup:
    def test_creates_group(self, gdir):
        create_group(gdir, "prod", ["snap1", "snap2"])
        assert get_group(gdir, "prod") == ["snap1", "snap2"]

    def test_replaces_existing_group(self, gdir):
        create_group(gdir, "prod", ["snap1"])
        create_group(gdir, "prod", ["snap2", "snap3"])
        assert get_group(gdir, "prod") == ["snap2", "snap3"]

    def test_empty_snapshot_list(self, gdir):
        create_group(gdir, "empty", [])
        assert get_group(gdir, "empty") == []


class TestAddToGroup:
    def test_adds_snapshot(self, gdir):
        create_group(gdir, "dev", ["snap1"])
        add_to_group(gdir, "dev", "snap2")
        assert "snap2" in get_group(gdir, "dev")

    def test_creates_group_if_absent(self, gdir):
        add_to_group(gdir, "newgroup", "snap1")
        assert get_group(gdir, "newgroup") == ["snap1"]

    def test_no_duplicate_entries(self, gdir):
        create_group(gdir, "dev", ["snap1"])
        add_to_group(gdir, "dev", "snap1")
        assert get_group(gdir, "dev").count("snap1") == 1


class TestRemoveFromGroup:
    def test_removes_snapshot(self, gdir):
        create_group(gdir, "dev", ["snap1", "snap2"])
        result = remove_from_group(gdir, "dev", "snap1")
        assert result is True
        assert "snap1" not in get_group(gdir, "dev")

    def test_returns_false_when_not_present(self, gdir):
        create_group(gdir, "dev", ["snap1"])
        result = remove_from_group(gdir, "dev", "ghost")
        assert result is False


class TestDeleteGroup:
    def test_deletes_group(self, gdir):
        create_group(gdir, "staging", ["s1"])
        assert delete_group(gdir, "staging") is True
        assert get_group(gdir, "staging") is None

    def test_returns_false_for_missing_group(self, gdir):
        assert delete_group(gdir, "nonexistent") is False


class TestListGroups:
    def test_returns_all_groups(self, gdir):
        create_group(gdir, "a", ["s1"])
        create_group(gdir, "b", ["s2", "s3"])
        groups = list_groups(gdir)
        assert "a" in groups and "b" in groups

    def test_empty_when_no_groups(self, gdir):
        assert list_groups(gdir) == {}


# ── cli_group tests ──────────────────────────────────────────────────────────

def test_cmd_create_prints_confirmation(gdir, capsys):
    cmd_group(_args(gdir, "create", name="prod", snapshots=["s1", "s2"]))
    out = capsys.readouterr().out
    assert "prod" in out and "2" in out


def test_cmd_add_prints_confirmation(gdir, capsys):
    create_group(gdir, "dev", [])
    cmd_group(_args(gdir, "add", name="dev", snapshot="s1"))
    out = capsys.readouterr().out
    assert "s1" in out and "dev" in out


def test_cmd_show_lists_members(gdir, capsys):
    create_group(gdir, "dev", ["alpha", "beta"])
    cmd_group(_args(gdir, "show", name="dev"))
    out = capsys.readouterr().out
    assert "alpha" in out and "beta" in out


def test_cmd_list_shows_all_groups(gdir, capsys):
    create_group(gdir, "g1", ["s1"])
    create_group(gdir, "g2", ["s2"])
    cmd_group(_args(gdir, "list"))
    out = capsys.readouterr().out
    assert "g1" in out and "g2" in out


def test_cmd_delete_removes_group(gdir, capsys):
    create_group(gdir, "old", ["s1"])
    cmd_group(_args(gdir, "delete", name="old"))
    assert get_group(gdir, "old") is None
