"""Snapshot signing and verification using HMAC-SHA256."""

import hashlib
import hmac
import json
from pathlib import Path
from typing import Optional


def _get_signature_path(store_dir: str) -> Path:
    return Path(store_dir) / ".signatures.json"


def _load_signatures(store_dir: str) -> dict:
    path = _get_signature_path(store_dir)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_signatures(store_dir: str, data: dict) -> None:
    path = _get_signature_path(store_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _canonical_bytes(snapshot: dict) -> bytes:
    """Produce a stable canonical JSON bytes representation of a snapshot."""
    return json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode()


def sign_snapshot(snapshot: dict, snapshot_name: str, secret: str, store_dir: str) -> str:
    """Sign a snapshot dict with the given secret and persist the signature.

    Returns the hex-encoded HMAC-SHA256 signature.
    """
    canonical = _canonical_bytes(snapshot)
    sig = hmac.new(secret.encode(), canonical, hashlib.sha256).hexdigest()
    sigs = _load_signatures(store_dir)
    sigs[snapshot_name] = sig
    _save_signatures(store_dir, sigs)
    return sig


def verify_snapshot(snapshot: dict, snapshot_name: str, secret: str, store_dir: str) -> bool:
    """Verify a snapshot against its stored signature.

    Returns True if the signature matches, False otherwise.
    Raises KeyError if no signature is stored for the given name.
    """
    sigs = _load_signatures(store_dir)
    if snapshot_name not in sigs:
        raise KeyError(f"No signature found for snapshot '{snapshot_name}'")
    canonical = _canonical_bytes(snapshot)
    expected = hmac.new(secret.encode(), canonical, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sigs[snapshot_name])


def get_signature(snapshot_name: str, store_dir: str) -> Optional[str]:
    """Return the stored signature for a snapshot, or None if absent."""
    return _load_signatures(store_dir).get(snapshot_name)


def remove_signature(snapshot_name: str, store_dir: str) -> bool:
    """Remove the stored signature for a snapshot. Returns True if it existed."""
    sigs = _load_signatures(store_dir)
    if snapshot_name not in sigs:
        return False
    del sigs[snapshot_name]
    _save_signatures(store_dir, sigs)
    return True
