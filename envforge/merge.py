"""Merge multiple snapshots into a single combined snapshot."""

from typing import Dict, List, Optional
from envforge.core import load_snapshot, save_snapshot


MERGE_STRATEGY_LAST_WINS = "last_wins"
MERGE_STRATEGY_FIRST_WINS = "first_wins"
MERGE_STRATEGY_ERROR_ON_CONFLICT = "error_on_conflict"


def merge_snapshots(
    snapshot_names: List[str],
    snapshot_dir: str,
    strategy: str = MERGE_STRATEGY_LAST_WINS,
) -> Dict[str, str]:
    """Merge multiple named snapshots into a single dict of env vars.

    Args:
        snapshot_names: Ordered list of snapshot names to merge.
        snapshot_dir: Directory where snapshots are stored.
        strategy: Conflict resolution strategy when the same key appears
                  in more than one snapshot.

    Returns:
        Merged dictionary of environment variables.

    Raises:
        ValueError: If strategy is unknown or a conflict is detected under
                    MERGE_STRATEGY_ERROR_ON_CONFLICT.
        FileNotFoundError: If a referenced snapshot does not exist.
    """
    if strategy not in (
        MERGE_STRATEGY_LAST_WINS,
        MERGE_STRATEGY_FIRST_WINS,
        MERGE_STRATEGY_ERROR_ON_CONFLICT,
    ):
        raise ValueError(f"Unknown merge strategy: {strategy!r}")

    merged: Dict[str, str] = {}

    for name in snapshot_names:
        snapshot = load_snapshot(name, snapshot_dir)
        variables: Dict[str, str] = snapshot.get("variables", {})

        for key, value in variables.items():
            if key in merged:
                if strategy == MERGE_STRATEGY_ERROR_ON_CONFLICT:
                    raise ValueError(
                        f"Conflict: key {key!r} exists in multiple snapshots"
                    )
                elif strategy == MERGE_STRATEGY_FIRST_WINS:
                    continue  # keep existing value
            merged[key] = value

    return merged


def save_merged_snapshot(
    snapshot_names: List[str],
    output_name: str,
    snapshot_dir: str,
    strategy: str = MERGE_STRATEGY_LAST_WINS,
    metadata: Optional[Dict] = None,
) -> str:
    """Merge snapshots and persist the result as a new snapshot.

    Args:
        snapshot_names: Ordered list of snapshot names to merge.
        output_name: Name for the resulting merged snapshot.
        snapshot_dir: Directory where snapshots are stored.
        strategy: Conflict resolution strategy.
        metadata: Optional extra metadata to attach to the merged snapshot.

    Returns:
        Path to the saved merged snapshot file.
    """
    merged_vars = merge_snapshots(snapshot_names, snapshot_dir, strategy)
    extra_meta = metadata or {}
    extra_meta["merged_from"] = snapshot_names
    extra_meta["merge_strategy"] = strategy
    return save_snapshot(output_name, merged_vars, snapshot_dir, extra_meta)
