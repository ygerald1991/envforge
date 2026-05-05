"""Tests for envforge.snapshot_labels."""

from __future__ import annotations

import pytest
from envforge.snapshot_labels import (
    set_label,
    remove_label,
    get_labels,
    get_label,
    find_by_label,
    _get_label_index_path,
)


@pytest.fixture()
def ldir(tmp_path):
    return str(tmp_path / "labels_store")


# --- set_label / get_label ---

def test_set_and_get_label(ldir):
    set_label(ldir, "snap1", "env", "production")
    assert get_label(ldir, "snap1", "env") == "production"


def test_get_missing_label_returns_none(ldir):
    assert get_label(ldir, "snap1", "missing") is None


def test_get_labels_empty_returns_empty_dict(ldir):
    assert get_labels(ldir, "snap1") == {}


def test_set_multiple_labels(ldir):
    set_label(ldir, "snap1", "env", "staging")
    set_label(ldir, "snap1", "owner", "alice")
    labels = get_labels(ldir, "snap1")
    assert labels == {"env": "staging", "owner": "alice"}


def test_overwrite_existing_label(ldir):
    set_label(ldir, "snap1", "env", "dev")
    set_label(ldir, "snap1", "env", "prod")
    assert get_label(ldir, "snap1", "env") == "prod"


def test_labels_are_isolated_per_snapshot(ldir):
    set_label(ldir, "snap1", "env", "dev")
    set_label(ldir, "snap2", "env", "prod")
    assert get_label(ldir, "snap1", "env") == "dev"
    assert get_label(ldir, "snap2", "env") == "prod"


# --- remove_label ---

def test_remove_existing_label_returns_true(ldir):
    set_label(ldir, "snap1", "env", "dev")
    result = remove_label(ldir, "snap1", "env")
    assert result is True
    assert get_label(ldir, "snap1", "env") is None


def test_remove_missing_label_returns_false(ldir):
    result = remove_label(ldir, "snap1", "nonexistent")
    assert result is False


def test_remove_last_label_cleans_up_snapshot_entry(ldir):
    set_label(ldir, "snap1", "env", "dev")
    remove_label(ldir, "snap1", "env")
    assert get_labels(ldir, "snap1") == {}


# --- find_by_label ---

def test_find_by_key_only(ldir):
    set_label(ldir, "snap1", "env", "dev")
    set_label(ldir, "snap2", "env", "prod")
    set_label(ldir, "snap3", "owner", "bob")
    results = find_by_label(ldir, "env")
    assert set(results) == {"snap1", "snap2"}


def test_find_by_key_and_value(ldir):
    set_label(ldir, "snap1", "env", "dev")
    set_label(ldir, "snap2", "env", "prod")
    results = find_by_label(ldir, "env", "prod")
    assert results == ["snap2"]


def test_find_returns_empty_when_no_match(ldir):
    assert find_by_label(ldir, "env", "staging") == []


def test_find_returns_sorted(ldir):
    set_label(ldir, "zsnap", "tier", "gold")
    set_label(ldir, "asnap", "tier", "gold")
    results = find_by_label(ldir, "tier")
    assert results == ["asnap", "zsnap"]


# --- persistence ---

def test_index_file_is_created(ldir):
    set_label(ldir, "snap1", "k", "v")
    assert _get_label_index_path(ldir).exists()
