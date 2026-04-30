"""Group multiple snapshots under a named collection."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional


def _get_group_index_path(base_dir: str) -> Path:
    return Path(base_dir) / ".groups.json"


def _load_group_index(base_dir: str) -> Dict[str, List[str]]:
    path = _get_group_index_path(base_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_group_index(base_dir: str, index: Dict[str, List[str]]) -> None:
    path = _get_group_index_path(base_dir)
    Path(base_dir).mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(index, f, indent=2)


def create_group(base_dir: str, group_name: str, snapshot_names: List[str]) -> None:
    """Create or replace a named group with the given snapshots."""
    index = _load_group_index(base_dir)
    index[group_name] = list(snapshot_names)
    _save_group_index(base_dir, index)


def add_to_group(base_dir: str, group_name: str, snapshot_name: str) -> None:
    """Add a snapshot to an existing group (creates group if absent)."""
    index = _load_group_index(base_dir)
    members = index.get(group_name, [])
    if snapshot_name not in members:
        members.append(snapshot_name)
    index[group_name] = members
    _save_group_index(base_dir, index)


def remove_from_group(base_dir: str, group_name: str, snapshot_name: str) -> bool:
    """Remove a snapshot from a group. Returns True if removed, False if not found."""
    index = _load_group_index(base_dir)
    members = index.get(group_name, [])
    if snapshot_name not in members:
        return False
    members.remove(snapshot_name)
    index[group_name] = members
    _save_group_index(base_dir, index)
    return True


def delete_group(base_dir: str, group_name: str) -> bool:
    """Delete a group entirely. Returns True if it existed."""
    index = _load_group_index(base_dir)
    if group_name not in index:
        return False
    del index[group_name]
    _save_group_index(base_dir, index)
    return True


def get_group(base_dir: str, group_name: str) -> Optional[List[str]]:
    """Return the list of snapshot names in a group, or None if not found."""
    index = _load_group_index(base_dir)
    return index.get(group_name)


def list_groups(base_dir: str) -> Dict[str, List[str]]:
    """Return all groups and their members."""
    return _load_group_index(base_dir)
