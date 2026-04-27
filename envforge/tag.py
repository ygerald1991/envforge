"""Tag and label snapshots for easier organization and retrieval."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from envforge.core import _ensure_snapshot_dir


def _get_tag_index_path(snapshot_dir: str) -> Path:
    """Return path to the tag index file."""
    return Path(snapshot_dir) / ".tags.json"


def _load_tag_index(snapshot_dir: str) -> Dict[str, List[str]]:
    """Load the tag index mapping tag -> list of snapshot names."""
    path = _get_tag_index_path(snapshot_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_tag_index(snapshot_dir: str, index: Dict[str, List[str]]) -> None:
    """Persist the tag index to disk."""
    path = _get_tag_index_path(snapshot_dir)
    with open(path, "w") as f:
        json.dump(index, f, indent=2)


def add_tag(snapshot_name: str, tag: str, snapshot_dir: str) -> None:
    """Associate a tag with a snapshot."""
    _ensure_snapshot_dir(snapshot_dir)
    index = _load_tag_index(snapshot_dir)
    index.setdefault(tag, [])
    if snapshot_name not in index[tag]:
        index[tag].append(snapshot_name)
    _save_tag_index(snapshot_dir, index)


def remove_tag(snapshot_name: str, tag: str, snapshot_dir: str) -> bool:
    """Remove a tag from a snapshot. Returns True if tag was present."""
    index = _load_tag_index(snapshot_dir)
    if tag not in index or snapshot_name not in index[tag]:
        return False
    index[tag].remove(snapshot_name)
    if not index[tag]:
        del index[tag]
    _save_tag_index(snapshot_dir, index)
    return True


def list_tags(snapshot_dir: str) -> Dict[str, List[str]]:
    """Return all tags and their associated snapshots."""
    return _load_tag_index(snapshot_dir)


def snapshots_for_tag(tag: str, snapshot_dir: str) -> List[str]:
    """Return all snapshot names associated with a given tag."""
    index = _load_tag_index(snapshot_dir)
    return index.get(tag, [])


def tags_for_snapshot(snapshot_name: str, snapshot_dir: str) -> List[str]:
    """Return all tags associated with a given snapshot."""
    index = _load_tag_index(snapshot_dir)
    return [tag for tag, names in index.items() if snapshot_name in names]
