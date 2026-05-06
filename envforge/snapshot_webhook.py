"""Webhook notification support for snapshot events."""

from __future__ import annotations

import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any

_WEBHOOK_FILE = "webhooks.json"


def _get_webhook_path(base_dir: str) -> Path:
    return Path(base_dir) / _WEBHOOK_FILE


def _load_webhooks(base_dir: str) -> dict:
    path = _get_webhook_path(base_dir)
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save_webhooks(base_dir: str, data: dict) -> None:
    path = _get_webhook_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def register_webhook(base_dir: str, name: str, url: str, events: list[str] | None = None) -> dict:
    """Register a webhook URL for given event types."""
    if not url.startswith(("http://", "https://")):
        raise ValueError(f"Invalid webhook URL: {url!r}")
    webhooks = _load_webhooks(base_dir)
    entry = {"url": url, "events": events or ["capture", "restore", "merge"]}
    webhooks[name] = entry
    _save_webhooks(base_dir, webhooks)
    return entry


def remove_webhook(base_dir: str, name: str) -> bool:
    """Remove a registered webhook by name. Returns True if removed."""
    webhooks = _load_webhooks(base_dir)
    if name not in webhooks:
        return False
    del webhooks[name]
    _save_webhooks(base_dir, webhooks)
    return True


def list_webhooks(base_dir: str) -> dict:
    """Return all registered webhooks."""
    return _load_webhooks(base_dir)


def fire_event(base_dir: str, event: str, payload: dict[str, Any]) -> list[dict]:
    """Fire an event to all matching webhooks. Returns list of result dicts."""
    webhooks = _load_webhooks(base_dir)
    results = []
    body = json.dumps({"event": event, **payload}).encode()
    for name, cfg in webhooks.items():
        if event not in cfg.get("events", []):
            continue
        req = urllib.request.Request(
            cfg["url"],
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                results.append({"webhook": name, "status": resp.status, "error": None})
        except urllib.error.URLError as exc:
            results.append({"webhook": name, "status": None, "error": str(exc)})
    return results
