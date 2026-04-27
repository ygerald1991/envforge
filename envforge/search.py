"""Search snapshots by tag, name pattern, or variable key presence."""

import fnmatch
from typing import Dict, List, Optional

from envforge.core import list_snapshots, load_snapshot
from envforge.tag import snapshots_for_tag


def search_by_tag(tag: str, snapshot_dir: str) -> List[str]:
    """Return snapshot names that carry the given tag."""
    return snapshots_for_tag(tag, snapshot_dir)


def search_by_name(pattern: str, snapshot_dir: str) -> List[str]:
    """Return snapshot names matching a glob pattern (e.g. 'prod-*')."""
    all_snaps = list_snapshots(snapshot_dir)
    return fnmatch.filter(all_snaps, pattern)


def search_by_key(key: str, snapshot_dir: str) -> List[str]:
    """Return snapshot names that contain the given environment variable key."""
    results = []
    for name in list_snapshots(snapshot_dir):
        try:
            snapshot = load_snapshot(name, snapshot_dir)
            if key in snapshot.get("vars", {}):
                results.append(name)
        except Exception:
            continue
    return results


def search_by_value_pattern(key: str, pattern: str, snapshot_dir: str) -> List[str]:
    """Return snapshot names where key exists and its value matches a glob pattern."""
    results = []
    for name in list_snapshots(snapshot_dir):
        try:
            snapshot = load_snapshot(name, snapshot_dir)
            value = snapshot.get("vars", {}).get(key)
            if value is not None and fnmatch.fnmatch(value, pattern):
                results.append(name)
        except Exception:
            continue
    return results


def combined_search(
    snapshot_dir: str,
    tag: Optional[str] = None,
    name_pattern: Optional[str] = None,
    key: Optional[str] = None,
) -> List[str]:
    """Intersect results from multiple search criteria."""
    candidates = set(list_snapshots(snapshot_dir))

    if tag is not None:
        candidates &= set(search_by_tag(tag, snapshot_dir))
    if name_pattern is not None:
        candidates &= set(search_by_name(name_pattern, snapshot_dir))
    if key is not None:
        candidates &= set(search_by_key(key, snapshot_dir))

    return sorted(candidates)
