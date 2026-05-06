"""Bookmark management for snapshots — assign memorable shorthand names."""

import json
from pathlib import Path
from typing import Dict, List, Optional


def _get_bookmark_path(base_dir: str) -> Path:
    return Path(base_dir) / ".bookmarks.json"


def _load_bookmarks(base_dir: str) -> Dict[str, str]:
    path = _get_bookmark_path(base_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_bookmarks(base_dir: str, data: Dict[str, str]) -> None:
    path = _get_bookmark_path(base_dir)
    Path(base_dir).mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_bookmark(base_dir: str, bookmark: str, snapshot_name: str) -> None:
    """Associate a bookmark name with a snapshot."""
    data = _load_bookmarks(base_dir)
    data[bookmark] = snapshot_name
    _save_bookmarks(base_dir, data)


def remove_bookmark(base_dir: str, bookmark: str) -> bool:
    """Remove a bookmark. Returns True if it existed, False otherwise."""
    data = _load_bookmarks(base_dir)
    if bookmark not in data:
        return False
    del data[bookmark]
    _save_bookmarks(base_dir, data)
    return True


def resolve_bookmark(base_dir: str, bookmark: str) -> Optional[str]:
    """Return the snapshot name for a bookmark, or None if not found."""
    return _load_bookmarks(base_dir).get(bookmark)


def list_bookmarks(base_dir: str) -> Dict[str, str]:
    """Return all bookmark -> snapshot_name mappings."""
    return _load_bookmarks(base_dir)


def bookmarks_for_snapshot(base_dir: str, snapshot_name: str) -> List[str]:
    """Return all bookmark names pointing to the given snapshot."""
    data = _load_bookmarks(base_dir)
    return [bm for bm, sn in data.items() if sn == snapshot_name]
