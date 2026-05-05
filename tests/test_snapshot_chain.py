"""Tests for envforge.snapshot_chain."""

from __future__ import annotations

import pytest

from envforge.snapshot_chain import (
    get_ancestors,
    get_children,
    get_parent,
    remove_from_chain,
    set_parent,
)


@pytest.fixture()
def cdir(tmp_path):
    return str(tmp_path)


def test_set_and_get_parent(cdir):
    set_parent(cdir, "child", "parent")
    assert get_parent(cdir, "child") == "parent"


def test_get_parent_missing_returns_none(cdir):
    assert get_parent(cdir, "nonexistent") is None


def test_overwrite_parent(cdir):
    set_parent(cdir, "child", "parent_v1")
    set_parent(cdir, "child", "parent_v2")
    assert get_parent(cdir, "child") == "parent_v2"


def test_get_ancestors_single_level(cdir):
    set_parent(cdir, "child", "root")
    assert get_ancestors(cdir, "child") == ["root"]


def test_get_ancestors_multi_level(cdir):
    set_parent(cdir, "c", "b")
    set_parent(cdir, "b", "a")
    assert get_ancestors(cdir, "c") == ["b", "a"]


def test_get_ancestors_no_parent(cdir):
    assert get_ancestors(cdir, "orphan") == []


def test_get_ancestors_cycle_protection(cdir):
    """A cycle must not cause infinite recursion."""
    set_parent(cdir, "a", "b")
    set_parent(cdir, "b", "a")
    result = get_ancestors(cdir, "a")
    assert len(result) == 2
    assert set(result) == {"a", "b"}


def test_get_children_basic(cdir):
    set_parent(cdir, "child1", "root")
    set_parent(cdir, "child2", "root")
    children = get_children(cdir, "root")
    assert set(children) == {"child1", "child2"}


def test_get_children_empty(cdir):
    assert get_children(cdir, "leaf") == []


def test_remove_existing_entry(cdir):
    set_parent(cdir, "snap", "base")
    assert remove_from_chain(cdir, "snap") is True
    assert get_parent(cdir, "snap") is None


def test_remove_nonexistent_returns_false(cdir):
    assert remove_from_chain(cdir, "ghost") is False


def test_index_persists_across_calls(cdir):
    set_parent(cdir, "x", "y")
    set_parent(cdir, "a", "b")
    assert get_parent(cdir, "x") == "y"
    assert get_parent(cdir, "a") == "b"
