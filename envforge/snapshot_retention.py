"""Retention policy management for snapshots."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_RETENTION_FILE = "retention_policies.json"


def _get_retention_path(base_dir: str) -> Path:
    return Path(base_dir) / _RETENTION_FILE


def _load_retention(base_dir: str) -> dict[str, Any]:
    path = _get_retention_path(base_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_retention(base_dir: str, data: dict[str, Any]) -> None:
    path = _get_retention_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def set_retention_policy(base_dir: str, name: str, max_count: int, max_age_days: int | None = None) -> dict[str, Any]:
    """Set a named retention policy."""
    if max_count < 1:
        raise ValueError("max_count must be at least 1")
    if max_age_days is not None and max_age_days < 1:
        raise ValueError("max_age_days must be at least 1")
    data = _load_retention(base_dir)
    policy: dict[str, Any] = {
        "name": name,
        "max_count": max_count,
        "max_age_days": max_age_days,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    data[name] = policy
    _save_retention(base_dir, data)
    return policy


def get_retention_policy(base_dir: str, name: str) -> dict[str, Any] | None:
    """Retrieve a named retention policy, or None if not found."""
    return _load_retention(base_dir).get(name)


def remove_retention_policy(base_dir: str, name: str) -> bool:
    """Remove a retention policy by name. Returns True if it existed."""
    data = _load_retention(base_dir)
    if name not in data:
        return False
    del data[name]
    _save_retention(base_dir, data)
    return True


def list_retention_policies(base_dir: str) -> list[dict[str, Any]]:
    """Return all retention policies sorted by name."""
    data = _load_retention(base_dir)
    return sorted(data.values(), key=lambda p: p["name"])


def apply_retention_policy(base_dir: str, name: str, snapshots: list[dict[str, Any]]) -> list[str]:
    """Apply a retention policy to a list of snapshot metadata dicts.

    Each snapshot dict must have 'name' and 'created_at' (ISO-8601) keys.
    Returns a list of snapshot names that should be pruned.
    """
    policy = get_retention_policy(base_dir, name)
    if policy is None:
        raise KeyError(f"Retention policy '{name}' not found")

    sorted_snaps = sorted(snapshots, key=lambda s: s["created_at"], reverse=True)
    to_prune: list[str] = []

    # Enforce max_count
    if len(sorted_snaps) > policy["max_count"]:
        to_prune.extend(s["name"] for s in sorted_snaps[policy["max_count"]:])

    # Enforce max_age_days
    if policy["max_age_days"] is not None:
        cutoff = datetime.now(timezone.utc).timestamp() - policy["max_age_days"] * 86400
        for snap in sorted_snaps:
            ts = datetime.fromisoformat(snap["created_at"]).timestamp()
            if ts < cutoff and snap["name"] not in to_prune:
                to_prune.append(snap["name"])

    return to_prune
