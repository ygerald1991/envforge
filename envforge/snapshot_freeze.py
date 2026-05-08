"""Snapshot freeze/unfreeze — prevent a snapshot from being modified or deleted."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

_FREEZE_FILE = "freeze_index.json"


def _get_freeze_path(store_dir: str) -> Path:
    return Path(store_dir) / _FREEZE_FILE


def _load_freeze_index(store_dir: str) -> List[str]:
    path = _get_freeze_path(store_dir)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _save_freeze_index(store_dir: str, index: List[str]) -> None:
    path = _get_freeze_path(store_dir)
    Path(store_dir).mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(set(index)), indent=2))


def freeze_snapshot(store_dir: str, snapshot_name: str) -> None:
    """Mark *snapshot_name* as frozen (immutable)."""
    index = _load_freeze_index(store_dir)
    if snapshot_name not in index:
        index.append(snapshot_name)
    _save_freeze_index(store_dir, index)


def unfreeze_snapshot(store_dir: str, snapshot_name: str) -> None:
    """Remove the frozen mark from *snapshot_name*."""
    index = _load_freeze_index(store_dir)
    index = [n for n in index if n != snapshot_name]
    _save_freeze_index(store_dir, index)


def is_frozen(store_dir: str, snapshot_name: str) -> bool:
    """Return True if *snapshot_name* is currently frozen."""
    return snapshot_name in _load_freeze_index(store_dir)


def list_frozen(store_dir: str) -> List[str]:
    """Return all frozen snapshot names."""
    return list(_load_freeze_index(store_dir))
