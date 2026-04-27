"""Snapshot history tracking: list, prune, and summarize snapshot timelines."""

from __future__ import annotations

import os
from datetime import datetime
from typing import List, Dict, Optional

from envforge.core import list_snapshots, load_snapshot


def get_snapshot_history(snapshot_dir: str, prefix: Optional[str] = None) -> List[Dict]:
    """Return snapshots sorted by creation time (oldest first).

    Each entry contains: name, timestamp, var_count, path.
    """
    names = list_snapshots(snapshot_dir)
    if prefix:
        names = [n for n in names if n.startswith(prefix)]

    history = []
    for name in names:
        path = os.path.join(snapshot_dir, f"{name}.json")
        try:
            mtime = os.path.getmtime(path)
            snapshot = load_snapshot(snapshot_dir, name)
            history.append({
                "name": name,
                "timestamp": datetime.fromtimestamp(mtime).isoformat(timespec="seconds"),
                "var_count": len(snapshot),
                "path": path,
            })
        except (FileNotFoundError, ValueError):
            continue

    history.sort(key=lambda e: e["timestamp"])
    return history


def prune_history(
    snapshot_dir: str,
    keep: int,
    prefix: Optional[str] = None,
    dry_run: bool = False,
) -> List[str]:
    """Remove oldest snapshots, keeping only *keep* most recent ones.

    Returns list of snapshot names that were (or would be) deleted.
    """
    if keep < 1:
        raise ValueError("keep must be >= 1")

    history = get_snapshot_history(snapshot_dir, prefix=prefix)
    to_delete = history[:-keep] if len(history) > keep else []

    deleted = []
    for entry in to_delete:
        deleted.append(entry["name"])
        if not dry_run:
            try:
                os.remove(entry["path"])
            except FileNotFoundError:
                pass

    return deleted


def format_history(history: List[Dict]) -> str:
    """Return a human-readable table of snapshot history."""
    if not history:
        return "No snapshots found."

    lines = [f"{'#':<4} {'Name':<30} {'Timestamp':<22} {'Vars':>5}"]
    lines.append("-" * 65)
    for idx, entry in enumerate(history, start=1):
        lines.append(
            f"{idx:<4} {entry['name']:<30} {entry['timestamp']:<22} {entry['var_count']:>5}"
        )
    return "\n".join(lines)
