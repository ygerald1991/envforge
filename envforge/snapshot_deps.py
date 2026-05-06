"""Snapshot dependency tracking: record which snapshots were derived from others."""

import json
from pathlib import Path
from typing import Dict, List, Optional


def _get_deps_path(base_dir: str) -> Path:
    return Path(base_dir) / ".envforge" / "snapshot_deps.json"


def _load_deps(base_dir: str) -> Dict[str, List[str]]:
    path = _get_deps_path(base_dir)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_deps(base_dir: str, deps: Dict[str, List[str]]) -> None:
    path = _get_deps_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(deps, f, indent=2)


def add_dependency(base_dir: str, snapshot: str, depends_on: str) -> None:
    """Record that `snapshot` depends on `depends_on`."""
    deps = _load_deps(base_dir)
    current = deps.get(snapshot, [])
    if depends_on not in current:
        current.append(depends_on)
    deps[snapshot] = current
    _save_deps(base_dir, deps)


def remove_dependency(base_dir: str, snapshot: str, depends_on: str) -> bool:
    """Remove a specific dependency. Returns True if it existed."""
    deps = _load_deps(base_dir)
    current = deps.get(snapshot, [])
    if depends_on not in current:
        return False
    current.remove(depends_on)
    if current:
        deps[snapshot] = current
    else:
        deps.pop(snapshot, None)
    _save_deps(base_dir, deps)
    return True


def get_dependencies(base_dir: str, snapshot: str) -> List[str]:
    """Return all snapshots that `snapshot` directly depends on."""
    deps = _load_deps(base_dir)
    return deps.get(snapshot, [])


def get_dependents(base_dir: str, snapshot: str) -> List[str]:
    """Return all snapshots that depend on `snapshot`."""
    deps = _load_deps(base_dir)
    return [snap for snap, parents in deps.items() if snapshot in parents]


def get_all_dependencies(base_dir: str) -> Dict[str, List[str]]:
    """Return the full dependency index."""
    return _load_deps(base_dir)
