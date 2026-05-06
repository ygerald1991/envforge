"""Tests for envforge.snapshot_deps."""

import pytest
from pathlib import Path
from envforge.snapshot_deps import (
    add_dependency,
    remove_dependency,
    get_dependencies,
    get_dependents,
    get_all_dependencies,
)


@pytest.fixture
def ddir(tmp_path):
    return str(tmp_path)


def test_add_and_get_dependency(ddir):
    add_dependency(ddir, "snap_b", "snap_a")
    assert get_dependencies(ddir, "snap_b") == ["snap_a"]


def test_get_dependencies_missing_returns_empty(ddir):
    assert get_dependencies(ddir, "nonexistent") == []


def test_add_multiple_dependencies(ddir):
    add_dependency(ddir, "snap_c", "snap_a")
    add_dependency(ddir, "snap_c", "snap_b")
    deps = get_dependencies(ddir, "snap_c")
    assert "snap_a" in deps
    assert "snap_b" in deps
    assert len(deps) == 2


def test_duplicate_add_is_idempotent(ddir):
    add_dependency(ddir, "snap_b", "snap_a")
    add_dependency(ddir, "snap_b", "snap_a")
    assert get_dependencies(ddir, "snap_b") == ["snap_a"]


def test_remove_existing_dependency(ddir):
    add_dependency(ddir, "snap_b", "snap_a")
    result = remove_dependency(ddir, "snap_b", "snap_a")
    assert result is True
    assert get_dependencies(ddir, "snap_b") == []


def test_remove_nonexistent_dependency_returns_false(ddir):
    result = remove_dependency(ddir, "snap_b", "snap_a")
    assert result is False


def test_remove_one_of_multiple_dependencies(ddir):
    add_dependency(ddir, "snap_c", "snap_a")
    add_dependency(ddir, "snap_c", "snap_b")
    remove_dependency(ddir, "snap_c", "snap_a")
    deps = get_dependencies(ddir, "snap_c")
    assert deps == ["snap_b"]


def test_get_dependents_single(ddir):
    add_dependency(ddir, "snap_b", "snap_a")
    dependents = get_dependents(ddir, "snap_a")
    assert "snap_b" in dependents


def test_get_dependents_multiple(ddir):
    add_dependency(ddir, "snap_b", "snap_a")
    add_dependency(ddir, "snap_c", "snap_a")
    dependents = get_dependents(ddir, "snap_a")
    assert set(dependents) == {"snap_b", "snap_c"}


def test_get_dependents_none_returns_empty(ddir):
    assert get_dependents(ddir, "snap_a") == []


def test_get_all_dependencies_empty(ddir):
    assert get_all_dependencies(ddir) == {}


def test_get_all_dependencies_populated(ddir):
    add_dependency(ddir, "snap_b", "snap_a")
    add_dependency(ddir, "snap_c", "snap_b")
    all_deps = get_all_dependencies(ddir)
    assert "snap_b" in all_deps
    assert "snap_c" in all_deps


def test_persists_across_calls(ddir):
    add_dependency(ddir, "snap_b", "snap_a")
    # Re-read from disk
    deps = get_dependencies(ddir, "snap_b")
    assert deps == ["snap_a"]
