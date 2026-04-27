"""Audit log for snapshot operations in envforge."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

AUDIT_LOG_FILENAME = "audit.log"


def _get_audit_log_path(snapshot_dir: str) -> Path:
    return Path(snapshot_dir) / AUDIT_LOG_FILENAME


def record_event(
    snapshot_dir: str,
    action: str,
    snapshot_name: str,
    metadata: Optional[dict] = None,
) -> None:
    """Append an audit event to the audit log."""
    log_path = _get_audit_log_path(snapshot_dir)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "snapshot": snapshot_name,
        "user": os.environ.get("USER", os.environ.get("USERNAME", "unknown")),
        "metadata": metadata or {},
    }
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def read_audit_log(snapshot_dir: str) -> list[dict]:
    """Return all audit log entries as a list of dicts."""
    log_path = _get_audit_log_path(snapshot_dir)
    if not log_path.exists():
        return []
    entries = []
    with open(log_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def format_audit_log(entries: list[dict]) -> str:
    """Return a human-readable string of audit log entries."""
    if not entries:
        return "No audit events recorded."
    lines = []
    for e in entries:
        meta_str = ""
        if e.get("metadata"):
            meta_str = "  " + ", ".join(f"{k}={v}" for k, v in e["metadata"].items())
        lines.append(
            f"[{e['timestamp']}] {e['action']:12s} snapshot={e['snapshot']}  user={e['user']}{meta_str}"
        )
    return "\n".join(lines)
