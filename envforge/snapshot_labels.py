"""Snapshot label management — attach arbitrary key/value labels to snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

_LABEL_INDEX_FILE = "label_index.json"


def _get_label_index_path(store_dir: str) -> Path:
    return Path(store_dir) / _LABEL_INDEX_FILE


def _load_label_index(store_dir: str) -> Dict[str, Dict[str, str]]:
    path = _get_label_index_path(store_dir)
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def _save_label_index(store_dir: str, index: Dict[str, Dict[str, str]]) -> None:
    path = _get_label_index_path(store_dir)
    Path(store_dir).mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(index, fh, indent=2)


def set_label(store_dir: str, snapshot_name: str, key: str, value: str) -> None:
    """Attach a label key/value pair to *snapshot_name*."""
    index = _load_label_index(store_dir)
    labels = index.setdefault(snapshot_name, {})
    labels[key] = value
    _save_label_index(store_dir, index)


def remove_label(store_dir: str, snapshot_name: str, key: str) -> bool:
    """Remove a label key from *snapshot_name*. Returns True if it existed."""
    index = _load_label_index(store_dir)
    labels = index.get(snapshot_name, {})
    if key not in labels:
        return False
    del labels[key]
    if not labels:
        index.pop(snapshot_name, None)
    _save_label_index(store_dir, index)
    return True


def get_labels(store_dir: str, snapshot_name: str) -> Dict[str, str]:
    """Return all labels for *snapshot_name* (empty dict if none)."""
    index = _load_label_index(store_dir)
    return dict(index.get(snapshot_name, {}))


def get_label(store_dir: str, snapshot_name: str, key: str) -> Optional[str]:
    """Return a single label value or None."""
    return get_labels(store_dir, snapshot_name).get(key)


def find_by_label(store_dir: str, key: str, value: Optional[str] = None) -> list[str]:
    """Return snapshot names that have *key* (optionally matching *value*)."""
    index = _load_label_index(store_dir)
    results = []
    for snap, labels in index.items():
        if key in labels:
            if value is None or labels[key] == value:
                results.append(snap)
    return sorted(results)
