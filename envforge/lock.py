"""Lock/unlock snapshots to prevent accidental modification or deletion."""

import json
import os
from pathlib import Path
from typing import List


def _get_lock_index_path(snapshot_dir: str) -> Path:
    return Path(snapshot_dir) / ".lock_index.json"


def _load_lock_index(snapshot_dir: str) -> dict:
    path = _get_lock_index_path(snapshot_dir)
    if not path.exists():
        return {"locked": []}
    with open(path, "r") as f:
        return json.load(f)


def _save_lock_index(snapshot_dir: str, index: dict) -> None:
    path = _get_lock_index_path(snapshot_dir)
    Path(snapshot_dir).mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(index, f, indent=2)


def lock_snapshot(snapshot_dir: str, name: str) -> None:
    """Mark a snapshot as locked."""
    index = _load_lock_index(snapshot_dir)
    if name not in index["locked"]:
        index["locked"].append(name)
        _save_lock_index(snapshot_dir, index)


def unlock_snapshot(snapshot_dir: str, name: str) -> None:
    """Remove the lock from a snapshot."""
    index = _load_lock_index(snapshot_dir)
    if name in index["locked"]:
        index["locked"].remove(name)
        _save_lock_index(snapshot_dir, index)


def is_locked(snapshot_dir: str, name: str) -> bool:
    """Return True if the snapshot is locked."""
    index = _load_lock_index(snapshot_dir)
    return name in index["locked"]


def list_locked(snapshot_dir: str) -> List[str]:
    """Return a list of all locked snapshot names."""
    return list(_load_lock_index(snapshot_dir)["locked"])


def assert_not_locked(snapshot_dir: str, name: str) -> None:
    """Raise RuntimeError if the snapshot is locked."""
    if is_locked(snapshot_dir, name):
        raise RuntimeError(
            f"Snapshot '{name}' is locked. Unlock it before modifying or deleting."
        )
