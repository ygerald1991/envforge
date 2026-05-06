"""Namespace support for grouping snapshots under logical scopes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _get_namespace_path(base_dir: str) -> Path:
    return Path(base_dir) / ".namespaces.json"


def _load_namespace_index(base_dir: str) -> Dict[str, List[str]]:
    path = _get_namespace_path(base_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_namespace_index(base_dir: str, index: Dict[str, List[str]]) -> None:
    path = _get_namespace_path(base_dir)
    Path(base_dir).mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(index, f, indent=2)


def add_to_namespace(base_dir: str, namespace: str, snapshot_name: str) -> None:
    """Add a snapshot to a namespace. Creates the namespace if it does not exist."""
    index = _load_namespace_index(base_dir)
    if namespace not in index:
        index[namespace] = []
    if snapshot_name not in index[namespace]:
        index[namespace].append(snapshot_name)
    _save_namespace_index(base_dir, index)


def remove_from_namespace(base_dir: str, namespace: str, snapshot_name: str) -> bool:
    """Remove a snapshot from a namespace. Returns True if removed, False if not found."""
    index = _load_namespace_index(base_dir)
    if namespace not in index or snapshot_name not in index[namespace]:
        return False
    index[namespace].remove(snapshot_name)
    if not index[namespace]:
        del index[namespace]
    _save_namespace_index(base_dir, index)
    return True


def get_namespace(base_dir: str, namespace: str) -> Optional[List[str]]:
    """Return list of snapshot names in a namespace, or None if namespace missing."""
    index = _load_namespace_index(base_dir)
    return index.get(namespace)


def list_namespaces(base_dir: str) -> List[str]:
    """Return all defined namespace names."""
    return list(_load_namespace_index(base_dir).keys())


def delete_namespace(base_dir: str, namespace: str) -> bool:
    """Delete an entire namespace. Returns True if deleted, False if not found."""
    index = _load_namespace_index(base_dir)
    if namespace not in index:
        return False
    del index[namespace]
    _save_namespace_index(base_dir, index)
    return True
