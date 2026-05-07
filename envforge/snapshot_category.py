"""Snapshot category management — assign, remove, and query categories for snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_CATEGORY_FILE = "categories.json"


def _get_category_path(store_dir: str) -> Path:
    return Path(store_dir) / _CATEGORY_FILE


def _load_category_index(store_dir: str) -> Dict[str, List[str]]:
    """Return mapping of category -> list of snapshot names."""
    path = _get_category_path(store_dir)
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def _save_category_index(store_dir: str, index: Dict[str, List[str]]) -> None:
    path = _get_category_path(store_dir)
    Path(store_dir).mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(index, fh, indent=2)


def set_category(store_dir: str, snapshot: str, category: str) -> str:
    """Assign *snapshot* to *category*, replacing any previous category assignment."""
    if not category or not category.strip():
        raise ValueError("Category must be a non-empty string.")
    index = _load_category_index(store_dir)
    # Remove snapshot from any existing category first
    for cat, members in index.items():
        if snapshot in members:
            members.remove(snapshot)
    index.setdefault(category, [])
    if snapshot not in index[category]:
        index[category].append(snapshot)
    _save_category_index(store_dir, index)
    return category


def get_category(store_dir: str, snapshot: str) -> Optional[str]:
    """Return the category assigned to *snapshot*, or None."""
    index = _load_category_index(store_dir)
    for cat, members in index.items():
        if snapshot in members:
            return cat
    return None


def remove_from_category(store_dir: str, snapshot: str) -> bool:
    """Remove *snapshot* from its current category. Returns True if it was removed."""
    index = _load_category_index(store_dir)
    for cat, members in index.items():
        if snapshot in members:
            members.remove(snapshot)
            _save_category_index(store_dir, index)
            return True
    return False


def list_by_category(store_dir: str, category: str) -> List[str]:
    """Return all snapshot names belonging to *category*."""
    index = _load_category_index(store_dir)
    return list(index.get(category, []))


def all_categories(store_dir: str) -> List[str]:
    """Return a sorted list of all known category names."""
    index = _load_category_index(store_dir)
    return sorted(k for k, v in index.items() if v)
