"""Tests for envforge.snapshot_freeze."""

from __future__ import annotations

import pytest
from pathlib import Path
from envforge.snapshot_freeze import (
    freeze_snapshot,
    unfreeze_snapshot,
    is_frozen,
    list_frozen,
)


@pytest.fixture()
def fdir(tmp_path: Path) -> str:
    return str(tmp_path / "store")


def test_freeze_creates_index(fdir: str) -> None:
    freeze_snapshot(fdir, "snap-a")
    assert Path(fdir, "freeze_index.json").exists()


def test_frozen_snapshot_is_detected(fdir: str) -> None:
    freeze_snapshot(fdir, "snap-a")
    assert is_frozen(fdir, "snap-a") is True


def test_unfrozen_snapshot_not_detected(fdir: str) -> None:
    assert is_frozen(fdir, "snap-missing") is False


def test_unfreeze_removes_entry(fdir: str) -> None:
    freeze_snapshot(fdir, "snap-a")
    unfreeze_snapshot(fdir, "snap-a")
    assert is_frozen(fdir, "snap-a") is False


def test_unfreeze_nonexistent_is_noop(fdir: str) -> None:
    # Should not raise
    unfreeze_snapshot(fdir, "snap-ghost")
    assert is_frozen(fdir, "snap-ghost") is False


def test_duplicate_freeze_is_idempotent(fdir: str) -> None:
    freeze_snapshot(fdir, "snap-a")
    freeze_snapshot(fdir, "snap-a")
    assert list_frozen(fdir).count("snap-a") == 1


def test_list_frozen_returns_all(fdir: str) -> None:
    freeze_snapshot(fdir, "snap-a")
    freeze_snapshot(fdir, "snap-b")
    result = list_frozen(fdir)
    assert "snap-a" in result
    assert "snap-b" in result


def test_list_frozen_empty_store(fdir: str) -> None:
    assert list_frozen(fdir) == []


def test_freeze_multiple_independent_snapshots(fdir: str) -> None:
    freeze_snapshot(fdir, "snap-x")
    assert is_frozen(fdir, "snap-x") is True
    assert is_frozen(fdir, "snap-y") is False


def test_unfreeze_only_removes_target(fdir: str) -> None:
    freeze_snapshot(fdir, "snap-a")
    freeze_snapshot(fdir, "snap-b")
    unfreeze_snapshot(fdir, "snap-a")
    assert is_frozen(fdir, "snap-a") is False
    assert is_frozen(fdir, "snap-b") is True


def test_list_frozen_sorted(fdir: str) -> None:
    freeze_snapshot(fdir, "snap-c")
    freeze_snapshot(fdir, "snap-a")
    freeze_snapshot(fdir, "snap-b")
    result = list_frozen(fdir)
    assert result == sorted(result)
