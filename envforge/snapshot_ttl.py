"""TTL (time-to-live) management for snapshots."""

import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

_TTL_INDEX_FILE = "ttl_index.json"


def _get_ttl_index_path(store_dir: str) -> Path:
    return Path(store_dir) / _TTL_INDEX_FILE


def _load_ttl_index(store_dir: str) -> dict:
    path = _get_ttl_index_path(store_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_ttl_index(store_dir: str, index: dict) -> None:
    path = _get_ttl_index_path(store_dir)
    Path(store_dir).mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(index, f, indent=2)


def set_ttl(store_dir: str, snapshot_name: str, seconds: int) -> datetime:
    """Set a TTL for a snapshot. Returns the expiry datetime."""
    if seconds <= 0:
        raise ValueError("TTL must be a positive number of seconds.")
    index = _load_ttl_index(store_dir)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=seconds)
    index[snapshot_name] = expires_at.isoformat()
    _save_ttl_index(store_dir, index)
    return expires_at


def remove_ttl(store_dir: str, snapshot_name: str) -> bool:
    """Remove TTL for a snapshot. Returns True if it existed."""
    index = _load_ttl_index(store_dir)
    if snapshot_name in index:
        del index[snapshot_name]
        _save_ttl_index(store_dir, index)
        return True
    return False


def get_ttl(store_dir: str, snapshot_name: str) -> Optional[datetime]:
    """Return expiry datetime for a snapshot, or None if no TTL is set."""
    index = _load_ttl_index(store_dir)
    raw = index.get(snapshot_name)
    if raw is None:
        return None
    return datetime.fromisoformat(raw)


def is_expired(store_dir: str, snapshot_name: str) -> bool:
    """Return True if the snapshot TTL has passed."""
    expiry = get_ttl(store_dir, snapshot_name)
    if expiry is None:
        return False
    return datetime.now(timezone.utc) >= expiry


def get_expired_snapshots(store_dir: str) -> list:
    """Return list of snapshot names whose TTL has expired."""
    index = _load_ttl_index(store_dir)
    now = datetime.now(timezone.utc)
    return [
        name
        for name, raw in index.items()
        if datetime.fromisoformat(raw) <= now
    ]
