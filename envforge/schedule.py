"""Schedule periodic automatic snapshots of environment variables."""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

DEFAULT_SCHEDULE_FILE = ".envforge_schedule.json"


def _get_schedule_path(base_dir: str = ".") -> Path:
    return Path(base_dir) / DEFAULT_SCHEDULE_FILE


def load_schedule(base_dir: str = ".") -> dict:
    path = _get_schedule_path(base_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_schedule(schedule: dict, base_dir: str = ".") -> None:
    path = _get_schedule_path(base_dir)
    with open(path, "w") as f:
        json.dump(schedule, f, indent=2)


def set_schedule(
    name: str,
    interval_seconds: int,
    label_prefix: str = "auto",
    base_dir: str = ".",
) -> dict:
    """Register a named schedule entry."""
    schedule = load_schedule(base_dir)
    schedule[name] = {
        "interval_seconds": interval_seconds,
        "label_prefix": label_prefix,
        "last_run": None,
        "created_at": datetime.utcnow().isoformat(),
    }
    save_schedule(schedule, base_dir)
    return schedule[name]


def remove_schedule(name: str, base_dir: str = ".") -> bool:
    """Remove a named schedule. Returns True if it existed."""
    schedule = load_schedule(base_dir)
    if name not in schedule:
        return False
    del schedule[name]
    save_schedule(schedule, base_dir)
    return True


def get_due_schedules(base_dir: str = ".") -> list:
    """Return schedule names that are due to run."""
    schedule = load_schedule(base_dir)
    now = time.time()
    due = []
    for name, entry in schedule.items():
        last_run = entry.get("last_run")
        interval = entry.get("interval_seconds", 3600)
        if last_run is None:
            due.append(name)
        else:
            last_ts = datetime.fromisoformat(last_run).timestamp()
            if now - last_ts >= interval:
                due.append(name)
    return due


def mark_ran(name: str, base_dir: str = ".") -> None:
    """Update last_run timestamp for a schedule entry."""
    schedule = load_schedule(base_dir)
    if name in schedule:
        schedule[name]["last_run"] = datetime.utcnow().isoformat()
        save_schedule(schedule, base_dir)


def list_schedules(base_dir: str = ".") -> dict:
    return load_schedule(base_dir)
