"""Compute and verify content checksums for snapshots."""

import hashlib
import json
from pathlib import Path

_CHECKSUM_FILE = "checksums.json"


def _get_checksum_path(store_dir: str) -> Path:
    return Path(store_dir) / _CHECKSUM_FILE


def _load_checksums(store_dir: str) -> dict:
    path = _get_checksum_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_checksums(store_dir: str, data: dict) -> None:
    path = _get_checksum_path(store_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def compute_checksum(variables: dict) -> str:
    """Return a SHA-256 hex digest for the given variables dict."""
    canonical = json.dumps(variables, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def store_checksum(store_dir: str, snapshot_name: str, variables: dict) -> str:
    """Compute and persist the checksum for *snapshot_name*.

    Returns the computed hex digest.
    """
    digest = compute_checksum(variables)
    index = _load_checksums(store_dir)
    index[snapshot_name] = digest
    _save_checksums(store_dir, index)
    return digest


def get_checksum(store_dir: str, snapshot_name: str) -> str | None:
    """Return the stored checksum for *snapshot_name*, or None."""
    return _load_checksums(store_dir).get(snapshot_name)


def verify_checksum(store_dir: str, snapshot_name: str, variables: dict) -> bool:
    """Return True if the stored checksum matches the current variables."""
    stored = get_checksum(store_dir, snapshot_name)
    if stored is None:
        return False
    return stored == compute_checksum(variables)


def remove_checksum(store_dir: str, snapshot_name: str) -> bool:
    """Delete the checksum entry for *snapshot_name*.

    Returns True if an entry existed, False otherwise.
    """
    index = _load_checksums(store_dir)
    if snapshot_name not in index:
        return False
    del index[snapshot_name]
    _save_checksums(store_dir, index)
    return True


def list_checksums(store_dir: str) -> dict:
    """Return all stored {snapshot_name: digest} pairs."""
    return dict(_load_checksums(store_dir))
