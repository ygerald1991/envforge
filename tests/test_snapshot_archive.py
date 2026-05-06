"""Tests for envforge.snapshot_archive."""

import json
import zipfile
from pathlib import Path
import pytest

from envforge.snapshot_archive import (
    archive_snapshot,
    list_archived_snapshots,
    extract_snapshot,
    delete_archive,
)


@pytest.fixture
def dirs(tmp_path):
    snap_dir = tmp_path / "snapshots"
    snap_dir.mkdir()
    archive_dir = tmp_path / "archives"
    return snap_dir, archive_dir, tmp_path


def _write_snapshot(snap_dir: Path, name: str, data: dict) -> Path:
    p = snap_dir / name
    p.write_text(json.dumps(data))
    return p


def test_archive_creates_zip(dirs):
    snap_dir, archive_dir, tmp_path = dirs
    snap = _write_snapshot(snap_dir, "dev.json", {"KEY": "val"})
    result = archive_snapshot(str(snap), str(archive_dir), "myarchive")
    assert result.exists()
    assert result.suffix == ".zip"


def test_archive_contains_snapshot(dirs):
    snap_dir, archive_dir, _ = dirs
    snap = _write_snapshot(snap_dir, "dev.json", {"A": "1"})
    archive_snapshot(str(snap), str(archive_dir), "myarchive")
    names = list_archived_snapshots(str(archive_dir), "myarchive")
    assert "dev.json" in names


def test_archive_multiple_snapshots(dirs):
    snap_dir, archive_dir, _ = dirs
    for name in ("dev.json", "prod.json", "staging.json"):
        snap = _write_snapshot(snap_dir, name, {"ENV": name})
        archive_snapshot(str(snap), str(archive_dir), "multi")
    names = list_archived_snapshots(str(archive_dir), "multi")
    assert set(names) == {"dev.json", "prod.json", "staging.json"}


def test_duplicate_add_does_not_duplicate(dirs):
    snap_dir, archive_dir, _ = dirs
    snap = _write_snapshot(snap_dir, "dev.json", {"X": "y"})
    archive_snapshot(str(snap), str(archive_dir), "myarchive")
    archive_snapshot(str(snap), str(archive_dir), "myarchive")
    names = list_archived_snapshots(str(archive_dir), "myarchive")
    assert names.count("dev.json") == 1


def test_list_missing_archive_returns_empty(dirs):
    _, archive_dir, _ = dirs
    result = list_archived_snapshots(str(archive_dir), "ghost")
    assert result == []


def test_archive_missing_snapshot_raises(dirs):
    _, archive_dir, _ = dirs
    with pytest.raises(FileNotFoundError):
        archive_snapshot("/nonexistent/snap.json", str(archive_dir), "a")


def test_extract_restores_file(dirs):
    snap_dir, archive_dir, tmp_path = dirs
    snap = _write_snapshot(snap_dir, "dev.json", {"K": "v"})
    archive_snapshot(str(snap), str(archive_dir), "myarchive")
    out_dir = tmp_path / "extracted"
    out_dir.mkdir()
    result = extract_snapshot(str(archive_dir), "myarchive", "dev.json", str(out_dir))
    assert result.exists()
    assert json.loads(result.read_text()) == {"K": "v"}


def test_extract_missing_archive_raises(dirs):
    _, archive_dir, tmp_path = dirs
    with pytest.raises(FileNotFoundError):
        extract_snapshot(str(archive_dir), "ghost", "dev.json", str(tmp_path))


def test_extract_missing_snapshot_raises(dirs):
    snap_dir, archive_dir, tmp_path = dirs
    snap = _write_snapshot(snap_dir, "dev.json", {})
    archive_snapshot(str(snap), str(archive_dir), "myarchive")
    with pytest.raises(KeyError):
        extract_snapshot(str(archive_dir), "myarchive", "missing.json", str(tmp_path))


def test_delete_archive(dirs):
    snap_dir, archive_dir, _ = dirs
    snap = _write_snapshot(snap_dir, "dev.json", {})
    archive_snapshot(str(snap), str(archive_dir), "myarchive")
    assert delete_archive(str(archive_dir), "myarchive") is True
    assert not (archive_dir / "myarchive.zip").exists()


def test_delete_missing_archive_returns_false(dirs):
    _, archive_dir, _ = dirs
    assert delete_archive(str(archive_dir), "ghost") is False
