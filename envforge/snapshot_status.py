"""Snapshot status tracking — assign and query lifecycle-independent status labels."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

VALID_STATUSES = {"active", "deprecated", "experimental", "stable", "archived"}


def _get_status_path(store_dir: str) -> Path:
    return Path(store_dir) / ".snapshot_status.json"


def _load_status_index(store_dir: str) -> Dict[str, str]:
    path = _get_status_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_status_index(store_dir: str, index: Dict[str, str]) -> None:
    path = _get_status_path(store_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index, indent=2))


def set_status(store_dir: str, snapshot_name: str, status: str) -> str:
    """Assign a status to a snapshot. Returns the status string."""
    if status not in VALID_STATUSES:
        raise ValueError(
            f"Invalid status '{status}'. Choose from: {sorted(VALID_STATUSES)}"
        )
    index = _load_status_index(store_dir)
    index[snapshot_name] = status
    _save_status_index(store_dir, index)
    return status


def get_status(store_dir: str, snapshot_name: str) -> Optional[str]:
    """Return the status of a snapshot, or None if not set."""
    return _load_status_index(store_dir).get(snapshot_name)


def remove_status(store_dir: str, snapshot_name: str) -> bool:
    """Remove the status entry for a snapshot. Returns True if it existed."""
    index = _load_status_index(store_dir)
    if snapshot_name not in index:
        return False
    del index[snapshot_name]
    _save_status_index(store_dir, index)
    return True


def list_by_status(store_dir: str, status: str) -> List[str]:
    """Return all snapshot names that have the given status."""
    if status not in VALID_STATUSES:
        raise ValueError(
            f"Invalid status '{status}'. Choose from: {sorted(VALID_STATUSES)}"
        )
    index = _load_status_index(store_dir)
    return [name for name, s in index.items() if s == status]


def get_all_statuses(store_dir: str) -> Dict[str, str]:
    """Return the full status index."""
    return dict(_load_status_index(store_dir))
