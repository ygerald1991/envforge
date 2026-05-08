"""Track snapshot lineage: forks, merges, and derivation history."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _get_lineage_path(store_dir: str) -> Path:
    return Path(store_dir) / ".lineage.json"


def _load_lineage(store_dir: str) -> Dict:
    path = _get_lineage_path(store_dir)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_lineage(store_dir: str, data: Dict) -> None:
    path = _get_lineage_path(store_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def record_fork(store_dir: str, parent: str, child: str) -> Dict:
    """Record that *child* was forked from *parent*."""
    data = _load_lineage(store_dir)
    entry = {"type": "fork", "parent": parent}
    data[child] = entry
    _save_lineage(store_dir, data)
    return entry


def record_merge(store_dir: str, sources: List[str], result: str) -> Dict:
    """Record that *result* was produced by merging *sources*."""
    if len(sources) < 2:
        raise ValueError("merge requires at least two source snapshots")
    data = _load_lineage(store_dir)
    entry = {"type": "merge", "sources": list(sources)}
    data[result] = entry
    _save_lineage(store_dir, data)
    return entry


def get_lineage(store_dir: str, snapshot: str) -> Optional[Dict]:
    """Return the lineage entry for *snapshot*, or None if untracked."""
    return _load_lineage(store_dir).get(snapshot)


def get_descendants(store_dir: str, snapshot: str) -> List[str]:
    """Return all snapshots that directly or indirectly derive from *snapshot*."""
    data = _load_lineage(store_dir)
    descendants: List[str] = []
    for name, entry in data.items():
        if entry.get("type") == "fork" and entry.get("parent") == snapshot:
            descendants.append(name)
            descendants.extend(get_descendants(store_dir, name))
    return descendants


def remove_lineage(store_dir: str, snapshot: str) -> bool:
    """Remove lineage record for *snapshot*. Returns True if it existed."""
    data = _load_lineage(store_dir)
    if snapshot not in data:
        return False
    del data[snapshot]
    _save_lineage(store_dir, data)
    return True
