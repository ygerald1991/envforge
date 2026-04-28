"""Pin snapshots to prevent accidental deletion or overwrite."""

import json
import os
from pathlib import Path
from typing import List

_PIN_INDEX_FILE = "pins.json"


def _get_pin_index_path(snapshot_dir: str) -> Path:
    return Path(snapshot_dir) / _PIN_INDEX_FILE


def _load_pin_index(snapshot_dir: str) -> List[str]:
    path = _get_pin_index_path(snapshot_dir)
    if not path.exists():
        return []
    with open(path, "r") as f:
        data = json.load(f)
    return data.get("pinned", [])


def _save_pin_index(snapshot_dir: str, pinned: List[str]) -> None:
    path = _get_pin_index_path(snapshot_dir)
    with open(path, "w") as f:
        json.dump({"pinned": sorted(set(pinned))}, f, indent=2)


def pin_snapshot(snapshot_dir: str, name: str) -> None:
    """Mark a snapshot as pinned."""
    pinned = _load_pin_index(snapshot_dir)
    if name not in pinned:
        pinned.append(name)
    _save_pin_index(snapshot_dir, pinned)


def unpin_snapshot(snapshot_dir: str, name: str) -> None:
    """Remove the pin from a snapshot."""
    pinned = _load_pin_index(snapshot_dir)
    pinned = [p for p in pinned if p != name]
    _save_pin_index(snapshot_dir, pinned)


def is_pinned(snapshot_dir: str, name: str) -> bool:
    """Return True if the snapshot is pinned."""
    return name in _load_pin_index(snapshot_dir)


def list_pinned(snapshot_dir: str) -> List[str]:
    """Return all pinned snapshot names."""
    return _load_pin_index(snapshot_dir)
