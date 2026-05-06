"""Snapshot workflow: define ordered sequences of snapshots for promotion pipelines."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _get_workflow_path(base_dir: str) -> Path:
    return Path(base_dir) / "workflows.json"


def _load_workflows(base_dir: str) -> Dict[str, List[str]]:
    path = _get_workflow_path(base_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_workflows(base_dir: str, index: Dict[str, List[str]]) -> None:
    path = _get_workflow_path(base_dir)
    Path(base_dir).mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index, indent=2))


def create_workflow(base_dir: str, name: str, steps: List[str]) -> Dict:
    """Create or replace a named workflow with an ordered list of snapshot steps."""
    if not steps:
        raise ValueError("A workflow must have at least one step.")
    index = _load_workflows(base_dir)
    index[name] = list(steps)
    _save_workflows(base_dir, index)
    return {"name": name, "steps": index[name]}


def get_workflow(base_dir: str, name: str) -> Optional[List[str]]:
    """Return the ordered steps for a workflow, or None if not found."""
    return _load_workflows(base_dir).get(name)


def list_workflows(base_dir: str) -> List[str]:
    """Return all workflow names."""
    return list(_load_workflows(base_dir).keys())


def delete_workflow(base_dir: str, name: str) -> bool:
    """Delete a workflow by name. Returns True if it existed."""
    index = _load_workflows(base_dir)
    if name not in index:
        return False
    del index[name]
    _save_workflows(base_dir, index)
    return True


def append_step(base_dir: str, name: str, snapshot: str) -> List[str]:
    """Append a snapshot step to an existing workflow."""
    index = _load_workflows(base_dir)
    if name not in index:
        raise KeyError(f"Workflow '{name}' does not exist.")
    if snapshot not in index[name]:
        index[name].append(snapshot)
        _save_workflows(base_dir, index)
    return index[name]
