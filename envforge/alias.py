"""Snapshot alias management — assign human-friendly names to snapshot IDs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

_ALIAS_FILE = "aliases.json"


def _get_alias_path(snapshot_dir: str) -> Path:
    return Path(snapshot_dir) / _ALIAS_FILE


def _load_aliases(snapshot_dir: str) -> Dict[str, str]:
    path = _get_alias_path(snapshot_dir)
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save_aliases(snapshot_dir: str, aliases: Dict[str, str]) -> None:
    path = _get_alias_path(snapshot_dir)
    Path(snapshot_dir).mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(aliases, f, indent=2)


def set_alias(snapshot_dir: str, alias: str, snapshot_name: str) -> None:
    """Assign *alias* to *snapshot_name*, overwriting any previous mapping."""
    aliases = _load_aliases(snapshot_dir)
    aliases[alias] = snapshot_name
    _save_aliases(snapshot_dir, aliases)


def remove_alias(snapshot_dir: str, alias: str) -> bool:
    """Remove *alias*. Returns True if it existed, False otherwise."""
    aliases = _load_aliases(snapshot_dir)
    if alias not in aliases:
        return False
    del aliases[alias]
    _save_aliases(snapshot_dir, aliases)
    return True


def resolve_alias(snapshot_dir: str, alias: str) -> Optional[str]:
    """Return the snapshot name for *alias*, or None if not found."""
    return _load_aliases(snapshot_dir).get(alias)


def list_aliases(snapshot_dir: str) -> Dict[str, str]:
    """Return a copy of the full alias → snapshot-name mapping."""
    return dict(_load_aliases(snapshot_dir))


def get_aliases_for_snapshot(snapshot_dir: str, snapshot_name: str) -> list[str]:
    """Return all aliases that point to *snapshot_name*."""
    return [
        alias
        for alias, name in _load_aliases(snapshot_dir).items()
        if name == snapshot_name
    ]
