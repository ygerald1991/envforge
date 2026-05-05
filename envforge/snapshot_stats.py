"""Compute statistics and summaries over a collection of snapshots."""

from __future__ import annotations

import os
from collections import Counter
from typing import Any

from envforge.core import load_snapshot, list_snapshots


def _load_all(snapshot_dir: str) -> dict[str, dict[str, str]]:
    """Return {name: vars} for every readable snapshot in *snapshot_dir*."""
    result: dict[str, dict[str, str]] = {}
    for name in list_snapshots(snapshot_dir):
        try:
            snap = load_snapshot(snapshot_dir, name)
            result[name] = snap.get("vars", {})
        except Exception:
            pass
    return result


def key_frequency(snapshot_dir: str) -> dict[str, int]:
    """Return a mapping of env-var key -> number of snapshots it appears in."""
    counter: Counter[str] = Counter()
    for vars_ in _load_all(snapshot_dir).values():
        counter.update(vars_.keys())
    return dict(counter)


def most_common_keys(snapshot_dir: str, top_n: int = 10) -> list[tuple[str, int]]:
    """Return the *top_n* most common keys across all snapshots."""
    freq = key_frequency(snapshot_dir)
    return sorted(freq.items(), key=lambda kv: kv[1], reverse=True)[:top_n]


def unique_values_per_key(snapshot_dir: str) -> dict[str, set[str]]:
    """Return a mapping of key -> set of distinct values seen across snapshots."""
    mapping: dict[str, set[str]] = {}
    for vars_ in _load_all(snapshot_dir).values():
        for k, v in vars_.items():
            mapping.setdefault(k, set()).add(v)
    return mapping


def snapshot_summary(snapshot_dir: str) -> dict[str, Any]:
    """High-level statistics dict for the snapshot store."""
    all_snaps = _load_all(snapshot_dir)
    if not all_snaps:
        return {
            "total_snapshots": 0,
            "total_unique_keys": 0,
            "avg_keys_per_snapshot": 0.0,
            "most_common_keys": [],
        }

    sizes = [len(v) for v in all_snaps.values()]
    freq = key_frequency(snapshot_dir)
    return {
        "total_snapshots": len(all_snaps),
        "total_unique_keys": len(freq),
        "avg_keys_per_snapshot": sum(sizes) / len(sizes),
        "most_common_keys": most_common_keys(snapshot_dir, top_n=5),
    }


def format_summary(summary: dict[str, Any]) -> str:
    """Render a *snapshot_summary* dict as a human-readable string."""
    lines = [
        f"Total snapshots     : {summary['total_snapshots']}",
        f"Unique keys seen    : {summary['total_unique_keys']}",
        f"Avg keys/snapshot   : {summary['avg_keys_per_snapshot']:.1f}",
        "Top keys:",
    ]
    for key, count in summary.get("most_common_keys", []):
        lines.append(f"  {key:<30} {count} snapshot(s)")
    return os.linesep.join(lines)
