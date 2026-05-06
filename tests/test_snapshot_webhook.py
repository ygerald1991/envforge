"""Tests for envforge.snapshot_webhook."""

from __future__ import annotations

import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from envforge.snapshot_webhook import (
    register_webhook,
    remove_webhook,
    list_webhooks,
    fire_event,
)


@pytest.fixture
def wdir(tmp_path):
    return str(tmp_path)


def test_register_creates_entry(wdir):
    entry = register_webhook(wdir, "slack", "https://hooks.example.com/abc")
    assert entry["url"] == "https://hooks.example.com/abc"
    assert "capture" in entry["events"]


def test_register_persists_to_file(wdir):
    register_webhook(wdir, "slack", "https://hooks.example.com/abc")
    path = Path(wdir) / "webhooks.json"
    assert path.exists()
    data = json.loads(path.read_text())
    assert "slack" in data


def test_register_custom_events(wdir):
    entry = register_webhook(wdir, "ci", "https://ci.example.com", events=["capture"])
    assert entry["events"] == ["capture"]


def test_register_invalid_url_raises(wdir):
    with pytest.raises(ValueError, match="Invalid webhook URL"):
        register_webhook(wdir, "bad", "ftp://not-valid.com")


def test_remove_existing_returns_true(wdir):
    register_webhook(wdir, "slack", "https://hooks.example.com/abc")
    result = remove_webhook(wdir, "slack")
    assert result is True


def test_remove_missing_returns_false(wdir):
    result = remove_webhook(wdir, "nonexistent")
    assert result is False


def test_remove_deletes_entry(wdir):
    register_webhook(wdir, "slack", "https://hooks.example.com/abc")
    remove_webhook(wdir, "slack")
    hooks = list_webhooks(wdir)
    assert "slack" not in hooks


def test_list_empty_returns_empty_dict(wdir):
    assert list_webhooks(wdir) == {}


def test_list_returns_all_hooks(wdir):
    register_webhook(wdir, "a", "https://a.example.com")
    register_webhook(wdir, "b", "https://b.example.com")
    hooks = list_webhooks(wdir)
    assert set(hooks.keys()) == {"a", "b"}


def test_fire_event_calls_matching_hooks(wdir):
    register_webhook(wdir, "ci", "https://ci.example.com", events=["capture"])
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
        results = fire_event(wdir, "capture", {"snapshot": "snap1"})
    assert len(results) == 1
    assert results[0]["status"] == 200
    assert results[0]["error"] is None
    mock_open.assert_called_once()


def test_fire_event_skips_non_matching_hooks(wdir):
    register_webhook(wdir, "ci", "https://ci.example.com", events=["restore"])
    with patch("urllib.request.urlopen") as mock_open:
        results = fire_event(wdir, "capture", {"snapshot": "snap1"})
    assert results == []
    mock_open.assert_not_called()


def test_fire_event_records_error_on_failure(wdir):
    import urllib.error
    register_webhook(wdir, "fail", "https://fail.example.com", events=["capture"])
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timeout")):
        results = fire_event(wdir, "capture", {})
    assert results[0]["error"] is not None
    assert results[0]["status"] is None
