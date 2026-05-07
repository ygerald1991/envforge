"""Snapshot expiry: mark snapshots with an expiry date and check if they are expired."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_EXPIRY_FILE = "expiry_index.json"


def _get_expiry_path(store_dir: str) -> Path:
    return Path(store_dir) / _EXPIRY_FILE


def _load_expiry_index(store_dir: str) -> dict:
    path = _get_expiry_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_expiry_index(store_dir: str, index: dict) -> None:
    path = _get_expiry_path(store_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index, indent=2))


def set_expiry(store_dir: str, snapshot_name: str, expires_at: datetime) -> str:
    """Assign an expiry datetime (UTC) to a snapshot. Returns ISO string."""
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    iso = expires_at.astimezone(timezone.utc).isoformat()
    index = _load_expiry_index(store_dir)
    index[snapshot_name] = iso
    _save_expiry_index(store_dir, index)
    return iso


def get_expiry(store_dir: str, snapshot_name: str) -> Optional[datetime]:
    """Return the expiry datetime for a snapshot, or None if not set."""
    index = _load_expiry_index(store_dir)
    raw = index.get(snapshot_name)
    if raw is None:
        return None
    return datetime.fromisoformat(raw)


def remove_expiry(store_dir: str, snapshot_name: str) -> bool:
    """Remove expiry from a snapshot. Returns True if it existed."""
    index = _load_expiry_index(store_dir)
    if snapshot_name not in index:
        return False
    del index[snapshot_name]
    _save_expiry_index(store_dir, index)
    return True


def is_expired(store_dir: str, snapshot_name: str) -> bool:
    """Return True if the snapshot has an expiry that is in the past."""
    expiry = get_expiry(store_dir, snapshot_name)
    if expiry is None:
        return False
    now = datetime.now(tz=timezone.utc)
    return now >= expiry


def list_expired(store_dir: str) -> list[str]:
    """Return names of all snapshots whose expiry has passed."""
    index = _load_expiry_index(store_dir)
    now = datetime.now(tz=timezone.utc)
    return [
        name
        for name, iso in index.items()
        if now >= datetime.fromisoformat(iso)
    ]
