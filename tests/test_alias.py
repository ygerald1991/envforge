"""Tests for envforge.alias."""

from __future__ import annotations

import pytest

from envforge import alias as _alias


@pytest.fixture()
def adir(tmp_path):
    return str(tmp_path / "snaps")


class TestSetAlias:
    def test_creates_mapping(self, adir):
        _alias.set_alias(adir, "prod", "snap_prod_2024")
        assert _alias.resolve_alias(adir, "prod") == "snap_prod_2024"

    def test_overwrites_existing(self, adir):
        _alias.set_alias(adir, "prod", "old_snap")
        _alias.set_alias(adir, "prod", "new_snap")
        assert _alias.resolve_alias(adir, "prod") == "new_snap"

    def test_multiple_aliases(self, adir):
        _alias.set_alias(adir, "dev", "snap_dev")
        _alias.set_alias(adir, "staging", "snap_staging")
        assert _alias.resolve_alias(adir, "dev") == "snap_dev"
        assert _alias.resolve_alias(adir, "staging") == "snap_staging"

    def test_persists_to_disk(self, adir):
        _alias.set_alias(adir, "ci", "snap_ci_001")
        # reload from disk
        result = _alias._load_aliases(adir)
        assert result["ci"] == "snap_ci_001"


class TestRemoveAlias:
    def test_removes_existing(self, adir):
        _alias.set_alias(adir, "prod", "snap_prod")
        removed = _alias.remove_alias(adir, "prod")
        assert removed is True
        assert _alias.resolve_alias(adir, "prod") is None

    def test_returns_false_for_missing(self, adir):
        assert _alias.remove_alias(adir, "nonexistent") is False

    def test_does_not_affect_other_aliases(self, adir):
        _alias.set_alias(adir, "a", "snap_a")
        _alias.set_alias(adir, "b", "snap_b")
        _alias.remove_alias(adir, "a")
        assert _alias.resolve_alias(adir, "b") == "snap_b"


class TestResolveAlias:
    def test_returns_none_when_missing(self, adir):
        assert _alias.resolve_alias(adir, "ghost") is None

    def test_returns_snapshot_name(self, adir):
        _alias.set_alias(adir, "latest", "snap_latest")
        assert _alias.resolve_alias(adir, "latest") == "snap_latest"


class TestListAliases:
    def test_empty_when_none_defined(self, adir):
        assert _alias.list_aliases(adir) == {}

    def test_returns_all_aliases(self, adir):
        _alias.set_alias(adir, "x", "snap_x")
        _alias.set_alias(adir, "y", "snap_y")
        result = _alias.list_aliases(adir)
        assert result == {"x": "snap_x", "y": "snap_y"}

    def test_returns_copy(self, adir):
        _alias.set_alias(adir, "z", "snap_z")
        result = _alias.list_aliases(adir)
        result["z"] = "tampered"
        assert _alias.resolve_alias(adir, "z") == "snap_z"


class TestGetAliasesForSnapshot:
    def test_finds_single_alias(self, adir):
        _alias.set_alias(adir, "prod", "snap_001")
        assert _alias.get_aliases_for_snapshot(adir, "snap_001") == ["prod"]

    def test_finds_multiple_aliases(self, adir):
        _alias.set_alias(adir, "prod", "snap_001")
        _alias.set_alias(adir, "live", "snap_001")
        result = _alias.get_aliases_for_snapshot(adir, "snap_001")
        assert sorted(result) == ["live", "prod"]

    def test_returns_empty_for_unknown_snapshot(self, adir):
        assert _alias.get_aliases_for_snapshot(adir, "no_such_snap") == []
