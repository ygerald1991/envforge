"""Snapshot event hooks: register and fire callbacks on snapshot lifecycle events."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Dict, List, Optional

_VALID_EVENTS = {"on_capture", "on_restore", "on_delete", "on_merge", "on_export"}

_registry: Dict[str, List[Callable[[str, dict], None]]] = {event: [] for event in _VALID_EVENTS}


def _get_event_hooks_path(base_dir: str) -> Path:
    return Path(base_dir) / "event_hooks.json"


def _load_event_hooks(base_dir: str) -> dict:
    path = _get_event_hooks_path(base_dir)
    if not path.exists():
        return {event: [] for event in _VALID_EVENTS}
    with open(path) as f:
        return json.load(f)


def _save_event_hooks(base_dir: str, hooks: dict) -> None:
    path = _get_event_hooks_path(base_dir)
    Path(base_dir).mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(hooks, f, indent=2)


def register_hook(base_dir: str, event: str, label: str) -> dict:
    """Persist a named hook label for a given event type."""
    if event not in _VALID_EVENTS:
        raise ValueError(f"Unknown event '{event}'. Valid events: {sorted(_VALID_EVENTS)}")
    hooks = _load_event_hooks(base_dir)
    if label not in hooks.get(event, []):
        hooks.setdefault(event, []).append(label)
    _save_event_hooks(base_dir, hooks)
    return {"event": event, "label": label}


def remove_hook(base_dir: str, event: str, label: str) -> bool:
    """Remove a named hook label. Returns True if it existed."""
    hooks = _load_event_hooks(base_dir)
    if label in hooks.get(event, []):
        hooks[event].remove(label)
        _save_event_hooks(base_dir, hooks)
        return True
    return False


def get_hooks(base_dir: str, event: Optional[str] = None) -> dict:
    """Return all hooks, or hooks for a specific event."""
    hooks = _load_event_hooks(base_dir)
    if event is not None:
        if event not in _VALID_EVENTS:
            raise ValueError(f"Unknown event '{event}'.")
        return {event: hooks.get(event, [])}
    return hooks


def fire_event(event: str, snapshot_name: str, context: Optional[dict] = None) -> List[str]:
    """Fire in-process callbacks registered for an event. Returns list of fired labels."""
    if event not in _registry:
        return []
    ctx = context or {}
    fired = []
    for cb in _registry[event]:
        cb(snapshot_name, ctx)
        fired.append(getattr(cb, "__name__", repr(cb)))
    return fired


def subscribe(event: str, callback: Callable[[str, dict], None]) -> None:
    """Register an in-process callback for a lifecycle event."""
    if event not in _VALID_EVENTS:
        raise ValueError(f"Unknown event '{event}'.")
    _registry[event].append(callback)


def clear_subscribers(event: Optional[str] = None) -> None:
    """Clear in-process subscribers (useful in tests)."""
    global _registry
    if event:
        _registry[event] = []
    else:
        _registry = {e: [] for e in _VALID_EVENTS}
