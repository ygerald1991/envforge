"""Tests for envforge.encrypt."""

import json
import pytest
from pathlib import Path

pytest.importorskip("cryptography", reason="cryptography package not installed")

from envforge.encrypt import (
    generate_key,
    encrypt_snapshot,
    decrypt_snapshot,
    save_encrypted_snapshot,
    load_encrypted_snapshot,
)


SAMPLE = {"vars": {"APP_ENV": "prod", "DB_PASS": "s3cr3t"}, "name": "prod"}


def test_generate_key_returns_string():
    key = generate_key()
    assert isinstance(key, str)
    assert len(key) > 0


def test_encrypt_returns_bytes():
    key = generate_key()
    ciphertext = encrypt_snapshot(SAMPLE, key)
    assert isinstance(ciphertext, bytes)


def test_roundtrip_encrypt_decrypt():
    key = generate_key()
    ciphertext = encrypt_snapshot(SAMPLE, key)
    result = decrypt_snapshot(ciphertext, key)
    assert result == SAMPLE


def test_decrypt_with_wrong_key_raises():
    key1 = generate_key()
    key2 = generate_key()
    ciphertext = encrypt_snapshot(SAMPLE, key1)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt_snapshot(ciphertext, key2)


def test_decrypt_corrupted_data_raises():
    key = generate_key()
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt_snapshot(b"notvalidciphertext", key)


def test_save_and_load_encrypted_snapshot(tmp_path):
    key = generate_key()
    dest = tmp_path / "snap.enc"
    save_encrypted_snapshot(SAMPLE, dest, key)
    assert dest.exists()
    loaded = load_encrypted_snapshot(dest, key)
    assert loaded == SAMPLE


def test_load_missing_file_raises(tmp_path):
    key = generate_key()
    with pytest.raises(FileNotFoundError):
        load_encrypted_snapshot(tmp_path / "missing.enc", key)


def test_save_creates_parent_dirs(tmp_path):
    key = generate_key()
    nested = tmp_path / "a" / "b" / "snap.enc"
    save_encrypted_snapshot(SAMPLE, nested, key)
    assert nested.exists()
