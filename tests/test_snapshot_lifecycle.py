"""Tests for envforge.snapshot_lifecycle."""

import pytest
from pathlib import Path
from envforge.snapshot_lifecycle import (
    set_lifecycle_state,
    get_lifecycle_state,
    list_by_state,
    remove_lifecycle_state,
    VALID_STATES,
)


@pytest.fixture
def ldir(tmp_path):
    return str(tmp_path)


def test_set_and_get_state(ldir):
    entry = set_lifecycle_state(ldir, "snap1", "active")
    assert entry["state"] == "active"
    assert "updated_at" in entry
    assert get_lifecycle_state(ldir, "snap1") == "active"


def test_get_missing_state_returns_none(ldir):
    assert get_lifecycle_state(ldir, "nonexistent") is None


def test_overwrite_existing_state(ldir):
    set_lifecycle_state(ldir, "snap1", "draft")
    set_lifecycle_state(ldir, "snap1", "deprecated")
    assert get_lifecycle_state(ldir, "snap1") == "deprecated"


def test_invalid_state_raises(ldir):
    with pytest.raises(ValueError, match="Invalid state"):
        set_lifecycle_state(ldir, "snap1", "unknown")


def test_list_by_state_returns_matching(ldir):
    set_lifecycle_state(ldir, "snap1", "active")
    set_lifecycle_state(ldir, "snap2", "active")
    set_lifecycle_state(ldir, "snap3", "draft")
    result = list_by_state(ldir, "active")
    assert set(result) == {"snap1", "snap2"}


def test_list_by_state_empty(ldir):
    assert list_by_state(ldir, "archived") == []


def test_list_by_invalid_state_raises(ldir):
    with pytest.raises(ValueError, match="Invalid state"):
        list_by_state(ldir, "bogus")


def test_remove_existing_state(ldir):
    set_lifecycle_state(ldir, "snap1", "active")
    removed = remove_lifecycle_state(ldir, "snap1")
    assert removed is True
    assert get_lifecycle_state(ldir, "snap1") is None


def test_remove_missing_state_returns_false(ldir):
    assert remove_lifecycle_state(ldir, "ghost") is False


def test_all_valid_states_accepted(ldir):
    for i, state in enumerate(VALID_STATES):
        entry = set_lifecycle_state(ldir, f"snap{i}", state)
        assert entry["state"] == state


def test_persists_across_calls(ldir):
    set_lifecycle_state(ldir, "persistent", "archived")
    # Simulate a fresh load by calling get independently
    result = get_lifecycle_state(ldir, "persistent")
    assert result == "archived"


def test_index_file_is_created(ldir):
    set_lifecycle_state(ldir, "snap1", "draft")
    assert (Path(ldir) / ".lifecycle.json").exists()
