"""Tests for envforge.snapshot_workflow."""

from __future__ import annotations

import pytest
from envforge.snapshot_workflow import (
    create_workflow,
    get_workflow,
    list_workflows,
    delete_workflow,
    append_step,
)


@pytest.fixture()
def wdir(tmp_path):
    return str(tmp_path)


def test_create_workflow_returns_dict(wdir):
    result = create_workflow(wdir, "deploy", ["dev", "staging", "prod"])
    assert result["name"] == "deploy"
    assert result["steps"] == ["dev", "staging", "prod"]


def test_create_workflow_persists(wdir):
    create_workflow(wdir, "release", ["snap1", "snap2"])
    steps = get_workflow(wdir, "release")
    assert steps == ["snap1", "snap2"]


def test_get_missing_workflow_returns_none(wdir):
    assert get_workflow(wdir, "nonexistent") is None


def test_create_empty_steps_raises(wdir):
    with pytest.raises(ValueError, match="at least one step"):
        create_workflow(wdir, "empty", [])


def test_list_workflows_empty(wdir):
    assert list_workflows(wdir) == []


def test_list_workflows_returns_names(wdir):
    create_workflow(wdir, "alpha", ["a"])
    create_workflow(wdir, "beta", ["b"])
    names = list_workflows(wdir)
    assert set(names) == {"alpha", "beta"}


def test_delete_existing_workflow(wdir):
    create_workflow(wdir, "to_delete", ["x"])
    removed = delete_workflow(wdir, "to_delete")
    assert removed is True
    assert get_workflow(wdir, "to_delete") is None


def test_delete_missing_workflow_returns_false(wdir):
    assert delete_workflow(wdir, "ghost") is False


def test_create_replaces_existing(wdir):
    create_workflow(wdir, "pipe", ["a", "b"])
    create_workflow(wdir, "pipe", ["x"])
    assert get_workflow(wdir, "pipe") == ["x"]


def test_append_step_adds_to_end(wdir):
    create_workflow(wdir, "pipe", ["dev"])
    steps = append_step(wdir, "pipe", "prod")
    assert steps == ["dev", "prod"]


def test_append_step_duplicate_is_idempotent(wdir):
    create_workflow(wdir, "pipe", ["dev", "prod"])
    steps = append_step(wdir, "pipe", "prod")
    assert steps.count("prod") == 1


def test_append_step_missing_workflow_raises(wdir):
    with pytest.raises(KeyError, match="does not exist"):
        append_step(wdir, "missing", "snap")
