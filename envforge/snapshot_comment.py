"""Snapshot inline comment management for envforge."""

import json
from pathlib import Path
from typing import Dict, List, Optional


def _get_comment_path(base_dir: str) -> Path:
    return Path(base_dir) / ".envforge_comments.json"


def _load_comments(base_dir: str) -> Dict[str, List[Dict]]:
    path = _get_comment_path(base_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_comments(base_dir: str, data: Dict[str, List[Dict]]) -> None:
    path = _get_comment_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def add_comment(base_dir: str, snapshot_name: str, author: str, text: str) -> Dict:
    """Add a comment to a snapshot. Returns the new comment entry."""
    import datetime
    data = _load_comments(base_dir)
    entry = {
        "author": author,
        "text": text,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    }
    data.setdefault(snapshot_name, []).append(entry)
    _save_comments(base_dir, data)
    return entry


def get_comments(base_dir: str, snapshot_name: str) -> List[Dict]:
    """Return all comments for a snapshot, oldest first."""
    data = _load_comments(base_dir)
    return data.get(snapshot_name, [])


def delete_comment(base_dir: str, snapshot_name: str, index: int) -> bool:
    """Delete the comment at the given index. Returns True if deleted."""
    data = _load_comments(base_dir)
    comments = data.get(snapshot_name, [])
    if index < 0 or index >= len(comments):
        return False
    comments.pop(index)
    data[snapshot_name] = comments
    _save_comments(base_dir, data)
    return True


def clear_comments(base_dir: str, snapshot_name: str) -> int:
    """Remove all comments for a snapshot. Returns count removed."""
    data = _load_comments(base_dir)
    removed = len(data.pop(snapshot_name, []))
    _save_comments(base_dir, data)
    return removed


def format_comments(comments: List[Dict]) -> str:
    """Return a human-readable string of comments."""
    if not comments:
        return "  (no comments)"
    lines = []
    for i, c in enumerate(comments):
        lines.append(f"  [{i}] {c['timestamp']}  {c['author']}: {c['text']}")
    return "\n".join(lines)
