"""Attach and retrieve arbitrary metadata key-value pairs for snapshots."""

import json
from pathlib import Path
from typing import Any, Dict, Optional


def _get_meta_path(snapshot_dir: str) -> Path:
    return Path(snapshot_dir) / ".snapshot_meta.json"


def _load_meta(snapshot_dir: str) -> Dict[str, Dict[str, Any]]:
    path = _get_meta_path(snapshot_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_meta(snapshot_dir: str, data: Dict[str, Dict[str, Any]]) -> None:
    path = _get_meta_path(snapshot_dir)
    Path(snapshot_dir).mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_meta(snapshot_dir: str, snapshot_name: str, key: str, value: Any) -> None:
    """Set a metadata key for the given snapshot."""
    data = _load_meta(snapshot_dir)
    if snapshot_name not in data:
        data[snapshot_name] = {}
    data[snapshot_name][key] = value
    _save_meta(snapshot_dir, data)


def get_meta(snapshot_dir: str, snapshot_name: str, key: str) -> Optional[Any]:
    """Get a single metadata value; returns None if not found."""
    data = _load_meta(snapshot_dir)
    return data.get(snapshot_name, {}).get(key)


def get_all_meta(snapshot_dir: str, snapshot_name: str) -> Dict[str, Any]:
    """Return all metadata for a snapshot as a dict (empty if none)."""
    data = _load_meta(snapshot_dir)
    return dict(data.get(snapshot_name, {}))


def remove_meta_key(snapshot_dir: str, snapshot_name: str, key: str) -> bool:
    """Remove a single metadata key. Returns True if removed, False if not found."""
    data = _load_meta(snapshot_dir)
    if snapshot_name in data and key in data[snapshot_name]:
        del data[snapshot_name][key]
        if not data[snapshot_name]:
            del data[snapshot_name]
        _save_meta(snapshot_dir, data)
        return True
    return False


def clear_meta(snapshot_dir: str, snapshot_name: str) -> None:
    """Remove all metadata for a snapshot."""
    data = _load_meta(snapshot_dir)
    if snapshot_name in data:
        del data[snapshot_name]
        _save_meta(snapshot_dir, data)


def list_meta_snapshots(snapshot_dir: str) -> list:
    """Return list of snapshot names that have metadata entries."""
    return list(_load_meta(snapshot_dir).keys())
