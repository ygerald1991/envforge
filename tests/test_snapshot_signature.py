"""Tests for envforge.snapshot_signature."""

import json
import pytest

from envforge.snapshot_signature import (
    get_signature,
    remove_signature,
    sign_snapshot,
    verify_snapshot,
)

SECRET = "test-secret-key"
SNAPSHOT = {"APP_ENV": "production", "DB_HOST": "db.example.com", "PORT": "5432"}


@pytest.fixture
def sdir(tmp_path):
    return str(tmp_path)


def test_sign_returns_hex_string(sdir):
    sig = sign_snapshot(SNAPSHOT, "snap1", SECRET, sdir)
    assert isinstance(sig, str)
    assert len(sig) == 64  # SHA-256 hex digest length


def test_sign_is_deterministic(sdir):
    sig1 = sign_snapshot(SNAPSHOT, "snap1", SECRET, sdir)
    sig2 = sign_snapshot(SNAPSHOT, "snap1", SECRET, sdir)
    assert sig1 == sig2


def test_sign_differs_for_different_secrets(sdir):
    sig1 = sign_snapshot(SNAPSHOT, "snap1", "secret-a", sdir)
    sig2 = sign_snapshot(SNAPSHOT, "snap1", "secret-b", sdir)
    assert sig1 != sig2


def test_sign_persists_to_file(sdir):
    sig = sign_snapshot(SNAPSHOT, "snap1", SECRET, sdir)
    index_path = (pytest.importorskip("pathlib").Path(sdir) / ".signatures.json")
    data = json.loads(index_path.read_text())
    assert data["snap1"] == sig


def test_verify_valid_signature(sdir):
    sign_snapshot(SNAPSHOT, "snap1", SECRET, sdir)
    assert verify_snapshot(SNAPSHOT, "snap1", SECRET, sdir) is True


def test_verify_wrong_secret_returns_false(sdir):
    sign_snapshot(SNAPSHOT, "snap1", SECRET, sdir)
    assert verify_snapshot(SNAPSHOT, "snap1", "wrong-secret", sdir) is False


def test_verify_tampered_snapshot_returns_false(sdir):
    sign_snapshot(SNAPSHOT, "snap1", SECRET, sdir)
    tampered = dict(SNAPSHOT, APP_ENV="staging")
    assert verify_snapshot(tampered, "snap1", SECRET, sdir) is False


def test_verify_missing_signature_raises_key_error(sdir):
    with pytest.raises(KeyError, match="snap_missing"):
        verify_snapshot(SNAPSHOT, "snap_missing", SECRET, sdir)


def test_get_signature_returns_stored_value(sdir):
    sig = sign_snapshot(SNAPSHOT, "snap1", SECRET, sdir)
    assert get_signature("snap1", sdir) == sig


def test_get_signature_missing_returns_none(sdir):
    assert get_signature("nonexistent", sdir) is None


def test_remove_existing_signature_returns_true(sdir):
    sign_snapshot(SNAPSHOT, "snap1", SECRET, sdir)
    assert remove_signature("snap1", sdir) is True
    assert get_signature("snap1", sdir) is None


def test_remove_missing_signature_returns_false(sdir):
    assert remove_signature("ghost", sdir) is False


def test_multiple_snapshots_signed_independently(sdir):
    snap_a = {"KEY": "alpha"}
    snap_b = {"KEY": "beta"}
    sig_a = sign_snapshot(snap_a, "a", SECRET, sdir)
    sig_b = sign_snapshot(snap_b, "b", SECRET, sdir)
    assert sig_a != sig_b
    assert verify_snapshot(snap_a, "a", SECRET, sdir) is True
    assert verify_snapshot(snap_b, "b", SECRET, sdir) is True
