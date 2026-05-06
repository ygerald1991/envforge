"""Compute similarity scores between snapshots based on shared keys/values."""

from __future__ import annotations

import os
from typing import Dict, List, Tuple

from envforge.core import load_snapshot


def _jaccard(set_a: set, set_b: set) -> float:
    """Return Jaccard similarity coefficient for two sets."""
    if not set_a and not set_b:
        return 1.0
    union = set_a | set_b
    intersection = set_a & set_b
    return len(intersection) / len(union)


def key_similarity(vars_a: Dict[str, str], vars_b: Dict[str, str]) -> float:
    """Fraction of keys shared between two variable dicts (Jaccard)."""
    return _jaccard(set(vars_a.keys()), set(vars_b.keys()))


def value_similarity(vars_a: Dict[str, str], vars_b: Dict[str, str]) -> float:
    """Fraction of key=value pairs that are identical across both dicts."""
    pairs_a = set(vars_a.items())
    pairs_b = set(vars_b.items())
    return _jaccard(pairs_a, pairs_b)


def compare_similarity(
    snapshot_dir: str,
    name_a: str,
    name_b: str,
) -> Dict[str, float]:
    """Return key and value similarity scores for two named snapshots."""
    snap_a = load_snapshot(snapshot_dir, name_a)
    snap_b = load_snapshot(snapshot_dir, name_b)
    vars_a: Dict[str, str] = snap_a.get("vars", {})
    vars_b: Dict[str, str] = snap_b.get("vars", {})
    return {
        "key_similarity": key_similarity(vars_a, vars_b),
        "value_similarity": value_similarity(vars_a, vars_b),
    }


def rank_by_similarity(
    snapshot_dir: str,
    reference: str,
    candidates: List[str],
    mode: str = "value",
) -> List[Tuple[str, float]]:
    """Rank *candidates* by similarity to *reference*.

    Args:
        snapshot_dir: Directory containing snapshots.
        reference: Name of the reference snapshot.
        candidates: Names of snapshots to rank.
        mode: ``"key"`` or ``"value"`` similarity metric.

    Returns:
        List of (name, score) tuples sorted descending by score.
    """
    if mode not in ("key", "value"):
        raise ValueError(f"Unknown similarity mode: {mode!r}. Use 'key' or 'value'.")

    ref_snap = load_snapshot(snapshot_dir, reference)
    ref_vars: Dict[str, str] = ref_snap.get("vars", {})

    results: List[Tuple[str, float]] = []
    for name in candidates:
        snap = load_snapshot(snapshot_dir, name)
        cand_vars: Dict[str, str] = snap.get("vars", {})
        if mode == "key":
            score = key_similarity(ref_vars, cand_vars)
        else:
            score = value_similarity(ref_vars, cand_vars)
        results.append((name, score))

    results.sort(key=lambda t: t[1], reverse=True)
    return results
