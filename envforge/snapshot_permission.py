"""Snapshot permission management for envforge."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

VALID_ROLES = {"owner", "editor", "viewer"}


def _get_permission_path(base_dir: str) -> Path:
    return Path(base_dir) / "permissions.json"


def _load_permissions(base_dir: str) -> Dict[str, Dict[str, str]]:
    path = _get_permission_path(base_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_permissions(base_dir: str, index: Dict[str, Dict[str, str]]) -> None:
    path = _get_permission_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index, indent=2))


def set_permission(base_dir: str, snapshot: str, user: str, role: str) -> Dict[str, str]:
    """Grant *user* the given *role* on *snapshot*."""
    if role not in VALID_ROLES:
        raise ValueError(f"Invalid role '{role}'. Choose from: {sorted(VALID_ROLES)}")
    index = _load_permissions(base_dir)
    if snapshot not in index:
        index[snapshot] = {}
    index[snapshot][user] = role
    _save_permissions(base_dir, index)
    return {"snapshot": snapshot, "user": user, "role": role}


def remove_permission(base_dir: str, snapshot: str, user: str) -> bool:
    """Revoke *user*'s access to *snapshot*. Returns True if removed."""
    index = _load_permissions(base_dir)
    if snapshot not in index or user not in index[snapshot]:
        return False
    del index[snapshot][user]
    if not index[snapshot]:
        del index[snapshot]
    _save_permissions(base_dir, index)
    return True


def get_permission(base_dir: str, snapshot: str, user: str) -> Optional[str]:
    """Return the role for *user* on *snapshot*, or None."""
    index = _load_permissions(base_dir)
    return index.get(snapshot, {}).get(user)


def list_permissions(base_dir: str, snapshot: str) -> Dict[str, str]:
    """Return all user→role mappings for *snapshot*."""
    index = _load_permissions(base_dir)
    return dict(index.get(snapshot, {}))


def get_users_with_role(base_dir: str, snapshot: str, role: str) -> List[str]:
    """Return all users that hold *role* on *snapshot*."""
    perms = list_permissions(base_dir, snapshot)
    return [u for u, r in perms.items() if r == role]
