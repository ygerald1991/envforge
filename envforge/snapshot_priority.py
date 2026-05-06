"""Snapshot priority management — assign and query numeric priority levels."""

from __future__ import annotations

import json
from pathlib import Path

_PRIORITY_FILE = "priority_index.json"
_MIN_PRIORITY = 1
_MAX_PRIORITY = 10


def _get_priority_path(base_dir: str) -> Path:
    return Path(base_dir) / _PRIORITY_FILE


def _load_priority_index(base_dir: str) -> dict:
    path = _get_priority_path(base_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_priority_index(base_dir: str, index: dict) -> None:
    path = _get_priority_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index, indent=2))


def set_priority(base_dir: str, snapshot_name: str, level: int) -> int:
    """Assign a priority level (1–10) to a snapshot. Returns the stored level."""
    if not (_MIN_PRIORITY <= level <= _MAX_PRIORITY):
        raise ValueError(
            f"Priority must be between {_MIN_PRIORITY} and {_MAX_PRIORITY}, got {level}."
        )
    index = _load_priority_index(base_dir)
    index[snapshot_name] = level
    _save_priority_index(base_dir, index)
    return level


def get_priority(base_dir: str, snapshot_name: str) -> int | None:
    """Return the priority level for a snapshot, or None if not set."""
    index = _load_priority_index(base_dir)
    return index.get(snapshot_name)


def remove_priority(base_dir: str, snapshot_name: str) -> bool:
    """Remove the priority entry for a snapshot. Returns True if it existed."""
    index = _load_priority_index(base_dir)
    if snapshot_name not in index:
        return False
    del index[snapshot_name]
    _save_priority_index(base_dir, index)
    return True


def list_by_priority(base_dir: str) -> list[tuple[str, int]]:
    """Return all snapshots sorted by priority descending (highest first)."""
    index = _load_priority_index(base_dir)
    return sorted(index.items(), key=lambda kv: kv[1], reverse=True)
