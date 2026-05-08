"""Snapshot trigger rules: define conditions that auto-trigger a snapshot capture."""

import json
from pathlib import Path
from typing import Any

VALID_CONDITIONS = {"key_added", "key_removed", "value_changed", "any_change"}


def _get_trigger_path(store_dir: str) -> Path:
    return Path(store_dir) / "trigger_rules.json"


def _load_triggers(store_dir: str) -> dict:
    path = _get_trigger_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_triggers(store_dir: str, data: dict) -> None:
    path = _get_trigger_path(store_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def set_trigger(store_dir: str, name: str, condition: str, prefix: str = "auto") -> dict:
    """Register a named trigger rule with a condition and optional snapshot prefix."""
    if condition not in VALID_CONDITIONS:
        raise ValueError(
            f"Invalid condition '{condition}'. Must be one of: {sorted(VALID_CONDITIONS)}"
        )
    triggers = _load_triggers(store_dir)
    entry: dict[str, Any] = {"condition": condition, "prefix": prefix, "enabled": True}
    triggers[name] = entry
    _save_triggers(store_dir, triggers)
    return entry


def get_trigger(store_dir: str, name: str) -> dict | None:
    """Return the trigger rule for *name*, or None if not found."""
    return _load_triggers(store_dir).get(name)


def remove_trigger(store_dir: str, name: str) -> bool:
    """Delete a trigger rule. Returns True if it existed, False otherwise."""
    triggers = _load_triggers(store_dir)
    if name not in triggers:
        return False
    del triggers[name]
    _save_triggers(store_dir, triggers)
    return True


def list_triggers(store_dir: str) -> dict:
    """Return all registered trigger rules."""
    return _load_triggers(store_dir)


def set_trigger_enabled(store_dir: str, name: str, enabled: bool) -> dict:
    """Enable or disable an existing trigger without removing it."""
    triggers = _load_triggers(store_dir)
    if name not in triggers:
        raise KeyError(f"Trigger '{name}' not found.")
    triggers[name]["enabled"] = enabled
    _save_triggers(store_dir, triggers)
    return triggers[name]
