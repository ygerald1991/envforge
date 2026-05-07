"""Lifecycle state management for snapshots (draft, active, deprecated, archived)."""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List

VALID_STATES = ("draft", "active", "deprecated", "archived")


def _get_lifecycle_path(store_dir: str) -> Path:
    return Path(store_dir) / ".lifecycle.json"


def _load_lifecycle_index(store_dir: str) -> dict:
    path = _get_lifecycle_path(store_dir)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_lifecycle_index(store_dir: str, index: dict) -> None:
    path = _get_lifecycle_path(store_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(index, f, indent=2)


def set_lifecycle_state(store_dir: str, snapshot_name: str, state: str) -> dict:
    """Set the lifecycle state of a snapshot."""
    if state not in VALID_STATES:
        raise ValueError(f"Invalid state '{state}'. Must be one of: {VALID_STATES}")
    index = _load_lifecycle_index(store_dir)
    entry = {
        "state": state,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    index[snapshot_name] = entry
    _save_lifecycle_index(store_dir, index)
    return entry


def get_lifecycle_state(store_dir: str, snapshot_name: str) -> Optional[str]:
    """Return the current lifecycle state of a snapshot, or None if unset."""
    index = _load_lifecycle_index(store_dir)
    entry = index.get(snapshot_name)
    return entry["state"] if entry else None


def list_by_state(store_dir: str, state: str) -> List[str]:
    """Return all snapshot names with the given lifecycle state."""
    if state not in VALID_STATES:
        raise ValueError(f"Invalid state '{state}'. Must be one of: {VALID_STATES}")
    index = _load_lifecycle_index(store_dir)
    return [name for name, entry in index.items() if entry.get("state") == state]


def remove_lifecycle_state(store_dir: str, snapshot_name: str) -> bool:
    """Remove lifecycle state for a snapshot. Returns True if it existed."""
    index = _load_lifecycle_index(store_dir)
    if snapshot_name not in index:
        return False
    del index[snapshot_name]
    _save_lifecycle_index(store_dir, index)
    return True
