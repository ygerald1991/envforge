"""Snapshot chaining: link snapshots in a parent→child lineage."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_CHAIN_INDEX_FILE = "chain_index.json"


def _get_chain_index_path(store_dir: str) -> Path:
    return Path(store_dir) / _CHAIN_INDEX_FILE


def _load_chain_index(store_dir: str) -> Dict[str, Optional[str]]:
    path = _get_chain_index_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_chain_index(store_dir: str, index: Dict[str, Optional[str]]) -> None:
    path = _get_chain_index_path(store_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index, indent=2))


def set_parent(store_dir: str, snapshot_name: str, parent_name: str) -> None:
    """Record that *parent_name* is the direct parent of *snapshot_name*."""
    index = _load_chain_index(store_dir)
    index[snapshot_name] = parent_name
    _save_chain_index(store_dir, index)


def get_parent(store_dir: str, snapshot_name: str) -> Optional[str]:
    """Return the direct parent of *snapshot_name*, or None."""
    return _load_chain_index(store_dir).get(snapshot_name)


def get_ancestors(store_dir: str, snapshot_name: str) -> List[str]:
    """Return ordered list of ancestors, oldest last."""
    index = _load_chain_index(store_dir)
    ancestors: List[str] = []
    current = index.get(snapshot_name)
    visited = set()
    while current is not None and current not in visited:
        ancestors.append(current)
        visited.add(current)
        current = index.get(current)
    return ancestors


def get_children(store_dir: str, snapshot_name: str) -> List[str]:
    """Return all snapshots whose direct parent is *snapshot_name*."""
    index = _load_chain_index(store_dir)
    return [name for name, parent in index.items() if parent == snapshot_name]


def remove_from_chain(store_dir: str, snapshot_name: str) -> bool:
    """Remove *snapshot_name* from the chain index. Returns True if it existed."""
    index = _load_chain_index(store_dir)
    if snapshot_name not in index:
        return False
    del index[snapshot_name]
    _save_chain_index(store_dir, index)
    return True
