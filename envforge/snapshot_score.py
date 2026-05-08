"""Snapshot scoring: assign, retrieve, and rank snapshots by a numeric score."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def _get_score_path(store_dir: str) -> Path:
    return Path(store_dir) / ".score_index.json"


def _load_scores(store_dir: str) -> dict:
    path = _get_score_path(store_dir)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_scores(store_dir: str, data: dict) -> None:
    path = _get_score_path(store_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_score(store_dir: str, snapshot_name: str, score: float) -> float:
    """Assign a numeric score (0.0–100.0) to a snapshot."""
    if not (0.0 <= score <= 100.0):
        raise ValueError(f"Score must be between 0.0 and 100.0, got {score}")
    data = _load_scores(store_dir)
    data[snapshot_name] = score
    _save_scores(store_dir, data)
    return score


def get_score(store_dir: str, snapshot_name: str) -> Optional[float]:
    """Return the score for a snapshot, or None if not set."""
    return _load_scores(store_dir).get(snapshot_name)


def remove_score(store_dir: str, snapshot_name: str) -> bool:
    """Remove the score for a snapshot. Returns True if it existed."""
    data = _load_scores(store_dir)
    if snapshot_name not in data:
        return False
    del data[snapshot_name]
    _save_scores(store_dir, data)
    return True


def rank_snapshots(store_dir: str, descending: bool = True) -> list[tuple[str, float]]:
    """Return all scored snapshots sorted by score."""
    data = _load_scores(store_dir)
    return sorted(data.items(), key=lambda kv: kv[1], reverse=descending)
