"""Tests for envforge.watch module."""

import os
import json
import pytest
from pathlib import Path
from unittest.mock import patch, call

from envforge.watch import watch_env, get_watch_snapshots, _timestamp_name
from envforge.core import load_snapshot


@pytest.fixture()
def snapshot_dir(tmp_path):
    d = tmp_path / ".envforge"
    d.mkdir()
    return str(d)


# ---------------------------------------------------------------------------
# _timestamp_name
# ---------------------------------------------------------------------------

def test_timestamp_name_default_prefix():
    name = _timestamp_name()
    assert name.startswith("watch_")


def test_timestamp_name_custom_prefix():
    name = _timestamp_name(prefix="ci")
    assert name.startswith("ci_")


def test_timestamp_name_contains_utc_marker():
    name = _timestamp_name()
    assert "Z" in name


# ---------------------------------------------------------------------------
# watch_env — no change
# ---------------------------------------------------------------------------

def test_no_change_saves_nothing(snapshot_dir):
    base_env = {"FOO": "bar", "HOME": "/home/user"}
    with patch("envforge.watch.capture_env", return_value=base_env), \
         patch("envforge.watch.time.sleep"):
        saved = watch_env(
            interval=0,
            snapshot_dir=snapshot_dir,
            iterations=3,
        )
    assert saved == []


# ---------------------------------------------------------------------------
# watch_env — detects a change
# ---------------------------------------------------------------------------

def test_change_saves_snapshot(snapshot_dir):
    env_before = {"FOO": "1"}
    env_after = {"FOO": "1", "BAR": "new"}
    side_effects = [env_before, env_after, env_after]

    with patch("envforge.watch.capture_env", side_effect=side_effects), \
         patch("envforge.watch.time.sleep"):
        saved = watch_env(
            interval=0,
            snapshot_dir=snapshot_dir,
            prefix="test",
            iterations=2,
        )

    assert len(saved) == 1
    assert saved[0].startswith("test_")


def test_change_snapshot_has_new_value(snapshot_dir):
    env_before = {"FOO": "old"}
    env_after = {"FOO": "new"}

    with patch("envforge.watch.capture_env", side_effect=[env_before, env_after]), \
         patch("envforge.watch.time.sleep"):
        saved = watch_env(
            interval=0,
            snapshot_dir=snapshot_dir,
            prefix="chk",
            iterations=1,
        )

    snap = load_snapshot(saved[0], snapshot_dir=snapshot_dir)
    assert snap["variables"]["FOO"] == "new"


def test_on_change_callback_is_called(snapshot_dir):
    env_before = {"X": "1"}
    env_after = {"X": "2"}
    received = []

    with patch("envforge.watch.capture_env", side_effect=[env_before, env_after]), \
         patch("envforge.watch.time.sleep"):
        watch_env(
            interval=0,
            snapshot_dir=snapshot_dir,
            on_change=lambda d: received.append(d),
            iterations=1,
        )

    assert len(received) == 1
    assert "changed" in received[0]


def test_max_snapshots_stops_watch(snapshot_dir):
    envs = [{"K": str(i)} for i in range(10)]

    with patch("envforge.watch.capture_env", side_effect=envs), \
         patch("envforge.watch.time.sleep"):
        saved = watch_env(
            interval=0,
            snapshot_dir=snapshot_dir,
            max_snapshots=3,
            iterations=None,
        )

    assert len(saved) == 3


# ---------------------------------------------------------------------------
# get_watch_snapshots
# ---------------------------------------------------------------------------

def test_get_watch_snapshots_filters_by_prefix(snapshot_dir):
    env_v = {"A": "1"}
    for name in ("watch_20240101T000000Z", "watch_20240102T000000Z", "other_20240103T000000Z"):
        path = Path(snapshot_dir) / f"{name}.json"
        path.write_text(json.dumps({"variables": env_v}))

    snaps = get_watch_snapshots(prefix="watch", snapshot_dir=snapshot_dir)
    assert len(snaps) == 2
    assert all(s.startswith("watch_") for s in snaps)
