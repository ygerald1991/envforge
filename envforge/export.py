"""Export snapshots to various formats (dotenv, JSON, shell script)."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

from envforge.core import load_snapshot


def export_as_dotenv(snapshot_name: str, snapshot_dir: str, output_path: Optional[str] = None) -> str:
    """Export a snapshot as a .env (dotenv) formatted string or file."""
    variables = load_snapshot(snapshot_name, snapshot_dir)

    lines = [f"# envforge snapshot: {snapshot_name}"]
    for key in sorted(variables):
        value = variables[key]
        # Quote values that contain spaces or special characters
        if any(c in value for c in (" ", "\t", "'", '"', "#", "$", "`")):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f"{key}={value}")

    content = "\n".join(lines) + "\n"

    if output_path:
        Path(output_path).write_text(content)

    return content


def export_as_json(snapshot_name: str, snapshot_dir: str, output_path: Optional[str] = None, indent: int = 2) -> str:
    """Export a snapshot as a JSON string or file."""
    variables = load_snapshot(snapshot_name, snapshot_dir)
    payload = {"snapshot": snapshot_name, "variables": variables}
    content = json.dumps(payload, indent=indent, sort_keys=True) + "\n"

    if output_path:
        Path(output_path).write_text(content)

    return content


def export_as_shell(snapshot_name: str, snapshot_dir: str, output_path: Optional[str] = None) -> str:
    """Export a snapshot as an executable shell export script."""
    variables = load_snapshot(snapshot_name, snapshot_dir)

    lines = [
        "#!/usr/bin/env sh",
        f"# envforge snapshot: {snapshot_name}",
        "",
    ]
    for key in sorted(variables):
        escaped = variables[key].replace("'", "'\"'\"'")
        lines.append(f"export {key}='{escaped}'")

    content = "\n".join(lines) + "\n"

    if output_path:
        path = Path(output_path)
        path.write_text(content)
        path.chmod(path.stat().st_mode | 0o111)

    return content


EXPORT_FORMATS = {
    "dotenv": export_as_dotenv,
    "json": export_as_json,
    "shell": export_as_shell,
}


def export_snapshot(snapshot_name: str, snapshot_dir: str, fmt: str, output_path: Optional[str] = None) -> str:
    """Dispatch export to the requested format handler."""
    if fmt not in EXPORT_FORMATS:
        raise ValueError(f"Unknown export format '{fmt}'. Choose from: {', '.join(EXPORT_FORMATS)}.")
    return EXPORT_FORMATS[fmt](snapshot_name, snapshot_dir, output_path)
