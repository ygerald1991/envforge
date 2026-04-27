"""Compare multiple snapshots side-by-side and summarize environment drift."""

from typing import Dict, List, Optional
from envforge.core import load_snapshot


def compare_snapshots(snapshot_names: List[str], base_dir: Optional[str] = None) -> Dict:
    """Load and compare multiple snapshots, returning a unified comparison structure.

    Returns a dict with:
      - keys: sorted union of all keys across snapshots
      - snapshots: ordered list of snapshot names
      - matrix: {key: {snapshot_name: value_or_None}}
      - drift: keys where values differ across at least two snapshots
    """
    if len(snapshot_names) < 2:
        raise ValueError("At least two snapshot names are required for comparison.")

    loaded = {}
    for name in snapshot_names:
        loaded[name] = load_snapshot(name, base_dir=base_dir)

    all_keys = sorted(set(k for snap in loaded.values() for k in snap))

    matrix = {}
    for key in all_keys:
        matrix[key] = {name: loaded[name].get(key) for name in snapshot_names}

    drift = [
        key for key, vals in matrix.items()
        if len(set(v for v in vals.values() if v is not None)) > 1
        or len([v for v in vals.values() if v is None]) > 0
    ]

    return {
        "keys": all_keys,
        "snapshots": snapshot_names,
        "matrix": matrix,
        "drift": drift,
    }


def format_comparison(comparison: Dict, show_all: bool = False) -> str:
    """Render a comparison dict as a human-readable table."""
    snapshots = comparison["snapshots"]
    matrix = comparison["matrix"]
    drift = set(comparison["drift"])
    keys_to_show = comparison["keys"] if show_all else [k for k in comparison["keys"] if k in drift]

    if not keys_to_show:
        return "No drift detected across snapshots.\n"

    col_width = max(20, *(len(s) for s in snapshots), *(len(k) for k in keys_to_show)) + 2
    header = f"{'KEY':<{col_width}}" + "".join(f"{s:<{col_width}}" for s in snapshots)
    separator = "-" * len(header)

    lines = [header, separator]
    for key in keys_to_show:
        row = f"{key:<{col_width}}"
        for snap in snapshots:
            val = matrix[key].get(snap)
            cell = val if val is not None else "<missing>"
            row += f"{cell:<{col_width}}"
        lines.append(row)

    return "\n".join(lines) + "\n"
