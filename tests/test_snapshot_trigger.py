"""Tests for envforge.snapshot_trigger."""

import pytest

from envforge.snapshot_trigger import (
    set_trigger,
    get_trigger,
    remove_trigger,
    list_triggers,
    set_trigger_enabled,
)


@pytest.fixture()
def tdir(tmp_path):
    return str(tmp_path)


# ---------------------------------------------------------------------------
# set_trigger / get_trigger
# ---------------------------------------------------------------------------

def test_set_returns_entry(tdir):
    entry = set_trigger(tdir, "watch_prod", "any_change")
    assert entry["condition"] == "any_change"
    assert entry["prefix"] == "auto"
    assert entry["enabled"] is True


def test_set_custom_prefix(tdir):
    entry = set_trigger(tdir, "ci", "value_changed", prefix="ci-snap")
    assert entry["prefix"] == "ci-snap"


def test_get_existing_trigger(tdir):
    set_trigger(tdir, "t1", "key_added")
    result = get_trigger(tdir, "t1")
    assert result is not None
    assert result["condition"] == "key_added"


def test_get_missing_trigger_returns_none(tdir):
    assert get_trigger(tdir, "ghost") is None


def test_invalid_condition_raises(tdir):
    with pytest.raises(ValueError, match="Invalid condition"):
        set_trigger(tdir, "bad", "on_fire")


def test_overwrite_existing_trigger(tdir):
    set_trigger(tdir, "t1", "key_added")
    set_trigger(tdir, "t1", "key_removed", prefix="new-prefix")
    entry = get_trigger(tdir, "t1")
    assert entry["condition"] == "key_removed"
    assert entry["prefix"] == "new-prefix"


# ---------------------------------------------------------------------------
# remove_trigger
# ---------------------------------------------------------------------------

def test_remove_existing_returns_true(tdir):
    set_trigger(tdir, "t1", "any_change")
    assert remove_trigger(tdir, "t1") is True
    assert get_trigger(tdir, "t1") is None


def test_remove_missing_returns_false(tdir):
    assert remove_trigger(tdir, "nope") is False


# ---------------------------------------------------------------------------
# list_triggers
# ---------------------------------------------------------------------------

def test_list_empty_store(tdir):
    assert list_triggers(tdir) == {}


def test_list_multiple_triggers(tdir):
    set_trigger(tdir, "a", "key_added")
    set_trigger(tdir, "b", "value_changed")
    rules = list_triggers(tdir)
    assert set(rules.keys()) == {"a", "b"}


# ---------------------------------------------------------------------------
# set_trigger_enabled
# ---------------------------------------------------------------------------

def test_disable_trigger(tdir):
    set_trigger(tdir, "t1", "any_change")
    entry = set_trigger_enabled(tdir, "t1", False)
    assert entry["enabled"] is False


def test_enable_trigger(tdir):
    set_trigger(tdir, "t1", "any_change")
    set_trigger_enabled(tdir, "t1", False)
    entry = set_trigger_enabled(tdir, "t1", True)
    assert entry["enabled"] is True


def test_enable_missing_trigger_raises(tdir):
    with pytest.raises(KeyError, match="not found"):
        set_trigger_enabled(tdir, "ghost", True)


def test_persists_across_calls(tdir):
    set_trigger(tdir, "persist", "key_removed", prefix="snap")
    # reload from disk via a fresh list_triggers call
    rules = list_triggers(tdir)
    assert "persist" in rules
    assert rules["persist"]["prefix"] == "snap"
