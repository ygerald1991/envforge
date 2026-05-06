"""Snapshot archiving: compress and store snapshots in a zip archive."""

import json
import zipfile
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional


def _get_archive_path(base_dir: str, archive_name: str) -> Path:
    return Path(base_dir) / f"{archive_name}.zip"


def archive_snapshot(snapshot_path: str, archive_dir: str, archive_name: str) -> Path:
    """Add a snapshot JSON file into a named zip archive."""
    src = Path(snapshot_path)
    if not src.exists():
        raise FileNotFoundError(f"Snapshot not found: {snapshot_path}")

    Path(archive_dir).mkdir(parents=True, exist_ok=True)
    archive_path = _get_archive_path(archive_dir, archive_name)

    with zipfile.ZipFile(archive_path, mode="a", compression=zipfile.ZIP_DEFLATED) as zf:
        # avoid duplicates
        if src.name not in zf.namelist():
            zf.write(src, arcname=src.name)

    return archive_path


def list_archived_snapshots(archive_dir: str, archive_name: str) -> List[str]:
    """Return the names of snapshots stored in an archive."""
    archive_path = _get_archive_path(archive_dir, archive_name)
    if not archive_path.exists():
        return []
    with zipfile.ZipFile(archive_path, mode="r") as zf:
        return sorted(zf.namelist())


def extract_snapshot(archive_dir: str, archive_name: str, snapshot_name: str, dest_dir: str) -> Path:
    """Extract a single snapshot from an archive to dest_dir."""
    archive_path = _get_archive_path(archive_dir, archive_name)
    if not archive_path.exists():
        raise FileNotFoundError(f"Archive not found: {archive_path}")

    with zipfile.ZipFile(archive_path, mode="r") as zf:
        if snapshot_name not in zf.namelist():
            raise KeyError(f"Snapshot '{snapshot_name}' not in archive '{archive_name}'")
        zf.extract(snapshot_name, path=dest_dir)

    return Path(dest_dir) / snapshot_name


def delete_archive(archive_dir: str, archive_name: str) -> bool:
    """Delete an entire archive file. Returns True if deleted, False if not found."""
    archive_path = _get_archive_path(archive_dir, archive_name)
    if archive_path.exists():
        archive_path.unlink()
        return True
    return False
