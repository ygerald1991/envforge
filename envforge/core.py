"""Core module for envforge — snapshot, diff, and restore environment variable sets."""

import os
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_SNAPSHOT_DIR = Path.home() / ".envforge" / "snapshots"


def _ensure_snapshot_dir(snapshot_dir: Path) -> None:
    """Create the snapshot directory if it doesn't exist."""
    snapshot_dir.mkdir(parents=True, exist_ok=True)


def capture_env(exclude_prefixes: Optional[list[str]] = None) -> dict[str, str]:
    """
    Capture the current environment variables.

    Args:
        exclude_prefixes: List of prefixes to exclude (e.g. ['_', 'BASH_']).

    Returns:
        A dictionary of environment variable key-value pairs.
    """
    exclude_prefixes = exclude_prefixes or []
    return {
        key: value
        for key, value in os.environ.items()
        if not any(key.startswith(prefix) for prefix in exclude_prefixes)
    }


def save_snapshot(
    name: str,
    env: dict[str, str],
    snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR,
    tags: Optional[list[str]] = None,
) -> Path:
    """
    Save an environment snapshot to disk as a JSON file.

    Args:
        name: Human-readable label for the snapshot (e.g. 'prod-2024-01').
        env: Dictionary of environment variables to snapshot.
        snapshot_dir: Directory where snapshots are stored.
        tags: Optional list of tags for categorisation.

    Returns:
        Path to the saved snapshot file.
    """
    _ensure_snapshot_dir(snapshot_dir)

    timestamp = datetime.now(timezone.utc).isoformat()
    checksum = hashlib.sha256(json.dumps(env, sort_keys=True).encode()).hexdigest()

    snapshot = {
        "name": name,
        "created_at": timestamp,
        "checksum": checksum,
        "tags": tags or [],
        "env": env,
    }

    # Sanitise name for use as a filename
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    filename = snapshot_dir / f"{safe_name}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)

    return filename


def load_snapshot(name: str, snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> dict:
    """
    Load a previously saved snapshot by name.

    Args:
        name: The snapshot name used when saving.
        snapshot_dir: Directory where snapshots are stored.

    Returns:
        The full snapshot dictionary including metadata and env vars.

    Raises:
        FileNotFoundError: If no snapshot with that name exists.
        ValueError: If the snapshot file is corrupt or has an invalid checksum.
    """
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    filename = snapshot_dir / f"{safe_name}.json"

    if not filename.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found at {filename}")

    with open(filename, "r", encoding="utf-8") as f:
        snapshot = json.load(f)

    # Verify checksum integrity on load
    expected = hashlib.sha256(
        json.dumps(snapshot["env"], sort_keys=True).encode()
    ).hexdigest()
    if snapshot.get("checksum") != expected:
        raise ValueError(
            f"Checksum mismatch for snapshot '{name}': file may be corrupt or tampered with."
        )

    return snapshot


def list_snapshots(snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> list[dict]:
    """
    List all available snapsh
