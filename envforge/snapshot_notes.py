"""Attach, retrieve, and manage human-readable notes for snapshots."""

import json
from pathlib import Path
from typing import Optional


def _get_notes_path(snapshot_dir: str) -> Path:
    return Path(snapshot_dir) / ".snapshot_notes.json"


def _load_notes(snapshot_dir: str) -> dict:
    path = _get_notes_path(snapshot_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_notes(snapshot_dir: str, notes: dict) -> None:
    path = _get_notes_path(snapshot_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(notes, f, indent=2)


def set_note(snapshot_dir: str, snapshot_name: str, note: str) -> None:
    """Attach a note to a snapshot, replacing any existing note."""
    notes = _load_notes(snapshot_dir)
    notes[snapshot_name] = note
    _save_notes(snapshot_dir, notes)


def get_note(snapshot_dir: str, snapshot_name: str) -> Optional[str]:
    """Return the note for a snapshot, or None if not set."""
    notes = _load_notes(snapshot_dir)
    return notes.get(snapshot_name)


def remove_note(snapshot_dir: str, snapshot_name: str) -> bool:
    """Remove the note for a snapshot. Returns True if a note was removed."""
    notes = _load_notes(snapshot_dir)
    if snapshot_name not in notes:
        return False
    del notes[snapshot_name]
    _save_notes(snapshot_dir, notes)
    return True


def list_notes(snapshot_dir: str) -> dict:
    """Return all snapshot notes as a dict of {snapshot_name: note}."""
    return _load_notes(snapshot_dir)


def format_notes(notes: dict) -> str:
    """Format notes dict as a human-readable string."""
    if not notes:
        return "No notes found."
    lines = []
    for name, note in sorted(notes.items()):
        lines.append(f"  {name}: {note}")
    return "\n".join(lines)
