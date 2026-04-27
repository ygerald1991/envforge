"""Restore environment snapshots to shell export scripts or current process."""

import os
from typing import Optional
from envforge.core import load_snapshot


def restore_to_env(snapshot_name: str, snapshots_dir: str = ".envforge") -> dict:
    """Load a snapshot and apply it to the current process environment.

    Returns the dict of variables that were applied.
    """
    snapshot = load_snapshot(snapshot_name, snapshots_dir)
    variables = snapshot.get("variables", {})

    for key, value in variables.items():
        os.environ[key] = value

    return variables


def restore_to_shell_script(
    snapshot_name: str,
    snapshots_dir: str = ".envforge",
    shell: str = "bash",
    output_path: Optional[str] = None,
) -> str:
    """Generate a shell script that exports all variables from a snapshot.

    Supports 'bash'/'sh' and 'fish' shell formats.
    Returns the script content as a string, and writes to output_path if given.
    """
    snapshot = load_snapshot(snapshot_name, snapshots_dir)
    variables = snapshot.get("variables", {})

    lines = []
    if shell in ("bash", "sh"):
        lines.append("#!/usr/bin/env bash")
        lines.append(f"# Restored from envforge snapshot: {snapshot_name}")
        for key, value in sorted(variables.items()):
            escaped = value.replace('"', '\\"')
            lines.append(f'export {key}="{escaped}"')
    elif shell == "fish":
        lines.append(f"# Restored from envforge snapshot: {snapshot_name}")
        for key, value in sorted(variables.items()):
            escaped = value.replace('"', '\\"')
            lines.append(f'set -x {key} "{escaped}"')
    else:
        raise ValueError(f"Unsupported shell: {shell!r}. Use 'bash', 'sh', or 'fish'.")

    script = "\n".join(lines) + "\n"

    if output_path:
        with open(output_path, "w") as f:
            f.write(script)

    return script


def selective_restore(
    snapshot_name: str,
    keys: list,
    snapshots_dir: str = ".envforge",
) -> dict:
    """Restore only specific keys from a snapshot into the current process.

    Returns a dict of the keys that were applied.
    """
    snapshot = load_snapshot(snapshot_name, snapshots_dir)
    variables = snapshot.get("variables", {})
    applied = {}

    for key in keys:
        if key in variables:
            os.environ[key] = variables[key]
            applied[key] = variables[key]

    return applied
