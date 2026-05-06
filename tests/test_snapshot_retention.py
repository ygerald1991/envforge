"""Tests for envforge.snapshot_retention."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from envforge.snapshot_retention import (
    apply_retention_policy,
    get_retention_policy,
    list_retention_policies,
    remove_retention_policy,
    set_retention_policy,
)


@pytest.fixture()
def rdir(tmp_path: Path) -> str:
    return str(tmp_path)


def _snap(name: str, days_ago: float = 0) -> dict:
    ts = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return {"name": name, "created_at": ts.isoformat()}


# --- set / get ---

def test_set_returns_policy(rdir):
    p = set_retention_policy(rdir, "default", max_count=10)
    assert p["name"] == "default"
    assert p["max_count"] == 10
    assert p["max_age_days"] is None


def test_set_persists_to_file(rdir):
    set_retention_policy(rdir, "prod", max_count=5, max_age_days=30)
    raw = json.loads(Path(rdir, "retention_policies.json").read_text())
    assert "prod" in raw
    assert raw["prod"]["max_age_days"] == 30


def test_get_existing_policy(rdir):
    set_retention_policy(rdir, "ci", max_count=3, max_age_days=7)
    p = get_retention_policy(rdir, "ci")
    assert p is not None
    assert p["max_count"] == 3


def test_get_missing_policy_returns_none(rdir):
    assert get_retention_policy(rdir, "nonexistent") is None


def test_overwrite_existing_policy(rdir):
    set_retention_policy(rdir, "dev", max_count=5)
    set_retention_policy(rdir, "dev", max_count=20, max_age_days=14)
    p = get_retention_policy(rdir, "dev")
    assert p["max_count"] == 20
    assert p["max_age_days"] == 14


# --- validation ---

def test_max_count_zero_raises(rdir):
    with pytest.raises(ValueError, match="max_count"):
        set_retention_policy(rdir, "bad", max_count=0)


def test_max_age_days_zero_raises(rdir):
    with pytest.raises(ValueError, match="max_age_days"):
        set_retention_policy(rdir, "bad", max_count=5, max_age_days=0)


# --- remove ---

def test_remove_existing_returns_true(rdir):
    set_retention_policy(rdir, "tmp", max_count=2)
    assert remove_retention_policy(rdir, "tmp") is True
    assert get_retention_policy(rdir, "tmp") is None


def test_remove_missing_returns_false(rdir):
    assert remove_retention_policy(rdir, "ghost") is False


# --- list ---

def test_list_returns_sorted_by_name(rdir):
    set_retention_policy(rdir, "zebra", max_count=1)
    set_retention_policy(rdir, "alpha", max_count=2)
    policies = list_retention_policies(rdir)
    assert [p["name"] for p in policies] == ["alpha", "zebra"]


def test_list_empty_returns_empty(rdir):
    assert list_retention_policies(rdir) == []


# --- apply ---

def test_apply_prunes_excess_by_count(rdir):
    set_retention_policy(rdir, "small", max_count=2)
    snaps = [_snap(f"s{i}", days_ago=i) for i in range(5)]
    pruned = apply_retention_policy(rdir, "small", snaps)
    assert len(pruned) == 3
    # oldest should be pruned
    assert "s4" in pruned


def test_apply_prunes_by_age(rdir):
    set_retention_policy(rdir, "fresh", max_count=100, max_age_days=5)
    snaps = [_snap("recent", days_ago=1), _snap("old", days_ago=10)]
    pruned = apply_retention_policy(rdir, "fresh", snaps)
    assert pruned == ["old"]


def test_apply_no_pruning_needed(rdir):
    set_retention_policy(rdir, "generous", max_count=10)
    snaps = [_snap(f"s{i}", days_ago=i) for i in range(3)]
    assert apply_retention_policy(rdir, "generous", snaps) == []


def test_apply_unknown_policy_raises(rdir):
    with pytest.raises(KeyError, match="missing"):
        apply_retention_policy(rdir, "missing", [])


def test_apply_no_duplicates_in_pruned(rdir):
    set_retention_policy(rdir, "tight", max_count=1, max_age_days=2)
    snaps = [_snap("new", days_ago=0), _snap("old", days_ago=5)]
    pruned = apply_retention_policy(rdir, "tight", snaps)
    assert len(pruned) == len(set(pruned))
