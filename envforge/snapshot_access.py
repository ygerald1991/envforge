"""Track and query access (read) events for snapshots."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


def _get_access_log_path(base_dir: str) -> Path:
    return Path(base_dir) / ".envforge_access_log.json"


def _load_access_log(base_dir: str) -> List[dict]:
    path = _get_access_log_path(base_dir)
    if not path.exists():
        return []
    with open(path, "r") as f:
        return json.load(f)


def _save_access_log(base_dir: str, log: List[dict]) -> None:
    path = _get_access_log_path(base_dir)
    Path(base_dir).mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(log, f, indent=2)


def record_access(base_dir: str, snapshot_name: str, action: str = "read", actor: Optional[str] = None) -> dict:
    """Record an access event for a snapshot."""
    entry = {
        "snapshot": snapshot_name,
        "action": action,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": actor or os.environ.get("USER", "unknown"),
    }
    log = _load_access_log(base_dir)
    log.append(entry)
    _save_access_log(base_dir, log)
    return entry


def get_access_log(base_dir: str, snapshot_name: Optional[str] = None) -> List[dict]:
    """Return access log entries, optionally filtered by snapshot name."""
    log = _load_access_log(base_dir)
    if snapshot_name is not None:
        log = [e for e in log if e["snapshot"] == snapshot_name]
    return log


def get_last_accessed(base_dir: str, snapshot_name: str) -> Optional[dict]:
    """Return the most recent access entry for a snapshot, or None."""
    entries = get_access_log(base_dir, snapshot_name)
    return entries[-1] if entries else None


def format_access_log(entries: List[dict]) -> str:
    """Format access log entries as a human-readable string."""
    if not entries:
        return "No access records found."
    lines = []
    for e in entries:
        actor = e.get("actor", "unknown")
        lines.append(f"[{e['timestamp']}] {e['action'].upper():8s}  {e['snapshot']}  (by {actor})")
    return "\n".join(lines)
