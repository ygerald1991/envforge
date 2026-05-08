"""Snapshot quota management — enforce limits on the number of snapshots per namespace or globally."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

_QUOTA_FILE = "quota_index.json"
_DEFAULT_GLOBAL_KEY = "__global__"


def _get_quota_path(store_dir: str) -> Path:
    return Path(store_dir) / _QUOTA_FILE


def _load_quota_index(store_dir: str) -> dict:
    p = _get_quota_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_quota_index(store_dir: str, index: dict) -> None:
    p = _get_quota_path(store_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(index, indent=2))


def set_quota(store_dir: str, limit: int, namespace: Optional[str] = None) -> dict:
    """Set a quota limit for a namespace (or globally)."""
    if limit < 1:
        raise ValueError("Quota limit must be a positive integer.")
    key = namespace or _DEFAULT_GLOBAL_KEY
    index = _load_quota_index(store_dir)
    entry = {"limit": limit, "namespace": key}
    index[key] = entry
    _save_quota_index(store_dir, index)
    return entry


def get_quota(store_dir: str, namespace: Optional[str] = None) -> Optional[dict]:
    """Return the quota entry for a namespace, or None if not set."""
    key = namespace or _DEFAULT_GLOBAL_KEY
    index = _load_quota_index(store_dir)
    return index.get(key)


def remove_quota(store_dir: str, namespace: Optional[str] = None) -> bool:
    """Remove quota for a namespace. Returns True if it existed."""
    key = namespace or _DEFAULT_GLOBAL_KEY
    index = _load_quota_index(store_dir)
    if key not in index:
        return False
    del index[key]
    _save_quota_index(store_dir, index)
    return True


def list_quotas(store_dir: str) -> list[dict]:
    """Return all quota entries."""
    index = _load_quota_index(store_dir)
    return list(index.values())


def check_quota(store_dir: str, current_count: int, namespace: Optional[str] = None) -> bool:
    """Return True if current_count is within the quota limit (or no quota is set)."""
    entry = get_quota(store_dir, namespace)
    if entry is None:
        # fall back to global quota
        if namespace is not None:
            entry = get_quota(store_dir, None)
    if entry is None:
        return True
    return current_count < entry["limit"]
