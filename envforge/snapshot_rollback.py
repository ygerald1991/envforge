"""Snapshot rollback support: track rollback history and revert to a previous snapshot."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_ROLLBACK_FILE = "rollback_log.json"


def _get_rollback_path(store_dir: str) -> Path:
    return Path(store_dir) / _ROLLBACK_FILE


def _load_rollback_log(store_dir: str) -> list[dict]:
    path = _get_rollback_path(store_dir)
    if not path.exists():
        return []
    with path.open() as fh:
        return json.load(fh)


def _save_rollback_log(store_dir: str, log: list[dict]) -> None:
    path = _get_rollback_path(store_dir)
    Path(store_dir).mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(log, fh, indent=2)


def record_rollback(store_dir: str, from_snapshot: str, to_snapshot: str, reason: str = "") -> dict:
    """Record a rollback event from one snapshot to another."""
    entry = {
        "from": from_snapshot,
        "to": to_snapshot,
        "reason": reason,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    log = _load_rollback_log(store_dir)
    log.append(entry)
    _save_rollback_log(store_dir, log)
    return entry


def get_rollback_log(store_dir: str, snapshot: Optional[str] = None) -> list[dict]:
    """Return rollback log, optionally filtered to entries involving *snapshot*."""
    log = _load_rollback_log(store_dir)
    if snapshot is None:
        return log
    return [e for e in log if e["from"] == snapshot or e["to"] == snapshot]


def get_last_rollback(store_dir: str) -> Optional[dict]:
    """Return the most recent rollback entry, or None if the log is empty."""
    log = _load_rollback_log(store_dir)
    return log[-1] if log else None


def format_rollback_log(entries: list[dict]) -> str:
    """Return a human-readable representation of rollback log entries."""
    if not entries:
        return "No rollback events recorded."
    lines = []
    for e in entries:
        reason_part = f" ({e['reason']})" if e.get("reason") else ""
        lines.append(f"[{e['timestamp']}] {e['from']} -> {e['to']}{reason_part}")
    return "\n".join(lines)
