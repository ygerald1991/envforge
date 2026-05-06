"""Tests for envforge.snapshot_event."""

from __future__ import annotations

import pytest

from envforge.snapshot_event import (
    clear_subscribers,
    fire_event,
    get_hooks,
    register_hook,
    remove_hook,
    subscribe,
)


@pytest.fixture
def edir(tmp_path):
    return str(tmp_path / "hooks")


# --- register_hook ---

def test_register_hook_creates_entry(edir):
    entry = register_hook(edir, "on_capture", "notify_slack")
    assert entry["event"] == "on_capture"
    assert entry["label"] == "notify_slack"


def test_register_hook_persists(edir):
    register_hook(edir, "on_restore", "log_restore")
    hooks = get_hooks(edir, event="on_restore")
    assert "log_restore" in hooks["on_restore"]


def test_register_duplicate_is_idempotent(edir):
    register_hook(edir, "on_export", "my_hook")
    register_hook(edir, "on_export", "my_hook")
    hooks = get_hooks(edir, event="on_export")
    assert hooks["on_export"].count("my_hook") == 1


def test_register_invalid_event_raises(edir):
    with pytest.raises(ValueError, match="Unknown event"):
        register_hook(edir, "on_invalid", "some_hook")


# --- remove_hook ---

def test_remove_existing_hook_returns_true(edir):
    register_hook(edir, "on_merge", "to_remove")
    result = remove_hook(edir, "on_merge", "to_remove")
    assert result is True


def test_remove_missing_hook_returns_false(edir):
    result = remove_hook(edir, "on_merge", "ghost_hook")
    assert result is False


def test_remove_hook_no_longer_in_list(edir):
    register_hook(edir, "on_delete", "temp_hook")
    remove_hook(edir, "on_delete", "temp_hook")
    hooks = get_hooks(edir, event="on_delete")
    assert "temp_hook" not in hooks["on_delete"]


# --- get_hooks ---

def test_get_hooks_all_events_returned(edir):
    hooks = get_hooks(edir)
    assert "on_capture" in hooks
    assert "on_restore" in hooks
    assert "on_delete" in hooks


def test_get_hooks_filtered_by_event(edir):
    register_hook(edir, "on_capture", "hook_a")
    hooks = get_hooks(edir, event="on_capture")
    assert list(hooks.keys()) == ["on_capture"]


def test_get_hooks_invalid_event_raises(edir):
    with pytest.raises(ValueError):
        get_hooks(edir, event="on_unknown")


# --- subscribe / fire_event ---

def test_fire_event_calls_subscriber(edir):
    clear_subscribers()
    called = []

    def my_cb(name, ctx):
        called.append((name, ctx))

    subscribe("on_capture", my_cb)
    fire_event("on_capture", "snap1", {"key": "val"})
    assert len(called) == 1
    assert called[0] == ("snap1", {"key": "val"})
    clear_subscribers()


def test_fire_event_no_subscribers_returns_empty():
    clear_subscribers()
    result = fire_event("on_delete", "snap2")
    assert result == []


def test_subscribe_invalid_event_raises():
    with pytest.raises(ValueError):
        subscribe("on_bogus", lambda n, c: None)
