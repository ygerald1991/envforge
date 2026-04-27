"""Watch for environment variable changes and record diffs over time."""

import os
import time
from datetime import datetime
from typing import Callable, Optional

from envforge.core import capture_env, save_snapshot
from envforge.diff import diff_snapshots


def _timestamp_name(prefix: str = "watch") -> str:
    """Generate a snapshot name based on current timestamp."""
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}_{ts}"


def watch_env(
    interval: float = 5.0,
    snapshot_dir: str = ".envforge",
    prefix: str = "watch",
    max_snapshots: int = 10,
    on_change: Optional[Callable[[dict], None]] = None,
    iterations: Optional[int] = None,
) -> list:
    """
    Poll the environment at `interval` seconds and save a new snapshot
    whenever a change is detected.  Returns a list of saved snapshot names.

    Parameters
    ----------
    interval      : seconds between polls
    snapshot_dir  : directory used by envforge snapshots
    prefix        : name prefix for auto-generated snapshots
    max_snapshots : stop after saving this many change-snapshots (0 = unlimited)
    on_change     : optional callback(diff_dict) invoked on every detected change
    iterations    : if set, only poll this many times total (useful for tests)
    """
    saved: list = []
    previous = capture_env()
    poll = 0

    while True:
        time.sleep(interval)
        current = capture_env()
        diff = diff_snapshots(
            {"variables": previous},
            {"variables": current},
        )

        changed = any(diff[k] for k in ("added", "removed", "changed"))
        if changed:
            name = _timestamp_name(prefix)
            save_snapshot(name, current, snapshot_dir=snapshot_dir)
            saved.append(name)
            if on_change is not None:
                on_change(diff)
            previous = current

        poll += 1
        if iterations is not None and poll >= iterations:
            break
        if max_snapshots and len(saved) >= max_snapshots:
            break

    return saved


def get_watch_snapshots(prefix: str = "watch", snapshot_dir: str = ".envforge") -> list:
    """Return all snapshot names that were created by the watcher (by prefix)."""
    from envforge.core import list_snapshots
    return [s for s in list_snapshots(snapshot_dir=snapshot_dir) if s.startswith(prefix + "_")]
