"""Tests for envforge.snapshot_checksum."""

import json
import pytest
from pathlib import Path

from envforge.snapshot_checksum import (
    compute_checksum,
    store_checksum,
    get_checksum,
    verify_checksum,
    remove_checksum,
    list_checksums,
)


@pytest.fixture()
def cdir(tmp_path):
    return str(tmp_path)


SAMPLE = {"APP_ENV": "production", "DB_HOST": "db.prod"}


# --- compute_checksum ---

def test_compute_checksum_returns_hex_string():
    digest = compute_checksum(SAMPLE)
    assert isinstance(digest, str)
    assert len(digest) == 64  # SHA-256 hex


def test_compute_checksum_is_deterministic():
    assert compute_checksum(SAMPLE) == compute_checksum(SAMPLE)


def test_compute_checksum_order_independent():
    a = {"X": "1", "Y": "2"}
    b = {"Y": "2", "X": "1"}
    assert compute_checksum(a) == compute_checksum(b)


def test_compute_checksum_differs_for_different_vars():
    assert compute_checksum({"A": "1"}) != compute_checksum({"A": "2"})


# --- store_checksum / get_checksum ---

def test_store_returns_digest(cdir):
    digest = store_checksum(cdir, "snap1", SAMPLE)
    assert digest == compute_checksum(SAMPLE)


def test_get_returns_stored_digest(cdir):
    store_checksum(cdir, "snap1", SAMPLE)
    assert get_checksum(cdir, "snap1") == compute_checksum(SAMPLE)


def test_get_missing_returns_none(cdir):
    assert get_checksum(cdir, "nonexistent") is None


def test_store_persists_to_file(cdir):
    store_checksum(cdir, "snap1", SAMPLE)
    raw = json.loads(Path(cdir, "checksums.json").read_text())
    assert "snap1" in raw


def test_multiple_snapshots_stored_independently(cdir):
    vars_a = {"K": "a"}
    vars_b = {"K": "b"}
    store_checksum(cdir, "a", vars_a)
    store_checksum(cdir, "b", vars_b)
    assert get_checksum(cdir, "a") == compute_checksum(vars_a)
    assert get_checksum(cdir, "b") == compute_checksum(vars_b)


# --- verify_checksum ---

def test_verify_returns_true_when_unchanged(cdir):
    store_checksum(cdir, "snap1", SAMPLE)
    assert verify_checksum(cdir, "snap1", SAMPLE) is True


def test_verify_returns_false_when_changed(cdir):
    store_checksum(cdir, "snap1", SAMPLE)
    modified = dict(SAMPLE, DB_HOST="other.host")
    assert verify_checksum(cdir, "snap1", modified) is False


def test_verify_returns_false_when_no_checksum_stored(cdir):
    assert verify_checksum(cdir, "snap1", SAMPLE) is False


# --- remove_checksum ---

def test_remove_existing_returns_true(cdir):
    store_checksum(cdir, "snap1", SAMPLE)
    assert remove_checksum(cdir, "snap1") is True


def test_remove_missing_returns_false(cdir):
    assert remove_checksum(cdir, "ghost") is False


def test_remove_deletes_entry(cdir):
    store_checksum(cdir, "snap1", SAMPLE)
    remove_checksum(cdir, "snap1")
    assert get_checksum(cdir, "snap1") is None


# --- list_checksums ---

def test_list_empty_store_returns_empty(cdir):
    assert list_checksums(cdir) == {}


def test_list_returns_all_entries(cdir):
    store_checksum(cdir, "a", {"X": "1"})
    store_checksum(cdir, "b", {"X": "2"})
    result = list_checksums(cdir)
    assert set(result.keys()) == {"a", "b"}
