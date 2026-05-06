"""Snapshot versioning: track sequential version numbers for named snapshots."""

import json
from pathlib import Path
from typing import Optional

_VERSION_FILE = "version_index.json"


def _get_version_path(base_dir: str) -> Path:
    return Path(base_dir) / _VERSION_FILE


def _load_version_index(base_dir: str) -> dict:
    path = _get_version_path(base_dir)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_version_index(base_dir: str, index: dict) -> None:
    path = _get_version_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(index, f, indent=2)


def bump_version(base_dir: str, snapshot_name: str) -> int:
    """Increment and return the version number for a snapshot."""
    index = _load_version_index(base_dir)
    current = index.get(snapshot_name, 0)
    next_version = current + 1
    index[snapshot_name] = next_version
    _save_version_index(base_dir, index)
    return next_version


def get_version(base_dir: str, snapshot_name: str) -> Optional[int]:
    """Return the current version number for a snapshot, or None if unversioned."""
    index = _load_version_index(base_dir)
    return index.get(snapshot_name)


def set_version(base_dir: str, snapshot_name: str, version: int) -> int:
    """Explicitly set the version number for a snapshot."""
    if version < 1:
        raise ValueError(f"Version must be >= 1, got {version}")
    index = _load_version_index(base_dir)
    index[snapshot_name] = version
    _save_version_index(base_dir, index)
    return version


def reset_version(base_dir: str, snapshot_name: str) -> None:
    """Remove version tracking for a snapshot."""
    index = _load_version_index(base_dir)
    index.pop(snapshot_name, None)
    _save_version_index(base_dir, index)


def list_versions(base_dir: str) -> dict:
    """Return a mapping of all snapshot names to their current version numbers."""
    return dict(_load_version_index(base_dir))
