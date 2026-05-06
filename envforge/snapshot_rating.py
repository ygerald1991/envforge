"""Snapshot rating module — lets users rate snapshots (1-5 stars) with optional comments."""

import json
from pathlib import Path
from typing import Optional


def _get_rating_path(base_dir: str) -> Path:
    return Path(base_dir) / ".envforge_ratings.json"


def _load_ratings(base_dir: str) -> dict:
    path = _get_rating_path(base_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_ratings(base_dir: str, data: dict) -> None:
    path = _get_rating_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_rating(base_dir: str, snapshot_name: str, stars: int, comment: str = "") -> dict:
    """Set a star rating (1-5) and optional comment for a snapshot."""
    if not 1 <= stars <= 5:
        raise ValueError(f"Rating must be between 1 and 5, got {stars}")
    data = _load_ratings(base_dir)
    entry = {"stars": stars, "comment": comment}
    data[snapshot_name] = entry
    _save_ratings(base_dir, data)
    return entry


def get_rating(base_dir: str, snapshot_name: str) -> Optional[dict]:
    """Return the rating entry for a snapshot, or None if not rated."""
    data = _load_ratings(base_dir)
    return data.get(snapshot_name)


def remove_rating(base_dir: str, snapshot_name: str) -> bool:
    """Remove the rating for a snapshot. Returns True if it existed."""
    data = _load_ratings(base_dir)
    if snapshot_name not in data:
        return False
    del data[snapshot_name]
    _save_ratings(base_dir, data)
    return True


def list_ratings(base_dir: str) -> dict:
    """Return all ratings keyed by snapshot name."""
    return _load_ratings(base_dir)


def top_rated(base_dir: str, limit: int = 5) -> list:
    """Return top-rated snapshots sorted by stars descending."""
    data = _load_ratings(base_dir)
    ranked = sorted(data.items(), key=lambda kv: kv[1]["stars"], reverse=True)
    return [{"snapshot": name, **entry} for name, entry in ranked[:limit]]
