"""Encryption support for snapshots using Fernet symmetric encryption."""

import os
import json
import base64
from pathlib import Path
from typing import Optional

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:
    Fernet = None  # type: ignore
    InvalidToken = Exception  # type: ignore


def _require_cryptography() -> None:
    if Fernet is None:
        raise ImportError(
            "The 'cryptography' package is required for encryption support. "
            "Install it with: pip install cryptography"
        )


def generate_key() -> str:
    """Generate a new Fernet encryption key and return it as a string."""
    _require_cryptography()
    return Fernet.generate_key().decode()


def encrypt_snapshot(snapshot: dict, key: str) -> bytes:
    """Encrypt a snapshot dict and return ciphertext bytes."""
    _require_cryptography()
    f = Fernet(key.encode() if isinstance(key, str) else key)
    plaintext = json.dumps(snapshot).encode()
    return f.encrypt(plaintext)


def decrypt_snapshot(ciphertext: bytes, key: str) -> dict:
    """Decrypt ciphertext bytes and return the snapshot dict."""
    _require_cryptography()
    f = Fernet(key.encode() if isinstance(key, str) else key)
    try:
        plaintext = f.decrypt(ciphertext)
    except InvalidToken as exc:
        raise ValueError("Decryption failed: invalid key or corrupted data.") from exc
    return json.loads(plaintext.decode())


def save_encrypted_snapshot(snapshot: dict, path: Path, key: str) -> None:
    """Encrypt and write a snapshot to *path* (binary file)."""
    ciphertext = encrypt_snapshot(snapshot, key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(ciphertext)


def load_encrypted_snapshot(path: Path, key: str) -> dict:
    """Read and decrypt a snapshot from *path*."""
    if not path.exists():
        raise FileNotFoundError(f"Encrypted snapshot not found: {path}")
    ciphertext = path.read_bytes()
    return decrypt_snapshot(ciphertext, key)
